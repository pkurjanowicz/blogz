from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy 
import os

app = Flask(__name__)
app.config['DEBUG'] = True

project_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(project_dir, "build-a-blog.db"))
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '7-DhNsqjfQjLe2dFcpzDZaHLVk'

def check_character_len(string):
    if int(len(string)) > 20 or int(len(string)) < 3:
        return False

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(800))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route("/newpost", methods=["POST", "GET"])
def newpost():
    if request.method == "POST":
        title = request.form["title"]
    return render_template("newpost.html")

@app.route("/blog", methods=["POST", "GET"])
def blog():
    if request.method == "POST":
        user = User.query.filter_by(username=session['username']).first()
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
        new_post = Blog(title,entry,user)
        db.session.add(new_post)
        db.session.commit()
        entry = Blog.query.filter_by(title=title).first()
        return redirect(f"/blog?id={entry.id}")
    if request.method == "GET":        
        entries = Blog.query.all()
        users = User.query.all()
        for user in users:
            user = User.query.filter_by(id=user.id).first()

        if request.args.get('id'):
            value = request.args.get('id')
            entries2 = Blog.query.filter_by(id=value).first()
            blog_user = Blog.query.filter_by(owner_id=value).first()
            user = User.query.filter_by(id=blog_user.id).first()
            return render_template("singleUserid.html", user=user, entries2 = entries2)

        if request.args.get('user'):
            user = request.args.get('user')
            user = User.query.filter_by(username=user).first()
            user_entries = Blog.query.filter_by(owner=user).all()
            return render_template("singleUser.html", user_entries=user_entries, user=user)
        return render_template("blog.html", entries=entries, user=user)
        


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('User password does not exist or user does not exist', 'error')
            return redirect('/login')
    return render_template("login.html")

@app.route('/signup', methods=['GET','POST'])
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        password_error = ''
        verify_error = ''
        if password == '' or check_character_len(password) == False:
            flash("That's not a valid password")
        if verify == '' or check_character_len(verify) == False or password != verify:
            flash("Passwords don't match")
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash("This is a duplicate user", 'error')
            return redirect('/signup')

    return render_template('signup.html')

@app.route('/',endpoint='homepage', methods=['GET', 'POST'])
def index():
    blog_users = User.query.all()
    return render_template('index.html', blog_users=blog_users)

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'homepage']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

if __name__ == "__main__":
    app.run()