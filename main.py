from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("users.db")
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        db.commit()

@app.route("/")
@app.route("/logout")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db = get_db()
        curs = db.cursor()
        curs.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = curs.fetchone()
        if user:
            return render_template("index.html", username=username)
        else:
            return render_template("login.html", message="Invalid username or password!")
    return render_template("login.html")

@app.route("/create-new")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_rentered = request.form.get("confirm-password")
        if not (username and password and password_rentered):
            return render_template("register.html", message="username and password required")
        if password != password_rentered:
            return render_template("register.html", message="Passwords do not match")
        db = get_db()
        curs = db.cursor()
        curs.execute("SELECT * FROM users WHERE username=?", (username,))
        user = curs.fetchone()
        if user:
            return render_template("register.html", message="account already exists")
        try:
            curs.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
        except sqlite3.IntegrityError:
            return render_template("register.html", message="account already exists")
        return render_template("register.html", message="Account created successfully")
    return render_template("register.html")

@app.route("/add-task", methods=["GET", "POST"])
def add_task():
    return request.form.get("task")

@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)