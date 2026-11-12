#!/bin/sh
# Tira as capturas da prancha "a pagina de entrada" (direto do arquivo, sem servidor). Precisa de: python
# docs/pranchas/ux-pagina-inicial/gerar.py, dos sprites em D:\Trab\digilab\Assets (fora do git) e da rede, para as fontes.
# As capturas vao para D:\Trab\digilab\capturas_ux_pagina_inicial\, fora do git. A pagina inteira (ALT_D e ALT_C sao a altura dela a
# 1440 e a 390, medidas no navegador) e a primeira dobra. O celular entra num iframe e e recortado.
set -e
cd "$(dirname "$0")"
ALT_D=${ALT_D:-3518}; ALT_C=${ALT_C:-4826}
OUT=/d/Trab/digilab/capturas_ux_pagina_inicial; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B="file:///$(cygpath -m "$(pwd)")"
cap1(){ timeout 90 "$C" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files --virtual-time-budget=8000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
cap(){ rm -f "$1"; cap1 "$@" || cap1 "$@"; [ -s "$1" ] || { echo "sem captura: $1" >&2; exit 1; }; }
cel(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="inicial.html?%s" style="width:390px;height:%spx;border:0"></iframe>' "$1" "$2" > _m.html
  cap "$OUT/_m.png" 500,$2 "$B/_m.html"
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m.png")').crop((0,0,390,$2)).save(r'$(cygpath -w "$3")')"
  rm -f "$OUT/_m.png" _m.html
}
for pele in vidro xcom; do
  n=$([ $pele = xcom ] && echo militar || echo vidro)
  cap "$OUT/inicial_1440_$n.png" 1440,$ALT_D "$B/inicial.html?pele=$pele"
  cap "$OUT/inicial_1440_dobra_$n.png" 1440,900 "$B/inicial.html?pele=$pele&sem"
  cel "pele=$pele" $ALT_C "$OUT/inicial_390_$n.png"
  cel "pele=$pele" 844 "$OUT/inicial_390_dobra_$n.png"
done
cap "$OUT/inicial_1440_vidro_limpa.png" 1440,$ALT_D "$B/inicial.html?pele=vidro&sem"
ls "$OUT" | wc -l
