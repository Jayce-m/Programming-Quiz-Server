# Student ID: 22751096 | Student Name: Jalil Inayat-Hussain | Contribution: 25%
# Student ID: 15204630 | Student Name: Cormac Larkin | Contribution: 25%
# Student ID: 15113005 | Student Name: Killian McCarthy | Contribution: 25%
# Student ID: 15202398 | Student Name: Diarmuid Murphy | Contribution: 25%


import socket
import datetime
import string
import random
import json
from urllib.parse import parse_qs
import http.cookies
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import argparse
import threading

# SET THESE TO THE CORRECT VALUES FOR YOUR SYSTEM AND FOR THE SYSTEM THE QUESTION BANK IS RUNNING ON
# TO DETERMINE QB SERVER IP ADDRESS AND PORT RUN THE QB SERVER AND THE IP AND PORT WILL BE PRINTED TO THE TERMINAL

basedir = os.path.abspath(os.path.dirname(__file__))

# This is the JavaScript that will be injected into the test page for the submit, next and back buttons
script = """
    <script>
    var questionNum = '%s';
    var attempts = '%s';
    if (attempts > 3) {
        document.getElementById("attemptStr").innerHTML = "This is question " + \
                                questionNum + ", you have no attempts left";
        document.getElementById("submitBtn").disabled = true;
    } else {
        document.getElementById("attemptStr").innerHTML = "You are on question " + \
                                questionNum + \
                                    " (attempt " + attempts + "/3) out of 10";
    }

    if (questionNum >= 10) {
        document.getElementById("nextBtn").disabled = true;
    } else if (questionNum <= 1) {
        document.getElementById("backBtn").disabled = true;
    }

    function nextQuestion() {

        fetch('/next', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
        })
        .then(response => {
            console.log('POST request sent successfully');
            location.reload();
        })
        .catch(error => {
            console.error('Error sending POST request:', error);
        });
    }

    function prevQuestion() {
        fetch('/back', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
        })
        .then(response => {
            console.log('POST request sent successfully');
            location.reload();
        })
        .catch(error => {
            console.error('Error sending POST request:', error);
        });
    }

    function submitAnswer() {

        // If the text area is on the DOM then replace data with the text area value
        //console.log(document.getElementById("text-input"));
        let data;
        if (document.getElementById("text-input") != null) {
            data = document.getElementById("text-input").value;
        } else {
            data = document.querySelector(
                'input[name="answer"]:checked').value;
        }
        fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
        })

        .then(response => {
            console.log('POST request sent successfully');
            if (response.status == 200) {
            document.getElementById("submitBtn").disabled = true;
            document.getElementById(
                "attemptStr").innerHTML = "This is question " + questionNum + ", you have no attempts left";
            } else {
            attempts = parseInt(attempts) + 1;
            if (parseInt(attempts) > 3) {
                document.getElementById("submitBtn").disabled = true;
                document.getElementById(
                    "attemptStr").innerHTML = "This is question " + questionNum + ", you have no attempts left";
            } else {
                document.getElementById("attemptStr").innerHTML = "You are on question " + \
                                        questionNum + \
                                            " (attempt " + attempts + \
                                               "/3) out of 10";
            }
            }
            return response.json();
        })
        .then(data => {
            document.getElementById(
                "totalStr").innerHTML = "Total marks so far: "+data.curMarks+"/30";
            document.getElementById(
                "markStr").innerHTML = "Marks for this question: "+data.curMarksQ+"/3";
            alert(data.message);
        })
        .catch(error => {
            console.error('Error sending POST request:', error);
        });
    }

    function resetQuiz() {
        fetch('/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
        })
        .then(response => {
            console.log('POST request sent successfully');
            location.reload();
        })
        .catch(error => {
            console.error('Error sending POST request:', error);
        });
    }
    </script>"""

# This is the HTML that displays the test page
testpage = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Test Manager</title>
    <style>
        .logoutLblPos {
        position: fixed;
        right: 10px;
        top: 5px;
        }

        #editor {
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        }

        #editor-container {
        height: 100%%;
        min-height: 400px;
        position: relative;
        }
    </style>
    </head>

    <body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container-fluid">
        <a class="navbar-brand disabled">Test Manager</a>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
            <li class="nav-item">
                <!-- fullname - username -->
                <a class="nav-link">Welcome, %s (ID: %s)! </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="attemptStr"></a>
            </li>
            <li class="nav-item">
                <!-- curMarks-->
                <a class="nav-link" id="totalStr">Total marks so far: %s/30</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="markStr">Marks for this question: %s/3</a>
            </li>
            </ul>
        </div>
        <form class="d-flex" name="form1" method="post" action="logout">
            <label class="logoutLblPos">
            <input class="btn btn-outline-success" name="submit2" type="submit" id="submit2" value="Log Out">
            </label>
        </form>
        </div>
    </nav>
    <div class="container mt-3">
        <form>
        <!-- questionNum -->
        <h4>Question %s:</h4>
        <!-- current_question -->
        <div>
            %s
        </div>
        <!-- options_html -->
        <div>
            %s
        </div>
        </form>
        <button onclick="submitAnswer()" id="submitBtn" class="btn btn-primary mt-3">Submit Answer</button>
        <button onclick="prevQuestion()" id="backBtn" class="btn btn-primary mt-3">Back</button>
        <button onclick="nextQuestion()" id="nextBtn" class="btn btn-primary mt-3">Next</button>
        <button onclick="resetQuiz()" id="resetBtn" class="btn btn-primary mt-3">Restart Quiz</button>
    </div>
    </body>
    </html>"""

# This is the HTML that displays the login page
landing = """
    <html>
        <head>
            <title> TM Login </title>
        </head>
    <body>
        <style>
            .loginbox {
                background-color:rgba(50, 135, 83, 0.3);
                width: 1000px;
                border: 3px solid rgb(15,82,40);
                padding: 10px;
                margin: 10px;
            }
            h1 {
            text-align: center;
            }
            h3 {
            text-align: center;
            }
            form {
            text-align: center;
            }
        </style>
        <div class="loginbox">
            <h1>Login to TM</h1>
            <h3>Enter your credentials</h3>
            <form class="login-form">
                <input
                    type="text" placeholder="Username"/>
                    <br/><br/>
                <input
                    type="password" placeholder="Password"
                    />
                    <br/><br/>
                    <button type="submit">LOGIN</button>
                </form>
            </div>
            <script>
            document.querySelector('.login-form').addEventListener('submit', function(event) {
                    // prevent the default form submission
                    event.preventDefault();

                    // get the username and password from the form
                    var username = document.querySelector('input[type="text"]').value;
                    var password = document.querySelector('input[type="password"]').value;

                    // make an HTTP POST request to the server with the user's credentials
                    var login = new XMLHttpRequest();
                    login.open('POST', '/login', true);
                    login.setRequestHeader(
                        'Content-Type', 'application/x-www-form-urlencoded');
                    login.onreadystatechange = function() {
                        if (login.readyState === XMLHttpRequest.DONE && login.status === 200) {
                            // login successful, redirect to test.html
                            window.location.href = 'test.html';
                        } else if (login.readyState === XMLHttpRequest.DONE && login.status === 401) {
                            // login failed, show an error message
                            alert('Invalid username or password');
                        }
                    };
                    login.send('username=' + encodeURIComponent(username) + \
                               '&password=' + encodeURIComponent(password));
                });
            </script>
            </body>


    </html>"""


def sendRequestToQbServer(request, httpd):
    # For a request for questions the request should be in the format:
    # "<UserID> requestQuestions"

    # For a request for MCQ to be marked the request should be in the format:
    # "<UserID> requestMCQMarking <QuestionID> <attempts> <answer>"

    # For a request for programming question to be marked the request should be in the format:
    # "<UserID> requestPQMarking <QuestionID> <attempts> <language> <code>"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("\033[1;32mConnecting to QB server...\n\033[0m")
        s.connect((qbServerIpAddress, qbServerPort))
        print("\033[1;32mConnected established with QB server...\n\033[0m")
        # Take the request string and split it
        if (request.split()[1] == 'requestQuestions'):
            # Send the request to the QB server on the socket
            s.sendall(request.encode())

            data = s.recv(4096)
            # Create file to store the questions, the file name is the user ID
            fileName = 'storage/users/usersQuestions/' + \
                request.split()[0] + '.json'
            # Write the data received from the QB server to the file
            with open(fileName, 'wb') as f:
                f.write(data)
        # If the request string is for marking
        elif (request.split()[1] == 'requestPQMarking'):
            s.sendall(request.encode())
            data = s.recv(4096)
            data = data.decode("utf-8")
            print("Received response from QB server." + data)
            print(data)
            # Response from QB is delimited by commas
            data = data.split(' ', 3)
            username = data[0]
            questionId = data[1]
            marksReceived = data[2]
            answer = data[3]
            print(answer)

            with open(os.path.join(basedir, 'storage/users/usersQuestions/' + username + '.json')) as json_file:
                data = json.load(json_file)
                # FIXME: What is the purpose of this? Could this not be
                questionNumId = -1
                # For every question in the questions file (USERID.json)
                for question in data:
                    questionNumId += 1
                    # Question id the id of the current question the user is on
                    if (str(question['id']) == str(questionId)):
                        questionNum = questionNumId
                        break
            with open(os.path.join(basedir, 'storage/users/users.json')) as json_file:
                if answer.find("Incorrect") != -1:
                    data = json.load(json_file)
                    data[username]['attempts'][str(questionNum+1)] += 1
                    httpd.send_response_only(403)
                    httpd.send_header('Content-type', 'application/json')
                    httpd.end_headers()
                    response = {
                        'message': answer, 'curMarks': data[username]['marks'], 'curMarksQ': 0}
                    httpd.wfile.write(json.dumps(response).encode())
                    if (data[username]['attempts'][str(questionNum+1)] == 4):
                        print("show answer")
                    with open(os.path.join(basedir, 'storage/users/users.json'), 'w') as outfile:
                        json.dump(data, outfile, indent=4)
                    return
                if answer.find("Correct") != -1:
                    data = json.load(json_file)
                    data[username]['marksForIndividualQuestion'][str(questionNum+1)] = int(
                        marksReceived)
                    data[username]['marks'] += int(marksReceived)
                    data[username]['attempts'][str(questionNum+1)] = 4
                    with open(os.path.join(basedir, 'storage/users/users.json'), 'w') as outfile:
                        json.dump(data, outfile, indent=4)
                    httpd.send_response_only(200)
                    httpd.send_header('Content-type', 'application/json')
                    httpd.end_headers()
                    response = {'message': answer, 'curMarks': data[username]['marks'], 'curMarksQ': int(
                        marksReceived)}
                    httpd.wfile.write(json.dumps(response).encode())
                    return
            s.close()

        elif (request.split()[1] == 'requestMCQMarking'):
            # Send the request, and then receive and decode the data
            s.sendall(request.encode())
            data = s.recv(4096)
            data = data.decode("utf-8")
            print("Received response from QB server." + data)
            # Response from QB is delimited by commas; get all the response variables
            data = data.split(',', 3)
            username = data[0]
            questionId = data[1]
            marksReceived = data[2]
            answer = data[3]
            # FIXME: What is this used for?
            questionNum = 0
            # Open the users file
            with open(os.path.join(basedir, 'storage/users/usersQuestions/' + username + '.json')) as json_file:
                data = json.load(json_file)
                questionNumId = -1
                # Convert the question ID (questions.json) into the users question number (23098648.json)
                for question in data:
                    questionNumId += 1
                    # Question id the id of the current question the user is on
                    if (str(question['id']) == str(questionId)):
                        questionNum = questionNumId
                        break
            # Open the user database
            with open(os.path.join(basedir, 'storage/users/users.json')) as json_file:
                # If the answer is incorrect
                if answer.find("Incorrect") != -1:
                    data = json.load(json_file)
                    # Increment the number of attempts for the question
                    data[username]['attempts'][str(questionNum+1)] += 1
                    # Save the information
                    httpd.send_response_only(403)
                    httpd.send_header('Content-type', 'application/json')
                    httpd.end_headers()
                    response = {
                        'message': answer, 'curMarks': data[username]['marks'], 'curMarksQ': 0}
                    httpd.wfile.write(json.dumps(response).encode())
                    with open(os.path.join(basedir, 'storage/users/users.json'), 'w') as outfile:
                        json.dump(data, outfile, indent=4)
                    return
                # If the answer is correct
                if answer.find("Correct") != -1:
                    data = json.load(json_file)
                    # Add to the users marks (calculated from the questionbank)
                    data[username]['marks'] += int(marksReceived)
                    data[username]['marksForIndividualQuestion'][str(questionNum +
                                                                 1)] = int(marksReceived)
                    data[username]['attempts'][str(questionNum+1)] = 4
                    # Save the information
                    with open(os.path.join(basedir, 'storage/users/users.json'), 'w') as outfile:
                        json.dump(data, outfile, indent=4)
                    # Send the message generated from the QuestionBank server to the user
                    httpd.send_response_only(200)
                    httpd.send_header('Content-type', 'application/json')
                    httpd.end_headers()
                    response = {'message': answer, 'curMarks': data[username]['marks'], 'curMarksQ': int(
                        marksReceived)}
                    httpd.wfile.write(json.dumps(response).encode())
                    return
        elif (request == 'close the QB server'):
            s.sendall(request.encode())
        s.close()


def serveTest(httpd, username):
    with open(os.path.join(basedir, 'storage/users/users.json')) as json_file:
        data = json.load(json_file)
        fullName = data[username]['fullname']
        questionNum = data[username]['question']
        curAttempt = data[username]['attempts'][str(
            questionNum)]
        curMarks = data[username]['marks']
        marksForIndividualQuestion = data[username]['marksForIndividualQuestion'][str(
            questionNum)]
        print("marks: " + str(marksForIndividualQuestion))
    if os.path.isfile(os.path.join(basedir, 'storage/users/usersQuestions/' + username + '.json')) == False:
        request = username + " requestQuestions"
        sendRequestToQbServer(request, httpd)
    with open(os.path.join(basedir, 'storage/users/usersQuestions/' + username + '.json')) as json_file:
        # Load the questions from the file
        data = json.load(json_file)

        # Get the current question
    current_question = data[questionNum-1]
    question = current_question['question'].replace(
        '\n', '<br>').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')

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

        # This ensures that the question is displayed properly

        # Fill in placeholders in HTML document
        print(str(questionNum))

        filled_doc = testpage % (fullName, username, curMarks,
                                 marksForIndividualQuestion, questionNum, question, options_html)

        filled_doc = filled_doc + (script % (questionNum, curAttempt))

        # Send response to client
        httpd.wfile.write(bytes(filled_doc, 'utf-8'))

    elif (current_question['multiple'] == False):

        # Adds textbox for programming question, textbox allows tabs
        programming_html = """
            <form>
            <div>
            <textarea id="text-input" placeholder="Write your answer here" rows="10" cols="50"></textarea>
            </div>
            </form>

            <script>
            const textarea = document.getElementById("text-input");
            textarea.addEventListener("keydown", function(e) {
            if (e.key === "Tab") {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;
                this.value = this.value.substring(
                    0, start) + "\t" + this.value.substring(end);
                this.selectionStart = this.selectionEnd = start + 1;
            }
            });
            </script>"""

        # Fill in placeholders in HTML document
        filled_doc = testpage % (fullName, username, curMarks, marksForIndividualQuestion,
                                 questionNum, question, programming_html)
        filled_doc = filled_doc + (script % (questionNum, curAttempt))

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
                        sessionid = ''.join(random.choice(
                            string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))
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
            # rfile is response file
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
                                        sendRequestToQbServer(request, self)
                                    elif (current_question['multiple'] == False):
                                        # If its a programming question then send to QB server with text input
                                        # "<UserID> requestPQMarking <QuestionID> <attempts> <language> <code>"
                                        request = user + ' requestPQMarking ' + \
                                            str(current_question['id']) + ' ' + str(
                                                curAttempt) + ' ' + current_question['language'] + ' ' + str.replace(answer, '"', '')
                                        sendRequestToQbServer(request, self)
        if self.path == '/reset':
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
                                print("Resetting question")
                                # Get the current question
                                data[user]['question'] = 1
                                print(data[user]['question'])
                                data[user]['marks'] = 0
                                for attempt in data[user]['attempts']:
                                    data[user]['attempts'][attempt] = 1
                                for mark in data[user]['marksForIndividualQuestion']:
                                    data[user]['marksForIndividualQuestion'][mark] = 0
                                questionNum = data[user]['question']

                                with open('storage/users/users.json', 'w') as outfile:
                                    json.dump(data, outfile, indent=4)
                                # Get the current attempt
                                with open(os.path.join(basedir, 'storage/users/usersQuestions/' + user + '.json')) as json_file:
                                    # Serve HTML page
                                    self.send_response(200)
                                    self.send_header(
                                        'Content-type', 'text/html')
                                    self.end_headers()
                                    serveTest(self, user)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('QB_SERVER_IP_ADDRESS',
                        help='the IP address of the QB server')
    parser.add_argument('QB_SERVER_PORT', type=int,
                        help='the port of the QB server')
    parser.add_argument('TM_SERVER_IP_ADDRESS',
                        help='the IP address of the TM server')
    parser.add_argument('TM_SERVER_PORT', type=int,
                        help='the port of the TM server')

    args = parser.parse_args()

    qbServerIpAddress = args.QB_SERVER_IP_ADDRESS
    qbServerPort = args.QB_SERVER_PORT
    tmServerIpAddress = args.TM_SERVER_IP_ADDRESS
    tmServerPort = args.TM_SERVER_PORT
    try:
        print("\033[1;32m\nYour IP address: " +
              str(tmServerIpAddress) + "\n\033[0m")
        print("\033[1;32mTM Your port: " + str(tmServerPort) + "\n\033[0m")
        print("\033[1;32mTM Server Starting...\n\033[0m")
        server_address = (tmServerIpAddress, tmServerPort)
        httpd = HTTPServer(server_address, TestManager)
        httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\033[1;31mTM server is terminating...\033[0m\n")
        print("\033[1;31mRequesting QB server to terminate...\033[0m\n")
        request = 'close the QB server'
        sendRequestToQbServer(request, None)
        print("\033[1;31mTM server has been terminated\033[0m\n")
        print("\033[1;31mQB server has been terminated\033[0m\n")
        # send closing request to QB server
        httpd.socket.close()
