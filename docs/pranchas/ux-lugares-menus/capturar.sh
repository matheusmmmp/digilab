#!/bin/sh
# Tira as capturas da prancha "Lugares da ilha: menus" (rodada 3: o desktop e o celular), no padrao de docs/pranchas/ux-pet/capturar.sh.
# Precisa de: python docs/pranchas/ux-lugares-menus/gerar.py (escreve o desktop e chama o gerar_movel.py) e python -m http.server 8765
# --bind 127.0.0.1 em D:\Trab\digilab (as pranchas leem os sprites de ..\Assets, fora do git). As capturas vao para
# D:\Trab\digilab\capturas_ux_lugares_menus_aprovar\, fora do git: <tela>_1920_<pele>.png, <tela>_390_<pele>.png, <tela>_360_<pele>.png e,
# so no Vidro, <tela>_390_vidro_notas.png (no celular as notas so aparecem com ?notas).
# O celular entra num iframe e e recortado, porque a janela headless nao desce de ~500 px. Os antes x depois sao paginas de 1920 x 950 e
# contam as palavras na propria pagina, no load: o tempo virtual de 6 s cobre.
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_lugares_menus_aprovar; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B=http://127.0.0.1:8765/v3-ux-lugares-menus/docs/pranchas/ux-lugares-menus
# o Chrome headless as vezes trava numa pagina: cada captura tem 60 s e uma segunda tentativa; se as duas falham, o script para (set -e)
cap1(){ timeout 60 "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=$2 --screenshot="$(cygpath -w "$1")" "$3" >/dev/null 2>&1; }
cap(){ rm -f "$1"; cap1 "$@" || cap1 "$@"; [ -s "$1" ] || { echo "sem captura: $1" >&2; exit 1; }; }
# cel <pagina sem .html> <largura> <altura> <query> <saida>: o celular num iframe, recortado
cel(){
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s.html?%s" style="width:%spx;height:%spx;border:0"></iframe>' "$1" "$4" "$2" "$3" > _m.html
  cap "$OUT/_m.png" 500,$3 "$B/_m.html"
  python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/_m.png")').crop((0,0,$2,$3)).save(r'$(cygpath -w "$5")')"
  rm -f "$OUT/_m.png" _m.html
}
T1920="transicao_1 transicao_2 transicao_3 crescer_treinar crescer_itens crescer_evolucao lutar_arena lutar_medalhas diario_registro diario_catalogo ajustes lugar_trancado lugar_destravado antes_depois_itens antes_depois_evolucao antes_depois_itens_390 antes_depois_evolucao_390"
T390="transicao_1 transicao_2 transicao_3 crescer_treinar crescer_itens crescer_evolucao lutar_arena lutar_medalhas diario_registro diario_catalogo ajustes mapa lugar_trancado lugar_destravado"
for pele in vidro xcom; do
  n=$([ $pele = xcom ] && echo militar || echo vidro)
  for t in $T1920; do
    case $t in *_390) arq="${t%_390}_390_1920"; pag="${t}.html";; *) arq="${t}_1920"; pag="${t}_1920.html";; esac
    cap "$OUT/${arq}_$n.png" 1920,950 "$B/$pag?pele=$pele"
  done
  for t in $T390; do
    cel "${t}_390" 390 844 "pele=$pele" "$OUT/${t}_390_$n.png"
    if [ $pele = vidro ]; then cel "${t}_390" 390 844 "pele=$pele&notas" "$OUT/${t}_390_vidro_notas.png"; fi
  done
  cel crescer_itens_360 360 800 "pele=$pele" "$OUT/crescer_itens_360_$n.png"
done
