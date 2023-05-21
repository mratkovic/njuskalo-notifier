import logging
import requests
import argparse
import configparser
from scrapy.crawler import CrawlerProcess
from sniffer_scraper.spider import NjuskaloSpider

# define logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def load_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="path to config file", required=True)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.optionxform = str #case sensitive names
    config.read(args.config)
    return config

def send_ping(ping_url):
    try:
        requests.get(ping_url, timeout=10)
    except requests.RequestException as e:
        logging.info(f'Sending ping failed! {ping_url}\n{e}')

def main():
    logging.info("Started...")
    config = load_config()

    crawler_settings = dict(config['CRAWLER_PROCESS_SETTINGS'])
    crawler_settings['ITEM_PIPELINES'] = {k: int(v) for k, v in config.items('ITEM_PIPELINES')}

    filters = {name: url for name, url in config.items('URLs')}
    n_pages = config.getint('CRAWLER_PROCESS_SETTINGS', 'n_pages')

    process = CrawlerProcess(crawler_settings)
    process.crawl(NjuskaloSpider, filters, n_pages)
    process.start()

    ping_url = config.get('MONITORING', 'ping_url', fallback=None)
    if ping_url:
        send_ping(ping_url)

    logging.info("Done...")


if __name__ == '__main__':
    main()