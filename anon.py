import json
import re
import sys
import os

# Pola, które mają być zamaskowane
FIELDS_TO_MASK = ["pole1", "pole2"]  # Zmień na nazwy pól, które chcesz zamaskować

def mask_json_fields(logs, fields):
    """
    Maskuje wskazane pola w danych JSON w logach.
    """
    masked_logs = []
    for log in logs:
        try:
            # Wyszukiwanie JSON-a w linii logu
            json_match = re.search(r'({.*?})', log)
            if json_match:
                json_data = json.loads(json_match.group(1))
                # Maskowanie wskazanych pól
                for field in fields:
                    if field in json_data:
                        json_data[field] = "********"
                # Zamiana zmienionego JSON-a w logu
                log = log.replace(json_match.group(1), json.dumps(json_data))
        except json.JSONDecodeError:
            pass  # Pomijamy linie, które nie zawierają poprawnego JSON-a
        masked_logs.append(log)
    return masked_logs

def main():
    # Sprawdzenie, czy użytkownik podał plik jako argument
    if len(sys.argv) < 2:
        print("Użycie: python script.py <ścieżka_do_pliku>")
        sys.exit(1)

    # Pobranie ścieżki do pliku wejściowego z argumentów
    input_file = sys.argv[1]

    # Sprawdzenie, czy plik istnieje
    if not os.path.isfile(input_file):
        print(f"Plik '{input_file}' nie istnieje.")
        sys.exit(1)

    # Generowanie nazwy pliku wynikowego z sufiksem "_anon.log"
    base_name, _ = os.path.splitext(input_file)
    output_file = f"{base_name}_anon.log"

    # Wczytanie pliku z logami
    with open(input_file, "r", encoding="utf-8") as file:
        logs = file.readlines()

    # Maskowanie pól w JSON-ach
    masked_logs = mask_json_fields(logs, FIELDS_TO_MASK)

    # Zapisanie zmienionych logów do nowego pliku
    with open(output_file, "w", encoding="utf-8") as file:
        file.writelines(masked_logs)

    print(f"Zmienione logi zapisano w pliku: {output_file}")

if __name__ == "__main__":
    main()
