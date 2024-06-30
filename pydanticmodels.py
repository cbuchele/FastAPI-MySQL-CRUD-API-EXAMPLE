from pydantic import BaseModel, Field
from typing import List, Optional


class S3UploadResponse(BaseModel):
    id: Optional[str] = Field(None, alias="id")
    url: Optional[str]


class UserBase(BaseModel):
    id: Optional[str] = Field(None, alias="id")
    nome: Optional[str] = Field(None, alias="nome")
    role: Optional[int]
    foto: Optional[str] = Field(None, alias="foto")
    telefone: Optional[int] = Field(None, alias="telefone")
    email: Optional[str]
    password: Optional[str]
    deleted: Optional[str]




