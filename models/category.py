from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, PickleType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Category(Base):
    '''This is Category sample Data model class.'''
    
    __tablename__ = "tCategories"
    __table_args__ = {"schema":"KnowHow.dbo"}

    id = Column(Integer, primary_key=True, nullable=False)
    categoryName = Column(Text, nullable=False)
    categoryDescription = Column(Text, nullable=True)
    showType = Column(Text,nullable=True)
    dataContainer = Column(Text,nullable=True)
    projectId = Column(Integer, nullable=True)
    
        
    def __repr__(self):
        return '<Category model {}>'.format(self.id)