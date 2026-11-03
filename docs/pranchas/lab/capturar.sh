#!/bin/sh
# Tira as 12 capturas da LM5a (3 telas x 390/1280 px x Vidro/Militar), Chrome headless. Precisa de: python -m http.server 8765 --bind 127.0.0.1
# em D:\Trab\digilab (as pranchas leem sprites e mapas de ..\Assets, fora do git). O celular entra num iframe de 390 px e e recortado,
# porque a janela headless nao desce de ~500 px; o painel no celular e a folha inteira, por isso a captura e mais alta (1420 px).
set -e
cd "$(dirname "$0")"; mkdir -p capturas
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B=http://127.0.0.1:8765/v3-lab-modular-lm5a/docs/pranchas/lab
cap(){ "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=$2 --screenshot="$(cygpath -w "$PWD/$1")" "$3" >/dev/null 2>&1; }
for pele in vidro xcom; do
  n=$([ $pele = xcom ] && echo militar || echo vidro)
  for tela in ajustes pet painel; do
    h=844; [ $tela = painel ] && h=1420
    hd=800; [ $tela = painel ] && hd=1180
    cap capturas/${tela}_1280_$n.png 1280,$hd "$B/${tela}_1280.html?pele=$pele"
    printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s_390.html?pele=%s" style="width:390px;height:%spx;border:0"></iframe>' $tela $pele $h > _m_$n.html
    cap capturas/_m_$n.png 500,$h "$B/_m_$n.html"
    python -c "from PIL import Image; Image.open('capturas/_m_$n.png').crop((0,0,390,$h)).save('capturas/${tela}_390_$n.png')"
    rm -f capturas/_m_$n.png _m_$n.html
  done
done
