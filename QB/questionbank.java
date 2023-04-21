import java.io.FileReader;
import java.io.IOException;
import javax.json.Json;
import javax.json.JsonArray;
import javax.json.JsonObject;
import javax.json.JsonReader;
import java.util.*;


public class questionbank{

    public class JsonParserExample {
        public static void main(String[] args) {
            try {
                // Create a JsonReader object and pass the file reader to it
                JsonReader reader = Json.createReader(new FileReader("questions.json"));

                // Get the JSON object from the reader
                JsonObject json = reader.readObject();

                // Get the "questions" array from the JSON object
                JsonArray questions = json.getJsonArray("questions");

                //select a random question
                String[] testQuestion = new String[10];
            
                for(int i = 0; i<testQuestion.length; i++){
                    testQuestion[i] = (String) questions.get("question");
                    
                    int questionIndex = (int) (Math.random() * questions.size());
                    JsonObject question = questions.getJsonObject(questionIndex);
                    testQuestion[i] = question.getInt("question");

                }
                
                // Get the question text


                // Iterate through each question in the array
                for (int i = 0; i < questions.size(); i++) {
                    JsonObject question = questions.getJsonObject(i);

                    // Get the values of the question's fields
                    int id = question.getInt("id");
                    String text = question.getString("text");

                    // Do something with the question's values
                    // ...
                }

                // Close the reader
                reader.close();

            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}

