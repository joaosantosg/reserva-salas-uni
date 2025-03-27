from datetime import datetime, timedelta


class DateTimeUtils:
    @classmethod
    def now(cls) -> datetime:
        """Retorna datetime atual no timezone de São Paulo"""
        return datetime.now() - timedelta(hours=3)

    @classmethod
    def is_past(cls, dt: datetime) -> bool:
        """
        Verifica se uma data é anterior ao momento atual

        Args:
            dt: Data a ser verificada

        Returns:
            bool: True se a data é anterior ao momento atual, False caso contrário
        """
        print(dt)
        print(cls.now())
        ## Se datetime possuir timezone, remove o timezone
        if dt.tzinfo:
            dt = dt.replace(tzinfo=None)
        return dt < cls.now()

    @classmethod
    def format_datetime(cls, dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Formata datetime para string no timezone de São Paulo"""
        return dt.strftime(format)

    @classmethod
    def parse_datetime(cls, dt_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """Converte string para datetime no timezone de São Paulo"""
        dt = datetime.strptime(dt_str, format)
        return dt

    @classmethod
    def get_default_datetime(cls) -> datetime:
        """Retorna datetime padrão para uso em colunas SQLAlchemy"""
        return cls.now()
