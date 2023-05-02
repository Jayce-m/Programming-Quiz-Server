import os
basedir = os.path.abspath(os.path.dirname(__file__))

from http.server import BaseHTTPRequestHandler, HTTPServer
import http.cookies
from urllib.parse import urlparse, parse_qs
import json,random,string,datetime,socket
import requestQuestions

landing = open(os.path.join(basedir, 'landing.html'), 'r').read()
testpage = open(os.path.join(basedir, 'test.html'), 'r').read()


def genSessionID():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))


def serveTest(httpd, username, fullName, questionNum, curAttempt, curMarks):

    # TODO: request questions from the question bank
    # Request questions.
    #requestQuestions.request()

    # If there exists a username.json, open and store in data
    
    # iterate over the questions json file inside storage
    # TODO: change the path to the username.json
    with open(os.path.join(basedir, 'storage/users/usersQuestions/' + username + '.json')) as json_file:
        # Load the questions from the file
        data = json.load(json_file)

        # Get the current question
        current_question = data[questionNum-1]

    # if the question is multiple choice then display options.
    if (current_question['multiple'] == True):
        # Get the options for the current question
        options = current_question['options']

        # Generate HTML code for options
        options_html = ''
        for option in options:
            options_html += '<div class="form-check">'
            options_html += '<input class="form-check-input" type="radio" name="answer" id="%s" value="%s">' % (
                option, option)
            options_html += '<label class="form-check-label" for="%s">%s</label>' % (
                option, option)
            options_html += '</div>'

        # Fill in placeholders in HTML document
        html_doc = open(os.path.join(basedir, 'test.html'), 'r').read()
        filled_doc = html_doc % (fullName, username, curMarks,
                                questionNum, current_question['question'], options_html)
        script_doc = open(os.path.join(basedir, 'script.html'), 'r').read()
        filled_doc = filled_doc + (script_doc % (questionNum, curAttempt))

        # Send response to client
        httpd.wfile.write(bytes(filled_doc, 'utf-8'))

    elif (current_question['multiple'] == False):
        # generate HTML ace editor
        programming_html = """<div class="d-flex justify-content-center align-items-center vh-100">
        <div class="container">
            <div id="editor-container">
                <div id="editor">testing</div>
                </div>
            </div>
        </div>"""

        # Open html doc
        html_doc = open(os.path.join(basedir, 'test.html'), 'r').read()


        # Fill in placeholders in HTML document
        #FIXME: needs extra format specifiers in test.html
        filled_doc = html_doc % (fullName, username, curMarks,
                                questionNum, current_question['question'], programming_html)        
        script_doc = open(os.path.join(basedir, 'script.html'), 'r').read()
        filled_doc = filled_doc + (script_doc % (questionNum, curAttempt))
        
        # Send response to client
        httpd.wfile.write(bytes(filled_doc, 'utf-8'))



class TestManager(BaseHTTPRequestHandler):
    def do_GET(self):
        # Check if the user has logged in before
        cookie = self.headers.get('Cookie')
        if cookie:
            for c in cookie.split(';'):
                name, value = c.strip().split('=')
                if name == 'session-id':
                    session_id = value

                    with open(os.path.join(basedir, 'storage/users/users.json')) as json_file:
                        data = json.load(json_file)
                        for user in data:
                            if (data[user]['session-id'] == session_id):
                                fullName = data[user]['fullname']
                                questionNum = data[user]['question']
                                curAttempt = data[user]['attempts'][str(questionNum)]
                                curMarks = data[user]['marks']

                                # Serve test
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                serveTest(self, user, fullName,
                                          questionNum, curAttempt, curMarks)
                                return
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        landing = open(os.path.join(basedir, 'landing.html'), 'r').read()
        self.wfile.write(bytes(landing, 'utf-8'))

    def do_POST(self):
        if (self.path == '/logout'):
            # Get session ID
            cookie = self.headers.get('Cookie')
            if cookie is None:
                self.send_response(401)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes("Session expired!", 'utf-8'))
                return
            for c in cookie.split(';'):
                name, value = c.strip().split('=')
                if name == 'session-id':
                    session_id = value
                    with open(os.path.join(basedir, 'storage/users/users.json')) as json_file:
                        data = json.load(json_file)
                        for user in data:
                            if (data[user]['session-id'] == session_id):
                                # Remove session ID
                                data[user]['session-id'] = ''
                                with open(os.path.join(basedir, 'storage/users/users.json'),'w') as outfile:
                                    json.dump(data, outfile, indent=4)
                                break
            # Serve landing page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            landing = open(os.path.join(basedir, 'landing.html'), 'r').read()
            self.wfile.write(bytes(landing, 'utf-8'))
            return
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data_dict = parse_qs(post_data)
            username = data_dict['username'][0]
            password = data_dict['password'][0]

            with open(os.path.join(basedir, 'storage/users/users.json')) as json_file:
                data = json.load(json_file)
                if (username in data):
                    if (password == data[username]['password']):
                        # Generate Session ID
                        sessionid = genSessionID()
                        cookie = http.cookies.SimpleCookie()
                        cookie['session-id'] = sessionid
                        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
                        cookie['session-id']['expires'] = expires.strftime(
                            "%a, %d-%b-%Y %H:%M:%S GMT")

                        # Send HTTP headers and response
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.send_header(
                            'Set-Cookie', cookie.output(header=''))
                        self.end_headers()

                        # Retrieve relevant information and store session ID in json
                        data[username]['session-id'] = sessionid
                        with open('storage/users/users.json', 'w') as outfile:
                            json.dump(data, outfile, indent=4)
                        fullName = data[username]['fullname']
                        questionNum = data[username]['question']
                        curAttempt = data[username]['attempts'][str(questionNum)]
                        curMarks = data[username]['marks']

                        # Serve HTML page
                        serveTest(self, username, fullName,
                                  questionNum, curAttempt, curMarks)
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
        if self.path == '/next':
            # Get session ID
            cookie = self.headers.get('Cookie')
            if cookie is None:
                self.send_response(401)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes("Session expired!", 'utf-8'))
                return
            for c in cookie.split(';'):
                name, value = c.strip().split('=')
                if name == 'session-id':
                    session_id = value
                    with open(os.path.join(basedir, 'storage/users/users.json')) as json_file:
                        data = json.load(json_file)
                        for user in data:
                            if (data[user]['session-id'] == session_id):
                                if (data[user]['question'] >= 10):
                                    return
                                data[user]['question'] += 1
                                fullName = data[user]['fullname']
                                questionNum = data[user]['question']
                                curAttempt = data[user]['attempts'][str(questionNum)]
                                curMarks = data[user]['marks']
                                with open(os.path.join(basedir, 'storage/users/users.json'),'w') as outfile:
                                    json.dump(data, outfile, indent=4)
                                # Serve test
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                serveTest(self, user, fullName, questionNum, curAttempt, curMarks)
                                return
                    self.send_response(401)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(bytes("Session expired!", 'utf-8'))
        if self.path == '/back':
            # Get session ID
            cookie = self.headers.get('Cookie')
            if cookie is None:
                self.send_response(401)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes("Session expired!", 'utf-8'))
                return
            for c in cookie.split(';'):
                name, value = c.strip().split('=')
                if name == 'session-id':
                    session_id = value
                    with open(os.path.join(basedir, 'storage/users/users.json')) as json_file:
                        data = json.load(json_file)
                        for user in data:
                            if (data[user]['session-id'] == session_id):
                                if (data[user]['question'] <= 1):
                                    return
                                data[user]['question'] -= 1
                                fullName = data[user]['fullname']
                                questionNum = data[user]['question']
                                curAttempt = data[user]['attempts'][str(questionNum)]
                                curMarks = data[user]['marks']
                                with open(os.path.join(basedir, 'storage/users/users.json'),'w') as outfile:
                                    json.dump(data, outfile, indent=4)
                                # Serve test
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                serveTest(self, user, fullName, questionNum, curAttempt, curMarks)
                                return
                    self.send_response(401)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(bytes("Session expired!", 'utf-8'))
            return


if __name__ == '__main__':
    try:
        server_address = ('', 8000)
        httpd = HTTPServer(server_address, TestManager)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Server is terminated')
        httpd.socket.close()
