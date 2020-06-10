import pymongo
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import csv


class flipkartScapper:


    def MongoDBConn(self, sString, mydict):
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017")  # opening a connection to Mongo
            db = dbConn['FlipkartScrapperDB']  # connecting to database
            table = db[sString]
            x = table.insert_one(mydict)


        except Exception as e:
            print(e)

    def CreateUrl(self, sString):
        flipkart_url = "https://www.flipkart.com/search?q=" + sString  # preparing url to search the product on flipkart
        return flipkart_url

    def read_WebPage(self, flipkart_url):
        uClient = uReq(flipkart_url)  # requesting the webpage form the internet
        flipkartPage = uClient.read()  # reading the webpage
        uClient.close()  # closing the connection to the webserver
        return flipkartPage

    def get_ProductLink(self, flipkartPage,i):
        flipkart_html = bs(flipkartPage, "html.parser")  # parsing webpage as HTML
        bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})  # searching for appropriate tag to redirect to the product link
        del bigboxes[0:3]  # the first 3 members of the list do not contain relevant information, hence deleting them
        box = bigboxes[0]  # taking the first iteration (for demo)
        productLink = "https://www.flipkart.com" + box.div.div.div.a['href']  # extracting the actual product link
        prodRes = requests.get(productLink)  # getting the product page from server
        prod_html = bs(prodRes.text, "html.parser")  # parsing the product page as HTML
        all_review = prod_html.find("div", {"class": "swINJg _3nrCtb"})
        all_review_link = all_review.find_parent().get('href')
        all_review_link = "https://www.flipkart.com" + all_review_link + '&page=' + str(i)
        return all_review_link

    def scrape(self, all_review_link):
        allReviewRes = requests.get(all_review_link)  # getting the product page from the server
        allreview_html = bs(allReviewRes.text, "html.parser")  # parsing the product page as HTMl
        commentboxes = allreview_html.find_all("div", {"class": "_3gijNv col-12-12"})  # finding the HTML section containing the customer comments
        del commentboxes[0:4]  # first 3 members of the list do not contain relevant infoemation, hence deleting them
        # cbox = commentboxes[1]
        return commentboxes

    def convertToCSV(self, sString, reviews):
        csv_columns = ['Product', 'Name', 'Rating', 'CommentHead', 'Comment','_id']
        with open(sString+'.csv', 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in reviews:
                writer.writerow(data)

