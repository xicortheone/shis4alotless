
from flask import Flask, request, render_template, redirect, url_for, send_file, session
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Paths for storing CSV files
CSV_DIRECTORY = './generated_csvs/'
os.makedirs(CSV_DIRECTORY, exist_ok=True)

# Admin password
ADMIN_PASSWORD = "6628"

# Default values for optional fields
csv_defaults = {
    "fromCompany": "",
    "fromPhone": "",
    "toCompany": "",
    "toPhone": "",
    "description": "",
    "class": "USPS_PRIORITY",  # Explicitly set to USPS_PRIORITY
    "state": "",
    "ref01": "",
    "ref02": "",
    "isContainsHazardous": "false",
    "shipmentDate": "2024-12-05",
    "template": "BASIC"
}

# CSV headers
csv_headers = [
    "fromName", "fromAddress", "fromAddress2", "fromCity", "fromState", "fromZip",
    "fromCompany", "fromPhone", "fromCountry", "toAddress", "toAddress2", "toName",
    "toCity", "toState", "toZip", "toCompany", "toPhone", "toCountry", "length",
    "width", "height", "weight", "description", "class", "state", "ref01", "ref02",
    "isContainsHazardous", "shipmentDate", "template"
]

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.form.to_dict()

    # Ensure optional fields are filled with defaults
    for field, default in csv_defaults.items():
        if field not in data or not data[field]:
            data[field] = default

    # Ensure the "class" field is always set to USPS_PRIORITY
    data["class"] = "USPS_PRIORITY"

    # Generate CSV file
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"label_{timestamp}.csv"
    filepath = os.path.join(CSV_DIRECTORY, filename)

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_headers)
        writer.writerow([data.get(header, "") for header in csv_headers])

    return redirect(url_for('home'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid password", 401
    return render_template('admin_login.html')

@app.route('/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    files = os.listdir(CSV_DIRECTORY)
    return render_template('dashboard.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    filepath = os.path.join(CSV_DIRECTORY, filename)
    return send_file(filepath, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    filepath = os.path.join(CSV_DIRECTORY, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
