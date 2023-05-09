import socket
import datetime
import string
import random
import json
from urllib.parse import parse_qs
import http.cookies
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

QB_SERVER_HOSTNAME = '127.0.0.1'
QB_SERVER_PORT = 8050

basedir = os.path.abspath(os.path.dirname(__file__))
landing = open(os.path.join(basedir, 'landing.html'), 'r').read()
testpage = open(os.path.join(basedir, 'test.html'), 'r').read()


def sendRequestToQbServer(request):
    # For a request for questions the request should be in the format:
    # "<UserID> requestQuestions"

    # For a request for MCQ to be marked the request should be in the format:
    # "<UserID> requestMCQMarking <QuestionID> <attempts> <answer>"

    # For a request for programming question to be marked the request should be in the format:
    # "<UserID> requestPQMarking <QuestionID> <attempts> <language> <code>"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("Connecting to QB server...")
        s.connect((QB_SERVER_HOSTNAME, QB_SERVER_PORT))
        print("Connected to QB server.")
        if (request.split()[1] == 'requestQuestions'):
            s.sendall(request.encode())
            data = s.recv(4096)
            fileName = 'storage/users/usersQuestions/' + \
                request.split()[0] + '.json'
            with open(fileName, 'wb') as f:
                f.write(data)
        elif (request.split()[1] == 'requestMCQMarking'):
            s.sendall(request.encode())
            data = s.recv(4096)
            print("Received response from QB server." + str(data))
        if (request.split()[1] == 'markMCQMarking'):
            s.sendall(request.encode())
        if (request.splti()[1] == 'requestPQMarking'):
            s.sendall(request.encode())
        s.close()


def genSessionID():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))


def serveTest(httpd, username):
    with open(os.path.join(basedir, 'storage/users/users.json')) as json_file:
        data = json.load(json_file)
        fullName = data[username]['fullname']
        questionNum = data[username]['question']
        curAttempt = data[username]['attempts'][str(
            questionNum)]
        curMarks = data[username]['marks']
    if os.path.isfile(os.path.join(basedir, 'storage/users/usersQuestions/' + username + '.json')) == False:
        request = username + " requestQuestions"
        sendRequestToQbServer(request)
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
        # FIXME: needs extra format specifiers in test.html
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
                                # Serve test
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                serveTest(self, user)
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
                                with open(os.path.join(basedir, 'storage/users/users.json'), 'w') as outfile:
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

                        # Serve HTML page
                        serveTest(self, username)
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
                                with open(os.path.join(basedir, 'storage/users/users.json'), 'w') as outfile:
                                    json.dump(data, outfile, indent=4)
                                # Serve test
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                serveTest(self, user)
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
                                with open(os.path.join(basedir, 'storage/users/users.json'), 'w') as outfile:
                                    json.dump(data, outfile, indent=4)
                                # Serve test
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                serveTest(self, user)
                                return
                    self.send_response(401)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(bytes("Session expired!", 'utf-8'))
            return
        if self.path == '/submit':
            print("Submitting question")
            # Get answer from post
            content_length = int(self.headers['Content-Length'])
            answer = self.rfile.read(content_length).decode('utf-8')
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
                                # Get the current question
                                questionNum = data[user]['question']
                                # Get the current attempt
                                with open(os.path.join(basedir, 'storage/users/usersQuestions/' + user + '.json')) as json_file:
                                    qData = json.load(json_file)
                                    current_question = qData[questionNum-1]
                                    curAttempt = data[user]['attempts'][str(
                                        questionNum)]
                                    if (current_question['multiple'] == True):
                                        request = user + ' requestMCQMarking ' + \
                                            str(current_question['id'])+' '+str(
                                                curAttempt)+' '+str.replace(answer, '"', '')
                                        sendRequestToQbServer(request)
                                        self.send_response(200)
                                        self.send_header(
                                            'Content-type', 'text/html')
                                        self.end_headers()
                                        serveTest(self, user)
            # if last question then display all results


if __name__ == '__main__':
    try:
        print("Setting up TM server")
        server_address = ('localhost', 8080)
        httpd = HTTPServer(server_address, TestManager)
        httpd.serve_forever()
        print("TM Server is running")

    except KeyboardInterrupt:
        print('Server is terminated')
        httpd.socket.close()
