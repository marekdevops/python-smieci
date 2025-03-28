import re
import sys
import os
import gzip
from time import perf_counter

class FieldMasker:
    def __init__(self, fields):
        combined = '|'.join(map(re.escape, fields))
        self.pattern = re.compile(
            fr'(\b({combined})\s*=\s*)([^&\s]+)|("({combined})"\s*:\s*")([^"]+)(")',
            flags=re.IGNORECASE
        )
    
    def mask(self, line):
        return self.pattern.sub(
            lambda m: (f'{m.group(1)}******') if m.group(1) else (f'{m.group(4)}******{m.group(7)}'),
            line
        )

def process_file(input_path, output_path, masker, is_gz):
    BUFFER_SIZE = 16 * 1024 * 1024
    BATCH_SIZE = 10000

    try:
        if is_gz:
            with gzip.open(input_path, 'rt') as f_in, \
                 gzip.open(output_path, 'wt') as f_out:
                process_lines(f_in, f_out, masker, BATCH_SIZE)
        else:
            with open(input_path, 'r', buffering=BUFFER_SIZE) as f_in, \
                 open(output_path, 'w', buffering=BUFFER_SIZE) as f_out:
                process_lines(f_in, f_out, masker, BATCH_SIZE)
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise

def process_lines(f_in, f_out, masker, batch_size):
    batch = []
    for line in f_in:
        batch.append(masker.mask(line))
        if len(batch) >= batch_size:
            f_out.writelines(batch)
            batch.clear()
    if batch:
        f_out.writelines(batch)

def main():
    if len(sys.argv) < 2:
        print("Użycie: python mask.py <ścieżka_do_katalogu>")
        sys.exit(1)

    input_dir = sys.argv[1]
    
    if not os.path.isdir(input_dir):
        print(f"Błąd: {input_dir} nie jest katalogiem!")
        sys.exit(1)

    fields_to_mask = ["password", "token", "email", "pole1"]
    masker = FieldMasker(fields_to_mask)
    
    processed_files = 0
    start_time = perf_counter()

    try:
        for entry in os.scandir(input_dir):
            if not entry.is_file():
                continue

            input_path = entry.path
            is_gz = input_path.lower().endswith('.gz')
            temp_path = f"{input_path}.tmp"

            try:
                # Przetwarzanie do pliku tymczasowego
                process_file(input_path, temp_path, masker, is_gz)
                
                # Zamiana plików
                os.replace(temp_path, input_path)
                processed_files += 1
                
            except Exception as e:
                print(f"Błąd przy przetwarzaniu {entry.name}: {str(e)}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        total_time = perf_counter() - start_time
        print(f"Przetworzono {processed_files} plików w {total_time:.2f}s")
        print(f"Średni czas na plik: {total_time/processed_files:.2f}s" if processed_files > 0 else "")

    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika")
        sys.exit(1)

if __name__ == "__main__":
    main()
