#!/bin/sh
# Tira as capturas da prancha "peles de rua" (direto do arquivo, sem servidor). Precisa de: python docs/pranchas/ux-peles-rua/gerar.py,
# dos sprites recortados em _spr/ (o gerar.py faz, a partir de D:\Trab\digilab\Assets, fora do git) e da rede, para as fontes.
# As capturas vao para D:\Trab\digilab\capturas_ux_peles_rua\, fora do git: <modelo>_<tela>.png, a 1920 x 950, e as telas do pet e do
# lugar tambem sem as notas (_limpa). Uso: sh capturar.sh            (os tres modelos)
#                                          sh capturar.sh zine       (so um)
set -e
cd "$(dirname "$0")"
OUT=/d/Trab/digilab/capturas_ux_peles_rua; mkdir -p "$OUT"
C="/c/Program Files/Google/Chrome/Application/chrome.exe"; B="file:///$(cygpath -m "$(pwd)")"
cap1(){ timeout 60 "$C" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files --virtual-time-budget=6000 --window-size=1920,950 --screenshot="$(cygpath -w "$1")" "$2" >/dev/null 2>&1; }
cap(){ rm -f "$1"; cap1 "$@" || cap1 "$@"; [ -s "$1" ] || { echo "sem captura: $1" >&2; exit 1; }; }
for m in ${1:-estencil zine arcade}; do
  for t in pet lugar celular folha; do cap "$OUT/${m}_${t}.png" "$B/${m}_${t}.html"; done
  for t in pet lugar; do cap "$OUT/${m}_${t}_limpa.png" "$B/${m}_${t}.html?sem"; done
done
# a rodada 2 (python gerar_r2.py): as outras telas, so nos dois modelos escolhidos (o Zine e o Estencil)
for m in ${1:-zine estencil}; do
  [ "$m" = arcade ] && continue
  for t in ajustes lutar diario scan estados; do cap "$OUT/${m}_${t}.png" "$B/${m}_${t}.html"; done
done
# as capturas versionadas (jpg, em capturas/) e, por ultimo, a comparacao, que usa as _limpa
python - "$OUT" <<'PY'
import os, sys
from PIL import Image
src, dst = sys.argv[1], "capturas"
os.makedirs(dst, exist_ok=True)
for f in sorted(os.listdir(src)):
    if f.endswith(".png") and not f.startswith("_") and f != "comparacao.png":
        Image.open(os.path.join(src, f)).convert("RGB").save(os.path.join(dst, f[:-4] + ".jpg"), quality=86)
PY
cap "$OUT/comparacao.png" "$B/comparacao.html"
python -c "from PIL import Image; Image.open(r'$(cygpath -w "$OUT/comparacao.png")').convert('RGB').save('capturas/comparacao.jpg', quality=86)"
ls capturas | wc -l
