#!/bin/bash

# Verifica se a chave SSH já existe
if [ -f ~/.ssh/id_ed25519 ]; then
    echo "Chave SSH já existe em ~/.ssh/id_ed25519"
    exit 1
fi

# Gera uma chave SSH Ed25519 com nome de usuário como comentário
echo -e "\n" | ssh-keygen -t ed25519 -C "raspberry@exemplo.com"

# Verifica se a chave foi criada com sucesso
if [ $? -eq 0 ]; then
    echo "Chave SSH Ed25519 gerada com sucesso em ~/.ssh/id_ed25519"
else
    echo "Falha ao gerar a chave SSH Ed25519"
    exit 1
fi

# Exibe a chave pública gerada
echo "Aqui está a chave pública:"
cat ~/.ssh/id_ed25519.pub
