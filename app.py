import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/images"
app.config["SECRET_KEY"] = "your_secret_key"
DATABASE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS post (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        image TEXT)''')
        conn.commit()

init_db()

@app.route("/")
def home():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM post").fetchall()
    conn.close()
    return render_template("home.html", posts=posts)

@app.route("/create", methods=["GET", "POST"])
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        image = request.files["image"]
        
        filename = None
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        
        conn = get_db_connection()
        conn.execute("INSERT INTO post (title, content, image) VALUES (?, ?, ?)",
                     (title, content, filename))
        conn.commit()
        conn.close()
        flash("Post Created Successfully!", "success")
        return redirect(url_for("home"))

    return render_template("create_post.html")

@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM post WHERE id = ?", (post_id,)).fetchone()
    
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        image = request.files["image"]
        
        filename = post["image"]
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        
        conn.execute("UPDATE post SET title = ?, content = ?, image = ? WHERE id = ?",
                     (title, content, filename, post_id))
        conn.commit()
        conn.close()
        flash("Post Updated Successfully!", "info")
        return redirect(url_for("home"))
    
    conn.close()
    return render_template("update_post.html", post=post)

@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM post WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    flash("Post Deleted!", "danger")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
