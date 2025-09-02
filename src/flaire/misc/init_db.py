import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flaire import models

BRANDS = (
    'Afnan',
    'Al Haramain',
    'French Avenue',
    'Lattafa'
    'Rasasi',
)

MERCHANTS = (
    'amazon',
    'brasty',
    'deloox',
    'douglas',
    'druni',
    'ferwer',
    'miravia',
    'notino',
)

def get_arguments():
    parser = argparse.ArgumentParser(
        prog='python -m flaire.misc.init_db',
        description='Flaire initialize database of static data',
    )

    parser.add_argument('-d', '--database', required=True)
    parser.add_argument('-m', '--merchant', action='store_true', help='Fill with merchant data')
    parser.add_argument('-b', '--brand', action='store_true', help='Fill with brand data')

    arguments = parser.parse_args()
    return arguments

def fill_merchants(session):
    for merchant_name in MERCHANTS:
        if not session.query(models.Merchant).filter_by(name=merchant_name).first():
            session.add(models.Merchant(name=merchant_name))
    session.commit()

def fill_brands(session):
    for brand_name in BRANDS:
        if not session.query(models.Brand).filter_by(name=brand_name).first():
            session.add(models.Brand(name=brand_name))
    session.commit()

def main():
    arguments = get_arguments()

    engine = create_engine(f"sqlite:///{arguments.database}")
    Session = sessionmaker(bind=engine)
    with Session() as session:
        if arguments.merchant:
            fill_merchants(session)

        if arguments.brand:
            fill_brands(session)

if __name__ == '__main__':
    main()
