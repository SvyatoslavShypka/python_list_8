import sys
from PySide6.QtCore import QDateTime, Qt, QTime, QDate
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QFileDialog, QTextBrowser, QDateTimeEdit
)
from PySide6.QtGui import QTextCursor, QColor
from lab_5_1_1 import *  # Zaimportowanie funkcji pomocniczych
from lab_5_1_3statistics import convert_str_to_datetime  # Zaimportowanie funkcji konwersji daty


class LogViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Przeglądarka logów")

        # Inicjalizacja głównego widżetu i układu
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Przycisk wczytywania logów
        self.load_button = QPushButton("Podłącz plik z logami")
        self.load_button.clicked.connect(self.load_logs)
        self.layout.addWidget(self.load_button)

        # Etykieta i przeglądarka tekstowa dla logów ogólnych
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

        # Przycisk filtracji
        self.filter_button = QPushButton("Filtruj")
        self.filter_button.clicked.connect(self.filter_logs)
        self.layout.addWidget(self.filter_button)

        # Przycisk usuwania filtra daty
        self.remove_date_button = QPushButton("Usuń datę")
        self.remove_date_button.clicked.connect(self.remove_date_filter)
        self.layout.addWidget(self.remove_date_button)

        # Przycisk usuwania filtra czasu
        self.remove_time_button = QPushButton("Usuń godzinę")
        self.remove_time_button.clicked.connect(self.remove_time_filter)
        self.layout.addWidget(self.remove_time_button)

        # Przyciski "Następny" i "Poprzedni" dla przeglądania logów
        self.prev_button = QPushButton("Poprzedni")
        self.prev_button.clicked.connect(self.prev_log)
        self.layout.addWidget(self.prev_button)
        self.next_button = QPushButton("Następny")
        self.next_button.clicked.connect(self.next_log)
        self.layout.addWidget(self.next_button)

        # Etykieta i pole tekstowe dla szczegółów loga
        self.details_label = QLabel("Log detalizowany:")
        self.layout.addWidget(self.details_label)
        self.details_text = QLabel()
        self.layout.addWidget(self.details_text)

        # Inicjalizacja zmiennych
        self.all_logs = []  # Lista wszystkich wierszy
        self.filtered_logs = []  # Lista przefiltrowanych wierszy
        self.highlighted_index = -1  # Inicjalizacja indeksu podświetlonego wiersza
        self.current_index = -1  # Inicjalizacja indeksu aktualnego wiersza

    def load_logs(self):
        # Wczytanie pliku z logami
        filename, _ = QFileDialog.getOpenFileName(self, 'Podłącz plik z logami', '.', 'Text files (*.log)')
        if filename:
            self.lista_dict = read_log(filename)  # Wczytanie logów z pliku
            self.all_logs = self.lista_dict.copy()  # Kopia wszystkich logów do przechowania
            log_entries = [entry['date'] + '...' for entry in self.lista_dict]
            self.log_text_browser.clear()
            self.log_text_browser.append('\n'.join(log_entries))
            self.filter_logs()  # Wywołanie filtracji po wczytaniu logów
            # self.current_index = 0  # Ustawienie current_index na 0 po wczytaniu logów

    def update_details_and_highlight_line(self):
        # Aktualizacja szczegółów wybranego loga i podświetlenie wiersza
        cursor = self.log_text_browser.textCursor()
        selected_index = cursor.blockNumber()

        # Wyczyszczenie poprzedniego podświetlenia
        if self.highlighted_index != -1:
            prev_block = self.log_text_browser.document().findBlockByNumber(self.highlighted_index)
            prev_cursor = QTextCursor(prev_block)
            prev_cursor.select(QTextCursor.BlockUnderCursor)
            char_format = prev_cursor.charFormat()
            char_format.setBackground(Qt.white)  # Powrót do koloru tła standardowego
            prev_cursor.setCharFormat(char_format)

        # Aktualizacja indeksu zaznaczonego wiersza
        self.highlighted_index = selected_index if 0 <= selected_index < len(self.filtered_logs) else -1

        # Jeśli nie ma żadnych przefiltrowanych logów, wyczyść szczegóły i zakończ funkcję
        if not self.filtered_logs:
            self.details_text.clear()
            return

        # Zaznaczenie aktualnego wiersza na żółto
        cursor.select(QTextCursor.BlockUnderCursor)
        char_format = cursor.charFormat()
        char_format.setBackground(QColor("#FFFF00"))  # Kolor tła podświetlenia (np. żółty)
        cursor.setCharFormat(char_format)

        # Aktualizacja danych szczegółowych, jeśli wiersz nadal istnieje w przefiltrowanych logach
        if 0 <= self.highlighted_index < len(self.filtered_logs):
            selected_log = self.filtered_logs[self.highlighted_index]
            ipv4s = get_ipv4s_from_log(selected_log)
            users = get_user_from_log(selected_log)
            message_type = get_message_type(selected_log)

            # Dodanie daty, czasu i kodu statusu do logu detalizowanego
            log_date = selected_log.get('date')
            status_code = selected_log.get('code')
            message = selected_log.get('message')

            details_text = f"IPv4s: {ipv4s}\nUsers: {users}\nMessage: {message}\nMessage Type: {message_type}\nDate: {log_date}\nStatus Code: {status_code}"
            self.details_text.setText(details_text)
        else:
            # Jeśli zaznaczony wiersz przestał istnieć w przefiltrowanych logach, wyczyść szczegóły
            self.details_text.clear()

    def filter_logs(self):
        # Filtracja logów na podstawie daty i czasu
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

        log_entries = [entry['date'] + '...' for entry in self.filtered_logs]
        self.log_text_browser.clear()
        self.log_text_browser.append('\n'.join(log_entries))

        # Ustaw bieżący indeks na pierwszy wiersz po filtrowaniu
        # if self.filtered_logs:
        #     self.current_index = 0

        # Sprawdź, czy poprzednio zaznaczony wiersz nadal jest na liście przefiltrowanych logów
        if self.highlighted_index < len(self.filtered_logs):
            # Zresetuj podświetlenie
            self.update_details_and_highlight_line()
        else:
            # Zresetuj podświetlenie i wyzeruj indeks zaznaczonego wiersza
            self.highlighted_index = -1

        # Dodaj zabezpieczenie, aby highlighted_index nie przekraczał zakresu listy przefiltrowanych logów
        self.highlighted_index = min(self.highlighted_index, len(self.filtered_logs) - 1)

        # Zaktualizuj stan przycisków "Następny" i "Poprzedni"
        self.update_buttons_state()

    def remove_date_filter(self):
        # Usunięcie filtra daty i ponowne przefiltrowanie logów
        self.filter_start_date_edit.setDate(QDate(1970, 1, 1))
        self.filter_end_date_edit.setDate(QDate(2100, 12, 31))
        self.filter_logs()

    def remove_time_filter(self):
        # Usunięcie filtra czasu i ponowne przefiltrowanie logów
        self.filter_start_time_edit.setTime(QTime(0, 0, 0))
        self.filter_end_time_edit.setTime(QTime(23, 59, 59))
        self.filter_logs()

    def next_log(self):
        # Przejście do następnego loga
        if self.current_index < len(self.filtered_logs) - 1:
            self.current_index += 1
            self.update_log_display()  # Dodaj wywołanie funkcji aktualizacji wyświetlania logu

    def prev_log(self):
        # Przejście do poprzedniego loga
        if self.current_index > 0:
            self.current_index -= 1
            self.update_log_display()  # Dodaj wywołanie funkcji aktualizacji wyświetlania logu

    def update_log_display(self):
        # Aktualizacja wyświetlania loga po zmianie indeksu
        if 0 <= self.highlighted_index < len(self.filtered_logs):
            self.update_details_and_highlight_line()

    def update_buttons_state(self):
        # Aktualizacja stanu przycisków "Następny" i "Poprzedni" w zależności od bieżącego indeksu
        self.next_button.setEnabled(self.current_index < len(self.filtered_logs) - 1)
        self.prev_button.setEnabled(self.current_index > 0)


if __name__ == '__main__':
    # Uruchomienie aplikacji
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec())
