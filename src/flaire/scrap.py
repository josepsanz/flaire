import urllib
import argparse

from . import scrapers as sc

_MERCHANT_SCRAPERS_LU = {
    'notino.es': sc.scrape_notino_price,
    'brasty.es': sc.scrape_brasty_price,
    'druni.es': sc.scrape_druni_price,
    'douglas.es': sc.scrape_douglas_price,
    'primor.eu': sc.scrape_primor_price,
    'deloox.es': sc.scrape_deloox_price,
    'ferwer.es': sc.scrape_ferwer_price,
    'miravia.es': sc.scrape_miravia_price,
    'amazon.es': sc.scrape_amazon_price,
    'perfumerias.com': sc.scrape_perfumerias_price,
    'zara.com': sc.scrape_zara_price,
    'es.afnan.com': sc.scrape_afnan_official_shop_price,
}

def get_merchant_scraper(url: str) -> tuple:
    domain = urllib.parse.urlparse(url).netloc.replace('www.', '')
    merchant_scraper = _MERCHANT_SCRAPERS_LU[domain]
    merchant = domain[:domain.rfind('.')]
    return merchant, merchant_scraper

def get_arguments():
    parser = argparse.ArgumentParser(
        prog='python -m flaire.scrap',
        description='Flaire scraper',
        epilog='Scrap a single url'
    )

    parser.add_argument('url', help='url to scrap')
    arguments = parser.parse_args()
    return arguments

def scrap(url):
    _, merchant_scraper = get_merchant_scraper(url)
    task = merchant_scraper(data={'url': url})
    price = task.get()
    print(f'{url}: {price}€')

def main():
    arguments = get_arguments()
    scrap(arguments.url)

if __name__ == '__main__':
    main()
