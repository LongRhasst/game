from sqlalchemy import Column, Integer, String
from connect import Base

class high_score(Base):
    __tablename__= 'high_score'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, default='player')
    high_score = Column(Integer, nullable=False )