#!/bin/sh
# Tira as seis capturas das pranchas da L1 de "Lugares da ilha" (Chrome headless, 1920 x 950, as peles Vidro e Militar), no padrao de
# docs/pranchas/ux-pet/capturar.sh. Antes:
#   - o fundo, fora do git, em D:\Trab\digilab\capturas_ux_lugares_aprovar\fundo\: cena_limpa.jpg (a captura real da ilha a 1920, a da
#     pagina de direcao), retrato.png (o Gomamon recortado dela), ilha.json (node docs/pranchas/ux-lugares/ilha_json.mts) e
#     ilha_cima.png (python docs/pranchas/ux-lugares/ilha_png.py ilha.json ilha_cima.png 6);
#   - python docs/pranchas/ux-lugares/gerar.py (as tres pranchas);
#   - python -m http.server 8765 --bind 127.0.0.1 em D:\Trab\digilab.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_lugares_aprovar; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B=http://127.0.0.1:8765/v3-ux-lugares/docs/pranchas/ux-lugares
cap(){ "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
for pele in vidro xcom; do
  n=$([ $pele = xcom ] && echo militar || echo vidro)
  for tela in normal longe mapa; do cap "$OUT/lugares_${tela}_1920_$n.png" 1920,950 "$B/lugares_$tela.html?pele=$pele"; done
done
