#!/bin/sh
# Tira as capturas da prancha "a pagina de entrada" (direto do arquivo, sem servidor). Precisa de: python
# docs/pranchas/ux-pagina-inicial/gerar.py, dos sprites em D:\Trab\digilab\Assets (fora do git) e da rede, para as fontes.
# As capturas vao para D:\Trab\digilab\capturas_ux_pagina_inicial\, fora do git: a pagina inteira (a altura e medida no navegador)
# e a primeira dobra, a 1440 e a 390. O celular entra num iframe e e recortado, porque a janela headless nao desce de ~500 px.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_pagina_inicial; mkdir -p "$OUT"; rm -f "$OUT"/*.png
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B="file:///$(cygpath -m "$(pwd)")"
cap1(){ timeout 90 "$C" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files --virtual-time-budget=8000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
cap(){ rm -f "$1"; cap1 "$@" || cap1 "$@"; [ -s "$1" ] || { echo "sem captura: $1" >&2; exit 1; }; }
medir(){
  printf '<!doctype html><title>x</title><body style="margin:0"><iframe id=f src="inicial.html?sem" style="width:%spx;height:900px;border:0"></iframe><script>addEventListener("load",()=>setTimeout(()=>{document.title="ALT="+document.getElementById("f").contentDocument.documentElement.scrollHeight},1500))</script>' "$1" > _h.html
  timeout 60 "$C" --headless=new --disable-gpu --allow-file-access-from-files --virtual-time-budget=6000 --window-size=1600,1000 --dump-dom "$B/_h.html" 2>/dev/null | grep -o "ALT=[0-9]*" | head -1 | cut -d= -f2
  rm -f _h.html
}
cel(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="inicial.html?sem" style="width:390px;height:%spx;border:0"></iframe>' "$1" > _m.html
  cap "$OUT/_m.png" 500,$1 "$B/_m.html"
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m.png")').crop((0,0,390,$1)).save(r'$(cygpath -w "$2")')"
  rm -f "$OUT/_m.png" _m.html
}
AD=$(medir 1440); AC=$(medir 390); echo "alturas: $AD e $AC"
cap "$OUT/inicial_1440.png" 1440,$AD "$B/inicial.html"
cap "$OUT/inicial_1440_limpa.png" 1440,$AD "$B/inicial.html?sem"
cap "$OUT/inicial_1440_dobra.png" 1440,900 "$B/inicial.html?sem"
cel $AC "$OUT/inicial_390.png"
cel 844 "$OUT/inicial_390_dobra.png"
ls "$OUT" | wc -l
