import scrapy
import logging
from scrapy.utils.log import configure_logging
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

configure_logging(install_root_handler=False)
logging.getLogger('scrapy').setLevel(logging.WARNING)
logging.getLogger('scrapy').propagate = False

class NjuskaloSpider(scrapy.Spider):
    name = "njuskalo"

    def __init__(self, filters=None, n_pages=1):
        self.n_pages = n_pages
        self.filters = {}
        if filters:
            self.filters = filters

    def start_requests(self):
        for filter_name, url in self.filters.items():
            yield scrapy.Request(url=url, callback=self.parse_page, meta={'filter_name': filter_name})

    def parse(self, response):
        price_eur, price_hrk = _parse_price(response)

        result = {
            'filter_name': response.meta.get('filter_name'),
            'url': response.url,
            'title': _css_get(response, '.ClassifiedDetailSummary-title::text'),
            'price_hrk': price_hrk,
            'price_eur': price_eur,
            'id': _css_get(response, '.ClassifiedDetailSummary-adCode::text').replace('Šifra oglasa:', '').strip(),
            'publish_date': _get_publish_date(response),
        }
        table = _parse_table(response)
        result['total_area'] = table.get('Stambena površina', '')
        result['table_data'] = str(table)

        yield result

    def parse_page(self, response):
        # logging.debug('Parsing %s', response.url)
        for href in response.css(".EntityList-item--Regular .entity-title .link::attr(href)"):
            oglas_url = response.urljoin(href.extract())
            yield scrapy.Request(oglas_url, self.parse, meta={'filter_name': response.meta.get('filter_name')})

        for req in self._next_page(response):
            yield req

    def _next_page(self, response):
        next_page_button = response.css(".Pagination-item--next .Pagination-link::text")
        next_page_url, page_num = _next_page_url(response.url)

        if next_page_button and page_num <= self.n_pages:
            yield scrapy.Request(next_page_url, self.parse_page, meta={'filter_name': response.meta.get('filter_name')})


def _next_page_url(url):
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    page_num = int(query_params.get('page', ['1'])[0]) + 1
    query_params['page'] = [page_num]

    new_query_string = urlencode(query_params, doseq=True)
    new_url = urlunsplit((scheme, netloc, path, new_query_string, fragment))

    return new_url, page_num


def _parse_table(response):
    table_values = response.css('.ClassifiedDetailBasicDetails-textWrapContainer')
    table_values = [_css_get(elem, '::text') for elem in table_values]

    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    table = {}
    for key, value in chunks(table_values, 2):
        table[key] = value
    return table


def _get_publish_date(response):
    data = response.css('.ClassifiedDetailSystemDetails-listData')
    if data:
        return _css_get(data[0], '::text')
    return ''

def _parse_price(response):
    def parse_price(val, currency):
        try:
            # sanitized = [d for d in val if d.isdigit()]
            sanitized = val.replace('.', '').replace(',', '').replace(currency, '')
            return int(sanitized)
        except:
            logging.error(f"Could not parse {currency} price: '{val}'")

    price_str = _css_get(response, f'.ClassifiedDetailSummary-priceDomestic::text')
    eur, *hrk = price_str.split(' / ', 1)
    eur = parse_price(eur,  u'€')
    hrk = parse_price(hrk[0], 'kn') if hrk else eur * 7.53450
    return eur, hrk

def _css_get(r, sel):
    selected = r.css(sel).extract()
    selected = filter(None, [x.strip() for x in selected])
    return ', '.join(selected)

