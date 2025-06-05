import java.io.*;
import java.util.*;

public class StudentManager {
    private HashMap<Integer, Student> students;
    private final String FILE_NAME = "students.dat";

    public StudentManager() {
        students = new HashMap<>();
        loadFromFile();
    }

    public boolean addStudent(Student student) {
        if (students.containsKey(student.getStudentId())) return false;
        students.put(student.getStudentId(), student);
        saveToFile();
        return true;
    }

    public boolean updateStudent(int id, String name, String branch, int year, double marks) {
        Student s = students.get(id);
        if (s != null) {
            s.setName(name);
            s.setBranch(branch);
            s.setYear(year);
            s.setMarks(marks);
            saveToFile();
            return true;
        }
        return false;
    }

    public boolean deleteStudent(int id) {
        if (students.remove(id) != null) {
            saveToFile();
            return true;
        }
        return false;
    }

    public Student getStudent(int id) {
        return students.get(id);
    }

    public List<Student> searchByName(String name) {
        List<Student> result = new ArrayList<>();
        for (Student s : students.values()) {
            if (s.getName().equalsIgnoreCase(name)) result.add(s);
        }
        return result;
    }

    public void viewAll() {
        if (students.isEmpty()) {
            System.out.println("No student records found.");
            return;
        }
        for (Student s : students.values()) {
            System.out.println(s);
        }
    }

    public void showStatistics() {
        if (students.isEmpty()) {
            System.out.println("No records for statistics.");
            return;
        }

        double total = 0;
        double max = Double.MIN_VALUE;
        Student topStudent = null;

        for (Student s : students.values()) {
            total += s.getMarks();
            if (s.getMarks() > max) {
                max = s.getMarks();
                topStudent = s;
            }
        }

        double avg = total / students.size();
        System.out.println("Average Marks: " + avg);
        System.out.println("Top Scorer: " + topStudent);
    }

    private void saveToFile() {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(FILE_NAME))) {
            oos.writeObject(students);
        } catch (IOException e) {
            System.out.println("Error saving data.");
        }
    }

    private void loadFromFile() {
        File file = new File(FILE_NAME);
        if (!file.exists()) return;
        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(file))) {
            students = (HashMap<Integer, Student>) ois.readObject();
        } catch (Exception e) {
            System.out.println("Error loading data.");
        }
    }
}
