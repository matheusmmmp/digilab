#!/bin/sh
# Tira as capturas da prancha "as janelas do pet", no padrao de docs/pranchas/ux-gosto-visual/capturar.sh (direto do arquivo, sem servidor).
# Precisa de: python docs/pranchas/ux-janelas/gerar.py, dos sprites em D:\Trab\digilab\Assets (fora do git) e da rede, para as fontes.
# As capturas vao para D:\Trab\digilab\capturas_ux_janelas\, fora do git: <tela>_<pele>.png, nas duas peles (vidro e militar).
# As telas estreitas (390 e 360) entram num iframe e sao recortadas, porque a janela headless nao desce de ~500 px.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_janelas; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B="file:///$(cygpath -m "$(pwd)")"
cap1(){ timeout 60 "$C" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files --virtual-time-budget=6000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
cap(){ rm -f "$1"; cap1 "$@" || cap1 "$@"; [ -s "$1" ] || { echo "sem captura: $1" >&2; exit 1; }; }
cel(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s.html?%s" style="width:%spx;height:%spx;border:0"></iframe>' "$1" "$4" "$2" "$3" > _m.html
  cap "$OUT/_m.png" 500,$3 "$B/_m.html"
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m.png")').crop((0,0,$2,$3)).save(r'$(cygpath -w "$5")')"
  rm -f "$OUT/_m.png" _m.html
}
for pele in vidro xcom; do
  n=$([ $pele = xcom ] && echo militar || echo vidro)
  for t in padrao arrastando arranjo menu exibir arrumar; do cap "$OUT/${t}_1920_$n.png" 1920,950 "$B/${t}_1920.html?pele=$pele"; done
  for t in exibir; do cel "${t}_390" 390 844 "pele=$pele" "$OUT/${t}_390_$n.png"; done
done
# sem as notas, so no Vidro (para o PR)
for t in arranjo arrastando; do cap "$OUT/${t}_1920_vidro_limpa.png" 1920,950 "$B/${t}_1920.html?pele=vidro&sem"; done
ls "$OUT" | wc -l
