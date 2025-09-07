import argparse
import datetime

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import streamlit as st

from flaire import models



class Controller:
    DELTA = datetime.timedelta(days=180)

    def __init__(self, database):
        self._engine = create_engine(f"sqlite:///{database}")
        self._session = sessionmaker(bind=self._engine)

    def get_prices_ts(self, start_dt=None, end_dt=None):
        dt = datetime.datetime.now()
        start_dt = start_dt or dt - self.DELTA
        end_dt = end_dt or dt
        assert start_dt < end_dt

        with self._session() as session:
            query = (
                session.query(
                    models.Prices.ts,
                    models.Perfums.name.label('perfum'),
                    models.Brands.name.label('brand'),
                    models.Merchants.name.label('merchant'),
                    (models.Prices.price / 100.0).label('price')
                )
                .join(models.Perfums, models.Prices.perfum_id == models.Perfums.id)
                .join(models.Brands, models.Perfums.brand_id == models.Brands.id)
                .join(models.Merchants, models.Prices.merchant_id == models.Merchants.id)
                .filter(models.Prices.ts >= start_dt, models.Prices.ts <= end_dt)
                .order_by(models.Prices.ts, models.Perfums.name, models.Prices.price)
            )

            df = pd.DataFrame(query.all())
            return df

    def get_last_prices(self):
        df = self.get_prices_ts()
        groups = df.groupby(['perfum', 'merchant'])

        it = (group.iloc[-1] for (perfum, merchant), group in groups)
        ddf = pd.DataFrame(it)
        return ddf

def get_arguments():
    parser = argparse.ArgumentParser(
        prog=f'python -m streamlit run {__file__}',
        description='Flaire Panel',
        epilog='View historic prices'
    )

    parser.add_argument('database', help='SQLite3 database file')
    arguments = parser.parse_args()
    return arguments

def main_view(last_prices_df):
    st.set_page_config(
        page_title='Flaire Panel',
        page_icon='🧴'
    )

    st.write('# Flaire Panel')

    last_prices_df['price'] = last_prices_df['price'].map(lambda x: f'{x:.02f}€')
    st.dataframe(last_prices_df, hide_index=True)

    with st.sidebar:
        perfum = st.selectbox('Target Perfum:', ['Perfum A', 'Perfum B', 'Perfum C'])
        st.write(f'Your choice: {perfum}')

def main():
    arguments = get_arguments()

    controller = Controller(arguments.database)
    last_prices_df = controller.get_last_prices()

    main_view(last_prices_df)

    #df = pd.read_csv("my_data.csv")
    #st.line_chart(df)

if __name__ == '__main__':
    main()
