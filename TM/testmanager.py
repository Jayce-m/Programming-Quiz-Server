from http.server import BaseHTTPRequestHandler, HTTPServer
import http.cookies
from urllib.parse import urlparse, parse_qs
import json
import random, string, datetime

landing = open('TM/index.html', 'r').read()

testpage = """
<html>
   <head>
      <style>logoutLblPos{position:fixed;right:10px;top:5px;}</style>
      <title>Test Manager</title>
   </head>
   <body>
      <h1>Test Manager</h1>
      <h2>Welcome, %s (ID: %s)!</h2>
      <h3> You are on question %s (attempt %s) out of 10</h3>
      <form align='right' name='form1' method='post' action='logout'><label class='logoutLblPos'><input name='submit2' type='submit' id='submit2' value='log out'></label></form>
      <body>
         <html>
         """

def genSessionID():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))


def serveTest(httpd, username, fullName, questionNum, curAttempt):
    httpd.wfile.write(bytes(testpage % (fullName,username,questionNum,curAttempt), 'utf-8'))
class TestManager(BaseHTTPRequestHandler):
    def do_GET(self):
        #Check if the user has logged in before
        cookie = self.headers.get('Cookie')
        if cookie:
            for c in cookie.split(';'):
                name, value = c.strip().split('=')
                if name == 'session-id':
                    session_id = value
                    with open('TM/storage/users/users.json') as json_file:
                        data = json.load(json_file)
                        for user in data:
                            if(data[user]['session-id'] == session_id):
                                fullName = data[user]['fullname']
                                questionNum = data[user]['question']
                                curAttempt = data[user]['attempt']

                                #Serve test
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                serveTest(self, user, fullName, questionNum, curAttempt)
                                return
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        self.wfile.write(bytes(landing, 'utf-8'))
        

    def do_POST(self):
        if(self.path == '/logout'):
            #Get session ID
            cookie = self.headers.get('Cookie')
            for c in cookie.split(';'):
                name, value = c.strip().split('=')
                if name == 'session-id':
                    session_id = value
                    with open('TM/storage/users/users.json') as json_file:
                        data = json.load(json_file)
                        for user in data:
                            if(data[user]['session-id'] == session_id):
                                #Remove session ID
                                data[user]['session-id'] = ''
                                with open('TM/storage/users/users.json', 'w') as outfile:
                                    json.dump(data, outfile, indent=4)
                                break
            #Serve landing page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            self.wfile.write(bytes(landing, 'utf-8'))
            return
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data_dict = parse_qs(post_data)
            username = data_dict['username'][0]
            password = data_dict['password'][0]
    
            with open('TM/storage/users/users.json') as json_file:
                data = json.load(json_file)
                if(username in data):
                    if(password == data[username]['password']):
                        #Generate Session ID
                        sessionid = genSessionID()
                        cookie = http.cookies.SimpleCookie()
                        cookie['session-id'] = sessionid
                        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
                        cookie['session-id']['expires'] = expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
                    
                        #Send HTTP headers and response
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Set-Cookie', cookie.output(header=''))
                        self.end_headers()

                        #Retrieve relevant information and store session ID in json
                        data[username]['session-id'] = sessionid
                        with open('TM/storage/users/users.json', 'w') as outfile:
                            json.dump(data, outfile, indent=4)
                        fullName = data[username]['fullname']
                        questionNum = data[username]['question']
                        curAttempt = data[username]['attempt']

                        #Serve HTML page
                        serveTest(self, username, fullName, questionNum, curAttempt)
                    else:
                        self.send_response(401)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(bytes("Wrong password!", 'utf-8'))
                else:
                    self.send_response(401)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(bytes("User not found!", 'utf-8'))

if __name__ == '__main__':
    try:
        server_address = ('', 8000)
        httpd = HTTPServer(server_address, TestManager)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Server is terminated')
        httpd.socket.close()