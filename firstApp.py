from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
# from data import Articles
import sqlite3
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, BooleanField
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

# Articles = Articles()
# length = len(Articles)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
@is_logged_in
def home():
    return render_template('home.html')


@app.route('/about')
@is_logged_in
def about():
    return render_template('about.html')


@app.route('/articles')
@is_logged_in
def articles():
    connection = sqlite3.connect('db/articles_fav.db')
    cursor = connection.cursor()
    result = cursor.execute("Select * from articles_fav")
    articles = cursor.fetchall()
    if result:
        return render_template('articles.html', articles=articles)
    else:
        return render_template('articles.html', msg = "No data found")

@app.route('/article/<int:id>')
@is_logged_in
def article(id):
    connection = sqlite3.connect('db/articles_fav.db')
    cursor = connection.cursor()
    result = cursor.execute("Select * from articles_fav")
    articles = cursor.fetchall()
    if result:
        for article in articles:
            if article[0] == id:
                return render_template('article.html', articles = article)
    else:
        return render_template('article.html', msg = 'id is not valid')


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data 
        email = form.email.data 
        username = form.username.data  
        password = sha256_crypt.encrypt(form.password.data)

        connection = sqlite3.connect('db/users.db')
        cursor = connection.cursor()
        cursor.execute("Insert into users(name,email,username,password) Values(?, ?, ?, ?)",(name,email,username,password))
        connection.commit()
        cursor.close()
        flash("You are now registered and can login", 'success')

        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        conn = sqlite3.connect('db/users.db')
        # Create cursor
        cur = conn.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username=?", (username,))

        if result:
            # Get stored hash
            data = cur.fetchone()
            password = data[4]

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = StringField('Body')
    favorite = BooleanField('Favorite')


@app.route('/add_articles', methods=['GET', 'POST'])
# @is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data 
        body = form.body.data 
        fav = form.favorite.data
        connection = sqlite3.connect('db/articles_fav.db')
        cursor = connection.cursor()
        cursor.execute("Insert into articles_fav(title, author, body, fav) Values(?, ?, ?, ?)",(title, "session['username']", body, fav))
        connection.commit()
        cursor.close()
        flash("Article Created", 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_articles.html', form=form)


@app.route('/edit_article/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    connection = sqlite3.connect('db/articles_fav.db')
    cursor = connection.cursor()
    cursor.execute('Select * from articles_fav where id=?',(id,))
    article = cursor.fetchone()
    form = ArticleForm(request.form)
    form.title.data = article[1]
    form.body.data = article[3]
    form.favorite.data = article[4]
    if request.method == 'POST' and form.validate():
        title = request.form['title'] 
        body = request.form['body']
        fav = request.form.get('favorite', '') 
        print(type(fav))
        if fav=='y':
            fav=1
        else:
            fav=0
        # connection = sqlite3.connect('db/articles.db')
        # cursor = connection.cursor()
        cursor.execute("Update articles_fav set title=?,body=?,fav=? where id=?",(title,body,fav,id))
        connection.commit()
        cursor.close()
        flash("Article Updated", 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    connection = sqlite3.connect('db/articles_fav.db')
    cursor = connection.cursor()
    result = cursor.execute("Select * from articles_fav")
    articles = cursor.fetchall()
    if result:
        return render_template('dashboard.html', articles=articles)
    else:
        return render_template('dashboard.html', msg = "No data found")


@app.route('/delete_article/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def delete_article(id):
    connection = sqlite3.connect('db/articles_fav.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM articles_fav WHERE id=?',(id,))
    connection.commit()
    flash('Article Deleted', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)