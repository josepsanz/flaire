import argparse
import datetime

import yaml
import pandas as pd
import ruptures as rpt
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import streamlit as st

from flaire import models, track

MD_PAD = '&nbsp;'

class Controller:
    DELTA = datetime.timedelta(days=180)

    def __init__(self, contract):
        self._clear_properties()
        self._engine = create_engine(f"sqlite:///{contract['database']}")
        self._session = sessionmaker(bind=self._engine)
        self._tracker = track.Tracker(contract)
        self.last_update_dt = None

    def _clear_properties(self):
        self._prices_df = None
        self._current_prices_df = None
        self._pm_trends = None

    @classmethod
    def from_yaml(cls, filename):
        with open(filename, 'r') as fp:
            return cls(yaml.load(fp, Loader=yaml.SafeLoader))

    @property
    def prices_df(self):
        if self._prices_df is None:
            self._prices_df = self.get_prices_ts()

        return self._prices_df

    @property
    def current_prices_df(self):
        if self._current_prices_df is None:
            self._current_prices_df = self.get_current_prices_ts()

        return self._current_prices_df

    @property
    def pm_trends(self):
        if self._pm_trends is None:
            self._pm_trends = self.get_pm_trends()

        return self._pm_trends

    def track(self):
        current_prices_df = self._tracker.track()
        self._tracker.insert_data(current_prices_df)
        self._clear_properties()
        self.last_update_dt = datetime.datetime.now()

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
            prices_df = pd.DataFrame(query.all())
            self._prices_df = prices_df
            return prices_df

    def get_current_prices_ts(self):
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
                .join(models.LastPrices, models.Prices.id == models.LastPrices.price_id)
                .join(models.Perfumes, models.Prices.perfume_id == models.Perfumes.id)
                .join(models.Brands, models.Perfumes.brand_id == models.Brands.id)
                .join(models.Merchants, models.Prices.merchant_id == models.Merchants.id)
                .join(models.MerchantLinks, sa.and_(models.MerchantLinks.perfume_id == models.Perfumes.id, models.MerchantLinks.merchant_id == models.Merchants.id))
                .order_by(models.Perfumes.name, models.Prices.price)
            )

        self._current_prices_df = pd.DataFrame(query.all())
        return self._current_prices_df

    def get_pm_trends(self, days=7):
        prices_df = self.prices_df
        end_date = pd.to_datetime(prices_df['ts'].max().date() + datetime.timedelta(days=1))
        start_date = end_date - datetime.timedelta(days=days)
        window_df = prices_df[(prices_df['ts'] >= start_date) & (prices_df['ts'] < end_date)]

        pm_trends = {}
        for (perfume, merchant), pm_df in window_df.groupby(['perfume', 'merchant']):
            signal = pm_df['price'].to_numpy()
            algo = rpt.Pelt(model='l2', min_size=1, jump=1).fit(signal)
            *brkpt, _ = algo.predict(pen=1)
            slope = signal[brkpt[-1]] / signal[brkpt[-1] - 1] if brkpt else 1
            pm_trends[(perfume, merchant)] = slope

        return pm_trends


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
        st.link_button('Admin', icon='🛠', type='tertiary', url='http://127.0.0.1:8503/admin')
        if st.button('Tracker', icon='👣', type='tertiary'):
            controller.track()
            print('-' * 80)

        if controller.last_update_dt:
            st.write(f'Last track at: {controller.last_update_dt}')

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

    prices_df = controller.get_prices_ts(start_dt, end_dt)
    return prices_df

def get_best_choices(current_prices_df):
    return {perfume: df.sort_value(price) for perfume, df in current_prices_df.groupby('perfume')}

def perfumes_recent_prices_section(controller):
    st.write('## Last Prices')
    current_prices_df = controller.current_prices_df

    df = current_prices_df[['ts', 'perfume', 'brand', 'merchant', 'price', 'merchant_link']].copy()
    st.data_editor(
        df,
        column_config={
            'merchant_link': st.column_config.LinkColumn('link', display_text='🔗'),
            'price': st.column_config.NumberColumn('Price (in €)', format='%.02f€')
        },
        hide_index=True,
        width='stretch',
        #width='content',
    )

    st.markdown('### Current Results ')
    st.markdown(f'- Number of tracks: {len(controller.current_prices_df):,}')
    st.markdown(f"- Number of perfumes: {controller.current_prices_df['perfume'].nunique():,}")

    st.markdown('### Total Results ')
    st.markdown(f'- Number of tracks: {len(controller.prices_df):,}')
    st.markdown(f"- Number of perfumes: {controller.prices_df['perfume'].nunique():,}")

def perfumes_price_trend_section(controller):
    st.write(f'## Perfume Price Trend')

    prices_df = controller.prices_df
    current_prices_df = controller.current_prices_df

    choices = {
        f'{perfume} - {brand}': (idx, perfume, brand)
        for idx, (perfume, brand) in enumerate(prices_df.groupby(['perfume', 'brand']).groups)
    }

    index, *_ = choices.get(st.session_state.get('perfume_brand'), (0,))
    perfume_brand = st.selectbox('Target Perfume:', choices, index=index, key='perfume_brand')
    _, perfume, brand = choices[perfume_brand]

    data = prices_df[prices_df['perfume'] == perfume].copy()
    info_link, img_link = data[['info_link', 'img_link']].iloc[0]

    col1, _, col2 = st.columns([2, .1, 1])
    with col1:
        data['ts'] = data['ts'].dt.floor(freq='s')
        pvt = data.pivot_table(index=['ts'], columns='merchant', values='price')
        st.line_chart(pvt)

    with col2:
        st.markdown(f'![{perfume.title()}!]({img_link} "{perfume.title()}")')

    st.markdown(f'Fragranctica info: [{perfume.title()} - {brand.title()}]({info_link})')
    st.markdown('Merchant prices:')

    merchant_data = []
    for merchant, group_df in data.groupby('merchant'):
        price, merchant_link = group_df[['price', 'merchant_link']].iloc[-1]
        merchant_data.append((price, merchant, merchant_link))

    pm_trends = controller.pm_trends
    current_merchants = current_prices_df[current_prices_df['perfume'] == perfume]['merchant'].unique()
    merchant_data.sort(key=lambda price, *_: price)
    for price, merchant, merchant_link in merchant_data:
        trend = pm_trends.get((perfume, merchant), 1)
        available_emoji = '🟢' if merchant in current_merchants else '🔴'
        trend_emoji = '⬇' if trend < 1 else '⬆' if trend > 1 else ''
        st.markdown(f'{available_emoji} {2 * MD_PAD}  [{merchant.title()} - {price:4.02f}€]({merchant_link}) {trend_emoji}')

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

    perfumes_price_trend_section(controller)
    perfumes_recent_prices_section(controller)

def get_arguments():
    parser = argparse.ArgumentParser(
        prog=f'python -m streamlit run {__file__}',
        description='Flaire Panel',
        epilog='View historic prices'
    )

    parser.add_argument('filename', help='YaML file with track info')
    arguments = parser.parse_args()
    return arguments

def main():
    arguments = get_arguments()
    if 'controller' not in st.session_state:
        st.session_state.controller = Controller.from_yaml(arguments.filename)

    main_view(st.session_state.controller)

if __name__ == '__main__':
    main()
