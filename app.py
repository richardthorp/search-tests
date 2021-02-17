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
# find({"field1": "one"}).find({"field2": "two"})


@app.route("/", methods=["GET", "POST"])
def search():
    return render_template("search.html")


def add_pagination(search_results):
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 9
    offset = page * per_page
    total = mongo.db.restaurants.count_documents(session["search_terms"]) - 9
    paginated_results = search_results[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')

    return paginated_results, page, per_page, pagination


@app.route("/searchbar_results", methods=["GET", "POST"])
def searchbar_results(**kwargs):
    if request.method == "POST":
        session["search_term"] = request.form.get("search")
        filters = dict(request.form.items())
        filters.pop("search")
        if session["search_term"] == "":
            search_terms = {}
        else:
            search_terms = {"$text": {"$search": session["search_term"]}}

        if filters:
            search_terms.update(filters)
        session["search_terms"] = search_terms

    if request.args:
        sort_by = request.args.to_dict()["sort_by"]
        print(sort_by)
        search_results = mongo.db.restaurants.find(
                         session["search_terms"]).sort(sort_by, 1)
    else:
        search_results = mongo.db.restaurants.find(session["search_terms"])

    #     session["sort_by"] = request.args.to_dict()["sort_by"]
    # if session["sort_by"]:
    #     search_results = mongo.db.restaurants.find(
    #                      session["search_terms"]).sort(session["sort_by"], 1)

    (paginated_results, page,
     per_page, pagination) = add_pagination(search_results)

    return render_template("result.html",
                           results=paginated_results,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           searchterm=session["search_term"])


# @app.route("/searchbar_results")
# def sort_results():

@app.route("/result/<keyword>")
def keyword_search(keyword):
    results = mongo.db.restaurants.find({"$text":
                                         {"$search": keyword}})
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page',
                                           offset='offset')

    # If you are hard coding the number of items per page
    # then uncomment the two lines below
    per_page = 9
    offset = page * per_page
    # Gets the total values to be used later
    total = results.count()
    # Paginates the values
    paginated_results = results[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4', search=True)

    return render_template("result.html",
                           results=paginated_results,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )


def get_average_rating():
    ratings = mongo.db.rating.find()
    votes_total = 0
    num_of_votes = mongo.db.rating.find().count()
    for rating in ratings:
        votes_total += int(rating["rating"])
    vote_average = votes_total / num_of_votes

    return vote_average


@app.route('/ratings', methods=["GET", "POST"])
def ratings():
    userId = 100
    if request.method == "POST":
        existing_rating = mongo.db.rating.find_one({"userId": userId})

        if existing_rating:
            flash("Vote already recieved")

        else:
            rating = {
                "userId": userId,
                "rating": request.form.get("rate")
            }
            mongo.db.rating.insert_one(rating)
            flash("Rating recieved")

    return render_template("ratings.html", user=userId)


# @app.route('/ratings', methods=["GET", "POST"])
# def favourite():
#     userId =  mongo.db.users.find_one({"userId": 100 })


#     return render_template("ratings.html")

#     return render_template("ratings.html", user=userId)

@app.route('/tests', methods=["GET", "POST"])
def tests():
    if request.method == "POST":
        query = {}
        # print(dir(request.form))
        filters = request.form.items()
        for key, value in filters:
            query[key] = value
        print(query)
        results = mongo.db.recipes.find(query)
        return render_template('tests.html', results=results)
    return render_template('tests.html')


# filter_dict = {}


# @app.route('/tests/<args>')
# def filter(args):
#     if args == 'clear':
#         return render_template('tests.html')
#     else:
#         filter_dict = {}
#         # take string passed from jinja and make into list of [key, value]
#         args_array = args.replace(" ", "").split(",")
#         filter_dict[args_array[0]] = args_array[1]
#         # session["filters"].update(filter_dict)

#     results = mongo.db.recipes.find(filter_dict)
#     return render_template('tests.html', results=results)


@app.route('/tests')
def clear_filter():
    print(session["filter"])
    del session["filter"]
    print(session["filter"])
    redirect(url_for('tests'))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
