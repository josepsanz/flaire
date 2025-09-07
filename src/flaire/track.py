import urllib
import hashlib
import logging
import argparse
import datetime

import yaml
import colorama
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import scrap
from . import scrapers as sc
from . import models

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Tracker:
    def __init__(self, filename):
        with open(filename, 'r') as fp:
            self.contract = yaml.load(fp, Loader=yaml.SafeLoader)

        self._connect_db()

    def _connect_db(self):
        self._engine = create_engine(f"sqlite:///{self.contract['database']}")
        self._session = sessionmaker(bind=self._engine)

    @classmethod
    def norm_text(cls, text):
        return text.lower()
        #return text.title().replace(' ', '')

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
        data_sig = f'{name} - {brand} - {type_} - {size}'
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
                'name': cls.norm_text(name),
                'brand': cls.norm_text(brand),
                'type': type_.lower(),
                'size': size,
                'merchant': cls.norm_text(merchant),
                'price': price
            }

    @classmethod
    def get_df(cls, track_list: list) -> pd.DataFrame:
        for target in track_list:
            target['tasks'] = tuple(cls.get_tasks(target))

        df = pd.DataFrame(cls.get_data(track_list))
        return df

    @classmethod
    def get_entity_id_by_name(cls, session, model, entity_name):
        stmt = sa.select(model.id).where(model.name == entity_name)
        if hasattr(model, '__lut__') is False:
            entity_id = session.scalar(stmt)
        elif (entity_id := model.__lut__.get(entity_name)) is None:
            if (entity_id := session.scalar(stmt)):
                model.__lut__[entity_name] = entity_id

        return entity_id

    @classmethod
    def _insert_merchant(cls, session, merchant):
        merchant_id = cls.get_entity_id_by_name(session, models.Merchants, merchant)
        if not merchant_id:
            entity = models.Merchants(name=merchant)
            session.add(entity)

    @classmethod
    def _insert_brand(cls, session, brand):
        brand_id = cls.get_entity_id_by_name(session, models.Brands, brand)
        if not brand_id:
            entity = models.Brands(name=brand)
            session.add(entity)

    @classmethod
    def _insert_perfum(cls, session, name: str, brand: str, type_: str, size: int, sig: str):
        if not cls.get_entity_id_by_name(session, models.Perfums, name):
            brand_id = cls.get_entity_id_by_name(session, models.Brands, brand)
            perfum = models.Perfums(
                name=name,
                brand_id=brand_id,
                type=type_,
                size=int(size),
                sig=sig
            )
            session.add(perfum)

    @classmethod
    def _insert_price(cls, session, perfum_name: str, merchant_name: str, price: float):
        perfum_id = cls.get_entity_id_by_name(session, models.Perfums, perfum_name)
        merchant_id = cls.get_entity_id_by_name(session, models.Merchants, merchant_name)
        price = int(100 * price)
        ts = datetime.datetime.now()
        price = models.Prices(perfum_id=perfum_id, merchant_id=merchant_id, ts=ts, price=price)
        session.add(price)

    def insert_data(self, df: pd.DataFrame):
        with self._session() as session:
            # Insert merchants
            for merchant in df['merchant'].unique():
                self._insert_merchant(session, merchant)
            session.commit()

            # Insert brands
            for brand in df['brand'].unique():
                self._insert_brand(session, brand)
            session.commit()

            # Insert perfums and prices
            groups = df.groupby('sig')
            for sig, group in groups:
                pf = group.iloc[0]
                perfum_name = pf['name']

                self._insert_perfum(
                    session,
                    name=perfum_name,
                    brand=pf['brand'],
                    type_=pf['type'],
                    size=pf['size'],
                    sig=pf['sig']
                )
                session.commit()

                for _, row in group.iterrows():
                    merchant_name = row['merchant']
                    self._insert_price(session, perfum_name, merchant_name, row['price'])
                session.commit()

    def track(self):
        df = self.get_df(self.contract['track'])
        df.dropna(subset='price', inplace=True)
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
    tracker.insert_data(df)

    print(df)
    print()

    print(f"--> {colorama.Style.BRIGHT}streamlit run src/flaire/panel.py {tracker.contract['database']}{colorama.Style.RESET_ALL}")

if __name__ == '__main__':
    main()
