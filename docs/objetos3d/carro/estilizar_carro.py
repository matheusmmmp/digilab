"""A textura do carro em cartoon limpo (rodada 3 do carro, docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 12).

O Matheus achou o carro da rodada 2 "um cartoon bem no feio": a malha esta boa, mas a pintura da Meshy e quase foto (a ferrugem em
degrade, o vidro sujo com o banco por dentro, o musgo de esponja) num mundo de cores chapadas e toon de dois tons. Aqui a pintura vira
cartoon limpo, por regiao, sem achatar cego como a E2 (7 cores):
  1. o filtro de deslocamento da media (mean shift) junta o ruido pintado em manchas;
  2. cada pixel cai numa classe pelo matiz (a tinta azul, a ferrugem, o musgo, o pneu, o metal, o farol, a lanterna); o cinza na faixa
     das janelas (a mascara janelas do mascaras_carro.py) vira o vidro chapado com o risco branco, sem o banco pintado por dentro;
  3. dentro da classe, o brilho cai em 2 ou 3 faixas de limiar fixo, cada uma com uma cor da paleta (PALETA), e a mediana tira os
     pontinhos soltos (MEDIANA);
  4. a oclusao assada pelo oclusao_carro.py escurece as caixas de roda e as frestas (FORCA_AO);
  5. as flores rosa do teto voltam por cima, pelo retocar do textura_carro.py (so as flores).
Os numeros sao PROPOSTOS, SEM FONTE: ajustados olhando a vitrine contra o esboco e o resto da ilha.

uso (da raiz): python -I docs/objetos3d/carro/estilizar_carro.py <textura_base_color.png> <mascaras.png> <oclusao.png> <saida.png> [janelas.png]
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import textura_carro as tc  # noqa: E402

RAIO_ESPACO, RAIO_COR = 10, 28
FORCA_AO, BORRAO_AO = 0.55, 9
# as faixas de cada classe: (limiar de brilho, cor RGB), do escuro ao claro; o ultimo limiar e 1. Limiares fixos, nao quantis: a
# tinta azul fica quase toda num tom so (a luz do jogo e que faz o volume), e o claro so pega as lascas
PALETA = {
    "azul": [(0.50, (44, 104, 168)), (0.86, (72, 148, 212)), (1, (150, 204, 236))],
    "ferrugem": [(0.42, (120, 52, 26)), (0.65, (172, 86, 38)), (1, (208, 128, 66))],
    "verde": [(0.45, (58, 112, 34)), (0.60, (96, 160, 44)), (1, (150, 200, 72))],
    "pneu": [(0.22, (36, 36, 40)), (1, (70, 70, 76))],
    "metal": [(0.50, (76, 92, 112)), (0.80, (138, 152, 168)), (1, (228, 236, 242))],
    "farol": [(0.85, (250, 206, 70)), (1, (255, 240, 180))],
    "lanterna": [(0.60, (178, 42, 36)), (1, (228, 74, 54))],
    "lasca": [(1, (150, 204, 236))],
    "vidro": [(0.90, (96, 136, 164)), (1, (226, 238, 246))],
}
MEDIANA = 5
# o farol cresce sobre a vizinhanca que nao e tinta azul nem pneu (a ferrugem pintada dentro e em volta da lente vira lente); as lascas cinza pequenas da lataria viram tinta clara
FECHO_FAROL, LASCA_MAX = 31, 900


def azul_bruto(h: np.ndarray, s: np.ndarray) -> np.ndarray:
    return (h > 0.45) & (h < 0.7) & (s > 0.18)


def classes(rgb: np.ndarray, mascaras: np.ndarray, janelas: np.ndarray | None) -> dict[str, np.ndarray]:
    h, s, v = tc.hsv(rgb)
    frente = mascaras[..., 1] > 0
    farol = frente & (h > 0.04) & (h < 0.2) & (s > 0.08) & (v > 0.5)
    lanterna = ((h < 0.03) | (h > 0.95)) & (s > 0.55) & (v > 0.45) & ~farol
    pneu = (v < 0.3) & ~farol & ~lanterna
    verde = (h > 0.17) & (h < 0.45) & (s > 0.22) & ~farol & ~pneu
    ferrugem = (h < 0.12) & (s > 0.3) & ~farol & ~lanterna & ~pneu
    azul = (h > 0.45) & (h < 0.7) & (s > 0.18) & ~pneu
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (FECHO_FAROL, FECHO_FAROL))
    perto = cv2.dilate(farol.astype(np.uint8), k) > 0
    farol = perto & frente & ~azul_bruto(h, s) & (v >= 0.3) & (s > 0.08)
    lanterna &= ~farol; pneu &= ~farol; verde &= ~farol
    ferrugem = (h < 0.12) & (s > 0.3) & ~farol & ~lanterna & ~pneu
    metal = ~(farol | lanterna | pneu | verde | ferrugem | azul)
    vidro = metal & janelas if janelas is not None else np.zeros_like(metal)
    metal &= ~vidro
    n, rot, est, _ = cv2.connectedComponentsWithStats(metal.astype(np.uint8), connectivity=8)
    lasca = (est[:, cv2.CC_STAT_AREA] < LASCA_MAX)[rot] & metal
    metal &= ~lasca
    return {"lasca": lasca, "vidro": vidro, "azul": azul, "ferrugem": ferrugem, "verde": verde, "pneu": pneu, "metal": metal, "farol": farol, "lanterna": lanterna}


def main(ent: str, masc: str, ao: str, sai: str, jan: str | None = None) -> None:
    base = np.asarray(Image.open(ent).convert("RGB"))
    lado = base.shape[0]
    m = np.asarray(Image.open(masc).convert("RGB").resize((lado, lado), Image.NEAREST))
    janelas = np.asarray(Image.open(jan).convert("L").resize((lado, lado), Image.NEAREST)) > 0 if jan else None
    liso = cv2.pyrMeanShiftFiltering(np.ascontiguousarray(base[..., ::-1]), RAIO_ESPACO, RAIO_COR)[..., ::-1]
    _, _, v = tc.hsv(liso)
    out = liso.astype(np.float32).copy()
    for nome, sel in classes(liso, m, janelas).items():
        lim = np.array([f[0] for f in PALETA[nome]][:-1]); pal = np.array([f[1] for f in PALETA[nome]], np.float32)
        out[sel] = pal[np.searchsorted(lim, v[sel])]
        print("CLASSE", nome, round(float(sel.mean()) * 100, 1), "%")
    out = cv2.medianBlur(np.clip(out, 0, 255).astype(np.uint8), MEDIANA).astype(np.float32)
    a = np.asarray(Image.open(ao).convert("L").resize((lado, lado), Image.BILINEAR)).astype(np.float32) / 255
    a = cv2.GaussianBlur(a, (0, 0), BORRAO_AO)
    out *= (1 - FORCA_AO * (1 - a))[..., None]
    rgb = np.clip(out, 0, 255).astype(np.uint8)
    rgb = flores(rgb, m)
    Image.fromarray(rgb, "RGB").save(sai)
    print("ESTILO", lado, "px ->", sai)


def flores(rgb: np.ndarray, m: np.ndarray) -> np.ndarray:
    """so as flores do retocar, sem o reforco de verde nem o farol (as cores ja sao as da paleta)"""
    sat, val, mist = tc.SAT_VERDE, tc.VAL_VERDE, tc.MISTURA_FAROL
    tc.SAT_VERDE, tc.VAL_VERDE, tc.MISTURA_FAROL = 1.0, 1.0, 0.0
    try:
        tmp = Path(sys.argv[4]).with_suffix(".masc.png")
        Image.fromarray(m, "RGB").save(tmp)
        return tc.retocar(rgb, str(tmp))
    finally:
        tc.SAT_VERDE, tc.VAL_VERDE, tc.MISTURA_FAROL = sat, val, mist
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    main(*sys.argv[1:6])
