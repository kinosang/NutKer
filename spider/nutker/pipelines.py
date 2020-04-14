# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don"t forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
from twisted.enterprise import adbapi

class SpiderPipeline(object):
    def __init__(self):
        self.file = codecs.open("guokr.json", "w", encoding="utf-8")

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()

class MySQLStorePipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host    = settings["MYSQL_HOST"],
            db      = settings["MYSQL_DBNAME"],
            user    = settings["MYSQL_USER"],
            passwd  = settings["MYSQL_PASSWD"],
            charset = "utf8",
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

    def _do_upsert(self, conn, item, spider):
        conn.execute("SELECT 1 FROM articles WHERE id = %s", (item["id"], ))

        ret = conn.fetchone()

        if ret:
            conn.execute(
                "update articles set subject = %s, subject_url = %s, author = %s, author_url = %s, url = %s, title = %s, small_image = %s, summary = %s, content = %s, date_created = %s, date_published = %s, date_modified = %s, resource_url = %s where id = %s",
                (item["subject"]["name"], item["subject"]["url"], item["author"]["nickname"], item["author"]["url"], item["url"], item["title"], item["small_image"], item["summary"], item["content"], item["date_created"], item["date_published"], item["date_modified"], item["resource_url"], item["id"])
            )
            spider.log("Item updated in db: %s" % item["id"])
        else:
            conn.execute(
                "insert into articles(id, subject, subject_url, author, author_url, url, title, small_image, summary, content, date_created, date_published, date_modified, resource_url) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (item["id"], item["subject"]["name"], item["subject"]["url"], item["author"]["nickname"], item["author"]["url"], item["url"], item["title"], item["small_image"], item["summary"], item["content"], item["date_created"], item["date_published"], item["date_modified"], item["resource_url"])
            )
            spider.log("Item stored in db: %s" % item["id"])

    def _handle_error(self, failue, item, spider):
        spider.log.err(failure)

