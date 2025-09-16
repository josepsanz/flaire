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
                    models.Perfumes.name.label('perfume'),
                    models.Brands.name.label('brand'),
                    models.Merchants.name.label('merchant'),
                    (models.Prices.price / 100.0).label('price'),
                    models.Perfumes.info_link.label('info_link'),
                    models.Perfumes.img_link.label('img_link'),
                    models.MerchantLinks.link.label('merchant_link'),
                )
                .join(models.Perfumes, models.Prices.perfume_id == models.Perfumes.id)
                .join(models.Brands, models.Perfumes.brand_id == models.Brands.id)
                .join(models.Merchants, models.Prices.merchant_id == models.Merchants.id)
                .join(models.MerchantLinks, sa.and_(models.MerchantLinks.perfume_id == models.Perfumes.id, models.MerchantLinks.merchant_id == models.Merchants.id))
                .filter(models.Prices.ts >= start_dt, models.Prices.ts <= end_dt)
                .order_by(models.Prices.ts, models.Perfumes.name, models.Prices.price)
            )

            self._df = pd.DataFrame(query.all())
            return self._df

    def get_last_prices(self):
        df = self.df
        groups = df.groupby(['perfume', 'merchant'])

        it = (group.iloc[-1] for (perfume, merchant), group in groups)
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

    with st.sidebar:
        st.markdown(f'Track current prices')
        if st.button('Tracker', icon='⚙️'):
            controller.track()
            print('-' * 80)
            now = datetime.datetime.now()
            st.write(f'Last track at: {now}')

def perfumes_head_section(controller):
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

def perfumes_recent_prices_section(controller):
    st.write('## Most updated prices')

    last_prices_df = controller.get_last_prices()
    last_prices_df['price'] = last_prices_df['price'].map(lambda x: f'{x:.02f}€')

    df = last_prices_df[['ts', 'perfume', 'brand', 'merchant', 'price']]
    st.dataframe(df, hide_index=True)

def perfumes_price_trend_section(controller):
    st.write(f'## Perfume price trend')

    df = controller.df

    choices = {
        f'{perfume} - {brand}': (perfume, brand)
        for perfume, brand in controller.df.groupby(['perfume', 'brand']).groups
    }
    perfume_brand = st.selectbox('Target Perfume:', choices)
    st.write(f'Your choice: {perfume_brand}')
    perfume, brand = choices[perfume_brand]

    st.write(f'### {perfume.title()} - {brand.title()}')
    data = df[df['perfume'] == perfume].copy()
    data['ts'] = data['ts'].dt.floor(freq='s')
    data = data.pivot_table(index=['ts'], columns='merchant', values='price')

    st.line_chart(data)

def main_view(controller):
    st.set_page_config(
        page_title='Flaire Panel',
        page_icon='🧴'
    )

    side_section(controller)
    df = perfumes_head_section(controller)
    if df.empty:
        st.markdown(
            """
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <span style="font-size: 4em; line-height: 1;">🕳️</span>
            <div style="text-align: center; font-size: 1.2em; margin-top: 0.5em;">
            No perfumes in this time range!
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    perfumes_recent_prices_section(controller)
    perfumes_price_trend_section(controller)

def main():
    arguments = get_arguments()
    controller = Controller.from_yaml(arguments.filename)
    main_view(controller)

if __name__ == '__main__':
    main()
