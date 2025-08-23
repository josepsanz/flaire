import enum
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class PerfumeType(enum.Enum):
    edt = 'edt'
    edp = 'edp'
    parfum = 'parfum'
    elixir = 'elixir'
    extract = 'extract'

class Perfume(Base):
    __tablename__ = 'perfums'
    __table_args__ = (
        sa.UniqueConstraint('hash', name='uq_perfume_hash'),
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.Enum(PerfumeType), nullable=False)
    size = sa.Column(sa.Integer, nullable=False)
    hash = sa.Column(sa.String(32), nullable=False, unique=True)  # md5 hash hex string

    prices = relationship('Price', back_populates='perfume', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Perfume(name={self.name}, type={self.type}, size={self.size})>'

class Price(Base):
    __tablename__ = 'prices'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    perfume_id = sa.Column(sa.Integer, sa.ForeignKey('perfums.id', ondelete='CASCADE'), nullable=False)
    ts = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    price = sa.Column(sa.Integer, nullable=False)

    perfume = relationship('Perfume', back_populates='prices')

    def __repr__(self):
        return f'<Price(perfume_id={self.perfume_id}, ts={self.ts}, price={self.price})>'
