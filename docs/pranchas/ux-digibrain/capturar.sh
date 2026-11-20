#!/bin/sh
# Tira as capturas da prancha D1 (o DigiBrain "scan holografico"), no padrao de docs/pranchas/ux-mobile/capturar.sh (Chrome headless).
# Uso, de qualquer pasta (bash do Git):  sh <pasta da prancha>/capturar.sh
# Precisa, numa outra janela, em D:\Trab\digilab:   python -m http.server 8765 --bind 127.0.0.1
# (a prancha le o dados.json pelo fetch, que nao roda em file://, e os icones e as fontes da rede).
# B e a url da pasta da prancha (o padrao: docs/pranchas/ux-digibrain/ servida de D:/Trab/digilab).
# As capturas vao para D:\Trab\digilab\capturas_ux_digibrain_aprovar\, fora do git (UX-8):
#   scan_<estado>_<1920|390>_<vidro|militar>.png; scan_<estado>_<largura>_vidro_notas.png; e os extras (o mapa em texto, a folha rolada,
#   o reduzir movimento e o pausado).
# O celular entra num iframe de 390 x 844 e e recortado, porque a janela headless nao desce de ~500 px de largura.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_digibrain_aprovar; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"
B=${B:-http://127.0.0.1:8765/v3-ux-digibrain/docs/pranchas/ux-digibrain}
cap(){ "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=8000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
confere(){ test -s "$1" || { echo "a captura $1 nao saiu (o servidor 8765 esta de pe? o B aponta para a pasta certa?)" >&2; exit 1; }; }
# desktop <nome> <parametros>
desktop(){ cap "$OUT/$1.png" 1920,950 "$B/digibrain.html?$2&largura=1920"; confere "$OUT/$1.png"; }
# celular <nome> <parametros>
celular(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s" style="width:390px;height:844px;border:0"></iframe>' "digibrain.html?$2&largura=390" > "_m_$1.html"
  cap "$OUT/_m_$1.png" 500,844 "$B/_m_$1.html"
  confere "$OUT/_m_$1.png"
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m_$1.png")').crop((0,0,390,844)).save(r'$(cygpath -w "$OUT/$1.png")')"
  rm -f "$OUT/_m_$1.png" "_m_$1.html"
}
for pele in vidro xcom; do
  nome=$pele; [ "$pele" = xcom ] && nome=militar
  for estado in com_escolha uma_opcao sem_decisao replay mudou; do
    desktop "scan_${estado}_1920_$nome" "estado=$estado&pele=$pele"
    celular "scan_${estado}_390_$nome" "estado=$estado&pele=$pele"
  done
  celular "scan_com_escolha_390_${nome}_rolada" "estado=com_escolha&pele=$pele&rolar"
done
# as notas de fonte por cima do desenho, no Vidro
for estado in com_escolha uma_opcao sem_decisao replay mudou; do
  desktop "scan_${estado}_1920_vidro_notas" "estado=$estado&pele=vidro&notas"
  celular "scan_${estado}_390_vidro_notas" "estado=$estado&pele=vidro&notas"
done
# os extras: o mapa em texto aberto, o reduzir movimento e o pausado
desktop "scan_com_escolha_1920_vidro_texto" "estado=com_escolha&pele=vidro&texto"
celular "scan_com_escolha_390_vidro_texto" "estado=com_escolha&pele=vidro&texto"
desktop "scan_mudou_1920_vidro_reduzir" "estado=mudou&pele=vidro&reduzir"
desktop "scan_com_escolha_1920_militar_pausado" "estado=com_escolha&pele=xcom&selo=pausado"
