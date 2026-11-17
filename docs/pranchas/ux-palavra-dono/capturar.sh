#!/bin/sh
# Tira as capturas da prancha "a palavra do dono", no padrao de docs/pranchas/ux-janelas/capturar.sh (direto do arquivo, sem servidor).
# Precisa de: python docs/pranchas/ux-palavra-dono/gerar.py, dos sprites em D:\Trab\digilab\Assets (fora do git) e da rede, para as fontes.
# As capturas vao para capturas/ ao lado (jpg, no padrao da prancha da conta), nas duas peles (vidro e militar).
# As telas estreitas (390) entram num iframe e sao recortadas, porque a janela headless nao desce de ~500 px.
set -e
cd "$(dirname "$0")"
OUT=capturas; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B="file:///$(cygpath -m "$(pwd)")"
cap1(){ timeout 60 "$C" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files --virtual-time-budget=6000 --window-size=$2 --screenshot="$(cygpath -w "$(pwd)/$1")" "$3" >/dev/null 2>&1; }
cap(){ rm -f "$1"; cap1 "$@" || cap1 "$@"; [ -s "$1" ] || { echo "sem captura: $1" >&2; exit 1; }; }
jpg(){ python -c "from PIL import Image; Image.open(r'$1').convert('RGB').save(r'$2', quality=86)"; rm -f "$1"; }
cel(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s.html?%s" style="width:%spx;height:%spx;border:0"></iframe>' "$1" "$4" "$2" "$3" > _m.html
  cap "$OUT/_m.png" 500,$3 "$B/_m.html"
  python -c "from PIL import Image; Image.open(r'$OUT/_m.png').crop((0,0,$2,$3)).convert('RGB').save(r'$5', quality=86)"
  rm -f "$OUT/_m.png" _m.html
}
for pele in vidro xcom; do
  n=$([ $pele = xcom ] && echo militar || echo vidro)
  for t in dizer ouviu liga; do cap "$OUT/_t.png" 1920,950 "$B/${t}_1920.html?pele=$pele"; jpg "$OUT/_t.png" "$OUT/${t}_1920_$n.jpg"; done
  for t in dizer habitos; do cel "${t}_390" 390 844 "pele=$pele" "$OUT/${t}_390_$n.jpg"; done
done
ls "$OUT" | wc -l
