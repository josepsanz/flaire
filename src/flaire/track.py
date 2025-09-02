import urllib
import hashlib
import logging
import argparse
import datetime

import yaml
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import scrap
from . import scrapers as sc
from . import models

logger = logging.getLogger(__name__)


class Tracker:
    def __init__(self, filename):
        with open(filename, 'r') as fp:
            self.contract = yaml.load(fp, Loader=yaml.SafeLoader)

        #self._engine = create_engine(f"sqlite:///{self.contract['database']}")
        #self._session = sessionmaker(bind=self._engine)

    @classmethod
    def get_tasks(cls, target: dict):
        for url in target['links']:
            merchant, merchant_scraper = scrap.get_merchant_scraper(url)
            task = merchant_scraper(data={'url': url})
            yield {'merchant': merchant, 'task': task}

    @classmethod
    def get_data(cls, track_list: list):
        for target in track_list:
            yield from cls.get_row(target)

    @classmethod
    def get_signature(cls, name, brand, type_, size):
        data_sig = f'{name.lower()} - {brand.lower()} - {type_.lower()} - {size}'
        md5 = hashlib.md5(data_sig.encode('utf-8'))
        return md5.hexdigest()

    @classmethod
    def get_row(cls, target: dict):
        name = target['name']
        brand = target['brand']
        type_ = target['type']
        size = target['size']

        sig = cls.get_signature(name, brand, type_, size)

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

    @classmethod
    def get_df(cls, track_list: list) -> pd.DataFrame:
        for target in track_list:
            target['tasks'] = tuple(cls.get_tasks(target))

        df = pd.DataFrame(cls.get_data(track_list))
        return df

    @classmethod
    def _insert_merchant(cls, session, name):
        pass

    @classmethod
    def _insert_brand(cls, session, name):
        pass

    @classmethod
    def _insert_perfum(cls, session, name: str, brand: str, type_: str, size: int, sig: str):
        perfum = models.Perfume(
            name=name,
            brand=brand,
            type=type_,
            size=size,
            sig=sig,
        )
        try:
            session.add(perfum)
        except IntegrityError:
            session.rollback()
            logger.warning(f'{name} perfume from {brand} is already in the database. Skip!')

    @classmethod
    def _insert_price(cls, merchant: str, price: str):
        pass

    def insert_data(self, df: pd.DataFrame):
        ts = datetime.datetime.now()
        gg = dg.groupby('sig')
        with self._session() as session:
            for sig, group in gg.groups:
                pf = group.iloc[0]
                self._insert_perfum(
                    name=pf['name'],
                    brand=pf['brand'],
                    type_=pf['type'],
                    size=pf['size'],
                    sig=pf['sig']
                )
                for _, row in group.iterrow():
                    merchant = row['merchant']
                    price = row['price']
                    sig = sig

    def track(self):
        df = self.get_df(self.contract['track'])
        return df

def get_arguments():
    parser = argparse.ArgumentParser(
        prog='python -m flaire.track',
        description='Flaire track',
        epilog='Scrap, track and smell!'
    )

    parser.add_argument('filename', help='YaML file with targets to scrap')
    arguments = parser.parse_args()
    return arguments

def main():
    arguments = get_arguments()

    tracker = Tracker(arguments.filename)
    df = tracker.track()
    #df.set_index('sig', inplace=True)
    print(df)

if __name__ == '__main__':
    main()
