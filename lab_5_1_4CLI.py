import argparse
import sys
from lab_5_1_3statistics import calculate_ssh_connection_stats, \
    get_random_logs_for_user, calculate_user_login_frequency
from read_log import read_log
import logging


def cli():
    parser = argparse.ArgumentParser(description="Analizator logów SSH")

    parser.add_argument("log_file", help="Ścieżka do log file")
    parser.add_argument("-l", "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        default="INFO", help="Opcjonalnie minimalny poziom logowania")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand
    random_logs_parser = subparsers.add_parser("random_logs", help="Losowe wpisy")
    # Subcommand's arguments
    random_logs_parser.add_argument("user", help="Użytkownik, po któremu szukamy logi")
    random_logs_parser.add_argument("n", type=int, help="Ilość losowo wybranych wpisów lub 0 dla wszystkich")
    connection_stats_parser = subparsers.add_parser("connection_stats", help="Oblilczenie statystyki sesii SSH")
    login_frequency_parser = subparsers.add_parser("login_frequency", help="Obliczenie częstotliwości logowania")

    args = parser.parse_args()

    # log level
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(encoding='utf-8', level=log_level)

    console_info_handler = logging.StreamHandler(sys.stdout)
    console_info_handler.setLevel(logging.INFO)
    console_info_handler.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger('').addHandler(console_info_handler)

    console_error_handler = logging.StreamHandler(sys.stderr)
    console_error_handler.setLevel(logging.ERROR)
    console_error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger('').addHandler(console_error_handler)

    # Wczytujemy logi
    log_entries = read_log(args.log_file)
    if not args.command:
        for slownik in log_entries:
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

    # Jeżeli są subcommands - odpalamy dodatkowe funkcje
    if args.command == "random_logs":
        random_logs = get_random_logs_for_user(log_entries, args.user, args.n)
        for log in random_logs:
            print(log)
    elif args.command == "connection_stats":
        calculate_ssh_connection_stats(log_entries)
    elif args.command == "login_frequency":
        calculate_user_login_frequency(log_entries)


if __name__ == "__main__":
    cli()

    # Test
    # python lab_5_1_4CLI.py -h
    # python lab_5_1_4CLI.py SSH.log        # długo
    # python lab_5_1_4CLI.py -l CRITICAL SSH.log random_logs root 3
    # python lab_5_1_4CLI.py SSH.log connection_stats
    # python lab_5_1_4CLI.py SSH.log login_frequency
