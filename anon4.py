import re
import sys
import os

# Konfiguracja
FIELDS_TO_MASK = ["password", "token", "email", "pole1"]  # Dostosuj do potrzeb
MASK = "******"

def mask_fields(line):
    """
    Maskuje pola w formacie:
    - pole=wartość
    - "pole": "wartość"
    """
    # Wzorzec dla formatu pole=wartość
    pattern_equal = re.compile(
        r'\b({})\s*=\s*([^&\s]+)'.format('|'.join(map(re.escape, FIELDS_TO_MASK))),
        flags=re.IGNORECASE
    )
    line = pattern_equal.sub(r'\1={}'.format(MASK), line)

    # Wzorzec dla formatu "pole": "wartość"
    pattern_json = re.compile(
        r'"({})"\s*:\s*"([^"]+)"'.format('|'.join(map(re.escape, FIELDS_TO_MASK))),
        flags=re.IGNORECASE
    )
    line = pattern_json.sub(r'"\1": "{}"'.format(MASK), line)

    return line

def main():
    if len(sys.argv) < 2:
        print("Użycie: python mask.py <plik_wejsciowy>")
        sys.exit(1)

    input_file = sys.argv[1]
    
    if not os.path.isfile(input_file):
        print(f"Plik {input_file} nie istnieje!")
        sys.exit(1)

    output_file = f"{os.path.splitext(input_file)[0]}_anon.log"

    with open(input_file, "r", encoding="utf-8") as f_in, \
         open(output_file, "w", encoding="utf-8") as f_out:

        for line in f_in:
            masked_line = mask_fields(line)
            f_out.write(masked_line)

    print(f"Plik wynikowy: {output_file}")

if __name__ == "__main__":
    main()
