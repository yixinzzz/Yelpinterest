from flask import Flask, request, render_template, jsonify, redirect, url_for
from string import punctuation
from itertools import compress
import psycopg2
import re
import sys
reload(sys)

sys.setdefaultencoding('utf8')

DB_NAME = "postgres"
USER_NAME = 'power_user'
PASSWORD ='pass'
HOST = 'ec2-52-53-159-60.us-west-1.compute.amazonaws.com'
PORT = '5432'

# functions
def execute(db_cursor, query):
    db_cursor.execute(query)

def select_data(db_cursor, table_name, column_name, constraint):
    select_data_query =  "SELECT " + column_name + " FROM " + table_name + " WHERE " + constraint + ";"
    execute(db_cursor, select_data_query)

def get_ph(keyword, rating = 0):
    words = re.findall(r"[\w']+|[\$]\d+", keyword)
    words = [j.replace("'", "''") for j in list(compress(words, [i not in punctuation for i in words]))]
    if 'food' in words:
        words.remove('food')
    constraint = "LOWER(reviews) LIKE '% " + words[0].lower() + " %'"
    if len(words) > 1:
        for i in range(1, len(words)):
            constraint += "AND LOWER(reviews) LIKE '% " + words[i].lower() + " %'"
            constraint += "OR LOWER(name) LIKE '% " + words[i].lower() + " %'"
            constraint += "OR LOWER(name) = '" + words[i].lower() + "'"
    constraint += " AND rating >= " + str(rating) + "ORDER BY random()"
    select_data(cursor, "yelpData", 'photos', constraint)
    return [i[0] for i in cursor.fetchall()]

# Flask
app = Flask(__name__)
@app.route('/search/<keyword>&<rating>', methods=["POST", "GET"])
def get_photos(keyword, rating = 0):
    results = get_ph(keyword, rating = 0)
    if len(results) > 0:
        return render_template("display_photos.html", results=results)
    else:
        return render_template("error_page.html")

@app.route('/business_info', methods=["POST", "GET"])
def post_info():
    image_url = request.form.get("url")
    image_id = re.search(r'bphoto/(.+?)/258s.jpg', image_url).group(1)
    return redirect(url_for('get_business_info', image_id=image_id))

@app.route('/business_info/<image_id>')
def get_business_info(image_id):
    constraint = "photos like '%" + image_id + "%'"
    select_data(cursor, "yelpData", '*', constraint)
    results = cursor.fetchall()[0]
    return render_template("business_info_page.html", results=results)

@app.route('/search', methods=["POST", "GET"])
def post_photos():
    keyword = request.form.get("keyword")
    page = render_template("error_page.html")
    if len(keyword) > 0:
        return redirect(url_for('get_photos', keyword=keyword, rating=request.form.get("rating")))
    return page

@app.route('/contact')
def about():
    return render_template("contact.html")

@app.route('/')
@app.route('/index')
def html():
    return render_template("index.html")

# API

@app.route('/api/business_info/<image_id>')
def api_get_business_info(image_id):
    constraint = "photos like '%" + image_id + "%'"
    select_data(cursor, "yelpData", '*', constraint)
    return jsonify(cursor.fetchall()[0])

@app.route('/api/search/<keyword>&<rating>', methods=["POST", "GET"])
def api_get_photos(keyword, rating = 0):
    return jsonify(get_ph(keyword, rating = 0))


if __name__ == "__main__":
    db_conn = psycopg2.connect(dbname=DB_NAME, user=USER_NAME,
                                         password = PASSWORD, port = PORT, host=HOST)
    cursor = db_conn.cursor()
    app.run()
    cursor.close()
    db_conn.close()




