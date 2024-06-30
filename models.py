from sqlalchemy import Column, Integer, String, TIMESTAMP
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(String(50), primary_key=True, index=True)
    nome = Column(String(50), unique=True)
    role = Column(Integer)
    foto = Column(String(100), nullable=True)
    telefone = Column(Integer, nullable=True)
    email = Column(String(50))
    password = Column(String(50))
    deleted = Column(TIMESTAMP(),nullable=True)

