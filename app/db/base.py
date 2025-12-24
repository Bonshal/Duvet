# app/db/base.py
from sqlalchemy.ext.declarative import declarative_base

# This class will be the parent of all your models (User, Product, etc.)
Base = declarative_base()