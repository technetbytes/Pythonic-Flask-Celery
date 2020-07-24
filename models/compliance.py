from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, PickleType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ShelfCompliance(Base):
    '''This is Shelf Compliance sample Data model class.'''
    
    __tablename__ = "tShelfCompliance"
    __table_args__ = {"schema":"KnowHow.dbo"}

    id = Column(Integer, primary_key=True, nullable=False)
    shelfName = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    shelfTag = Column(Text, nullable=True)
    complianceLevel = Column(Integer, nullable=True)
    complianceItem = Column(Text, nullable=True)
    projectId = Column(Integer, nullable=True)
        
    def __repr__(self):
        return '<ShelfCompliance model {}>'.format(self.id)