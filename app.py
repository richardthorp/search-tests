import os
from flask_pymongo import PyMongo
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
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
        return render_template("result.html", results=results)

    return render_template("search.html")


@app.route("/result/<keyword>")
def keyword_search(keyword):
    results = mongo.db.restaurants.find({"$text": {"$search": keyword}})
    return render_template("result.html", results=results)


@app.route("/result")
def result():
    return render_template("result.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
