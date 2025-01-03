from flask import Flask, render_template, request
from ikt import load_ikt_data, calculate_ikt, categorize_ikt, find_lowest_scoring_factors

app = Flask(__name__)

# Homepage route
@app.route('/')
def start():
    return render_template('mulai.html')

# Diagnosis form route
@app.route('/diagnosa', methods=['GET'])
def diagnosis_form():
    # Load IKT data to dynamically create a form if needed
    ikt_data = load_ikt_data("ikt.txt")  # Pastikan file ikt.txt ada di direktori yang sama dengan ikt.py
    indicators = list(ikt_data["scores"].keys())
    return render_template('base.html', indicators=indicators)

# Handle diagnosis result
@app.route('/diagnose', methods=['POST'])
def diagnose():
    ikt_data = load_ikt_data("ikt.txt")
    gejala_user = {
        "KestabilanAgregat": float(request.form.get("KestabilanAgregat", 0)),
        "Infiltrasi": float(request.form.get("Infiltrasi", 0)),
        "KedalamanEfektif": float(request.form.get("KedalamanEfektif", 0)),
        "pHTanah": float(request.form.get("pHTanah", 0)),
        "BanyaknyaPerakaran": float(request.form.get("BanyaknyaPerakaran", 0)),
        "PopulasiCacing": float(request.form.get("PopulasiCacing", 0)),
    }

    # Hitung skor IKT
    ikt_score = calculate_ikt(gejala_user, ikt_data)
    print(f"IKT Score Calculated: {ikt_score}")

    # Kategorikan skor IKT
    kategori = categorize_ikt(ikt_score, ikt_data)
    print(f"Category Assigned: {kategori}")

    lowest_factors = find_lowest_scoring_factors(gejala_user, ikt_data)
    print(f"Faktor Skor Terendah: {lowest_factors}")

    # Contoh dummy fuzzy diagnosis (ganti sesuai kebutuhan Anda)
    diagnosis_result = ("Example Diagnosis", 0)

    return render_template(
        'hasil.html',
        ikt=ikt_score,
        kategori=kategori,
        diagnosis_results=diagnosis_result, 
        lowest_factors=lowest_factors
    )

if __name__ == '__main__':
    app.run(debug=True)
