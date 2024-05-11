import nicegui as ui
from read_log import read_log
import re


# Tworzymy funkcję do wczytywania pliku z logami i aktualizowania interfejsu
def load_logs(button):
    filename = ui.ask_file('Choose a log file')
    if filename:
        lista_dict = read_log(filename)
        log_list.clear()
        for entry in lista_dict:
            log_list.append(entry['message'][:30] + '...')  # Wyświetl pierwsze 30 znaków z wiadomości
        update_details()


# Tworzymy funkcję do aktualizowania szczegółów wybranego loga
def update_details():
    selected_index = log_list.selected_index
    if selected_index is not None:
        selected_log = lista_dict[selected_index]
        ipv4s = get_ipv4s_from_log(selected_log)
        users = get_user_from_log(selected_log)
        message_type = get_message_type(selected_log)
        details.clear()
        details.append(f"IPv4s: {ipv4s}")
        details.append(f"Users: {users}")
        details.append(f"Message Type: {message_type}")


if __name__ == '__main__':
    # Tworzymy listę logów i detalów
    log_list = ui.list()
    details = ui.markdown()

    # Tworzymy przycisk do wczytywania pliku z logami
    load_button = ui.button('Load Logs', on_click=load_logs)

    # Tworzymy interfejs użytkownika
    ui.title('Log Viewer')
    ui.row(load_button)
    ui.row(log_list, details)

    # Uruchamiamy aplikację NiceGUI
    ui.app()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
