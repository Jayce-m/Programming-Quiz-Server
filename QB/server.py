import http.server
import socketserver

PORT = 8000


class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        landing = open('login.html', 'r').read()
        self.wfile.write(bytes(landing, 'utf-8'))

    def do_POST(self):
        # if post request is for login
        if self.path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            landing = open('test.html', 'r').read()
            self.wfile.write(bytes(landing, 'utf-8'))
            # Generate 10 questions
            # Display first question
            
        # if self.path == '/submit':     
        # if self.path == '/next':
        # if self.path == '/prev':


Handler = MyHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
