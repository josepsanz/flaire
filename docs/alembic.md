# Alembic

## Initial workflow

1. Create the models. You can ask any GenAI to generate them for you in SQLAlchemy format.
2. Initialize `alembic` for the first time:

```sh
alembic init migrations
```

This creates an `alembic.ini` and a `migrations` directory:
``` sh 
migrations
├── env.py
├── README
├── script.py.mako
└── versions
```

Edit `alembic.ini` and `migrations/env.py` as needed for your project. 

3. Run the following commands (for PostgreSQL and MariaDB, the database must already be created):
```
rm -rf perfumes.db migrations/versions/* 
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

This is going to create all empty tables with the indicated schema.

Optional step:

```python
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from flaire.models import Base

DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/perfumes"
engine = create_engine(DATABASE_URL)

if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)
```

## Upgrade workflow

``` sh
alembic revision --autogenerate -m "Example changing hash size column in perfums table"
alembic upgrade head
```
