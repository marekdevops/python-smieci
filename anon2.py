import json
import re
import sys
import os

# Konfiguracja
FIELDS_TO_MASK = ["password", "token", "email"]  # Dostosuj do potrzeb
MASK = "******"

def mask_json_fields(line):
    """Maskuje określone pola w obiektach JSON"""
    try:
        json_match = re.search(r'({.*?})', line)
        if json_match:
            json_data = json.loads(json_match.group(1))
            for field in FIELDS_TO_MASK:
                if field in json_data:
                    json_data[field] = MASK
            return line.replace(json_match.group(1), json.dumps(json_data))
    except json.JSONDecodeError:
        pass
    return line

def mask_text_fields(line):
    """Maskuje pola w formacie klucz=wartość"""
    pattern = re.compile(
        r'\b({})\s*=\s*([^&\s]+)'.format('|'.join(FIELDS_TO_MASK)),
        flags=re.IGNORECASE
    )
    return pattern.sub(r'\1={}'.format(MASK), line)

def process_line(line):
    """Przetwarza pojedynczą linię"""
    line = mask_json_fields(line)
    line = mask_text_fields(line)
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
            processed_line = process_line(line)
            f_out.write(processed_line)

    print(f"Plik wynikowy: {output_file}")

if __name__ == "__main__":
    main()
