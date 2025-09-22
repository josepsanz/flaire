"""
FLAIRE_DATABASE= uvicorn flaire.admin:app --host 127.0.0.1 --port 8503
"""
import os
import argparse

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqladmin import Admin, ModelView

from flaire.models import Perfumes, Merchants, Prices
from flaire.models.admin import User


FLAIRE_DATABASE = os.environ.get('FLAIRE_DATABASE', 'perfumes.db')

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name]

class PerfumesAdmin(ModelView, model=Perfumes):
    name = 'Perfume'
    column_list = [Perfumes.id, Perfumes.name, Perfumes.type, Perfumes.size, Perfumes.info_link, Perfumes.img_link]


def app():
    app = FastAPI()
    engine = create_engine(f"sqlite:///{FLAIRE_DATABASE}")
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(PerfumesAdmin)
    return app

