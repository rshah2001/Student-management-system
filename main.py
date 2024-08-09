from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout,\
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, \
    QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys, sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Student Management System")
        self.setMinimumSize(600, 500)
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        search_menu_item = self.menuBar().addMenu("&Search")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        self.load_data()

        # create toolbar and toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Creating a status bar and adding status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect Click from the user on the database
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)

        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog(self)
        dialog.exec()

    def search(self):
        dialog = SearchDialog(self)
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student Name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add course number
        self.course_name = QComboBox()
        courses = ['Biology', 'Astronomy', 'Math', 'Physics']
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("Phone Number")
        layout.addWidget(self.phone_number)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_student)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.phone_number.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)", (name, course, mobile))

        connection.commit()
        cursor.close()
        connection.close()
        self.main_window.load_data()
        self.close()  # Close the dialog after inserting the data


class SearchDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # setting the layout
        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # creating a button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))

        rows = list(result)
        print(rows)

        items = self.main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)

        for item in items:
            print(item)
            self.main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from the selected row
        index = main_window.table.currentRow()
        # Put 1 in bracket because 0 is to the id column and 1 is to the name column
        student_name = main_window.table.item(index, 1).text()

        # get ID from selected row
        self.student_id = main_window.table.item(index, 0).text()
        # Add student Name
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # using the seelcted rows course name
        course_name = main_window.table.item(index, 2).text()
        # Add course number
        self.course_name = QComboBox()
        courses = ['Biology', 'Astronomy', 'Math', 'Physics']
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # selecting the phone number from the selected row for editing
        phone_number = main_window.table.item(index, 3).text()
        self.phone_number = QLineEdit(phone_number)
        self.phone_number.setPlaceholderText("Phone Number")
        layout.addWidget(self.phone_number)

        self.add_button = QPushButton("Update")
        self.add_button.clicked.connect(self.update_student)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name  = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.phone_number.text(),
                        self.student_id))

        connection.commit()
        cursor.close()
        connection.close()
        # refresh the table
        main_window.load_data()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")
        self.setFixedSize(300, 150)

        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete the selected record?")
        yes_button = QPushButton("YES")
        no_button = QPushButton("NO")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 1)

        yes_button.clicked.connect(self.delete_student)
        no_button.clicked.connect(self.close)

        self.setLayout(layout)

    def delete_student(self):
        # Ensure a row is selected
        index = main_window.table.currentRow()
        # Get student id from the selected row
        student_id = main_window.table.item(index, 0).text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the main window table data
        main_window.load_data()

        # Close the delete confirmation dialog
        self.close()

        # Show a confirmation message
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Record Deleted")
        confirmation_widget.setText("The selected record has been deleted.")
        confirmation_widget.exec()



app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
