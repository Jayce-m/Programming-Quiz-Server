from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json

html = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Login</title>
    </head>
    <body>
        <form method="post">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username"><br><br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password"><br><br>
            <input type="submit" value="Submit">
        </form>
    </body>
</html>
"""

class TestManager(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(html, 'utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data_dict = parse_qs(post_data)
        username = data_dict['username'][0]
        password = data_dict['password'][0]
    
        with open('TM/storage/users/users.json') as json_file:
            data = json.load(json_file)
            if(username in data):
                if(password == data[username]['password']):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    fullName = data[username]['fullname']
                    questionNum = data[username]['question']
                    curAttempt = data[username]['attempt']
                    self.wfile.write(bytes("<html><head><title>Test Manager</title></head><body><h1>Test Manager</h1><h2>Welcome, %s (ID: %s)!</h2><h3> You are on question %s (attempt %s) out of 10</h3><body><html>" % (fullName,username,questionNum,curAttempt), 'utf-8'))

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
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, TestManager)
    httpd.serve_forever()