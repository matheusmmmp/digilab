#!/bin/sh
# Tira as capturas da prancha "o reset e as duas pontuacoes", no padrao de docs/pranchas/ux-gosto-visual/capturar.sh (direto do arquivo, sem servidor).
# Precisa de: python docs/pranchas/ux-reset/gerar.py, dos sprites em D:\Trab\digilab\Assets (fora do git) e da rede, para as fontes.
# As capturas vao para D:\Trab\digilab\capturas_ux_reset\, fora do git: <tela>_<pele>.png, nas duas peles (vidro e militar).
# As telas estreitas (390 e 360) entram num iframe e sao recortadas, porque a janela headless nao desce de ~500 px.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_reset; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B="file:///$(cygpath -m "$(pwd)")"
# o Chrome headless grava a captura e as vezes nao sai sozinho: espera o arquivo (ate 60 s) e encerra o processo
cap1(){
  "$C" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files --virtual-time-budget=6000 --user-data-dir="$(cygpath -w "$OUT/_perfil")" --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1 &
  p=$!; k=0
  while [ $k -lt 120 ] && ! [ -s "$1" ]; do sleep 0.5; k=$((k+1)); done
  sleep 0.5; kill $p 2>/dev/null; wait $p 2>/dev/null; [ -s "$1" ]
}
cap(){ rm -f "$1"; cap1 "$@" || cap1 "$@"; [ -s "$1" ] || { echo "sem captura: $1" >&2; exit 1; }; }
cel(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s.html?%s" style="width:%spx;height:%spx;border:0"></iframe>' "$1" "$4" "$2" "$3" > _m.html
  cap "$OUT/_m.png" 500,$3 "$B/_m.html"
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m.png")').crop((0,0,$2,$3)).save(r'$(cygpath -w "$5")')"
  rm -f "$OUT/_m.png" _m.html
}
for pele in vidro xcom; do
  n=$([ $pele = xcom ] && echo militar || echo vidro)
  for t in reset confirmar estados perfil rankings estados_perfil; do cap "$OUT/${t}_1920_$n.png" 1920,950 "$B/${t}_1920.html?pele=$pele"; done
  for t in reset confirmar perfil rankings; do cel "${t}_390" 390 844 "pele=$pele" "$OUT/${t}_390_$n.png"; done
done
# sem as notas, so no Vidro (para o PR)
cap "$OUT/reset_1920_vidro_limpa.png" 1920,950 "$B/reset_1920.html?pele=vidro&sem"
cap "$OUT/perfil_1920_vidro_limpa.png" 1920,950 "$B/perfil_1920.html?pele=vidro&sem"
rm -rf "$OUT/_perfil"
ls "$OUT" | wc -l
