#!/bin/sh
# Tira as capturas da prancha "a conta", no padrao de docs/pranchas/ux-gosto-visual/capturar.sh (direto do arquivo, sem servidor).
# Precisa de: python docs/pranchas/ux-conta/gerar.py, dos sprites em D:\Trab\digilab\Assets (fora do git) e da rede, para as fontes.
# As capturas vao para D:\Trab\digilab\capturas_ux_conta\, fora do git: <tela>_<pele>.png, nas duas peles (vidro e militar).
# As telas estreitas (390 e 360) entram num iframe e sao recortadas, porque a janela headless nao desce de ~500 px.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_conta; mkdir -p "$OUT"
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
  for t in ajustes_conta entrar estados primeiro apelido perfil apagar; do cap "$OUT/${t}_1920_$n.png" 1920,950 "$B/${t}_1920.html?pele=$pele"; done
  for t in ajustes_conta entrar falhou primeiro apelido perfil apagar; do cel "${t}_390" 390 844 "pele=$pele" "$OUT/${t}_390_$n.png"; done
  cel primeiro_360 360 800 "pele=$pele" "$OUT/primeiro_360_$n.png"
done
# sem as notas, so no Vidro (para o PR)
for t in entrar primeiro perfil; do cap "$OUT/${t}_1920_vidro_limpa.png" 1920,950 "$B/${t}_1920.html?pele=vidro&sem"; done
ls "$OUT" | wc -l
