import postgres_function
import user_definition
from flask import Flask, request, render_template, jsonify, redirect, url_for
from string import punctuation
from itertools import compress
import re
import sys
reload(sys)

sys.setdefaultencoding('utf8')

app = Flask(__name__)

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
    postgres_function.select_data(cursor, "yelpData", 'photos', constraint)
    return [i[0] for i in cursor.fetchall()]

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
    postgres_function.select_data(cursor, "yelpData", '*', constraint)
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
    postgres_function.select_data(cursor, "yelpData", '*', constraint)
    return jsonify(cursor.fetchall()[0])

@app.route('/api/search/<keyword>&<rating>', methods=["POST", "GET"])
def api_get_photos(keyword, rating = 0):
    return jsonify(get_ph(keyword, rating = 0))

if __name__ == "__main__":
    db_conn = postgres_function.connectdb(user_definition.dbname, user_definition.usr_name,
                                          user_definition.password, user_definition.port,
                                          user_definition.host)
    cursor = postgres_function.db_cursor(db_conn)

    app.run(debug=True)
    cursor.close()
    db_conn.close()



