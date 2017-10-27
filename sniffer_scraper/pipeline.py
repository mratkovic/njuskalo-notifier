from tqdm import tqdm
from datetime import datetime
from sniffer_scraper.send_email import Mail
import logging
import sqlite3


class PrintPipeline(object):

    def __init__(self):
        self.items = []
        self.pbar = tqdm(desc='Ads scraped', unit='ads')

    def process_item(self, item, spider):
        if item:
            self.pbar.update()
            self.items.append(item)
            return item

    def close_spider(self, spider):
        for item in sorted(self.items, key=lambda x: x['publish_date'], reverse=True):
            print('[{}], {} euro, {}'.format(item['publish_date'], item['price_eur'], item['title']))
            print(item['url'])
            print()

        print("Total: {}".format(len(self.items)))


class SqliteFilterNewPipeline(object):
    def __init__(self):
        self.con = None
        self.cur = None

    def setup(self, db_path):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()
        self.create_table()

    def drop_table(self):
        self.cur.execute("DROP TABLE IF EXISTS Ads")

    def con_close(self):
        self.con.close()

    def __del__(self):
        self.con_close()

    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Ads(
                id INTEGER PRIMARY KEY NOT NULL,
                ad_id TEXT,
                title TEXT,
                price_euro INTEGER,
                price_hrk INTEGER,
                date_published TEXT,
                total_area TEXT,
                url TEXT,
                table_data TEXT)"""
        )

    def process_item(self, item, spider):
        if not item:
            return item

        if self.con is None:
            self.setup(spider.settings.get('db_path'))

        if not self.exists(item):
            self.dump_to_db(item)
            return item

    def exists(self, item):
        return self.cur.execute("SELECT * from Ads where ad_id=? and date_published=?",
                                (item['id'], item['publish_date'])).fetchone()

    def dump_to_db(self, item):
        self.cur.execute(
            """INSERT INTO Ads(ad_id, title, price_euro, price_hrk, date_published, total_area, url, table_data)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
            (item['id'], item['title'], item['price_eur'],
             item['price_hrk'], item['publish_date'], item['total_area'],
             item['url'], item['table_data'])
        )
        self.con.commit()


class EmailPipeline(object):
    def __init__(self):
        self.items = []

    def process_item(self, item, spider):
        if item:
            self.items.append(item)
            return item

    def close_spider(self, spider):
        lines = []
        for item in sorted(self.items, key=lambda x: x['publish_date'], reverse=True):
            lines.append('[{}], {} eura, {}'.format(item['publish_date'], item['price_eur'], item['title']))
            lines.append(item['url'])
            lines.append('\n')
        if not lines:
            return

        body = '\n'.join(lines)
        title = 'Report - {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        def get(prop):
            return spider.settings.get(prop)

        mail = Mail(get('username'),
                    get('app_password'),
                    get('smtp_server'),
                    int(get('port')))
        mail.send_mail(title, body, get('recipient'))
