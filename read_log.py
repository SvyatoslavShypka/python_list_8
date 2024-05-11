import sys
from parsing import parsing_line


def read_log(log_file):
    result = []
    if log_file:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
                for line in lines:
                    if line:  # Jeżeli linia nie jest pusta
                        log_entry = parsing_line(line)
                        if log_entry:
                            result.append(log_entry)
        except FileNotFoundError:
            print("Nie ma takiego pliku: ", log_file)
            sys.exit(1)
    else:
        for line in sys.stdin:
            line = line.strip()
            # print("line: ", line)
            if line:  # Jeżeli linia nie jest pusta
                log_entry = parsing_line(line)
                if log_entry:
                    result.append(log_entry)
    return result

