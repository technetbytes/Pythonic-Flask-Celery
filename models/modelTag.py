from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, PickleType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ModelTag(Base):
    '''This is ModelTag sample Data model class.'''
    
    __tablename__ = "tModelTages"
    __table_args__ = {"schema":"KnowHow.dbo"}

    id = Column(Integer, primary_key=True, nullable=False)
    modelId = Column(Integer, nullable=True)
    modelTages = Column(Text, nullable=True)
    
        
    def __repr__(self):
        return '<ModelTag model {}>'.format(self.id)