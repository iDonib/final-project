from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, MetaData, Integer, String

Base = declarative_base()
metadata = MetaData()


class Voter(Base):
    __tablename__ = 'voter_tbl'
    voter_id = Column(Integer, primary_key = True, index = True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(String)
    location = Column(String)
    picture = Column(String)
    qr_code = Column(String)
    secret_key = Column(String)
    citizenship_number = Column(String, unique = True)


class Candidate(Base):
    __tablename__ = 'candidate_tbl'
    candidate_id = Column(Integer, primary_key = True, index = True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(String)
    location = Column(String)
    picture = Column(String)
    citizenship_number = Column(String, unique = True)
