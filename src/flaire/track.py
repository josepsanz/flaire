import urllib
import hashlib
import argparse

import yaml
import pandas as pd

from . import scrap
from . import scrapers as sc


def get_arguments():
    parser = argparse.ArgumentParser(
        prog='python -m flaire.track',
        description='Flaire track',
        epilog='Scrap, track and smell!'
    )

    parser.add_argument('filename', help='YaML file with targets to scrap')
    arguments = parser.parse_args()
    return arguments

def get_tasks(target: dict):
    for url in target['links']:
        merchant, merchant_scraper = scrap.get_merchant_scraper(url)
        task = merchant_scraper(data={'url': url})
        yield {'merchant': merchant, 'task': task}

def get_data(targets: dict):
    for target in targets:
        yield from get_row(target)

def get_signature(name, brand, type_, size):
    data_sig = f'{name.lower()} - {brand.lower()} - {type_.lower()} - {size}'
    md5 = hashlib.md5(data_sig.encode('utf-8'))
    return md5.hexdigest()

def get_row(target: dict):
    name = target['name']
    brand = target['brand']
    type_ = target['type']
    size = target['size']

    sig = get_signature(name, brand, type_, size)

    for url, task in zip(target['links'], target['tasks']):
        merchant = task['merchant']
        price = task['task'].get()
        yield {
            'sig': sig,
            'name': name,
            'brand': brand,
            'type': type_,
            'size': size,
            'merchant': merchant,
            'price': price
        }

def track(targets: list):
    for target in targets:
        target['tasks'] = tuple(get_tasks(target))

    df = pd.DataFrame(get_data(targets))
    return df

def main():
    arguments = get_arguments()

    with open(arguments.filename, 'r') as fp:
        contract = yaml.load(fp, Loader=yaml.SafeLoader)

    df = track(contract['track'])
    #df.set_index('sig', inplace=True)
    print(df)

if __name__ == '__main__':
    main()
