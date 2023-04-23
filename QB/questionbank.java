import java.io.*;
import java.net.*;

// 22/04/2023
// Laid out a skeleton of how everythings going to work'

public class QuestionBank {

  public synchronized void generateQuestions(String UserName) throws Exception {
    // This generates the 10 questions to send to the TM
    // It also includes the possible answers and the question ID

    // Generate JSON file for the user requesting the 10 questions
    // The file will be generated in the storage/usersQuestions section of the QB
    System.out.println(System.getProperty("user.dir"));
    String workingDir = System.getProperty("user.dir") + "/storage/usersQuestions/";
    File file = new File(workingDir + UserName + ".json");
    System.out.println("file created");
    boolean created = file.createNewFile();

  }

  public synchronized void sendQuestionsToTM() {
    // uses sockets to send questions to task manager
  }

  public synchronized void markMultipleChoiceQuestion() {
    // gets response from TM and checks if they got the question right
    // returns true or false
  }

  public synchronized void markProgrammingQuestion() {
    // This method compiles the answer given and compares it to the actual answer in
    // the database
  }

  public static void main(String[] args) throws Exception {

    // Create an instant of QB to create and send questions to the TM
    // Create an instance of QB to receive
    QuestionBank questionSender = new QuestionBank();
    QuestionBank questionMarker = new QuestionBank();

    // get the address of the host and set a port to commmunicate on
    InetAddress address = InetAddress.getLocalHost();
    int port = 8000;
    System.out.println("Your address: " + address);

    // Create a ServerSocket to communicate with TM

    ServerSocket serverSocket = new ServerSocket(port, 50, address);
    System.out.println("Server started");

    while (true) {

      // Wait for client to connect and create a Socket object when client connects
      Socket clientSocket = serverSocket.accept();
      System.out.println("Client connected: " + clientSocket.getInetAddress());

      // Read in client's request
      InputStream inputStream = clientSocket.getInputStream();
      byte[] buffer = new byte[1024];
      int length = inputStream.read(buffer);

      String request = new String(buffer, 0, length);
      System.out.println("Request received: " + request);

      // Respond accordingly
      // For a request for questions the request should be in the format: "<UserID>
      // requestQuestions"
      // For a request for MCQ to be marked the request should be in the format:
      // "<UserID> requestMCQMarking <answer>"
      // For a request for programming question to be marked the request should be in
      // the format: "<UserID> requestPQMarking <code>"

      String[] requestArray = request.split(" ");

      // If request is for questions
      // We need the userID so we can generate the 10 questions in a file for that
      // user
      if (requestArray[1].equals("requestQuestions")) {
        System.out.println("questions requested");
        String userID = requestArray[0];
        questionSender.generateQuestions(userID);
        questionSender.sendQuestionsToTM();
      } else if (requestArray[1].equals("requestMCQMarking")) {
        // If request is to mark question
        System.out.println("MCQ marking requested");
        questionMarker.markMultipleChoiceQuestion();
      } else if (requestArray[1].equals("requestPQMarking")) {
        questionMarker.markProgrammingQuestion();
      } else {
        continue;
      }

    }

  }

}