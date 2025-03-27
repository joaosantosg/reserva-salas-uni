from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class RespostaBase(BaseModel):
    """Modelo base para todas as respostas da API"""
    status: str = Field(default="sucesso", description="Status da resposta (sucesso/erro)")
    mensagem: Optional[str] = Field(default=None, description="Mensagem opcional da resposta")
    data_hora: datetime = Field(default_factory=datetime.now, description="Data e hora da resposta")

class RespostaDados(RespostaBase, Generic[T]):
    """Modelo para respostas com dados"""
    dados: T = Field(..., description="Dados da resposta")

class ParametrosPaginacao(BaseModel):
    """Parâmetros de paginação"""
    pagina: int = Field(default=1, ge=1, description="Número da página")
    tamanho: int = Field(default=10, ge=1, le=100, description="Quantidade de itens por página")
    ordenar_por: str = Field(default="id", description="Campo para ordenação")
    ordenacao: str = Field(default="desc", description="Direção da ordenação (asc/desc)")

class InformacoesPaginacao(BaseModel):
    """Informações de paginação"""
    total: int = Field(..., description="Total de registros")
    pagina: int = Field(..., description="Página atual")
    tamanho: int = Field(..., description="Tamanho da página")
    total_paginas: int = Field(..., description="Total de páginas")
    proxima: bool = Field(..., description="Indica se existe próxima página")
    anterior: bool = Field(..., description="Indica se existe página anterior")

class RespostaPaginada(RespostaBase, Generic[T]):
    """Modelo para respostas paginadas"""
    dados: list[T] = Field(..., description="Lista de dados")
    paginacao: InformacoesPaginacao = Field(..., description="Informações de paginação") 

class RespostaLista(RespostaBase, Generic[T]):
    """Modelo para respostas de lista"""
    dados: list[T] = Field(..., description="Lista de dados")
