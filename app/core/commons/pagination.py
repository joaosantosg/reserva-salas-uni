from typing import TypeVar, Generic, List
from app.core.commons.responses import ParametrosPaginacao, InformacoesPaginacao

T = TypeVar("T")


class Paginator(Generic[T]):
    """Utilitário para paginação"""

    @staticmethod
    def paginate(
        items: List[T], params: ParametrosPaginacao, total: int
    ) -> tuple[List[T], InformacoesPaginacao]:
        """
        Pagina uma lista de itens

        Args:
            items: Lista de itens a serem paginados
            params: Parâmetros de paginação
            total: Total de itens no banco de dados

        Returns:
            Tuple com lista paginada e informações de paginação
        """
        total_pages = (total + params.tamanho - 1) // params.tamanho

        informacoes_paginacao = InformacoesPaginacao(
            total=total,
            pagina=params.pagina,
            tamanho=params.tamanho,
            total_paginas=total_pages,
            proxima=params.pagina < total_pages,
            anterior=params.pagina > 1,
        )

        return items, informacoes_paginacao
