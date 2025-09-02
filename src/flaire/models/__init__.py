import enum
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

merchant_perfum = sa.Table(
    'merchant_perfum',
    Base.metadata,
    sa.Column('merchant_id', sa.Integer, sa.ForeignKey('merchant.id', ondelete='CASCADE'), primary_key=True),
    sa.Column('perfum_id', sa.Integer, sa.ForeignKey('perfum.id', ondelete='CASCADE'), primary_key=True)
)

class PerfumType(enum.Enum):
    edt = 'edt'
    edp = 'edp'
    parfum = 'parfum'
    elixir = 'elixir'
    extract = 'extract'

class Merchant(Base):
    __tablename__ = 'merchant'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False, unique=True)
    perfums = relationship(
        'Perfum',
        secondary=merchant_perfum,
        back_populates='merchants',
        passive_deletes=True
    )

    def __repr__(self):
        return f'<Merchant(name={self.name})>'

class Brand(Base):
    __tablename__ = 'brand'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False, unique=True)

    perfums = relationship(
        'Perfum',
        back_populates='brand',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f'<Brand(name={self.name})>'

class Perfum(Base):
    __tablename__ = 'perfum'
    __table_args__ = (
        sa.UniqueConstraint('sig', name='uq_perfum_sig'),
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    brand_id = sa.Column(sa.Integer, sa.ForeignKey('brand.id', ondelete='CASCADE'), nullable=False)
    type = sa.Column(sa.Enum(PerfumType), nullable=False)
    size = sa.Column(sa.Integer, nullable=False)
    sig = sa.Column(sa.String(32), nullable=False, unique=True)  # md5 hash hex string

    brand = relationship('Brand', back_populates='perfums')
    merchants = relationship(
        'Merchant',
        secondary=merchant_perfum,
        back_populates='perfums',
        passive_deletes=True
    )
    prices = relationship(
        'Price',
        back_populates='perfum',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f'<Perfum(name={self.name}, type={self.type}, size={self.size})>'

class Price(Base):
    __tablename__ = 'price'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    perfum_id = sa.Column(sa.Integer, sa.ForeignKey('perfum.id', ondelete='CASCADE'), nullable=False)
    ts = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    price = sa.Column(sa.Integer, nullable=False)

    perfum = relationship('Perfum', back_populates='prices')

    def __repr__(self):
        return f'<Price(perfum_id={self.perfum_id}, ts={self.ts}, price={self.price})>'
