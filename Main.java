import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        StudentManager manager = new StudentManager();
        Scanner sc = new Scanner(System.in);

        while (true) {
            System.out.println("\n--- Student Management System ---");
            System.out.println("1. Add Student");
            System.out.println("2. View All Students");
            System.out.println("3. Update Student");
            System.out.println("4. Delete Student");
            System.out.println("5. Search by ID");
            System.out.println("6. Search by Name");
            System.out.println("7. Statistics");
            System.out.println("8. Exit");
            System.out.print("Enter choice: ");

            int choice = sc.nextInt();
            sc.nextLine(); // clear buffer

            switch (choice) {
                case 1 -> {
                    System.out.print("Enter ID: ");
                    int id = sc.nextInt();
                    sc.nextLine();
                    System.out.print("Enter Name: ");
                    String name = sc.nextLine();
                    System.out.print("Enter Branch: ");
                    String branch = sc.nextLine();
                    System.out.print("Enter Year: ");
                    int year = sc.nextInt();
                    System.out.print("Enter Marks: ");
                    double marks = sc.nextDouble();

                    Student s = new Student(id, name, branch, year, marks);
                    if (manager.addStudent(s))
                        System.out.println("Student added.");
                    else
                        System.out.println("Student ID already exists.");
                }

                case 2 -> manager.viewAll();

                case 3 -> {
                    System.out.print("Enter ID to update: ");
                    int id = sc.nextInt();
                    sc.nextLine();
                    System.out.print("New Name: ");
                    String name = sc.nextLine();
                    System.out.print("New Branch: ");
                    String branch = sc.nextLine();
                    System.out.print("New Year: ");
                    int year = sc.nextInt();
                    System.out.print("New Marks: ");
                    double marks = sc.nextDouble();
                    if (manager.updateStudent(id, name, branch, year, marks))
                        System.out.println("Student updated.");
                    else
                        System.out.println("Student not found.");
                }

                case 4 -> {
                    System.out.print("Enter ID to delete: ");
                    int id = sc.nextInt();
                    if (manager.deleteStudent(id))
                        System.out.println("Student deleted.");
                    else
                        System.out.println("Student not found.");
                }

                case 5 -> {
                    System.out.print("Enter ID to search: ");
                    int id = sc.nextInt();
                    Student result = manager.getStudent(id);
                    if (result != null)
                        System.out.println(result);
                    else
                        System.out.println("Student not found.");
                }

                case 6 -> {
                    System.out.print("Enter Name to search: ");
                    String name = sc.nextLine();
                    var results = manager.searchByName(name);
                    if (results.isEmpty())
                        System.out.println("No matching students found.");
                    else
                        results.forEach(System.out::println);
                }

                case 7 -> manager.showStatistics();

                case 8 -> {
                    System.out.println("Exiting...");
                    sc.close();
                    return;
                }

                default -> System.out.println("Invalid choice.");
            }
        }
    }
}
