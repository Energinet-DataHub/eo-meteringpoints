"""
conftest.py according to pytest docs:
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
import pytest
import sys
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

# TODO: Fix pathing
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/../src/")

from meteringpoints_shared.db import db


@pytest.fixture(scope='module')
def session():
    with PostgresContainer('postgres:9.6') as psql:
        engine = create_engine(psql.get_connection_url())
        conn = psql.get_connection_url()
        Session = sessionmaker(bind=engine, expire_on_commit=False)
        db.ModelBase.metadata.create_all(engine)

        session = Session()
        yield session
        session.close()
