from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy 
import os

app = Flask(__name__)
app.config['DEBUG'] = True

project_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(project_dir, "build-a-blog.db"))
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(800))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/newpost", methods=["POST", "GET"])
def newpost():
    if request.method == "POST":
        title = request.form["title"]
    return render_template("newpost.html")

@app.route("/blog", methods=["POST", "GET"])
def blog():
    if request.method == "POST":
        entries = Blog.query.all()  
        title = request.form["title"]
        entry = request.form["entry"]  
        entry_error = ''
        title_error = ''
        if title == '':
            title_error = "Please fill in the name"
        if entry == '':
            entry_error = "Please fill in the body"
        if entry == '' or title == '':
            return render_template("newpost.html", title_error=title_error, entry_error=entry_error)        
        new_post = Blog(title,entry)
        db.session.add(new_post)
        db.session.commit()
        entry = Blog.query.filter_by(title=title).first()
        return redirect(f"/blog?id={entry.id}")
    if request.method == "GET":
        entries = Blog.query.all()
        if request.args.get('id') != 'None':
            value = request.args.get('id')
            entries2 = Blog.query.filter_by(id=value).first()
        return render_template("blog.html", entries = entries, entries2 = entries2)

if __name__ == "__main__":
    app.run()