#!/bin/sh
# Tira as capturas da prancha D1b (o DigiBrain como modal pequeno), como capturar.sh (Chrome headless).
# Uso, de qualquer pasta (bash do Git):  sh <pasta da prancha>/capturar_modal.sh
# Precisa, numa outra janela, em D:\Trab\digilab:   python -m http.server 8765 --bind 127.0.0.1
# E do fundo real em D:\Trab\digilab\capturas_ux_digibrain_aprovar\modal\fundo\pet_<vidro|militar>_<1920|390>.png (a Tela Pet do pet v11
# do e2e, sem painel), tirado do jogo por um spec temporario fora do git; sem ele, a prancha falha alto (ou use ?fundo=0).
# As capturas vao para D:\Trab\digilab\capturas_ux_digibrain_aprovar\modal\, fora do git (UX-8).
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_digibrain_aprovar/modal; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"
B=${B:-http://127.0.0.1:8765/v3-ux-digibrain/docs/pranchas/ux-digibrain}
cap(){ "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=8000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
confere(){ test -s "$1" || { echo "a captura $1 nao saiu (o servidor 8765 esta de pe? o B aponta para a pasta certa?)" >&2; exit 1; }; }
desktop(){ cap "$OUT/$1.png" 1920,950 "$B/modal.html?$2&largura=1920"; confere "$OUT/$1.png"; }
# o celular entra num iframe de 390 x 844 e e recortado, porque a janela headless nao desce de ~500 px de largura
celular(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s" style="width:390px;height:844px;border:0"></iframe>' "modal.html?$2&largura=390" > "_m_$1.html"
  cap "$OUT/_m_$1.png" 500,844 "$B/_m_$1.html"
  confere "$OUT/_m_$1.png"
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m_$1.png")').crop((0,0,390,844)).save(r'$(cygpath -w "$OUT/$1.png")')"
  rm -f "$OUT/_m_$1.png" "_m_$1.html"
}
for pele in vidro xcom; do
  nome=$pele; [ "$pele" = xcom ] && nome=militar
  desktop "modal_1920_$nome" "estado=com_escolha&pele=$pele"
  desktop "modal_1920_${nome}_centro" "estado=com_escolha&pele=$pele&lugar=centro"
  celular "modal_390_$nome" "estado=com_escolha&pele=$pele"
done
# os extras, no Vidro: a dica aberta, o mapa em texto, o aprendido mudando a escolha, sem decisao e o replay
desktop "modal_1920_vidro_dica" "estado=com_escolha&pele=vidro&dica"
celular "modal_390_vidro_dica" "estado=com_escolha&pele=vidro&dica"
desktop "modal_1920_vidro_texto" "estado=com_escolha&pele=vidro&texto"
celular "modal_390_vidro_texto" "estado=com_escolha&pele=vidro&texto"
desktop "modal_1920_vidro_mudou" "estado=mudou&pele=vidro"
desktop "modal_1920_vidro_sem_decisao" "estado=sem_decisao&pele=vidro"
desktop "modal_1920_militar_replay" "estado=replay&pele=xcom"
