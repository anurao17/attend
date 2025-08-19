from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Simple user database
users = {"admin": "password123", "user1": "pass123", "user2": "pass456"}

# CSV file path
CSV_FILE = "attendance.csv"

# Create file with headers if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Login Time", "Logout Time"])


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["username"] = username
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session["login_time"] = login_time

            # Normal user → dashboard
            if username != "admin":
                return redirect(url_for("dashboard"))
            # Admin → see all records
            else:
                return redirect(url_for("admin_dashboard"))
        else:
            return "Invalid Username/Password"
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    if username == "admin":
        return redirect(url_for("admin_dashboard"))
    login_time = session["login_time"]
    return render_template("dashboard.html", username=username, login_time=login_time)


@app.route("/logout")
def logout():
    if "username" in session:
        username = session["username"]
        if username != "admin":  # Don’t log admin into CSV
            login_time = session["login_time"]
            logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save record into CSV
            with open(CSV_FILE, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([username, login_time, logout_time])

        session.pop("username", None)
        session.pop("login_time", None)
    return redirect(url_for("login"))


@app.route("/admin")
def admin_dashboard():
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))

    records = []
    with open(CSV_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(row)

    return render_template("admin.html", records=records)


@app.route("/download-csv")
def download_csv():
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    return send_file(CSV_FILE, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
