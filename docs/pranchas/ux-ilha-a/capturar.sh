#!/bin/sh
# Tira as capturas da prancha ux-ilha-a ("Objetos que falam"), no padrao de docs/pranchas/ux-digibrain/capturar.sh (Chrome headless).
# Uso, de qualquer pasta (bash do Git):  sh <pasta da prancha>/capturar.sh
# Precisa, numa outra janela, em D:\Trab\digilab:   python -m http.server 8766 --bind 127.0.0.1
# (a prancha le o dados.json pelo fetch, que nao roda em file://, e o fundo de /capturas_ux_ilha_aprovar/prancha_a/fundo/).
# Os fundos sao capturas reais do jogo, tiradas pelo fonte/capturar_fundo.spec.ts (ver o gerar_dados.py).
# B e a url da pasta da prancha (o padrao: esta worktree servida de D:/Trab/digilab; depois do merge, /v3/docs/pranchas/ux-ilha-a).
# As capturas vao para D:\Trab\digilab\capturas_ux_ilha_aprovar\prancha_a\, fora do git (UX-8):
#   ilha_a_<estado>_<1920|390>_<vidro|militar>.png e ilha_a_<estado>_<1920|390>_vidro_notas.png (a tela e a legenda ao lado: 2364 x 950 e 834 x 844).
# O celular entra num iframe de 390 x 844 e e recortado, porque a janela headless nao desce de ~500 px de largura.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_ilha_aprovar/prancha_a; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"
B=${B:-http://127.0.0.1:8766/v3/.claude/worktrees/v3-ux-ilha-a-45c293/docs/pranchas/ux-ilha-a}
cap(){ "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=8000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
confere(){ test -s "$1" || { echo "a captura $1 nao saiu (o servidor 8766 esta de pe? o B aponta para a pasta certa?)" >&2; exit 1; }; }
desktop(){ cap "$OUT/$1.png" 1920,950 "$B/ilha_a.html?$2&largura=1920"; confere "$OUT/$1.png"; }
celular(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s" style="width:390px;height:844px;border:0"></iframe>' "ilha_a.html?$2&largura=390" > "_m_$1.html"
  cap "$OUT/_m_$1.png" 500,844 "$B/_m_$1.html"
  confere "$OUT/_m_$1.png"
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m_$1.png")').crop((0,0,390,844)).save(r'$(cygpath -w "$OUT/$1.png")')"
  rm -f "$OUT/_m_$1.png" "_m_$1.html"
}
ESTADOS=${ESTADOS:-"nada_tocado etiqueta_aberta fio_toque_pet indo_tigela toque_arvore"}
for pele in vidro xcom; do
  nome=$pele; [ "$pele" = xcom ] && nome=militar
  for estado in $ESTADOS; do
    desktop "ilha_a_${estado}_1920_$nome" "estado=$estado&pele=$pele"
    celular "ilha_a_${estado}_390_$nome" "estado=$estado&pele=$pele"
  done
done
# as notas de fonte, no Vidro: o numero sobre cada elemento e a legenda a direita da tela (a janela fica mais larga, sem recorte)
for estado in $ESTADOS; do
  cap "$OUT/ilha_a_${estado}_1920_vidro_notas.png" 2364,950 "$B/ilha_a.html?estado=$estado&pele=vidro&notas&largura=1920"
  confere "$OUT/ilha_a_${estado}_1920_vidro_notas.png"
  cap "$OUT/ilha_a_${estado}_390_vidro_notas.png" 834,844 "$B/ilha_a.html?estado=$estado&pele=vidro&notas&largura=390"
  confere "$OUT/ilha_a_${estado}_390_vidro_notas.png"
done
