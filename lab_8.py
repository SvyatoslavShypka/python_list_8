import sys

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFileDialog, QTextBrowser, QDateTimeEdit
from PySide6.QtGui import QTextCursor, QColor, Qt
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

        self.filter_start_label = QLabel("Filtruj od:")
        self.layout.addWidget(self.filter_start_label)

        self.filter_start_datetime_edit = QDateTimeEdit()
        self.filter_start_datetime_edit.setDateTime(QDateTime(2023, 12, 13, 9, 0, 0))
        self.filter_start_datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.layout.addWidget(self.filter_start_datetime_edit)

        self.filter_end_label = QLabel("Filtruj do:")
        self.layout.addWidget(self.filter_end_label)

        self.filter_end_datetime_edit = QDateTimeEdit()
        self.filter_end_datetime_edit.setDateTime(QDateTime(2023, 12, 13, 10, 0, 0))
        self.filter_end_datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.layout.addWidget(self.filter_end_datetime_edit)

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

        # Sprawdź, czy zaznaczony wiersz znajduje się w zakresie przefiltrowanych logów
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
                prev_cursor.select(QTextCursor.BlockUnderCursor)
                prev_cursor.setCharFormat(self.log_text_browser.textCursor().charFormat())
                char_format = prev_cursor.charFormat()
                char_format.setBackground(Qt.white)  # Przywracamy białe tło dla poprzedniego wiersza
                prev_cursor.setCharFormat(char_format)

            # Podświetlenie bieżącego wiersza
            cursor.select(QTextCursor.BlockUnderCursor)
            char_format = cursor.charFormat()
            char_format.setBackground(QColor("#FFFF00"))  # Kolor tła podświetlenia (np. żółty)
            cursor.setCharFormat(char_format)
            self.highlighted_index = selected_index
        else:
            self.details_text.clear()

    def filter_logs(self):
        start_datetime = self.filter_start_datetime_edit.dateTime().toPython()
        end_datetime = self.filter_end_datetime_edit.dateTime().toPython()
        self.filtered_logs = [log for log in self.lista_dict if
                              start_datetime <= convert_str_to_datetime(log.get('date')) <= end_datetime]
        log_entries = [entry['date'] + entry['message'] + '...' for entry in self.filtered_logs]
        self.log_text_browser.clear()
        self.log_text_browser.append('\n'.join(log_entries))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec())
