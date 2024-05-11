import re


def parsing_line(log_line):
    date_pattern = r'\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}'
    hostname_pattern = r'\w+'
    process_info_pattern = r'sshd\[(\d+)\]:'
    message = r'.*'

    full_pattern = f'({date_pattern}) ({hostname_pattern}) {process_info_pattern} ({message})'

    match = re.match(full_pattern, log_line)
    if match:
        groups = match.groups()
        log_entry = {
            "date": groups[0],
            "hostname": groups[1],
            "PID": groups[2],
            "message": groups[3]
        }
        return log_entry
    else:
        return None

# Dec 10 06:55:46 LabSZ sshd[24200]: reverse mapping checking getaddrinfo for ns.marryaldkfaczcz.com [173.234.31.186] failed - POSSIBLE BREAK-IN ATTEMPT!
# Dec 10 06:55:46
# (\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}): Ten fragment dopasowuje datę i czas w formacie "Mon DD HH:MM:SS".
# \w{3}: Dec
# \s+: spacji
# \d{1,2}: 10
# :: Dopasowuje dwukropek oddzielający godzinę od minut.
# \d{2}:\d{2}:\d{2}: 06:55:46.
# (\w+): Ten fragment dopasowuje nazwę hosta, która jest ciągiem znaków alfanumerycznych (bez spacji).
# sshd\[\d+\]: Ten fragment dopasowuje informacje o procesie zaczynające się od "sshd" i kończące na numerze PID, np. "sshd[24200]".
# sshd: Dopasowuje literał "sshd".
# \[\d+\]: Dopasowuje numer PID znajdujący się w nawiasach kwadratowych, składający się z jednego lub więcej cyfr.
# ((?:[^ ]+ ){3}): Ten fragment dopasowuje trzy słowa oddzielone spacjami po informacjach o procesie.
# (?:[^ ]+ ): Ta sekcja dopasowuje pojedyncze słowo, które nie zawiera spacji.
# {3}: Określa, że dopasowanie powinno wystąpić dokładnie trzy razy.
# (?:user (\w+) )?: Ten fragment jest opcjonalny i dopasowuje nazwę użytkownika poprzedzoną słowem "user", jeśli występuje.
# (?: ...): Ta sekcja tworzy grupę niezachłanną, która jest opcjonalna.
# user: Dopasowuje literał "user".
# (\w+): Dopasowuje nazwę użytkownika, która składa się z jednego lub więcej znaków alfanumerycznych.
# (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}): Ten fragment dopasowuje adres IP w formacie "X.X.X.X".
# \d{1,3}: Dopasowuje jedną, dwie lub trzy cyfry, co odpowiada jednej, dwóm lub trzem częściom adresu IP.
# \.: Dopasowuje kropkę oddzielającą poszczególne części adresu IP.
# (?:[^-]+)?: Ten fragment jest opcjonalny i dopasowuje wszystko do pierwszego znaku "-" (po adresie IP).
# (?: ... ): Ta sekcja tworzy grupę niezachłanną, która jest opcjonalna.
# [^-]+: Dopasowuje jeden lub więcej znaków, które nie są myślnikiem.
# - (.*): Ten fragment dopasowuje komunikat występujący po myślniku.
# -: Dopasowuje literał myślnika.
# (.*): Dopasowuje wszystkie znaki do końca linii, reprezentując komunikat.

