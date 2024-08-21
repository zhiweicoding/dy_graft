from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pydantic import BaseModel

database_url = os.environ.get('SQLALCHEMY_DATABASE_URL', 'postgresql://user:password@localhost:5432/dbname')
engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# 保存数据源
class RecordAction(Base):
    __tablename__ = "t_record_action"

    record_id = Column(String, primary_key=True, index=True, autoincrement=False)
    input_url_params = Column(String)
    input_args = Column(String)
    type = Column(String)
    mix_type = Column(String)
    output_body = Column(String)
    visitor_id = Column(String)
    is_delete = Column(Boolean)
    is_finish = Column(Boolean)
    creator = Column(String)
    updater = Column(String)
    create_time = Column(TIMESTAMP, server_default=func.now())
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


#  orm_mode = True 允许模型在从 ORM 模型（如 SQLAlchemy 的模型）接收数据时，能够正确地解析数据
#  orm_mode rename from_attributes
class RecordActionSchema(BaseModel):
    record_id: str
    input_url_params: str
    input_args: str
    type: str
    mix_type: str
    output_body: str
    visitor_id: str
    is_delete: bool
    is_finish: bool
    creator: str
    updater: str
    create_time: datetime
    update_time: datetime

    class Config:
        # orm_mode = True
        from_attributes = True
