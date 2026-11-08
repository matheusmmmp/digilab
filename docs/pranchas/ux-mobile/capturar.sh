#!/bin/sh
# Tira as capturas da prancha da M1 do mobile "minimo" (Chrome headless), no padrao de docs/pranchas/ux-pet/capturar.sh.
# Uso, de qualquer pasta (bash do Git):  sh docs/pranchas/ux-mobile/capturar.sh
# Precisa de: python docs/pranchas/ux-mobile/gerar.py (os sete pet_<estado>.html) e, numa outra janela, em D:\Trab\digilab:
#   python -m http.server 8765 --bind 127.0.0.1
# (a prancha le o fundo de D:\Trab\digilab\capturas_ux_mobile_aprovar\minimo\_fundo\, fora do git, e os icones e as fontes da rede).
# As capturas vao para D:\Trab\digilab\capturas_ux_mobile_aprovar\minimo\, fora do git (UX-8): minimo_<estado>_<largura>_<vidro|militar>.png,
# mais as mesmas a 390 com as notas de fonte (minimo_<estado>_390_<pele>_notas.png).
# O celular entra num iframe de 390 x 844 (ou 360 x 800) e e recortado, porque a janela headless nao desce de ~500 px de largura.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_mobile_aprovar/minimo; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B=http://127.0.0.1:8765/v3-ux-mobile/docs/pranchas/ux-mobile
cap(){ "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=8000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
# celular <nome da captura> <pagina?parametros> <largura> <altura>
celular(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s" style="width:%spx;height:%spx;border:0"></iframe>' "$2" $3 $4 > "_m_$1.html"
  cap "$OUT/_m_$1.png" 500,$4 "$B/_m_$1.html"
  test -s "$OUT/_m_$1.png" || { echo "a captura $1 nao saiu (o servidor 8765 esta de pe?)" >&2; exit 1; }
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m_$1.png")').crop((0,0,$3,$4)).save(r'$(cygpath -w "$OUT/$1.png")')"
  rm -f "$OUT/_m_$1.png" "_m_$1.html"
}
for pele in vidro xcom; do
  nome=$pele; [ "$pele" = xcom ] && nome=militar
  for estado in normal fome retrato mais dormindo chamado segurar; do
    celular "minimo_${estado}_390_$nome" "pet_$estado.html?pele=$pele" 390 844
  done
  celular "minimo_normal_360_$nome" "pet_normal.html?pele=$pele" 360 800
  celular "minimo_fome_360_$nome" "pet_fome.html?pele=$pele" 360 800
  celular "minimo_retrato_360_$nome" "pet_retrato.html?pele=$pele" 360 800
done
# as notas de fonte por cima do desenho, so a 390 e no Vidro (o desenho limpo e o das capturas acima)
for estado in normal fome retrato mais dormindo chamado segurar; do
  celular "minimo_${estado}_390_vidro_notas" "pet_$estado.html?pele=vidro&notas" 390 844
done
