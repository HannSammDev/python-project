import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/images"
app.config["SECRET_KEY"] = "your_secret_key"

db = SQLAlchemy(app)

# Database Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), nullable=True)

# Create Database
with app.app_context():
    db.create_all()

# Home - Display All Posts
@app.route("/")
def home():
    posts = Post.query.all()
    return render_template("home.html", posts=posts)

# Create a New Post
@app.route("/create", methods=["GET", "POST"])
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        image = request.files["image"]
        
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = None

        new_post = Post(title=title, content=content, image=filename)
        db.session.add(new_post)
        db.session.commit()
        flash("Post Created Successfully!", "success")
        return redirect(url_for("home"))

    return render_template("create_post.html")

# Update a Post
@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update_post(post_id):
    post = Post.query.get(post_id)
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        
        image = request.files["image"]
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            post.image = filename

        db.session.commit()
        flash("Post Updated Successfully!", "info")
        return redirect(url_for("home"))

    return render_template("update_post.html", post=post)

# Delete a Post
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
        flash("Post Deleted!", "danger")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
