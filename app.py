from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from flipkart_Scrapper.flipDAO import flipkartScapper
import os


app = Flask(__name__)   # initialising the flask app with the name 'app'


@app.route('/', methods=['POST', 'GET'])  # route with allowed methods as POST and GET
@cross_origin()
def home():
    return render_template('index.html')


@app.route('/search', methods = ['GET', 'POST'])
@cross_origin()
def searchReview():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ", "")
        try:
            k=1
            reviews = []
            dao = flipkartScapper()
            flip_url = dao.CreateUrl(searchString)
            flip_page = dao.read_WebPage(flip_url)
            while k < 2:
                flip_review_link = dao.get_ProductLink(flip_page, k)
                flip_scrapper = dao.scrape(flip_review_link)

                for commentbox in flip_scrapper:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except:
                        name = "No Name"
                    try:
                        rating = commentbox.div.div.div.div.div.text
                    except:
                        rating = "No Rating"
                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except:
                        custComment = "No Customer Comment"

                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}  # saving that details to a dictionary
                    dao.MongoDBConn(searchString, mydict)
                    reviews.append(mydict)
                k = k+1
                try:
                    dao.convertToCSV(searchString, reviews)
                except Exception as e:
                    print(e)


            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])  # showing the review to the user

        except:
            return 'something is wrong'
    else:
        return render_template('index.html')





port = int(os.getenv("PORT"))
if __name__ == '__main__':
    # app.run(port=8000, debug=True) # running the app on the local machine on port 8000
    app.run(host='0.0.0.0', port=port)
