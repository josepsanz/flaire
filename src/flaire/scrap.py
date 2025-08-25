import urllib
import argparse

import yaml

from . import scrapers as sc

MERCHANT_SCRAPERS_LU = {
    'notino.es': sc.scrape_notino_price,
    'brasty.es': sc.scrape_brasty_price,
    'druni.es': sc.scrape_druni_price,
    'douglas.es': sc.scrape_douglas_price,
    'primor.eu': sc.scrape_primor_price,
    'deloox.es': sc.scrape_deloox_price,
    'ferwer.es': sc.scrape_ferwer_price,
    'miravia.es': sc.scrape_miravia_price,
    'amazon.es': sc.scrape_amazon_price,
}

def get_arguments():
    parser = argparse.ArgumentParser(
        prog='python -m flaire.scrap',
        description='Flaire scraper',
        epilog='Scrap, track and smell!'
    )

    parser.add_argument('filename', help='YaML file with targets to scrap')
    arguments = parser.parse_args()
    return arguments

def scrap(targets):
    tasks = {
        'Notino - Lattafa - Asad': {
            'url': 'https://www.notino.es/lattafa/asad-eau-de-parfum-para-hombre/p-16145677/'
        },
        'Brasty - Afnan - Supremacy Not Only Intense': {
            'url': 'https://www.brasty.es/afnan-supremacy-not-only-intense-perfume-para-hombre-150-ml'
        },
        'Druni - Lattafa - Asad Bourbon': {
            'url': 'https://www.druni.es/asad-bourbon-lattafa-eau-parfum-hombre'
        },
        'Primor - Halloween - Halloween Man X': {
            'url': 'https://www.primor.eu/es_es/halloween-halloween-man-x-edt-112384.html?#854=66504'
        },
        "Deloox - Afnan - Supremacy Collector's": {
            'url': 'https://www.deloox.es/producto/1343240/afnan-supremacy-eau-de-parfum-edicion-de-coleccionista-100-ml.html'
        },
        "Ferwer - Afnan - Supremacy Collector's": {
            'url': 'https://www.ferwer.es/afnan-supremacy-not-only-intense-extracto-de-perfume-para-hombres'
        },
        'Miravia - Armaf - Odyssey Mandarin Sky Elixir': {
            'url': 'https://www.miravia.es/p/armaf-odyssey-mandarin-sky-elixir-eau-de-parfum-100ml-perume-arabe-original-para-hombre-i1373294636273528.html'
        },
        'Amazon - Lattafa - Khamrah Qahwa': {
            'url': 'https://www.amazon.es/dp/B0CWBS4NN7'
        },
        'Douglas - Lattafa - Asad': {
            'url': 'https://www.douglas.es/es/p/5011503009'
        },
    }

    for data in tasks.values():
        merchant = urllib.parse.urlparse(data['url']).netloc.replace('www.', '')
        merchant_scraper = MERCHANT_SCRAPERS_LU[merchant]

        data['task'] = merchant_scraper(data=data)

    for name, data in tasks.items():
        print(f"{name:64} {data['task'].get()}€")

def main():
    arguments = get_arguments()

    with open(arguments.filename, 'r') as fp:
        targets = yaml.load(fp, Loader=yaml.SafeLoader)

    scrap(targets)

if __name__ == '__main__':
    main()
