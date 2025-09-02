import urllib
import argparse

from . import scrapers as sc

_MERCHANT_SCRAPERS_LU = {
    'notino': sc.scrape_notino_price,
    'brasty': sc.scrape_brasty_price,
    'druni': sc.scrape_druni_price,
    'douglas': sc.scrape_douglas_price,
    'primor': sc.scrape_primor_price,
    'deloox': sc.scrape_deloox_price,
    'ferwer': sc.scrape_ferwer_price,
    'miravia': sc.scrape_miravia_price,
    'amazon': sc.scrape_amazon_price,
}

def get_merchant_scraper(url: str) -> tuple:
    merchant = urllib.parse.urlparse(url).netloc.replace('www.', '')
    merchant = merchant[:merchant.find('.')]
    merchant_scraper = _MERCHANT_SCRAPERS_LU[merchant]
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
