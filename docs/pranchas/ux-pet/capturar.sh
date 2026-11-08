#!/bin/sh
# Tira as quatro capturas das pranchas da P1 (Chrome headless), no padrao de docs/pranchas/b3/capturar.sh.
# Precisa de: python docs/pranchas/ux-pet/gerar.py (as duas pranchas) e python -m http.server 8765 --bind 127.0.0.1 em D:\Trab\digilab
# (as pranchas leem o sprite de ..\Assets, fora do git). As capturas vao para D:\Trab\digilab\capturas_ux_pet_aprovar\, fora do git (UX-8).
# O celular entra num iframe de 390 x 844 e e recortado, porque a janela headless nao desce de ~500 px.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_pet_aprovar; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B=http://127.0.0.1:8765/v3-ux-a2/docs/pranchas/ux-pet
cap(){ "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
for pele in vidro xcom; do
  n=$([ $pele = xcom ] && echo militar || echo vidro)
  cap "$OUT/pet_1920_$n.png" 1920,950 "$B/pet_1920.html?pele=$pele"
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="pet_390.html?pele=%s" style="width:390px;height:844px;border:0"></iframe>' $pele > _m_$n.html
  cap "$OUT/_m_$n.png" 500,844 "$B/_m_$n.html"
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m_$n.png")').crop((0,0,390,844)).save(r'$(cygpath -w "$OUT/pet_390_$n.png")')"
  rm -f "$OUT/_m_$n.png" _m_$n.html
done
