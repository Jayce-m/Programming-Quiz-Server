package qb;

import java.io.*;
import java.net.*;
import org.json.*;
import java.util.Random;

import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;
import java.nio.file.*;

public class QuestionBank {

    public synchronized void generateQuestions(String userName) throws Exception {
        // This generates the 10 questions to send to the TM
        // It also includes the possible answers and the question ID

        // Generate JSON file for the user requesting the 10 questions
        // The file will be generated in the storage/usersQuestions section of the QB
        // Ensure you are in the cits3002-proj directory when compiling so that the
        // files are retreived from the right path

        File file = new File("src/main/resources/usersQuestions/" + userName + ".json");
        boolean created = file.createNewFile();

        // Get questions from Questions.json and add to the users json file
        FileReader reader = new FileReader("src/main/resources/questions/questions.json");
        JSONTokener tokener = new JSONTokener(reader);

        // Create a JSON array from the JSONTokener object
        JSONArray allQuestionsJsonArray = new JSONArray(tokener);
        JSONArray usersQuestions = new JSONArray();
        boolean inArrayAlready = false;

        for (int i = 0; i < 10; i++) {
            inArrayAlready = false;
            Random rand = new Random();
            int randomNumber = rand.nextInt(allQuestionsJsonArray.length());
            for (int j = 0; j < usersQuestions.length(); j++) {
                if (usersQuestions.get(j).equals(allQuestionsJsonArray.get(randomNumber))) {
                    inArrayAlready = true;
                }
            }
            if (!(inArrayAlready)) {
                usersQuestions.put(allQuestionsJsonArray.get(randomNumber));
            }
        }

        FileWriter fileWriter = new FileWriter("src/main/resources/usersQuestions/" + userName + ".json");
        BufferedWriter bufferedWriter = new BufferedWriter(fileWriter);
        bufferedWriter.write(usersQuestions.toString());
        bufferedWriter.close();
    }

    public synchronized void sendMCQmarkingToTM(Socket clientSocket, Boolean correct, String userName, String QuestionID, String marksAwarded,
            String returnMessage) throws Exception {
        // Creates an output stream and sends the current
        // userName, QuestionID, marksAwarded, and a message to indicate if they were
        // correct/incorrect
        // or exceeded the number of attempts and therefore returns the expected answer
        OutputStream mcqOut = clientSocket.getOutputStream();
        mcqOut.write((userName + "," + QuestionID + "," + marksAwarded + "," + returnMessage).getBytes());
        if (correct) {
            mcqOut.write("Correct".getBytes());
        } else {
            mcqOut.write("Incorrect".getBytes());
        }
        mcqOut.flush();
        mcqOut.close();

        // Close the socket
        clientSocket.close();

    }

    public synchronized void sendQuestionsToTM(Socket clientSocket, String userName) throws Exception {
        // uses sockets to send questions to task manager
        FileInputStream fileInput = new FileInputStream("src/main/resources/usersQuestions/" + userName + ".json");

        byte[] buffer = new byte[4096];
        int bytesRead = 0;

        // Create an OutputStream object to send data to the client
        OutputStream out = clientSocket.getOutputStream();

        // Read the file and send its contents to the client
        while ((bytesRead = fileInput.read(buffer)) != -1) {
            out.write(buffer, 0, bytesRead);
        }

        System.out.println("\033[32mQuestions sent to: " + clientSocket.getInetAddress() + "\033[0m\n");

        // Close the FileInputStream and OutputStream
        out.close();
        fileInput.close();

        // Close the socket
        clientSocket.close();
    }

    public synchronized String[] markMultipleChoiceQuestion(String userId, String questionId, String usersAnswer, String attempts) throws Exception {
        // gets response from TM and checks if they got the question right
        // returns true or false

        // Get questions from Questions.json and add to the users json file
        FileReader reader = new FileReader("src/main/resources/questions/questions.json");
        JSONTokener tokener = new JSONTokener(reader);

        // Create a JSON array from the JSONTokener object
        JSONArray allQuestionsJsonArray = new JSONArray(tokener);
        // Retrieve the question to be marked from the questionbank using the QuestionID
        int id = Integer.parseInt(questionId) - 1; // Question ID starts at 1;
        JSONObject theQuestion = allQuestionsJsonArray.getJSONObject(id);
        String correctAnswer = theQuestion.getString("answer"); // find the corresponding answer

        boolean correct = false;

        String marks = "";
        String message = "";

        if (correctAnswer.equals(usersAnswer)) {
            message = "Correct!";
            switch (attempts) {
            case "1":
                marks = "3";
                break;
            case "2":
                marks = "2";
                break;
            case "3":
                marks = "1";
                break;
            }
        } else {
            marks = "0";
            message = attempts.equals("3") ? "Incorrect! The correct answer was: " + correctAnswer : "Incorrect, try again!";
        }

        // marking: <userName>, <QuestionID>, <marksAwarded>, <returnMessage>
        String[] response = new String[] { userId, questionId, marks, message };

        return response;

    }

    public synchronized String[] markProgrammingQuestion(String usersAnswer, String questionId, String userId, String attempts, String language)
            throws Exception {

        // Get questions from Questions.json and add to the users json file
        FileReader reader = new FileReader("src/main/resources/questions/questions.json");
        JSONTokener tokener = new JSONTokener(reader);
        // Create a JSON array from the JSONTokener object
        JSONArray allQuestionsJsonArray = new JSONArray(tokener);

        int id = Integer.parseInt(questionId) - 1;
        JSONObject question = allQuestionsJsonArray.getJSONObject(id);

        String correctCode = question.getString("answer");
        String usersOutput;
        String correctOutput;

        if (language.equals("Python")) {
            usersOutput = runPythonCode(usersAnswer);
            correctOutput = runPythonCode(correctCode);
        } else {
            usersOutput = runJavaCode(usersAnswer);
            correctOutput = runJavaCode(correctCode);
        }

        String marks = "";
        String message = "";

        if (correctOutput.equals(usersOutput)) {
            message = "Correct!";
            switch (attempts) {
            case "1":
                marks = "3";
                break;
            case "2":
                marks = "2";
                break;
            case "3":
                marks = "1";
                break;
            }
        } else {
            marks = "0";
            message = attempts.equals("3") ? "Incorrect! The correct answer was: " + correctCode : "Incorrect, try again!";
        }

        String[] response = new String[] { userId, questionId, marks, message };
        return response;
    }

    public synchronized String runPythonCode(String code) throws IOException {
        // Ensure you have python installed and can run python using the python3 command
        // as seen below
        ProcessBuilder pb = new ProcessBuilder("python3", "-c", code);
        Process process = pb.start();
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder builder = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            builder.append(line);
            builder.append(System.getProperty("line.separator"));
        }
        return builder.toString();
    }

    public synchronized String runJavaCode(String code) throws Exception {
        try {
            String name = code.split(" ")[2];

            // Create a temporary file to write the usersAnswer
            File usersFile = new File(name + ".java");
            Files.write(usersFile.toPath(), code.getBytes());

            // Create an instance of the Java compiler
            JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();

            // Compile the source code into a .class file
            int compilationResult = compiler.run(null, null, null, usersFile.getPath());
            if (compilationResult != 0) {
                System.err.println("Compilation Failed");
            }

            // Load the compiled class using a URLClassLoader
            URLClassLoader classLoader = URLClassLoader.newInstance(new URL[] { new File("").toURI().toURL() });
            String className = usersFile.getName().replaceAll(".java", "");
            Class<?> compiledClass = Class.forName(className, true, classLoader);

            // Redirect standard output to a ByteArrayOutputStream
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            PrintStream printStream = new PrintStream(outputStream);
            System.setOut(printStream);

            // Call the main method of the comiled class
            compiledClass.getMethod("main", String[].class).invoke(null, new Object[] { null });

            String output = new String(outputStream.toByteArray());

            System.setOut(new PrintStream(new FileOutputStream(FileDescriptor.out)));

            usersFile.delete();
            File classFile = new File(name + ".class");
            if (classFile.exists()) {
                classFile.delete();
            }

            return output;
        } catch (ArrayIndexOutOfBoundsException e) {
            return null;
        }
    }

    public static void main(String[] args) throws Exception {

        // Create an instant of QB to create and send questions to the TM
        // Create an instance of QB to receive
        QuestionBank questionSender = new QuestionBank();
        QuestionBank questionMarker = new QuestionBank();

        // questionMarker.markMultipleChoiceQuestion("jalil", "2", "char", "1");
        // get the address of the host and set a port to commmunicate on
        InetAddress address = InetAddress.getLocalHost();
        int port = 8000;
        System.out.println("\n\033[32mYour address: " + address + "\033[0m\n");

        // Create a ServerSocket to communicate with TM

        ServerSocket serverSocket = new ServerSocket(port, 50, address);
        System.out.println("\033[32mServer Started...\033[0m\n");

        while (true) {

            // Wait for client to connect and create a Socket object when client connects
            Socket clientSocket = serverSocket.accept();
            System.out.println("\033[34mClient connected: " + clientSocket.getInetAddress() + "\033[0m\n");

            // Read in client's request
            InputStream inputStream = clientSocket.getInputStream();
            byte[] buffer = new byte[1024];
            int length = inputStream.read(buffer);

            String request = new String(buffer, 0, length);
            System.out.println("\033[34mRequest received: " + request + "\033[0m\n");

            // Respond accordingly
            // For a request for questions the request should be in the format: "<UserID>
            // requestQuestions"
            // For a request for MCQ to be marked the request should be in the format:
            // "<UserID> requestMCQMarking <QuestionID> <answer>"
            // For a request for programming question to be marked the request should be in
            // the format: "<UserID> requestPQMarking <QuestionID> <language> <flag><code>"

            String[] requestArray = request.split(" ");

            // If request is for questions
            // We need the userID so we can generate the 10 questions in a file for that
            // user
            String requestType = requestArray[1];
            String userID = requestArray[0];
            String QuestionID = requestArray[2];
            String attemptsMade = requestArray[3];

            switch (requestType) {
            case "requestQuestions":
                System.out.println("\033[34mQuestions requested\033[0m\n");
                questionSender.generateQuestions(userID);
                questionSender.sendQuestionsToTM(clientSocket, userID);
                break;
            case "requestMCQMarking":
                System.out.println("MCQ marking requested");
                String studentAnswer = requestArray[3];
                String[] output = questionMarker.markMultipleChoiceQuestion(userID, QuestionID, studentAnswer, attemptsMade);
                if (output[3] == "Correct!") {
                    questionSender.sendMCQmarkingToTM(clientSocket, true, output[0], output[1], output[2], output[3]);
                } else {
                    questionSender.sendMCQmarkingToTM(clientSocket, false, output[0], output[1], output[2], output[3]);
                }
                break;
            case "requestPQMarking":
                // questionMarker.markProgrammingQuestion();
                String language = requestArray[2];
                String[] array2 = request.split(language);
                String code = array2[1];
                break;
            default:
                break;
            }
        }

    }

}