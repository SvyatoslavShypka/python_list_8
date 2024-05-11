import sys

from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFileDialog, QTextBrowser, QDateTimeEdit
from PySide6.QtGui import QTextCursor, QColor
from read_log import read_log
from lab_5_1_1 import *
from parsing import parsing_line
from lab_5_1_3statistics import convert_str_to_datetime


class LogViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Przeglądarka logów")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.load_button = QPushButton("Podłącz plik z logami")
        self.load_button.clicked.connect(self.load_logs)
        self.layout.addWidget(self.load_button)

        self.log_label = QLabel("Logi ogólnie:")
        self.layout.addWidget(self.log_label)

        self.log_text_browser = QTextBrowser()
        self.log_text_browser.setLineWrapMode(QTextBrowser.NoWrap)
        self.log_text_browser.cursorPositionChanged.connect(self.update_details_and_highlight_line)
        self.layout.addWidget(self.log_text_browser)

        # Filtracja od - data
        self.filter_start_date_label = QLabel("Filtruj od (Data):")
        self.layout.addWidget(self.filter_start_date_label)

        self.filter_start_date_edit = QDateTimeEdit()
        self.filter_start_date_edit.setDateTime(QDateTime(2023, 12, 13, 0, 0, 0))
        self.filter_start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.layout.addWidget(self.filter_start_date_edit)

        # Filtracja od - czas
        self.filter_start_time_label = QLabel("Filtruj od (Czas):")
        self.layout.addWidget(self.filter_start_time_label)

        self.filter_start_time_edit = QDateTimeEdit()
        self.filter_start_time_edit.setDateTime(QDateTime(2023, 12, 13, 9, 0, 0))
        self.filter_start_time_edit.setDisplayFormat("HH:mm:ss")
        self.layout.addWidget(self.filter_start_time_edit)

        # Filtracja do - data
        self.filter_end_date_label = QLabel("Filtruj do (Data):")
        self.layout.addWidget(self.filter_end_date_label)

        self.filter_end_date_edit = QDateTimeEdit()
        self.filter_end_date_edit.setDateTime(QDateTime(2023, 12, 13, 0, 0, 0))
        self.filter_end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.layout.addWidget(self.filter_end_date_edit)

        # Filtracja do - czas
        self.filter_end_time_label = QLabel("Filtruj do (Czas):")
        self.layout.addWidget(self.filter_end_time_label)

        self.filter_end_time_edit = QDateTimeEdit()
        self.filter_end_time_edit.setDateTime(QDateTime(2023, 12, 13, 10, 0, 0))
        self.filter_end_time_edit.setDisplayFormat("HH:mm:ss")
        self.layout.addWidget(self.filter_end_time_edit)

        self.filter_button = QPushButton("Filtruj")
        self.filter_button.clicked.connect(self.filter_logs)
        self.layout.addWidget(self.filter_button)

        self.remove_date_button = QPushButton("Usuń datę")
        self.remove_date_button.clicked.connect(self.remove_date_filter)
        self.layout.addWidget(self.remove_date_button)

        self.remove_time_button = QPushButton("Usuń godzinę")
        self.remove_time_button.clicked.connect(self.remove_time_filter)
        self.layout.addWidget(self.remove_time_button)

        self.details_label = QLabel("Log detalizowany:")
        self.layout.addWidget(self.details_label)

        self.details_text = QLabel()
        self.layout.addWidget(self.details_text)

        self.lista_dict = []
        self.filtered_logs = []  # Przechowuje przefiltrowane logi
        self.highlighted_index = -1  # Inicjalizacja atrybutu highlighted_index

    def load_logs(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Podłącz plik z logami', '.', 'Text files (*.log)')
        if filename:
            self.lista_dict = read_log(filename)
            log_entries = [entry['date'] + entry['message'] + '...' for entry in self.lista_dict]
            self.log_text_browser.clear()
            self.log_text_browser.append('\n'.join(log_entries))
            self.filter_logs()

    def update_details_and_highlight_line(self):
        cursor = self.log_text_browser.textCursor()
        selected_index = cursor.blockNumber()

        # Sprawdź, czy zaznaczony wiersz znajduje się w przefiltrowanych logach
        if selected_index < len(self.filtered_logs):
            selected_log = self.filtered_logs[selected_index]
            ipv4s = get_ipv4s_from_log(selected_log)
            users = get_user_from_log(selected_log)
            message_type = get_message_type(selected_log)

            # Dodanie daty, czasu i kodu statusu do logu detalizowanego
            log_date = selected_log.get('date')
            status_code = selected_log.get('code')

            details_text = f"IPv4s: {ipv4s}\nUsers: {users}\nMessage Type: {message_type}\nDate: {log_date}\nStatus Code: {status_code}"
            self.details_text.setText(details_text)

            # Wyczyszczenie podświetlenia poprzedniego wiersza
            if self.highlighted_index != -1:
                prev_highlighted_block = self.log_text_browser.document().findBlockByNumber(self.highlighted_index)
                prev_cursor = QTextCursor(prev_highlighted_block)
                prev_cursor.clearSelection()
                prev_cursor.setCharFormat(self.log_text_browser.textCursor().charFormat())

            # Podświetlenie bieżącego wiersza
            cursor.select(QTextCursor.BlockUnderCursor)
            char_format = cursor.charFormat()
            char_format.setBackground(QColor("#FFFF00"))  # Kolor tła podświetlenia (np. żółty)
            cursor.setCharFormat(char_format)
            self.highlighted_index = selected_index
        else:
            self.details_text.clear()

    def filter_logs(self):
        start_date = self.filter_start_date_edit.date().toPython()
        start_time = self.filter_start_time_edit.time().toPython()
        end_date = self.filter_end_date_edit.date().toPython()
        end_time = self.filter_end_time_edit.time().toPython()

        start_datetime = QDateTime(start_date, start_time).toPython()
        end_datetime = QDateTime(end_date, end_time).toPython()

        # Wykonaj filtrowanie tylko jeśli podano jakiekolwiek daty i czasy
        if start_datetime or end_datetime:
            self.filtered_logs = [log for log in self.lista_dict if
                                  start_datetime <= convert_str_to_datetime(log.get('date')) <= end_datetime]
        else:
            # Jeśli nie podano żadnych dat i czasów, wyświetl wszystkie wiersze logów
            self.filtered_logs = self.lista_dict

        log_entries = [entry['date'] + entry['message'] + '...' for entry in self.filtered_logs]
        self.log_text_browser.clear()
        self.log_text_browser.append('\n'.join(log_entries))

    def remove_date_filter(self):
        self.filter_start_date_edit.setDate(QDateTime(1970, 1, 1, 0, 0, 0).date())
        self.filter_end_date_edit.setDate(QDateTime(2100, 12, 31, 0, 0, 0).date())
        self.filter_logs()

    def remove_time_filter(self):
        self.filter_start_time_edit.setTime(QDateTime(2023, 12, 13, 0, 0, 0).time())
        self.filter_end_time_edit.setTime(QDateTime(2023, 12, 13, 23, 59, 59).time())
        self.filter_logs()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec())
