from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os, datetime

app = Flask(__name__)
app.secret_key = "rahasia_irma"

# === SETUP DATABASE ===
def init_db():
    if not os.path.exists("absensi.db"):
        conn = sqlite3.connect("absensi.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE absensi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            kelas TEXT,
            keterangan TEXT,
            tanggal TEXT
        )""")
        c.execute("""CREATE TABLE admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )""")
        c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "123"))
        conn.commit()
        conn.close()

init_db()

# === ROUTES ===

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/form_absensi")
def form_absensi():
    return render_template("form_absensi.html")

@app.route("/submit", methods=["POST"])
def submit():
    nama = request.form["nama"]
    kelas = request.form["kelas"]
    keterangan = request.form["keterangan"]
    tanggal = datetime.datetime.now().strftime("%d-%m-%Y")
    conn = sqlite3.connect("absensi.db")
    c = conn.cursor()
    c.execute("INSERT INTO absensi (nama, kelas, keterangan, tanggal) VALUES (?, ?, ?, ?)",
              (nama, kelas, keterangan, tanggal))
    conn.commit()
    conn.close()
    return render_template("form_absensi.html", success=True)

# === LOGIN ===
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("absensi.db")
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["admin"] = username
            return redirect(url_for("admin_page"))
        else:
            return "<h3>❌ Login gagal! <a href='/login'>Coba lagi</a></h3>"
    return render_template("login.html")

# === REGISTER ===
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("absensi.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return "<h3>✅ Akun berhasil dibuat! <a href='/login'>Login sekarang</a></h3>"
        except:
            return "<h3>⚠️ Username sudah ada! <a href='/register'>Coba lagi</a></h3>"
    return render_template("register.html")

# === ADMIN DASHBOARD ===
@app.route("/admin")
def admin_page():
    if "admin" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect("absensi.db")
    c = conn.cursor()
    c.execute("SELECT * FROM absensi")
    data = c.fetchall()
    conn.close()
    return render_template("admin.html", data=data)

# === LOGOUT ===
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)