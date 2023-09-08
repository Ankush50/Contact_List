import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, \
    QListWidget, QHBoxLayout, QDialog, QFormLayout, QMessageBox
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create an SQLite database for contacts
engine = create_engine('sqlite:///contacts.db', echo=False)
Base = declarative_base()

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# ...

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # Specify the maximum length for name
    phone = Column(String(10))  # Specify the maximum length for phone
    email = Column(String(255))  # Specify the maximum length for email

# ...



Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class ContactApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Contact List")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()

    def init_ui(self):
        self.contact_list = QListWidget()
        self.load_contacts()

        self.add_button = QPushButton("Add Contact")
        self.edit_button = QPushButton("Edit Contact")
        self.delete_button = QPushButton("Delete Contact")

        self.add_button.clicked.connect(self.add_contact)
        self.edit_button.clicked.connect(self.edit_contact)
        self.delete_button.clicked.connect(self.delete_contact)

        layout = QVBoxLayout()
        layout.addWidget(self.contact_list)
        layout.addWidget(self.add_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)

        self.central_widget.setLayout(layout)

    def load_contacts(self):
        self.contact_list.clear()
        session = Session()
        contacts = session.query(Contact).all()
        session.close()

        for contact in contacts:
            self.contact_list.addItem(contact.name) # type: ignore

    def add_contact(self):
        add_dialog = ContactDialog(self, add=True)
        result = add_dialog.exec_()
        if result == QDialog.Accepted:
            session = Session()
            new_contact = Contact(name=add_dialog.name.text(), phone=add_dialog.phone.text(), email=add_dialog.email.text())
            session.add(new_contact)
            session.commit()
            session.close()
            self.load_contacts()

    def edit_contact(self):
        current_item = self.contact_list.currentItem()
        if current_item:
            session = Session()
            contact = session.query(Contact).filter_by(name=current_item.text()).first()
            session.close()
            if contact:
                edit_dialog = ContactDialog(self, add=False, contact=contact)
                result = edit_dialog.exec_()
                if result == QDialog.Accepted:
                    session = Session()
                    contact.name = edit_dialog.name.text() # type: ignore
                    contact.phone = edit_dialog.phone.text() # type: ignore
                    contact.email = edit_dialog.email.text() # type: ignore
                    session.commit()
                    session.close()
                    self.load_contacts()

    def delete_contact(self):
        current_item = self.contact_list.currentItem()
        if current_item:
            session = Session()
            contact = session.query(Contact).filter_by(name=current_item.text()).first()
            if contact:
                session.delete(contact)
                session.commit()
            session.close()
            self.load_contacts()

class ContactDialog(QDialog):
    def __init__(self, parent, add=True, contact=None):
        super().__init__(parent)
        self.setWindowTitle("Add Contact" if add else "Edit Contact")
        self.setGeometry(200, 200, 300, 200)

        self.name_label = QLabel("Name:")
        self.name = QLineEdit()
        self.phone_label = QLabel("Phone:")
        self.phone = QLineEdit()
        self.email_label = QLabel("Email:")
        self.email = QLineEdit()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        layout = QFormLayout()
        layout.addRow(self.name_label, self.name)
        layout.addRow(self.phone_label, self.phone)
        layout.addRow(self.email_label, self.email)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        if contact:
            self.name.setText(contact.name)
            self.phone.setText(contact.phone)
            self.email.setText(contact.email)

    def validate_and_accept(self):
        phone_text = self.phone.text()
        if len(phone_text) > 10:
            QMessageBox.warning(self, "Validation Error", "Phone number cannot be more than 10 characters.")
        else:
            self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ContactApp()
    window.show()
    sys.exit(app.exec_())
