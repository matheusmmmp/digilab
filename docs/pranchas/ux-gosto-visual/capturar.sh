#!/bin/sh
# Tira as capturas da prancha "o pet assistindo TV", no padrao de docs/pranchas/ux-lugares-menus/capturar.sh, mas direto do arquivo
# (file://, sem servidor). Precisa de: python docs/pranchas/ux-gosto-visual/gerar.py e dos sprites em D:\Trab\digilab\Assets (fora do git).
# As capturas vao para D:\Trab\digilab\capturas_ux_gosto_visual\, fora do git: <tela>_<pele>.png, nas duas peles (vidro e militar).
# As telas estreitas (390 e 360) entram num iframe e sao recortadas, porque a janela headless nao desce de ~500 px.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_gosto_visual; mkdir -p "$OUT"
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
  for t in desligada_1440 ligada_1440 porque_1440 passando_1440 fechado_1440 reacoes_1440 giro_1440; do cap "$OUT/${t}_$n.png" 1440,900 "$B/$t.html?pele=$pele"; done
  cap "$OUT/ligada_900_$n.png" 900,700 "$B/ligada_900.html?pele=$pele"
  for t in recolhida_390 aberta_390 desligada_390; do cel "$t" 390 844 "pele=$pele" "$OUT/${t}_$n.png"; done
  cel janela_360 360 620 "pele=$pele" "$OUT/janela_360_$n.png"
done
# sem as notas, so no Vidro (para o PR)
cap "$OUT/ligada_1440_vidro_limpa.png" 1440,900 "$B/ligada_1440.html?pele=vidro&sem"
ls "$OUT" | wc -l
