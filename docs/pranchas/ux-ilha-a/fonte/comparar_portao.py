"""O portao da ilha A: compara base x ramo e, como controle, base x base (a variacao de uma carga para outra da cena 3D em tempo real).
- DOM: igual byte a byte, ou igual com os numeros trocados por "#" (so coordenadas da cena mudaram), ou diferente na estrutura/texto;
- px: os pixels diferentes de cada par; a tela "passa" se o ramo nao difere mais que o controle mais uma folga.
Escreve portao/resumo.json."""
import json
import re
from pathlib import Path
from PIL import Image, ImageChops

R = Path(r"D:\Trab\digilab\capturas_ux_ilha_aprovar\codigo_a")
NUM = re.compile(r"-?\d+(\.\d+)?")


def par(d: Path, i: str):
    a, b = Image.open(d / f"{i}_base.png").convert("RGB"), Image.open(d / f"{i}_ramo.png").convert("RGB")
    if a.size != b.size:
        px = -1
    else:
        dif = ImageChops.difference(a, b).convert("L")
        px = sum(1 for v in dif.getdata() if v > 0)
    ha, hb = (d / f"{i}_base.html").read_text(encoding="utf-8"), (d / f"{i}_ramo.html").read_text(encoding="utf-8")
    dom = "igual" if ha == hb else "so_numeros" if NUM.sub("#", ha) == NUM.sub("#", hb) else "DIFERENTE"
    return px, dom


ids = sorted({p.name[:-9] for p in (R / "portao").glob("*_base.png")})
resumo, linhas = [], []
for i in ids:
    px, dom = par(R / "portao", i)
    cpx, cdom = par(R / "portao_controle", i) if (R / "portao_controle" / f"{i}_base.png").exists() else (None, None)
    resumo.append({"tela": i, "ramo_px": px, "ramo_dom": dom, "controle_px": cpx, "controle_dom": cdom})
    linhas.append(f"{i:40s} ramo px={px:>7} dom={dom:10s} | controle px={cpx!s:>7} dom={cdom}")
(R / "portao" / "resumo.json").write_text(json.dumps(resumo, indent=1), encoding="utf-8")
print("\n".join(linhas))
print("telas:", len(ids), "| dom DIFERENTE no ramo:", sum(r["ramo_dom"] == "DIFERENTE" for r in resumo),
      "| dom DIFERENTE no controle:", sum(r["controle_dom"] == "DIFERENTE" for r in resumo))
