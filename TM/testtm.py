import random

# Define a list of 10 dictionaries to store information about each question
questions = []

# Generate 10 random questions and store them in the questions list
for i in range(10):
    x = random.randint(1, 10)
    y = random.randint(1, 10)
    question_text = f"What is {x} x {y}?"
    answer = x * y
    questions.append({'question_text': question_text,
                     'answer': answer, 'user_answer': None, 'attempts': 0})

# Define a function to display a single question and record the user's answer


def ask_question(question):
    print(question['question_text'])
    user_answer = input("Enter your answer: ")
    try:
        user_answer = int(user_answer)
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return ask_question(question)
    question['user_answer'] = user_answer
    question['attempts'] += 1


# Loop through the questions and ask each one, allowing the user to navigate forwards and backwards
current_question_index = 0
while True:
    question = questions[current_question_index]
    ask_question(question)
    if current_question_index == 0:
        print("You are at the beginning of the test.")
    else:
        print("Type 'b' to go back to the previous question.")
    if current_question_index == len(questions) - 1:
        print("You are at the end of the test.")
        submit_test = input(
            "Type 's' to submit the test or 'b' to go back to the previous question: ")
        if submit_test == 's':
            break
        elif submit_test == 'b':
            current_question_index -= 1
    else:
        print("Type 'f' to go to the next question.")
        nav_input = input()
        if nav_input == 'b' and current_question_index > 0:
            current_question_index -= 1
        elif nav_input == 'f' and current_question_index < len(questions) - 1:
            current_question_index += 1

# Display the user's score and the number of attempts made for each question
num_correct = 0
for question in questions:
    if question['user_answer'] == question['answer']:
        num_correct += 1
    print(f"Question: {question['question_text']}")
    print(f"Your answer: {question['user_answer']}")
    print(f"Correct answer: {question['answer']}")
    print(f"Attempts: {question['attempts']}")
print(f"You got {num_correct} out of {len(questions)} questions correct.")
