import os
import re

def load_ikt_data(file_path):
    ikt_data = {
        "scores": {},
        "categories": {}
    }

    # Mendapatkan direktori skrip saat ini
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, file_path)

    # Debug: Cetak jalur lengkap ke file
    print(f"Attempting to open IKT file at: {full_path}")

    try:
        with open(full_path, "r", encoding='utf-8') as file:
            current_indicator = None

            for line_number, line in enumerate(file, 1):
                original_line = line  # Simpan baris asli untuk debugging
                line = line.strip()
                
                # Debug: Cetak baris yang diproses
                print(f"Line {line_number}: Processing line: '{original_line.strip()}'")

                if not line:
                    print(f"Line {line_number}: Skipping empty line.")
                    continue

                # Parsing indikator
                if line.startswith("# Indikator:"):
                    current_indicator = line.replace("# Indikator:", "").strip()
                    ikt_data["scores"][current_indicator] = []  # Inisialisasi list skor untuk indikator ini
                    print(f"Line {line_number}: Initialized Indicator: '{current_indicator}'")
                    continue

                # Parsing kategori
                if line.startswith(("SAKIT", "SEDANG", "SEHAT")):
                    try:
                        category, range_str = line.split(":")
                        min_val, max_val = map(float, range_str.split("-"))
                        ikt_data["categories"][category.strip()] = (min_val, max_val)
                        print(f"Line {line_number}: Category Loaded: '{category.strip()}' with range {min_val}-{max_val}")
                    except ValueError as e:
                        raise ValueError(f"Line {line_number}: Error parsing category line: '{line}' - {e}")
                    continue

                # Parsing skor
                if line.startswith("Skor"):
                    if not current_indicator:
                        raise ValueError(f"Line {line_number}: Skor ditemukan sebelum indikator. Periksa format file.")

                    print(f"Line {line_number}: Parsing Skor line: '{line}'")
                    # Gunakan regex yang lebih fleksibel
                    match = re.match(r"Skor\s+(\d+):\s*(.+)", line, re.IGNORECASE)
                    if not match:
                        print(f"Line {line_number}: Skor line tidak cocok dengan pola.")
                        continue

                    score = int(match.group(1))
                    range_str = match.group(2).strip()
                    print(f"Line {line_number}: Found Score {score} with range string '{range_str}'")

                    # Menangani beberapa rentang yang dipisahkan oleh ';'
                    ranges = range_str.split(";")
                    for r in ranges:
                        r = r.strip()
                        if r.startswith(">"):
                            min_val = float(r.replace(">", "").strip())
                            max_val = float("inf")
                        elif r.startswith("<"):
                            min_val = float("-inf")
                            max_val = float(r.replace("<", "").strip())
                        elif "-" in r:
                            min_val, max_val = map(float, r.split("-"))
                        else:
                            # Asumsikan nilai eksak
                            min_val = max_val = float(r)

                        # Tambahkan skor ke indikator saat ini
                        ikt_data["scores"][current_indicator].append((score, min_val, max_val))
                        print(f"Line {line_number}: Added Score {score} with range {min_val}-{max_val} to Indicator '{current_indicator}'")

                    continue

                # Jika baris tidak dikenali
                print(f"Line {line_number}: Unrecognized line format: '{line}'")

        # Setelah parsing semua baris
        print(f"Scores Data Keys After Loading: {list(ikt_data['scores'].keys())}")

    except FileNotFoundError:
        print(f"Error: IKT file not found at path: {full_path}")
        raise FileNotFoundError(f"IKT file not found: {full_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e

    # Debug: Tampilkan data yang dimuat
    print(f"IKT Data Loaded: {ikt_data}")
    return ikt_data

def calculate_ikt(gejala_user, ikt_data):
    weights = {
        "KestabilanAgregat": 1.5,
        "Infiltrasi": 1.5,
        "KedalamanEfektif": 0.5,
        "pHTanah": 0.5,
        "BanyaknyaPerakaran": 0.5,
        "PopulasiCacing": 1.5,
    }

    ikt_score = 0.0
    for indicator, value in gejala_user.items():
        print(f"Indicator: {indicator}, Value: {value}")
        if indicator in ikt_data["scores"]:
            for score, min_val, max_val in ikt_data["scores"][indicator]:
                if min_val <= value <= max_val:
                    weight = weights.get(indicator, 0)
                    ikt_score += score * weight
                    print(f"Matched: Score={score}, Range=({min_val}, {max_val}), Weight={weight}, Running Total={ikt_score}")
                    break
        else:
            print(f"Warning: Indicator '{indicator}' not found in scores data.")

    print(f"Final Calculated IKT Score: {ikt_score}")
    return ikt_score


def categorize_ikt(ikt_score, ikt_data):
    if "categories" not in ikt_data:
        raise KeyError("'categories' not found in ikt_data")

    for category, (min_val, max_val) in ikt_data["categories"].items():
        if min_val <= ikt_score <= max_val:
            return category
    return "TIDAK DIKETAHUI"

def find_lowest_scoring_factors(gejala_user, ikt_data):
    lowest_factors = []
    for indicator, value in gejala_user.items():
        if indicator in ikt_data["scores"]:
            for score, min_val, max_val in ikt_data["scores"][indicator]:
                if min_val <= value <= max_val:
                    lowest_factors.append((indicator, score))
                    break
    lowest_factors.sort(key=lambda x: x[1])  # Urutkan berdasarkan skor
    return lowest_factors
