#!/bin/bash

# Verifica se o Poetry está instalado
if ! command -v poetry &> /dev/null; then
    echo "Poetry não está instalado. Instalando..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Remove o ambiente virtual existente (se houver)
if [ -d ".venv" ]; then
    echo "Removendo ambiente virtual existente..."
    rm -rf .venv
fi

# Remove o arquivo requirements.txt (se existir)
if [ -f "requirements.txt" ]; then
    echo "Removendo requirements.txt..."
    rm requirements.txt
fi

# Inicializa o Poetry e instala as dependências
echo "Inicializando Poetry e instalando dependências..."
poetry install

# Ativa o ambiente virtual
echo "Ativando ambiente virtual..."
poetry shell

echo "Migração concluída! Use 'poetry shell' para ativar o ambiente virtual." 