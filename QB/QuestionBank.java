
import java.io.*;
import java.net.*;
import org.json.*;
import java.util.Random;
import org.python.core.*;
import org.python.util.*;

// 22/04/2023
// Laid out a skeleton of how everythings going to work'

public class QuestionBank {

  public void generateQuestions(String userName) throws Exception {
    // This generates the 10 questions to send to the TM
    // It also includes the possible answers and the question ID

    // Generate JSON file for the user requesting the 10 questions
    // The file will be generated in the storage/usersQuestions section of the QB
    // Ensure you are in the cits3002-proj directory when compiling so that the
    // files are retreived from the right path

    File file = new File("QB/storage/usersQuestions/" + userName + ".json");
    boolean created = file.createNewFile();

    // Get questions from Questions.json and add to the users json file
    FileReader reader = new FileReader(System.getProperty("user.dir") + "/QB/storage/questions/questions.json");
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

    FileWriter fileWriter = new FileWriter("QB/storage/usersQuestions/" + userName + ".json");
    BufferedWriter bufferedWriter = new BufferedWriter(fileWriter);
    bufferedWriter.write(usersQuestions.toString());
    bufferedWriter.close();
  }
  public synchronized void sendMCQmarkingToTM(Socket clientSocket, Boolean correct, String userName, String QuestionID, String marksAwarded, String returnMessage) throws Exception {
    // Creates an output stream and sends the current
    // userName, QuestionID, marksAwarded, and a message to indicate if they were correct/incorrect
    // or exceeded the number of attempts and therefore returns the expected answer  
    OutputStream mcqOut = clientSocket.getOutputStream();
    mcqOut.write((userName+QuestionID+marksAwarded+returnMessage).getBytes());
    if(correct){
      mcqOut.write("Correct".getBytes());
    }else{
      mcqOut.write("Incorrect".getBytes());
    }
    mcqOut.flush();
    mcqOut.close();
    
    // Close the socket
    clientSocket.close();

  }

  public synchronized void sendQuestionsToTM(Socket clientSocket, String userName) throws Exception {
    // uses sockets to send questions to task manager
    FileInputStream fileInput = new FileInputStream("QB/storage/usersQuestions/" + userName + ".json");

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

  public synchronized String[] markMultipleChoiceQuestion(String userName, String QuestionID, String studentAnswer, String attempts) throws Exception {
    // gets response from TM and checks if they got the question right
    // returns true or false
    
    // Get questions from Questions.json and add to the users json file
    FileReader reader = new FileReader(System.getProperty("user.dir") + "/QB/storage/questions/questions.json");
    JSONTokener tokener = new JSONTokener(reader);

    // Create a JSON array from the JSONTokener object
    JSONArray allQuestionsJsonArray = new JSONArray(tokener);
    //Retrieve the question to be marked from the questionbank using the QuestionID
    int question = Integer.parseInt(QuestionID) - 1;                            //Question ID starts at 1;
    JSONObject theQuestion = allQuestionsJsonArray.getJSONObject(question);     
    String theAnswer = theQuestion.getString("answer");                     //find the corresponding answer

    boolean correct = false;
    if(studentAnswer == theAnswer){           //check if they were correct
      correct = true;
    } else correct = false;                   //add a return here that says they were wrong

    String marksAwarded = "0";
    String returnMessage = " ";
    if(correct || attempts == "3"){           //once they're either correct or exceed attempt limit, award marks or send correct solution.
      switch(attempts){
        case "0":
          marksAwarded = "3";
          returnMessage = "Correct!";
          break;
        case "1":
          marksAwarded = "2";
          returnMessage = "Correct!";
          break;
        case "2":
          marksAwarded = "1";
          returnMessage = "Correct!";
          break;
        case "3":
          marksAwarded = "0";
          returnMessage = "Incorrect! The correct answer was: " + theAnswer;
          break;
          }
      }else {
        returnMessage = "Incorrect, try again!";
      }

      //put everything into a string array so that it can be sent to TM
      //Format TM receives for marking array:
      //             [0]          [1]            [2]             [3]
      //marking: <userName>, <QuestionID>, <marksAwarded>, <returnMessage>
      String[] marking = new String[]{userName, QuestionID, marksAwarded, returnMessage}; 
      return marking;
  }

  public void markProgrammingQuestion(String programmingLanguage, String code, String numberOfAttemptsString) {
    PythonInterpreter interp = new PythonInterpreter();
    interp.exec(code);
    String output = interp;
    System.out.println(output);
  }

  public static void main(String[] args) throws Exception {

    // Create an instant of QB to create and send questions to the TM
    // Create an instance of QB to receive
    QuestionBank questionSender = new QuestionBank();
    QuestionBank questionMarker = new QuestionBank();
    String code2 = "for i in range(1, 11):\n\tprint(i)";

    questionMarker.markProgrammingQuestion("python", code2, "0");

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
          String [] output = questionMarker.markMultipleChoiceQuestion(userID, QuestionID, studentAnswer, attemptsMade);
          if(output[3] == "Correct!"){
            questionSender.sendMCQmarkingToTM(clientSocket, true, output[0], output[1], output[2], output[3]);
          }else{
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