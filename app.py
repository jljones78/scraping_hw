from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pymongo
import lxml
import scrape_mars

# intialize flask

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection

conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)
db = client.mars_db

# create routes
@app.route("/")
def home():
    mars_db = db.collection.find_one()
    return render_template("index.html", mars_db=mars_db)


@app.route("/scrape")
def scrape():
    mars_db = scrape_mars.scrape()
    db.collection.drop()
    db.collection.insert_one(mars_db)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
