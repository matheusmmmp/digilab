#!/usr/bin/env bash
# Monta o pacote do servidor (CN5): o git archive do commit, só com o que o servidor roda. O servidor importa o motor e algumas regras do
# jogo (web/app/motor, web/app/src: o envio, o ranking, o Tamer, o protocolo da nuvem), que vão juntos; o package.json do web/app vai pelo
# "type": "module". Nada fora do git (nem o node_modules, nem o banco, nem a pasta Assets).
#   bash servidor_web/deploy/montar_pacote.sh /tmp/pacote.tar.gz
set -euo pipefail
saida="${1:?o arquivo .tar.gz de saída}"
raiz="$(git rev-parse --show-toplevel)"
git -C "$raiz" archive --format=tar.gz -o "$saida" HEAD \
  servidor_web/package.json servidor_web/package-lock.json servidor_web/src servidor_web/catalogo_fala.json \
  web/app/package.json web/app/motor web/app/src
echo "pacote: $saida ($(du -h "$saida" | cut -f1))"
