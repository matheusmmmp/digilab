#!/bin/sh
# Tira as capturas da prancha "Lugares da ilha: menus" (Chrome headless, 1920 x 950), no padrao de docs/pranchas/ux-pet/capturar.sh.
# Precisa de: python docs/pranchas/ux-lugares-menus/gerar.py (os HTML) e python -m http.server 8765 --bind 127.0.0.1 em D:\Trab\digilab
# (as pranchas leem o sprite de ..\Assets, fora do git). As capturas vao para D:\Trab\digilab\capturas_ux_lugares_menus_aprovar\, fora
# do git, com o nome <tela>_1920_<vidro|militar>.png.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_lugares_menus_aprovar; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B=http://127.0.0.1:8765/v3-ux-lugares-menus/docs/pranchas/ux-lugares-menus
cap(){ "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
TELAS="transicao_1 transicao_2 transicao_3 crescer_treinar crescer_evolucao lutar_arena lutar_medalhas diario_registro diario_catalogo ajustes"
for pele in vidro xcom; do
  n=$([ $pele = xcom ] && echo militar || echo vidro)
  for t in $TELAS; do
    cap "$OUT/${t}_1920_$n.png" 1920,950 "$B/${t}_1920.html?pele=$pele"
  done
done
