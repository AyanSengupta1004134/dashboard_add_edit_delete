from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
# from data import Articles
import sqlite3
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, BooleanField
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

history = {}
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
    session['page'] = 'home'
    return render_template('home.html')


@app.route('/users')
def all_user():
    session['page'] = 'admin'
    connection = sqlite3.connect('db/users.db')
    cursor = connection.cursor()
    result = cursor.execute("Select * from users")
    users = cursor.fetchall()
    if result:
        return render_template('users.html', users=users)
    else:
        return render_template('users.html', msg='No user to display')

@app.route('/about')
@is_logged_in
def about():
    session['page'] = 'about'
    return render_template('about.html')


@app.route('/articles')
@is_logged_in
def articles():
    session['page'] = 'articles'
    connection = sqlite3.connect('db/articles_fav.db')
    cursor = connection.cursor()
    con = sqlite3.connect('db/admin.db')
    cur = con.cursor()
    res = cur.execute("Select username from admin")
    admin = cur.fetchall()
    admin = [i[0] for i in admin]
    if session['username'] in admin:
        result = cursor.execute("Select * from articles_fav")
        articles = cursor.fetchall()
    else:
        result = cursor.execute('Select * from articles_fav where author=?',(session['username'],))
        articles = cursor.fetchall()
    if result:
        return render_template('articles.html', articles=articles)
    else:
        return render_template('articles.html', msg = "No data found")

@app.route('/article/<int:id>')
@is_logged_in
def article(id):
    session['page'] = 'article'
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
        admin = request.form.get("admin")
        # if user asks for admin permission then username, password will be added to the tempadmin table for the admin to validate
        if admin == 'on':
            conn = sqlite3.connect('db/temp_admin.db')
            cur = conn.cursor()
            cur.execute("Insert into temp_admin(username, password) Values(?, ?)",(username, password))
            conn.commit()
            cur.close()
            flash("Data is added to temporary admin table to validate", 'success')
        connection = sqlite3.connect('db/users.db')
        cursor = connection.cursor()
        cursor.execute("Insert into users(name,email,username,password) Values(?, ?, ?, ?)",(name,email,username,password))
        connection.commit()
        cursor.close()
        flash('You are now registered', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        conn = sqlite3.connect('db/users.db')
        cur = conn.cursor()
        result = cur.execute("SELECT * FROM users WHERE username=?", (username,))
        if result:
            data = cur.fetchone()
            password = data[4]
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                # if the user is an admin then redirect him to admin choice page or else redirect him to dashboard
                connection = sqlite3.connect('db/admin.db')
                cursor = connection.cursor()
                res = cursor.execute("Select username from admin")
                admin = cursor.fetchall()
                admin = [i[0] for i in admin]
                if username in admin:
                    flash('You are now logged in', 'success')
                    session['admin'] = True
                    return redirect(url_for('admin_choice'))
                else:
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


@app.route('/admin', methods=['GET', 'POST'])
@is_logged_in
def admin():
    session['page'] = 'admin'
    connection = sqlite3.connect('db/admin.db')
    cur = connection.cursor()
    res = cur.execute('Select username from admin')
    adm = cur.fetchall()
    adm = [i[0] for i in adm]
    if session['username'] in adm:
        conn = sqlite3.connect('db/temp_admin.db')
        cursor = conn.cursor()
        result = cursor.execute("Select * from temp_admin")
        admin = cursor.fetchall()
        if result:
            return render_template('admin.html', admin=admin)
        else:
            return render_template('admin.html', msg="No data available")
    else:
        return redirect(url_for('dashboard'))
    

@app.route('/add_admin/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def add_admin(id):
    session['page'] = 'admin'
    connection = sqlite3.connect('db/admin.db')
    conn = sqlite3.connect('db/temp_admin.db')
    cursor = connection.cursor()
    cur = conn.cursor()
    result = cur.execute('Select * from temp_admin')
    admin = cur.fetchall()
    if result:
        for ad in admin:
            if ad[0] == id:
                cursor.execute('Insert into admin(username, password) Values(?, ?)', (ad[1],ad[2]))
                cur.execute('Delete from temp_admin where id=?',(id,))
                flash('{} added successfully as admin'.format(ad[1]), 'success')
                print('Hi')
                conn.commit()
                connection.commit()
    return redirect(url_for('admin'))

@app.route('/admin_choice', methods=['GET', 'POST'])
@is_logged_in
def admin_choice():
    session['page'] = 'admin_choice'
    if request.method == 'POST':
        name1= request.form.get('admin')
        name2 = request.form.get('dash_board')
        if name1 == 'on':
            return redirect(url_for('admin'))
        elif name2 == 'on':
            return redirect(url_for('dashboard'))
        else:
            error = 'Please choice anyone to move forward'
            return render_template('admin_choice.html', error =error)
    return render_template('admin_choice.html')

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = StringField('Body')
    favorite = BooleanField('Favorite')


@app.route('/add_articles', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    session['page'] = 'add_article'
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data 
        body = form.body.data 
        fav = form.favorite.data
        connection = sqlite3.connect('db/articles_fav.db')
        cursor = connection.cursor()
        cursor.execute("Insert into articles_fav(title, author, body, fav) Values(?, ?, ?, ?)",(title, session['username'], body, fav))
        connection.commit()
        cursor.close()
        flash("Article Created", 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_articles.html', form=form)

@app.route('/edit_article/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    session['page'] = 'edit_article'
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
        cursor.execute("Update articles_fav set title=?,body=?,fav=? where id=?",(title,body,fav,id))
        connection.commit()
        cursor.close()
        flash("Article Updated", 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You are logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    session['page'] = 'dashboard'
    connection = sqlite3.connect('db/articles_fav.db')
    cursor = connection.cursor()
    result = cursor.execute("Select * from articles_fav")
    articles = cursor.fetchall()
    if result:
        Article = []
        for i in articles:
            if i[2] == session['username']:
                Article.append(i)
        return render_template('dashboard.html', articles=Article)
    else:
        return render_template('dashboard.html', msg = "No data found")


@app.route('/delete_article/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def delete_article(id):
    session['page'] = 'dashboard'
    connection = sqlite3.connect('db/articles_fav.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM articles_fav WHERE id=?',(id,))
    connection.commit()
    flash('Article Deleted', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:id>', methods =['GET', 'POST'])
def delete_user(id):
    session['page'] = 'admin'
    connection = sqlite3.connect('db/users.db')
    cursor = connection.cursor()
    cursor.execute('Delete from users where id=?',(id,))
    connection.commit()
    flash('User deleted', 'success')
    return redirect(url_for('all_user'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)