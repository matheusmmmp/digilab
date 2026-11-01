#!/bin/sh
# Tira as quatro capturas das pranchas (Chrome headless). Precisa de: python -m http.server 8765 --bind 127.0.0.1 em D:\Trab\digilab
# (as pranchas leem os sprites e mapas de ..\Assets, fora do git). O celular entra num iframe de 390 px e e recortado, porque a janela
# headless nao desce de ~500 px.
set -e
cd "$(dirname "$0")"; mkdir -p capturas
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B=http://127.0.0.1:8765/v3-luta-layout/docs/pranchas/b3
cap(){ "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=$2 --screenshot="$(cygpath -w "$PWD/$1")" "$3" >/dev/null 2>&1; }
for pele in vidro xcom; do
  n=$([ $pele = xcom ] && echo militar || echo vidro)
  cap capturas/luta_1280_$n.png 1280,800 "$B/luta_1280.html?pele=$pele"
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="luta_390.html?pele=%s" style="width:390px;height:844px;border:0"></iframe>' $pele > _m_$n.html
  cap capturas/_m_$n.png 500,844 "$B/_m_$n.html"
  python -c "from PIL import Image; Image.open('capturas/_m_$n.png').crop((0,0,390,844)).save('capturas/luta_390_$n.png')"
  rm -f capturas/_m_$n.png _m_$n.html
done
