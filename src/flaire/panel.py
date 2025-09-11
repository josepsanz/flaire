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
        self._df = None

    @property
    def df(self):
        if self._df is None:
            self._df = self.get_prices_ts()

        return self._df

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

            self._df = pd.DataFrame(query.all())
            return self._df

    def get_last_prices(self):
        df = self.df
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

def side_view(controller):
    with st.sidebar:
        choices = {
            f'{perfum} - {brand}': (perfum, brand)
            for perfum, brand in controller.df.groupby(['perfum', 'brand']).groups
        }
        perfum_brand = st.selectbox('Target Perfum:', choices)
        st.write(f'Your choice: {perfum_brand}')

    return choices[perfum_brand]

def main_view(controller):
    st.set_page_config(
        page_title='Flaire Panel',
        page_icon='🧴'
    )

    st.write('# Flaire Panel')
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    start_dt, end_dt = st.slider(
        'Range of dates',
        min_value=(today - Controller.DELTA),
        max_value=tomorrow,
        value=((today - Controller.DELTA), tomorrow)
    )
    df = controller.get_prices_ts(start_dt, end_dt)
    if df.empty:
        st.write('🕳️ No perfums in this time range!')
        return

    last_prices_df = controller.get_last_prices()
    last_prices_df['price'] = last_prices_df['price'].map(lambda x: f'{x:.02f}€')

    st.write('## Most updated prices')
    st.dataframe(last_prices_df, hide_index=True)

    perfum, brand = side_view(controller)

    st.write(f'## {perfum.title()} - {brand.title()}')
    data = df[df['perfum'] == perfum].copy()
    data['ts'] = data['ts'].dt.floor(freq='s')
    data = data.pivot_table(index=['ts'], columns='merchant', values='price')

    st.line_chart(data)

    st.markdown(
        f'''
        <style>
            .sidebar .sidebar-content {{
                width: 33%;
            }}
        </style>
        ''',
        unsafe_allow_html=True
    )

def main():
    arguments = get_arguments()
    controller = Controller(arguments.database)
    main_view(controller)

if __name__ == '__main__':
    main()
