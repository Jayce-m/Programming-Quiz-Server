/**
 * Student ID: 22751096 | Student Name: Jalil Inayat-Hussain | Contribution: 25%
 * Student ID: 23283528 | Student Name: Jason Millman | Contribution: 25%
 * Student ID: 22717638 | Student Name: Janodi Weerasinghe | Contribution: 25%
 * Student ID: 23098648 | Student Name: Elijah Taylor | Contribution: 25%
**/

import java.io.*;
import java.net.*;
import java.util.Arrays;
import java.util.Random;
import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.List;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

// TODO
// 1. Change the program to send the questions without the answer
// 2. Clean up the code and right comments
// 3. Add language to MCQ request so that the Java Object can mark java questions etc.....
// 4. Remove programming questions that require input from the bank of questions - this is a limitation of our program


public class QuestionBank {

    public synchronized List<String> convertJsonFileToArray(String fileName) {
        List<String> jsonArray = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
            String line;
            StringBuilder sb = new StringBuilder();
            while ((line = br.readLine()) != null) {
                sb.append(line.trim());
            }
            String json = sb.toString();
            // remove any leading or trailing brackets or whitespaces
            json = json.replaceFirst("^\\s*\\[", "").replaceAll("\\]\\s*$", "");
            String[] elements = json.split(",(?=\\{)");
            for (String element : elements) {
                jsonArray.add(element);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return jsonArray;
    }

    public synchronized String getQuestionAnswer(String questionId) {
        List<String> allQuestion = convertJsonFileToArray("resources/questions/questions.json");
        int id = Integer.parseInt(questionId) - 1; // Question ID starts at 1;

        String correctAnswer = allQuestion.get(id).split("\"answer\": \"")[1];
        correctAnswer = correctAnswer.substring(0, correctAnswer.length() - 2);
        String expandedString = correctAnswer.replace("\\n", "\n").replace("\\t", "\t").replace("\\\"", "\"").replace("\\\\", "\\");
        return expandedString;
    }

    public synchronized void generateQuestions(String userName) throws Exception {
        // This generates the 10 questions to send to the TM
        // It also includes the possible answers and the question ID

        // Generate JSON file for the user requesting the 10 questions
        // The file will be generated in the storage/usersQuestions section of the QB
        // Ensure you are in the cits3002-proj directory when compiling so that the
        // files are retreived from the right path
        List<String> allQuestions = convertJsonFileToArray("resources/questions/questions.json");

        File file = new File(userName + ".json");
        file.createNewFile();

        List<String> usersQuestions = new ArrayList<>();
        boolean inArrayAlready = false;

        for (int i = 0; i < 10; i++) {
            inArrayAlready = false;
            Random rand = new Random();
            int randomNumber = rand.nextInt(allQuestions.size());
            for (int j = 0; j < usersQuestions.size(); j++) {
                if (usersQuestions.get(j).equals(allQuestions.get(randomNumber))) {
                    inArrayAlready = true;
                }
            }
            if (!(inArrayAlready)) {
                usersQuestions.add(allQuestions.get(randomNumber));
            } else {
                i--;
            }
        }

        FileWriter fileWriter = new FileWriter("resources/usersQuestions/" + userName + ".json");
        BufferedWriter bufferedWriter = new BufferedWriter(fileWriter);
        bufferedWriter.write(usersQuestions.toString());
        bufferedWriter.close();
    }

    public synchronized void sendMCQmarkingToTM(Socket clientSocket, Boolean correct, String userName,
            String QuestionID, String marksAwarded,
            String returnMessage) throws Exception {
        // Creates an output stream and sends the current
        // userName, QuestionID, marksAwarded, and a message to indicate if they were
        // correct/incorrect
        // or exceeded the number of attempts and therefore returns the expected answer
        OutputStream mcqOut = clientSocket.getOutputStream();
        mcqOut.write((userName + "," + QuestionID + "," + marksAwarded + "," + returnMessage).getBytes());
        // if (correct) {
        //     mcqOut.write("Correct".getBytes());
        // } else {
        //     mcqOut.write("Incorrect".getBytes());
        // }
        mcqOut.flush();
        mcqOut.close();

        // Close the socket
        clientSocket.close();

    }

    public synchronized void sendPQMarkingToTM(Socket clientSocket, String request) throws Exception {
        // Creates an output stream and sends the current
        // userName, QuestionID, marksAwarded, and a message to indicate if they were
        // correct/incorrect
        // or exceeded the number of attempts and therefore returns the expected answer
        OutputStream mcqOut = clientSocket.getOutputStream();
        mcqOut.write((request).getBytes());
        
        mcqOut.flush();
        mcqOut.close();

        // Close the socket
        clientSocket.close();

    }

    public synchronized void sendQuestionsToTM(Socket clientSocket, String userName) throws Exception {
        // uses sockets to send questions to task manager
        FileInputStream fileInput = new FileInputStream("resources/usersQuestions/" + userName + ".json");

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

    public synchronized String[] markMultipleChoiceQuestion(String userId, String questionId, String usersAnswer,
            String attempts) throws Exception {
        // gets response from TM and checks if they got the question right
        // returns true or false

        String correctAnswer = getQuestionAnswer(questionId);

        System.out.println("Correct answer: " + correctAnswer);
        System.out.println("User's answer: " + usersAnswer);
        
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
            message = attempts.equals("3") ? "Incorrect! The correct answer was: " + correctAnswer
                    : "Incorrect, try again!";
        }

        // marking: <userName>, <QuestionID>, <marksAwarded>, <returnMessage>
        String[] response = new String[] { userId, questionId, marks, message };

        return response;

    }

    public synchronized String markProgrammingQuestion(String userId, String questionId, String usersAnswer,  
            String attempts, String language)
            throws Exception {

        String correctCode = getQuestionAnswer(questionId);

        String usersOutput;
        String correctOutput;

        if (language.equals("Python")) {
            System.out.println("\nRunning users code\n");
            usersOutput = runPythonCode(usersAnswer);
            System.out.println("\nRunning answer code\n");
            correctOutput = runPythonCode(correctCode);
        } else {
            System.out.println("\nRunning users code\n");
            usersOutput = runJavaCode(usersAnswer);
            System.out.println("\nRunning answer code\n");
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
            message = attempts.equals("3") ? "Incorrect! The correct answer was: " + correctCode
                    : "Incorrect, try again!";
        }

        String response = userId + " " + questionId + " " + marks + " " + message;
        System.out.println(response);
        return response;
    }

    public synchronized String runPythonCode(String code) throws IOException {
        // Ensure you have python3 installed and can run python using the python3 command
        // as seen below
        try {
            code = code.replace("\\n", "\n").replace("\\t", "\t").replace("\\", "\"");

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
            
        } catch (ArrayIndexOutOfBoundsException e) {
            System.err.println("Error: " + e.getMessage());
            return null;
        }
    }

    public synchronized String runJavaCode(String code) throws Exception {
        try {
            String name = code.split(" ")[2];
            code = code.replace("\\n", "\n").replace("\\t", "\t").replace("\\", "\"");
            System.out.println("Code is: " + "\n" + code + "\n");
            // Create a temporary file to write the usersAnswer
            File usersFile = new File(name + ".java");
            BufferedWriter writer = new BufferedWriter(new FileWriter(usersFile));
            writer.write(code);
            writer.close();

            // Create an instance of the Java compiler
            JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();

            // Compile the source code into a .class file
            int compilationResult = compiler.run(null, null, null, usersFile.getPath());
            if (compilationResult != 0) {
                System.err.println("Compilation Failed");
                return null;
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
            System.err.println("Error: " + e.getMessage());
            return null;
        }
    }

    public static synchronized void requestHandler(String request, Socket clientSocket) throws Exception {

        // Create an instant of QB to create and send questions to the TM
        // Create an instance of QB to mark Java programming questions
        // Create an instance of QB to mark Python programming questions

        QuestionBank questionSender = new QuestionBank();
        QuestionBank javaQuestionMarker = new QuestionBank();       
        QuestionBank pythonQuestionMarker = new QuestionBank();

        // THE SYNTAX BELOW SPECIFIES THE AGGREED REQUEST SYNTAX THAT THE TM MUST SEND

        // For a request for questions the request should be in the format:
        // "<UserID> requestQuestions"

        // For a request for MCQ to be marked the request should be in the format:
        // "<UserID> requestMCQMarking <QuestionID> <attempts> <answer>"

        // For a request for programming question to be marked the request should be in the format:
        // "<UserID> requestPQMarking <QuestionID> <attempts> <language> <code>"
        
        // Variables to store the request information
        String[] requestArray = request.split(" ", 5);
        String userID = requestArray[0];
        String requestType = requestArray[1];
        String questionID;
        String attempts;
        String language;
        String code;

        switch (requestType) {
            case "requestQuestions":
                System.out.println("\033[1;34mQuestions requested\033[0m\n");
                questionSender.generateQuestions(userID);
                questionSender.sendQuestionsToTM(clientSocket, userID);
                clientSocket.close();
                break;
            case "requestMCQMarking":

                questionID = requestArray[2];
                attempts = requestArray[3];
                String answer = requestArray[4];
                System.out.println("\033[1;34mMCQ marking requested\033[0m\n");
                String[] output = javaQuestionMarker.markMultipleChoiceQuestion(userID, questionID, answer, attempts);

                if (output[3] == "Correct!") {
                    questionSender.sendMCQmarkingToTM(clientSocket, true, output[0], output[1], output[2],
                            output[3]);
                } else {
                    questionSender.sendMCQmarkingToTM(clientSocket, false, output[0], output[1], output[2],
                            output[3]);
                }
                clientSocket.close();
                break;
            case "requestPQMarking":
                System.out.println("\033[1;34mProgramming question marking requested\033[0m\n");
                requestArray = request.split(" ", 6);
                System.out.println(Arrays.toString(requestArray));
                questionID = requestArray[2];
                attempts = requestArray[3];
                language = requestArray[4];
                code = requestArray[5];

                if (language.equals("Java")) {
                    String response = javaQuestionMarker.markProgrammingQuestion(userID, questionID, code, attempts, language);;
                    javaQuestionMarker.sendPQMarkingToTM(clientSocket, response);
                } else if (language.equals("Python")) {
                    String response = pythonQuestionMarker.markProgrammingQuestion(userID, questionID, code, attempts, language);
                    pythonQuestionMarker.sendPQMarkingToTM(clientSocket, response);
                }
                clientSocket.close();
                break;
            default:
                break;
        }
    }

    public static void usage() {
        System.out.println("\033[1;31m\nError: Invalid arguments, please add your IP address/Port\033[0m\n");
        System.out.println("\033[1;31mUsage: java QuestionBank.java <IP Address> [Port]\033[0m\n");
        System.exit(1);
    }

    public static void main(String[] args) throws Exception {
        
        String ipAddress = "";

        // Program will use port 8000 by default unless specified otherwise
        int port = 8000;

        // Check if the user has specified an IP address and port
        // If not, print usage and exit
        if (args.length == 1) {
            ipAddress = args[0];
        } else if (args.length == 2) {
            ipAddress = args[0];
            port = Integer.parseInt(args[1]);   
        } else {
            usage();
        }


        // Get the address of the machine
        InetAddress address = InetAddress.getByName(ipAddress);
        System.out.println("\n\033[1;32mYour address: " + address + "\033[0m\n");
        System.out.println("\033[1;32mYour port: " + port + "\033[0m\n");

        // Try to create a server socket with the specified port and address
        // If the port is already in use, print error and exit
        try (ServerSocket serverSocket = new ServerSocket(port, 50, address)){
            
            System.out.println("\033[1;32mServer Started...\033[0m\n");

            while (true) {
    
                
                // Accept a client connection
                Socket clientSocket = serverSocket.accept();
                System.out.println("\033[1;34mClient connected: " + clientSocket.getInetAddress() + "\033[0m\n");
    
                // String to store the request from the TM
                String request = "";
    
                // Read in client's request
                InputStream inputStream = clientSocket.getInputStream();
                byte[] buffer = new byte[4096];
                int length = inputStream.read(buffer);
                request = new String(buffer, 0, length);
                System.out.println("\033[1;34mRequest received: " + request + "\033[0m\n");
                
                // If the TM is terminated the QB terminates as well
                if (request.equals("close the QB server")) {
                    System.out.println("\033[1;31mServer Closed\033[0m\n");
                    serverSocket.close();
                    break;
                }
    
                // Create a copy of the request variable
                String requestCopy = new String(request);
    
                // Create a thread to handle the request
                Thread thread = new Thread(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            requestHandler(requestCopy, clientSocket);
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                });
                
                thread.start();
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }

    }

}