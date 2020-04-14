# -*- coding: utf-8 -*-
import scrapy
import json
import MySQLdb

class GuokrSpider(scrapy.Spider):
    name = "guokr"

    allowed_domains = ["guokr.com"]

    handle_httpstatus_list = [500]

    offset = 0
    limit  = 100
    total = 0

    def __init__(self, db):
        self.db = db
        self.start_urls = ["http://www.guokr.com/apis/minisite/article.json?retrieve_type=by_subject&limit=%s&offset=0" % self.limit]

        c = self.db.cursor()
        c.execute("SELECT count(*) as total FROM articles")
        ret = c.fetchone()
        self.total_in_db = ret[0]

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        dbargs = dict(
            host    = settings["MYSQL_HOST"],
            db      = settings["MYSQL_DBNAME"],
            user    = settings["MYSQL_USER"],
            passwd  = settings["MYSQL_PASSWD"],
            charset = "utf8",
            use_unicode = True,
        )
        db = MySQLdb.connect(**dbargs)
        return cls(db)

    def parse(self, response):
        jsonresponse = json.loads(response.body_as_unicode())

        self.offset += self.limit

        if jsonresponse["ok"]:
            self.total = jsonresponse["total"] - self.total_in_db

            for article in jsonresponse["result"]:
                c = self.db.cursor()
                c.execute("SELECT 1 FROM articles WHERE id = %s", (article["id"], ))
                ret = c.fetchone()

                if not ret:
                    yield scrapy.Request(article["resource_url"], callback=self.parse_article)
                else:
                    continue
        else:
            print "Get %r" % (response)

        if self.offset <= self.total:
            link = "http://www.guokr.com/apis/minisite/article.json?retrieve_type=by_subject&limit=%s&offset=%s" % (self.limit, self.offset)

            yield scrapy.Request(link, callback=self.parse)

    def parse_article(self, response):
        jsonresponse = json.loads(response.body_as_unicode())

        yield jsonresponse["result"]

    def process_exception(self, response, exception, spider):
        pass
