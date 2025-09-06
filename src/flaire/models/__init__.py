import enum
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

merchant_perfum = sa.Table(
    'merchant_perfum',
    Base.metadata,
    sa.Column('merchant_id', sa.Integer, sa.ForeignKey('merchants.id', ondelete='CASCADE'), primary_key=True),
    sa.Column('perfum_id', sa.Integer, sa.ForeignKey('perfums.id', ondelete='CASCADE'), primary_key=True)
)

class PerfumType(enum.Enum):
    edt = 'edt'
    edp = 'edp'
    parfum = 'parfum'
    elixir = 'elixir'
    extract = 'extract'

class FlaireBase:
    pass

class Merchants(FlaireBase, Base):
    __tablename__ = 'merchants'
    __lut__ = {}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False, unique=True)
    perfums = relationship(
        'Perfums',
        secondary=merchant_perfum,
        back_populates='merchant',
        passive_deletes=True
    )

    prices = relationship(
        'Prices',
        back_populates='merchant',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f'<{self.__class__.__name__}(name={self.name})>'

class Brands(FlaireBase, Base):
    __tablename__ = 'brands'
    __lut__ = {}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False, unique=True)

    perfums = relationship(
        'Perfums',
        back_populates='brand',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f'<{self.__class__.__name__}(name={self.name})>'

class Perfums(FlaireBase, Base):
    __tablename__ = 'perfums'
    __table_args__ = (
        sa.UniqueConstraint('sig', name='uq_perfum_sig'),
    )
    __lut__ = {}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    brand_id = sa.Column(sa.Integer, sa.ForeignKey('brands.id', ondelete='CASCADE'), nullable=False)
    type = sa.Column(sa.Enum(PerfumType), nullable=False)
    size = sa.Column(sa.Integer, nullable=False)
    sig = sa.Column(sa.String(32), nullable=False, unique=True)  # md5 hash hex string

    brand = relationship('Brands', back_populates='perfums')
    merchant = relationship(
        'Merchants',
        secondary=merchant_perfum,
        back_populates='perfums',
        passive_deletes=True
    )
    prices = relationship(
        'Prices',
        back_populates='perfum',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f'<{self.__class__.__name__}(name={self.name}, type={self.type}, size={self.size})>'

class Prices(FlaireBase, Base):
    __tablename__ = 'prices'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    perfum_id = sa.Column(sa.Integer, sa.ForeignKey('perfums.id', ondelete='CASCADE'), nullable=False)
    merchant_id = sa.Column(sa.Integer, sa.ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    ts = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    price = sa.Column(sa.Integer, nullable=False)

    perfum = relationship('Perfums', back_populates='prices')
    merchant = relationship('Merchants', back_populates='prices')

    def __repr__(self):
        return f'<{self.__class__.__name__}(perfum_id={self.perfum_id}, ts={self.ts}, price={self.price})>'
