#!/bin/bash

mkdir -p repos_logados


while read -r usuario; do
    [ -z "$usuario" ] && continue
    
    echo "Clonando: $usuario/logado"
    git clone "https://github.com/$usuario/logado.git" "repos_logados/$usuario"
done < usuarios.txt

echo "Concluído!"
