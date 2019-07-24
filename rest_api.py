from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)



@app.route('/retrieve_article', methods=['GET'])
def retrieve_article():
    connection = sqlite3.connect('db/articles_fav.db')
    cursor = connection.cursor()
    result = cursor.execute("Select * from articles_fav")
    articles = cursor.fetchall()
    return jsonify(articles)


@app.route('/retrieve_article/<int:id>', methods=['GET'])
def retrieve_specific_article(id):
    conn = sqlite3.connect('db/articles_fav.db')
    cursor = conn.cursor()
    result = cursor.execute("Select * from articles_fav")
    articles = cursor.fetchall()
    if result:
        for article in articles:
            if article[0] == id:
                return jsonify(article)


@app.route('/add_articles', methods=['POST'])
def add_articles():
    if request.method == 'POST':
        conn = sqlite3.connect('db/articles_fav.db')
        cursor = conn.cursor()
        title = request.json['title']
        author = request.json['author']
        body = request.json['body']
        fav = request.json['fav']
        cursor.execute('Insert into articles_fav(title, author, body, fav) Values(?, ?, ?, ?)',(title,author,body,fav))
        conn.commit()
        cursor.close()
        return jsonify({'ayan': 'abcd'})
    return jsonify({'message': 'success'})

if __name__ == '__main__':
    app.run(debug=True,port=8080)
