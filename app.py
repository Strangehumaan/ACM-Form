from flask import Flask, render_template, request, redirect, url_for, flash
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json
from email_code.acm_email import generate_and_send_badge

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key-change-this')

# Google Sheets configuration
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

SHEET_ID = "1Ndk2pggbgQJxdbFZWH1_chOUnmxGidu8qA_9JsXRKXo"

def get_google_sheet():
    """Initialize and return Google Sheet object"""
    try:
        # For production (Render), get credentials from environment variable
        if os.environ.get('GOOGLE_CREDENTIALS_JSON'):
            creds_info = json.loads(os.environ.get('GOOGLE_CREDENTIALS_JSON'))
            creds = Credentials.from_service_account_info(creds_info, scopes=SCOPE)
        else:
            # For local development, use file
            creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
            creds = Credentials.from_service_account_file(creds_path, scopes=SCOPE)
        
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        return sheet
    except Exception as e:
        print(f"Error accessing Google Sheet: {e}")
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit_form():
    try:
        member_id = request.form.get("member_id")
        name = request.form.get("name")
        email = request.form.get("email")
        acm_email = request.form.get("acm_email")
        roll = request.form.get("roll")
        sap = request.form.get("sap")
        phone = request.form.get("phone")
        year = request.form.get("year")
        course = request.form.get("course")
        branch = request.form.get("branch") if course == "B.Tech" else "N/A"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [timestamp, member_id, name, email, acm_email, roll, sap, phone, year, course, branch]

        sheet = get_google_sheet()
        if sheet:
            if not sheet.row_values(1):
                headers = ["Timestamp", "Member ID", "Name", "Email", "ACM Email", "Roll", "SAP",
                          "Phone", "Year", "Course", "Branch"]
                sheet.insert_row(headers, 1)

            sheet.append_row(row_data)
            
            # Try to send email but don't block success page if it fails
            try:
                generate_and_send_badge(name, member_id, email)
                print(f"✅ Badge email sent successfully to {email}")
            except Exception as email_error:
                print(f"⚠️  Warning: Failed to send badge email: {email_error}")
                # Continue to success page even if email fails
            
            return render_template("success.html", name=name)
        else:
            flash("Error submitting form. Could not access Google Sheet.", "error")
            return redirect(url_for("index"))

    except Exception as e:
        print(f"Error submitting form: {e}")
        flash("Error submitting form. Please try again.", "error")
        return redirect(url_for("index"))

@app.route("/success")
def success():
    name = request.args.get('name', 'there')
    return render_template("success.html", name=name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)