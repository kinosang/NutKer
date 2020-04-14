#-*-coding:utf-8 -*-

import web

db = web.database(dbn='mysql', db='guokr', user='guokr', pw='hTPn7GjRNC4trVUP', charset='utf8')
render = web.template.render('templates/', cache=False)

urls = (
    '/', 'index'
)

class index:
    def GET(self):
        articles = db.select('articles', order="date_published DESC", limit=30)
        web.header('Content-Type', 'text/xml')
        return render.feed(articles)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
