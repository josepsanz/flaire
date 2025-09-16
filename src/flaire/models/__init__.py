import enum
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

merchant_perfume = sa.Table(
    'merchant_perfume',
    Base.metadata,
    sa.Column('merchant_id', sa.Integer, sa.ForeignKey('merchants.id', ondelete='CASCADE'), primary_key=True),
    sa.Column('perfume_id', sa.Integer, sa.ForeignKey('perfumes.id', ondelete='CASCADE'), primary_key=True)
)

class PerfumeType(enum.Enum):
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
    perfumes = relationship(
        'Perfumes',
        secondary=merchant_perfume,
        back_populates='merchant',
        passive_deletes=True
    )

    prices = relationship(
        'Prices',
        back_populates='merchant',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    merchant_links = relationship(
        'MerchantLinks',
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

    perfumes = relationship(
        'Perfumes',
        back_populates='brand',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f'<{self.__class__.__name__}(name={self.name})>'

class Perfumes(FlaireBase, Base):
    __tablename__ = 'perfumes'
    __table_args__ = (
        sa.UniqueConstraint('sig', name='uq_perfume_sig'),
    )
    __lut__ = {}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    brand_id = sa.Column(sa.Integer, sa.ForeignKey('brands.id', ondelete='CASCADE'), nullable=False)
    type = sa.Column(sa.Enum(PerfumeType), nullable=False)
    size = sa.Column(sa.Integer, nullable=False)
    info_link = sa.Column(sa.String, nullable=True)
    img_link = sa.Column(sa.String, nullable=True)
    sig = sa.Column(sa.String(32), nullable=False, unique=True)  # md5 hash hex string

    brand = relationship(
        'Brands',
        back_populates='perfumes'
    )

    merchant = relationship(
        'Merchants',
        secondary=merchant_perfume,
        back_populates='perfumes',
        passive_deletes=True
    )

    prices = relationship(
        'Prices',
        back_populates='perfume',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    merchant_links = relationship(
        'MerchantLinks',
        back_populates='perfume',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f'<{self.__class__.__name__}(name={self.name}, type={self.type}, size={self.size})>'

class Prices(FlaireBase, Base):
    __tablename__ = 'prices'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    perfume_id = sa.Column(sa.Integer, sa.ForeignKey('perfumes.id', ondelete='CASCADE'), nullable=False)
    merchant_id = sa.Column(sa.Integer, sa.ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    ts = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    price = sa.Column(sa.Integer, nullable=False)

    perfume = relationship('Perfumes', back_populates='prices')
    merchant = relationship('Merchants', back_populates='prices')

    def __repr__(self):
        return f'<{self.__class__.__name__}(perfume_id={self.perfume_id}, ts={self.ts}, price={self.price})>'

class MerchantLinks(FlaireBase, Base):
    __tablename__ = 'merchant_links'

    perfume_id = sa.Column(sa.Integer, sa.ForeignKey('perfumes.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    merchant_id = sa.Column(sa.Integer, sa.ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False, primary_key=True)

    link = sa.Column(sa.String, nullable=False)

    perfume = relationship('Perfumes', back_populates='merchant_links')
    merchant = relationship('Merchants', back_populates='merchant_links')

    def __repr__(self):
        return f'<{self.__class__.__name__}(perfume_id={self.perfume_id}, merchant_id={self.merchant_id}, price_id={self.price_id}, link={self.link})>'
