#-*-coding:utf-8 -*-

import web
import copy

db = web.database(dbn='mysql', db='guokr', user='guokr', pw='hTPn7GjRNC4trVUP', charset='utf8')
render = web.template.render('templates/', cache=False)

urls = (
    '/', 'index',
    '/page/(.+)', 'reading'
)

class index:
    def GET(self):
        return web.seeother('/page/0')

class reading:
    def GET(self, offset):
        offset = int(offset)
        articles_m = db.select('articles', what="id, title", order="date_published DESC", limit=10, offset=offset)
        articles = db.select('articles', order="date_published DESC", limit=10, offset=offset)
        return render.reading(articles_m, articles, offset)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
