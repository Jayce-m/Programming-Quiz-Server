package qb;

import java.io.*;
import java.util.Arrays;
import javax.tools.JavaCompiler;
import javax.tools.Tool;
import javax.tools.ToolProvider;
import java.nio.file.*;
import java.net.*;
import javax.json.*;

public class Compiler {

    public static String[] markPrQuestion(String usersAnswer, String questionId, String userId, String attempts) throws Exception {

        String usersOutput = runPythonCode(usersAnswer);

        // Get questions from Questions.json and add to the users json file
        FileReader reader = new FileReader(System.getProperty("user.dir") + "/storage/questions/questions.json");
        JSONTokener tokener = new JSONTokener(reader);
        // Create a JSON array from the JSONTokener object
        JSONArray allQuestionsJsonArray = new JSONArray(tokener);

        int id = Integer.parseInt(questionId) - 1;
        JSONObject question = allQuestionsJsonArray.getJSONObject(id);

        String correctCode = question.getString("answer");

        String correctOutput = runPythonCode(correctCode);

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

    public static String runPythonCode(String code) throws IOException {
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

    public static String runJavaCode(String code) throws Exception {

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
    }

}
