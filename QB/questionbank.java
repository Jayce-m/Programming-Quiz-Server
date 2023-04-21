import java.util.*;
import java.io.FileReader;
import javax.json.Json;
import javax.json.JsonObject;
import javax.json.JsonReader;

public class questionbank{

    public static void main(String[] args) {
        try (JsonReader reader = Json.createReader(new FileReader("data.json"))) {
            JsonObject jsonObj = reader.readObject();
            String name = jsonObj.getString("name");
            int age = jsonObj.getInt("age");
            boolean isMarried = jsonObj.getBoolean("isMarried");

            System.out.println("Name: " + name);
            System.out.println("Age: " + age);
            System.out.println("Married: " + isMarried);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}