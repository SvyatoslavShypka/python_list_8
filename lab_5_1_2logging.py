import sys
from read_log import read_log
import logging


# Konfiguracja loggera
logging.basicConfig(encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Ustawienie handlerów dla różnych poziomów logowania
console_info_handler = logging.StreamHandler(sys.stdout)
console_info_handler.setLevel(logging.INFO)
console_info_handler.setFormatter(logging.Formatter('%(message)s'))
logging.getLogger('').addHandler(console_info_handler)

console_error_handler = logging.StreamHandler(sys.stderr)
console_error_handler.setLevel(logging.ERROR)
console_error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger('').addHandler(console_error_handler)

if __name__ == "__main__":
    lista_dict = read_log(None)
    for slownik in lista_dict:
        logging.debug("Przeczytano %d bajtów", len(slownik.get("message")))
        if "Accepted password" in slownik.get("message") or "session opened for user" in slownik.get("message"):
            logging.info("Udana próba logowania lub otwarcie sesji")
        elif "Failed password" in slownik.get("message") and "invalid user" not in slownik.get("message"):
            logging.warning("Nieudana próba logowania")
        elif "Failed password" in slownik.get("message") and "invalid user" in slownik.get("message"):
            logging.error("Nieudana próba logowania - nieprawidłowy użytkownik")
        elif "error" in slownik.get("message").lower():
            logging.error("Wystąpił błąd")
        elif "POSSIBLE BREAK-IN ATTEMPT".lower() in slownik.get("message").lower():
            logging.critical("Wykryto próbę włamania")

    # 5.1.2 testowy wydruk     type SSH.log | python lab_5_1_2logging.py
