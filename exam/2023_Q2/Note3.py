import sys
import json
from datetime import datetime, timedelta
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel, QDialog, QFormLayout,
    QLineEdit, QDateTimeEdit, QMessageBox
)


class EditNoteDialog(QDialog):
    def __init__(self, note):
        super().__init__()
        self.setWindowTitle("Редактирование заметки")

        # Создаем текстовые поля для редактирования заголовка, содержания и дедлайна
        self.title_input = QLineEdit()
        self.title_input.setText(note["title"])

        self.content_input = QTextEdit()
        self.content_input.setPlainText(note["content"])

        self.deadline_input = QDateTimeEdit()
        self.deadline_input.setDateTime(datetime.strptime(note["deadline"], "%Y-%m-%d %H:%M:%S"))

        # Создаем кнопки для сохранения и отмены редактирования
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        # Создаем форму и добавляем элементы в нее
        layout = QFormLayout()
        layout.addRow(QLabel("Заголовок:"), self.title_input)
        layout.addRow(QLabel("Содержание:"), self.content_input)
        layout.addRow(QLabel("Дедлайн:"), self.deadline_input)
        layout.addRow(self.save_button, self.cancel_button)

        # Устанавливаем форму в диалоговое окно
        self.setLayout(layout)

    def get_edited_note(self):
        # Получаем отредактированные данные
        title = self.title_input.text()
        content = self.content_input.toPlainText()
        deadline = self.deadline_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        return {"title": title, "content": content, "deadline": deadline}


class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Заметки")

        # Инициализация списка заметок
        self.notes = []

        # Загружаем заметки из файла, если файл существует
        self.load_notes()

        # Определяем графические элементы
        self.note_list = QListWidget()
        self.note_list.setSelectionMode(QListWidget.SingleSelection)
        self.note_list.itemSelectionChanged.connect(self.display_note)

        self.note_text = QTextEdit()
        self.note_text.setReadOnly(True)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_note)

        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_note)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_note)

        # Создаем вертикальный контейнер и добавляем в него элементы
        layout = QVBoxLayout()
        layout.addWidget(self.note_list)
        layout.addWidget(self.note_text)
        layout.addWidget(self.add_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)

        # Создаем виджет и устанавливаем в него вертикальный контейнер
        widget = QWidget()
        widget.setLayout(layout)

        # Устанавливаем виджет в главное окно приложения
        self.setCentralWidget(widget)

        # Отображаем заметки в списке
        self.display_notes()

        # Создаем таймер для обновления дедлайнов каждую секунду
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_deadlines)
        self.timer.start(1000)

        # Изменяем цвет приложения
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(100, 200, 200))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(0, 150, 0))
        palette.setColor(QPalette.Button, QColor(200, 200, 200))
        palette.setColor(QPalette.ButtonText, QColor(0, 150, 0))
        palette.setColor(QPalette.Highlight, QColor(135, 206, 250))
        palette.setColor(QPalette.HighlightedText, QColor(0, 150, 0))
        self.setPalette(palette)

    def load_notes(self):
        # Загружаем заметки из файла JSON
        try:
            with open("notes.json", "r") as file:
                self.notes = json.load(file)
        except FileNotFoundError:
            self.notes = []

    def save_notes(self):
        # Сохраняем заметки в файл JSON
        with open("notes.json", "w") as file:
            json.dump(self.notes, file)

    def display_notes(self):
        # Отображаем заметки в списке
        self.note_list.clear()
        for note in self.notes:
            self.note_list.addItem(note["title"])

    def display_note(self):
        # Отображаем выбранную заметку и ее дедлайн
        selected_items = self.note_list.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            index = self.note_list.row(selected_item)
            note = self.notes[index]
            self.note_text.setPlainText(note["content"])
            deadline = datetime.strptime(note["deadline"], "%Y-%m-%d %H:%M:%S")
            time_left = deadline - datetime.now()
            time_left_str = str(time_left - timedelta(microseconds=time_left.microseconds))
            self.note_text.append("")
            self.note_text.append(f"Дедлайн: {note['deadline']} (осталось {time_left_str})")

    def update_deadlines(self):
        # Обновляем оставшееся время до дедлайна каждую секунду
        for i, note in enumerate(self.notes):
            deadline = datetime.strptime(note["deadline"], "%Y-%m-%d %H:%M:%S")
            time_left = deadline - datetime.now()
            time_left_str = str(time_left - timedelta(microseconds=time_left.microseconds))
            self.note_list.item(i).setText(f"{note['title']} (осталось: {time_left_str})")

    def add_note(self):
        # Добавляем новую заметку
        edit_dialog = EditNoteDialog(
            {"title": "", "content": "", "deadline": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        )

        if edit_dialog.exec() == QDialog.Accepted:
            new_note = edit_dialog.get_edited_note()
            self.notes.append(new_note)
            self.save_notes()
            self.display_notes()

    def edit_note(self):
        # Редактируем выбранную заметку
        selected_items = self.note_list.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            index = self.note_list.row(selected_item)
            note = self.notes[index]
            edit_dialog = EditNoteDialog(note)
            if edit_dialog.exec() == QDialog.Accepted:
                edited_note = edit_dialog.get_edited_note()
                self.notes[index] = edited_note
                self.save_notes()
                self.display_notes()

    def delete_note(self):
        # Удаляем выбранную заметку с подтверждением пользователя
        selected_items = self.note_list.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            index = self.note_list.row(selected_item)
            note = self.notes[index]
            reply = QMessageBox.question(
                self, "Подтверждение удаления", f"Вы уверены, что хотите удалить заметку '{note['title']}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                del self.notes[index]
                self.save_notes()
                self.display_notes()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    note_app = NoteApp()
    note_app.show()
    sys.exit(app.exec())

"""- Класс `EditNoteDialog` представляет собой диалоговое окно для редактирования заметок. Оно содержит текстовые поля 
для заголовка (`QLineEdit`), содержания (`QTextEdit`) и дедлайна (`QDateTimeEdit`).
- Класс `NoteApp` наследуется от `QMainWindow` и представляет главное окно приложения. В конструкторе:
  - Инициализируются графические элементы, включая список заметок (`QListWidget`), 
  окно отображения информации о заметке (`QTextEdit`) и кнопки (`QPushButton`) для добавления, редактирования и удаления заметок.
  - Устанавливается вертикальный контейнер (`QVBoxLayout`) для размещения элементов в окне.
  - Устанавливается виджет (`QWidget`) контейнером и основным виджетом главного окна с помощью `setCentralWidget`.
  - Отображаются заметки в списке (`display_notes`).
  - Создается и запускается таймер (`QTimer`) для обновления дедлайнов каждую секунду.
  - Изменяется цвет приложения с помощью `QPalette`, устанавливая различные цвета для различных элементов интерфейса.
- Методы `load_notes` и `save_notes` используются для загрузки заметок из файла JSON и сохранения заметок в файл.
- `display_notes` отображает заголовки заметок в списке.
- `display_note` отображает выбранную заметку и информацию о времени до дедлайна.
- `update_deadlines` обновляет оставшееся время до дедлайна каждую секунду для всех заметок.
- `add_note`, `edit_note` и `delete_note` служат для добавления, редактирования и удаления заметок, 
используя диалоговое окно `EditNoteDialog` и взаимодействуя с пользователем.
- В функции `__main__` создается экземпляр приложения, создается экземпляр класса `NoteApp` и запускается главный цикл приложения."""