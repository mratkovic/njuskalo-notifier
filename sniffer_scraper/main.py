import logging
import argparse
import configparser
from scrapy.crawler import CrawlerProcess
from sniffer_scraper.spider import NjuskaloSpider

# define logging
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def load_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default='./config_example.ini', help="path to config file")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.optionxform = str #case sensitive names
    config.read(args.config)
    return config


def main():
    config = load_config()

    crawler_settings = dict(config['CRAWLER_PROCESS_SETTINGS'])
    crawler_settings['ITEM_PIPELINES'] = {k: int(v) for k, v in config.items('ITEM_PIPELINES')}

    urls = [v for _, v in config.items('URLs')]
    n_pages = config.getint('CRAWLER_PROCESS_SETTINGS', 'n_pages')

    process = CrawlerProcess(crawler_settings)
    process.crawl(NjuskaloSpider, urls, n_pages)
    process.start()


if __name__ == '__main__':
    main()



