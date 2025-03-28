import re
import sys
import os
import gzip
import shutil
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

def process_file(input_file, output_file, masker, is_gz):
    BUFFER_SIZE = 16 * 1024 * 1024  # 16 MB
    BATCH_SIZE = 10000

    if is_gz:
        with gzip.open(input_file, 'rt') as f_in, \
             gzip.open(output_file, 'wt') as f_out:
            process_lines(f_in, f_out, masker, BATCH_SIZE)
    else:
        with open(input_file, 'r', buffering=BUFFER_SIZE) as f_in, \
             open(output_file, 'w', buffering=BUFFER_SIZE) as f_out:
            process_lines(f_in, f_out, masker, BATCH_SIZE)

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
        print("Użycie: python mask.py <plik_wejsciowy>")
        sys.exit(1)

    input_file = sys.argv[1]
    is_gz = input_file.lower().endswith('.gz')
    temp_file = input_file + '.temp'

    fields_to_mask = ["password", "token", "email", "pole1"]
    masker = FieldMasker(fields_to_mask)

    try:
        start_time = perf_counter()
        
        process_file(input_file, temp_file, masker, is_gz)

        # Zastąp oryginalny plik przetworzonym
        os.remove(input_file)
        os.rename(temp_file, input_file)

        print(f"Przetworzono w {perf_counter() - start_time:.2f}s")

    except Exception as e:
        print(f"Błąd: {str(e)}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        sys.exit(1)

if __name__ == "__main__":
    main()
