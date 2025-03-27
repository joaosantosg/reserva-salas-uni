from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class BaseModel(Base):
    __abstract__ = True
