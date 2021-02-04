import os
from flask_pymongo import PyMongo
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_paginate import Pagination, get_page_args
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)

"""
CREATE AN INDEX TO ENABLE SEARCHING
mongo.db.restaurants.create_index([("name", "text"),("cuisine", "text")])
"""


@app.route("/", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_term = request.form.get("search")
        results = mongo.db.restaurants.find({"$text":
                                            {"$search": search_term}})
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
                               pagination=pagination,)
    return render_template("search.html")


@app.route("/result/<keyword>")
def keyword_search(keyword):
    results = mongo.db.restaurants.find({"$text": {"$search": keyword}})
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    # If you are hard coding the number of items per page
    # then uncomment the two lines below
    per_page = 9
    offset = page * per_page

    # Gets the total values to be used later
    total = results.count()

    # Gets all the values
    # thetests = mongo.db.mongoTestingDataBase.find()
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


@app.route("/result")
def result():
    return render_template("result.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
