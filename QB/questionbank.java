import java.util.*;
import java.io.*;

public class QuestionBank{
   

    public static void main(String[] args){

        try {
            // Open a file output stream to the desired file
            FileOutputStream fileOutputStream = new FileOutputStream("test.json");
            
            // Use a PrintWriter to write the generated information to the file
            PrintWriter printWriter = new PrintWriter(fileOutputStream);
            //Get the questions randomly from either multi choice or CQ;
            
            //printWriter.print(fileInfo);
            
            // Close the file output stream
            fileOutputStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }


        /*Scanner input = new Scanner(System.in);
        Random rand = new Random();
        int numQuestions = input.nextInt();
        int numChoices = input.nextInt();
        
        int[] choices = new int[numChoices];
        for(int i = 0; i < numChoices; i++){
            choices[i] = input.nextInt();
            }
            String[] question = new String[numQuestions];
            for(int i = 0; i < numQuestions; i++){
                question[i] = input.next();
                }
                for(int i = 0; i < numQuestions; i++){
                    System.out.println(question[i] + " " + choices[rand.nextInt(numChoices)]);
                    }
        }
    */
    }
}
