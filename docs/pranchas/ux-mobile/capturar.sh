#!/bin/sh
# Tira as capturas da prancha da M1 do mobile "Digivice" (Chrome headless), no padrao de docs/pranchas/ux-pet/capturar.sh.
# Precisa de: python docs/pranchas/ux-mobile/gerar.py (os quatro HTMLs) e python -m http.server 8765 --bind 127.0.0.1 em D:\Trab\digilab
# (a prancha le o sprite de ..\Assets, fora do git). As capturas vao para D:\Trab\digilab\capturas_ux_mobile_aprovar\, fora do git (UX-8).
# O celular entra num iframe de 390 x 844 (ou 360 x 800) e e recortado, porque a janela headless nao desce de ~500 px de largura.
# O Digivice so usa os --dl-*: a pele (vidro|xcom) nao muda nada nele, e o que se captura sao os dois temas (claro e escuro).
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_mobile_aprovar; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B=http://127.0.0.1:8765/v3-ux-mobile/docs/pranchas/ux-mobile
cap(){ "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
# celular <nome da captura> <pagina?parametros> <largura> <altura>
celular(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s" style="width:%spx;height:%spx;border:0"></iframe>' "$2" $3 $4 > "_m_$1.html"
  cap "$OUT/_m_$1.png" 500,$4 "$B/_m_$1.html"
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m_$1.png")').crop((0,0,$3,$4)).save(r'$(cygpath -w "$OUT/$1.png")')"
  rm -f "$OUT/_m_$1.png" "_m_$1.html"
}
for tema in claro escuro; do
  for estado in normal vital dormindo chamado; do
    celular "mobile_${estado}_390_$tema" "pet_$estado.html?tema=$tema" 390 844
  done
  celular "mobile_normal_360_$tema" "pet_normal.html?tema=$tema" 360 800
  celular "mobile_chamado_360_$tema" "pet_chamado.html?tema=$tema" 360 800
done
# a aba ativa da direcao (amarela), para comparar com a do guia (pergunta M1-1); e a mesma tela sem as notas
celular "mobile_normal_390_claro_aba_amarela" "pet_normal.html?tema=claro&aba=amarela" 390 844
celular "mobile_normal_390_claro_sem_notas" "pet_normal.html?tema=claro&sem" 390 844
