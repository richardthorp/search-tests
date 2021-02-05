import os
from flask_pymongo import PyMongo
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from bson.objectid import ObjectId
from flask_paginate import Pagination, get_page_args
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

"""
CREATE AN INDEX TO ENABLE SEARCHING
mongo.db.restaurants.create_index([("name", "text"),("cuisine", "text")])
"""


@app.route("/", methods=["GET", "POST"])
def search():
    return render_template("search.html")


@app.route("/searchbar_results", methods=["GET", "POST"])
def searchbar_results():
    if request.method == "POST":
        session["search_term"] = request.form.get("search")

    results = mongo.db.restaurants.find({"$text":
                                        {"$search": session["search_term"]}})

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 9
    offset = page * per_page
    total = results.count()
    paginated_results = results[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template("result.html",
                           results=paginated_results,
                           page=page,
                           per_page=per_page,
                           pagination=pagination)

    results = list(session["results"])
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 9
    offset = page * per_page
    total = results.count()
    paginated_results = results[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template("result.html",
                           results=paginated_results,
                           page=page,
                           per_page=per_page,
                           pagination=pagination)


@app.route("/result/<keyword>")
def keyword_search(keyword):
    results = mongo.db.restaurants.find({"$text":
                                            {"$search": keyword}})
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')

    # If you are hard coding the number of items per page
    # then uncomment the two lines below
    per_page = 9
    offset = page * per_page

    # Gets the total values to be used later
    total = results.count()

    # Paginates the values
    paginated_results = results[offset: offset + per_page]

    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template("result.html",
                           results=paginated_results,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )


@app.route('/ratings', methods=["GET", "POST"])
def ratings():
    if request.method == "POST":
        userId = 107
        rating = {
                "userId": userId,
                "rating": request.form.get("rate")
                }
        existing_rating = mongo.db.ratings.find_one({"userId": userId})

        if existing_rating:
            mongo.db.rating.insert_one(rating)
            flash("Rating recieved")

        else:
            flash("Rating already recieved")


    return render_template("ratings.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
