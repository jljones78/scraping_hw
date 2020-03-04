# import dependencies
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import pymongo
import pprint
import lxml
from pymongo import MongoClient
from selenium import webdriver
from splinter import Browser


def scrape():
    scrape_results_dict = {}

    # scrape news site for title and paragraph text, save off to variables
    news_url = "https://mars.nasa.gov/news/"
    driver = webdriver.Firefox()
    driver.get(news_url)
    driver.implicitly_wait(10)
    html = driver.page_source
    news_soup = bs(html, "html.parser")
    news_title = (news_soup.find("div", class_="list_text")).find("a").text
    news_paragraph = news_soup.find("div", class_="article_teaser_body").text
    scrape_results_dict["news_title"] = news_title
    scrape_results_dict["news_paragraph"] = news_paragraph

    # find featured Mars image from JPL, save full-size image url
    # note: this url doesn't seem to pull up a Mars image any longer
    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    base_jpl_url = "https://www.jpl.nasa.gov"
    driver = webdriver.Firefox()
    driver.get(jpl_url)
    html = driver.page_source
    img_soup = bs(html, "html.parser")

    # build url from style tag
    image_url = (
        img_soup.find("article")["style"]
        .replace("background-image: url(", "")
        .replace(");", "")[1:-1]
    )
    featured_image_url = base_jpl_url + image_url
    scrape_results_dict["featured_image_url"] = featured_image_url

    # scrape latest mars weather from twitter
    mars_wx_url = "https://twitter.com/MarsWxReport"
    r = requests.get(mars_wx_url)
    html = r.text
    wx_soup = bs(html, "html.parser")

    mars_weather = wx_soup.find_all("div", class_="js-tweet-text-container")[0].text
    scrape_results_dict["mars_weather"] = mars_weather

    # scrape Mars facts website, display as html table str using pandas
    mars_facts_url = "https://space-facts.com/mars/"
    facts_df = pd.read_html(mars_facts_url)[0].rename(
        index=str, columns={"0": "Category", "1": "Data"}
    )
    facts_table = facts_df.to_html(na_rep="", index=False)
    scrape_results_dict["mars_facts"] = facts_table

    # scrape USGS Astrogeology site for high res photos of hemispheres
    usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser = Browser("firefox")
    browser.visit(usgs_url)

    # create list of titles and urls to loop through
    hemisphere_list = [
        (a.text, a["href"]) for a in browser.find_by_css('div[class="description"] a')
    ]

    hemisphere_dict = []
    for title, hemisphere_url in hemisphere_list:
        temp_dict = {}
        temp_dict["title"] = title
        browser.visit(hemisphere_url)
        temp_dict["img_url"] = browser.find_by_css('img[class="wide-image"]')["src"]
        hemisphere_dict.append(temp_dict)
    scrape_results_dict["hemisphere_dict"] = hemisphere_dict

    return scrape_results_dict
