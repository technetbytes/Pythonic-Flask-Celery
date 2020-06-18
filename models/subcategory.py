from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, PickleType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SubCategory(Base):
    '''This is SubCategory sample Data model class.'''
    
    __tablename__ = "tSubCategories"
    __table_args__ = {"schema":"KnowHow.dbo"}

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    categoryId = Column(Text, nullable=True)
    tages = Column(Integer, nullable=True)
    
        
    def __repr__(self):
        return '<SubCategory model {}>'.format(self.id)