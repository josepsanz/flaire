import argparse
import datetime

import yaml
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import streamlit as st

from flaire import models, track


class Controller:
    DELTA = datetime.timedelta(days=180)

    def __init__(self, contract):
        self._engine = create_engine(f"sqlite:///{contract['database']}")
        self._session = sessionmaker(bind=self._engine)
        self._tracker = track.Tracker(contract)
        self._df = None

    @classmethod
    def from_yaml(cls, filename):
        with open(filename, 'r') as fp:
            return cls(yaml.load(fp, Loader=yaml.SafeLoader))

    @property
    def df(self):
        if self._df is None:
            self._df = self.get_prices_ts()

        return self._df

    def track(self):
        current_prices_df = self._tracker.track()
        self._tracker.insert_data(current_prices_df)
        self._df = None

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

    parser.add_argument('filename', help='YaML file with track info')
    arguments = parser.parse_args()
    return arguments

def side_section(controller):
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

def perfums_head_section(controller):
    st.write('# Flaire Panel')

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    start_dt, end_dt = st.slider(
        'Range of dates',
        min_value=(today - Controller.DELTA),
        max_value=tomorrow,
        value=((today - Controller.DELTA), tomorrow)
    )

    return controller.get_prices_ts(start_dt, end_dt)

def perfums_recent_prices_section(controller):
    st.write('## Most updated prices')
    if st.button('Tracker', icon='⚙️'):
        controller.track()
        print('-' * 80)
        now = datetime.datetime.now()
        st.write(f'Last track at: {now}')

    last_prices_df = controller.get_last_prices()
    last_prices_df['price'] = last_prices_df['price'].map(lambda x: f'{x:.02f}€')
    st.dataframe(last_prices_df, hide_index=True)

def perfums_price_trend_section(controller):
    st.write(f'## Perfum price trend')

    df = controller.df

    choices = {
        f'{perfum} - {brand}': (perfum, brand)
        for perfum, brand in controller.df.groupby(['perfum', 'brand']).groups
    }
    perfum_brand = st.selectbox('Target Perfum:', choices)
    st.write(f'Your choice: {perfum_brand}')
    perfum, brand = choices[perfum_brand]

    st.write(f'### {perfum.title()} - {brand.title()}')
    data = df[df['perfum'] == perfum].copy()
    data['ts'] = data['ts'].dt.floor(freq='s')
    data = data.pivot_table(index=['ts'], columns='merchant', values='price')

    st.line_chart(data)

def main_view(controller):
    st.set_page_config(
        page_title='Flaire Panel',
        page_icon='🧴'
    )

    df = perfums_head_section(controller)
    if df.empty:
        st.write('🕳️')
        st.write('No perfums in this time range!')
        return

    perfums_recent_prices_section(controller)
    perfums_price_trend_section(controller)
    #side_section(controller)

def main():
    arguments = get_arguments()
    controller = Controller.from_yaml(arguments.filename)
    main_view(controller)

if __name__ == '__main__':
    main()
