import java.io.Serializable;

public class Student implements Serializable {
    private final int studentId;
    private String name;
    private String branch;
    private int year;
    private double marks;

    public Student(int studentId, String name, String branch, int year, double marks) {
        this.studentId = studentId;
        this.name = name;
        this.branch = branch;
        this.year = year;
        this.marks = marks;
    }

    public int getStudentId() {
        return studentId;
    }

    public String getName() {
        return name;
    }

    public String getBranch() {
        return branch;
    }

    public int getYear() {
        return year;
    }

    public double getMarks() {
        return marks;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setBranch(String branch) {
        this.branch = branch;
    }

    public void setYear(int year) {
        this.year = year;
    }

    public void setMarks(double marks) {
        this.marks = marks;
    }

    @Override
    public String toString() {
        return String.format("ID: %d | Name: %s | Branch: %s | Year: %d | Marks: %.2f",
                studentId, name, branch, year, marks);
    }
}
