from http.server import HTTPServer, BaseHTTPRequestHandler

# Define the quiz questions and answers
questions = {
    "What is the capital of France?": ["Paris", "Madrid", "Berlin", "London"],
    "What is the tallest mammal?": ["Giraffe", "Elephant", "Hippopotamus", "Rhino"],
    "What is the largest planet in our solar system?": ["Jupiter", "Mars", "Saturn", "Venus"]
}

# Define the HTML template for the quiz page
quiz_template = """
<!DOCTYPE html>
<html>
<head>
	<title>Quiz</title>
</head>
<body>
	<h1>Quiz</h1>
	<form method="POST">
		{questions}
		<input type="submit" value="Submit">
	</form>
</body>
</html>
"""

# Define the HTML template for each question
question_template = """
	<div>
		<p>{question}</p>
		{choices}
	</div>
"""

# Define the HTML template for each choice
choice_template = """
	<label>
		<input type="radio" name="{name}" value="{value}">
		{label}
	</label>
"""


class QuizHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Serve the quiz page
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        question_html = ""
        for question, choices in questions.items():
            choice_html = ""
            for choice in choices:
                choice_html += choice_template.format(
                    name=question, value=choice, label=choice)
            question_html += question_template.format(
                question=question, choices=choice_html)

        self.wfile.write(quiz_template.format(
            questions=question_html).encode())

    def do_POST(self):
        # Process the quiz results
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()

        # Parse the quiz answers from the POST data
        answers = {}
        for line in post_data.split("\n"):
            if "=" in line:
                name, value = line.split("=")
                answers[name] = value

        # Grade the quiz
        score = 0
        total = len(questions)
        for question, correct_answer in questions.items():
            if answers[question] == correct_answer[0]:
                score += 1

        # Serve the results page
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write("<h1>Results</h1>".encode())
        self.wfile.write(
            "<p>Score: {}/{} ({:.0%})</p>".format(score, total, score/total).encode())


if __name__ == '__main__':
    # Start the server
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, QuizHandler)
    print('Starting quiz server...')
    httpd.serve_forever()
