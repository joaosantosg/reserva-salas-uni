import logging
from logging.handlers import RotatingFileHandler

# Configuração do logger
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# Handler para arquivo
file_handler = RotatingFileHandler(
    "app.log",
    maxBytes=10485760,  # 10MB
    backupCount=5,
)
file_handler.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formato
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Adiciona handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def setup_logging():
    """Configura o logger para uso na aplicação"""
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
