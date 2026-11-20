"""Prancha ux-ilha-a ("Objetos que falam"): monta o dados.json da prancha a partir dos quadros reais do jogo.

Os quadros (as capturas da Tela Pet e o que o motor dizia em cada uma, por window.__digilab) ficam fora do git, em
D:\\Trab\\digilab\\capturas_ux_ilha_aprovar\\prancha_a\\fundo\\ (UX-8). Eles saem do spec temporario fonte/capturar_fundo.spec.ts (copiado para
web/app/e2e/ so na hora de rodar), com os saves fonte/save_dia.json (semente 6503) e fonte/save_noite.json (semente 6521, gerado por
fonte/sonda_noite.mjs).

Cada estado da prancha usa um quadro. Os numeros que a prancha mostra (a chance, a racao na tigela, o aprendido, os treinos do dia) saem daqui,
do quadro e do save; as posicoes do pet, da tigela e da bola sao a projecao do motor (cenaPara); as do saco, do ninho, da barraca e da arvore
(que o motor nao projeta) foram marcadas a mao na captura. Uso: python gerar_dados.py (de qualquer pasta). Falha alto se faltar um quadro.
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FUNDO = Path(r"D:\Trab\digilab\capturas_ux_ilha_aprovar\prancha_a\fundo")

# estado -> (prefixo do arquivo de quadros, quadro por largura; ou por (pele, largura) quando o tempo das duas capturas difere)
# Rodada 2 (2026-11-07): pets v19 sobre a main com o #689 (os modelos 3D dos lugares e o pegar o pet); sem o fio.
ESTADOS = {
    "nada_tocado": ("d", {1920: "d03", 390: "d03"}),
    "etiqueta_aberta": ("d", {1920: "d03", 390: "d03"}),
    "segurar_pet": ("p", {1920: "p00", 390: "p00"}),
    "indo_tigela": ("q", {("vidro", 1920): "q01", ("xcom", 1920): "q13", ("xcom", 390): "q07"}),
    "indo_tigela_r": ("r", {("vidro", 390): "r19"}),
    "toque_arvore": ("d", {1920: "d03", 390: "d03"}),
}
# a noite a 390 no Vidro saiu de uma segunda passada (prefixo r); o estado e o mesmo
NOME_ESTADO = {"indo_tigela_r": "indo_tigela"}
PELES = ("vidro", "xcom")

# as posicoes marcadas a mao na captura (o motor nao projeta os lugares nem os enfeites), por (quadro, largura) ou (quadro, largura, pele):
# o saco e a barraca (o pe do selo), o ninho, a copa da arvore e o ponto onde a fruta cairia. "tigela" corrige a projecao quando o quadro
# andou entre a leitura e a captura (o pet caminhando). None: fora da tela, ou coberto pelo balao do pet (I1-6).
MAO = {
    ("d03", 1920): {"saco": [752, 312], "barraca": [605, 135], "ninho": [415, 660], "arvore": [172, 150], "fruta": [196, 318]},
    ("d03", 390): {"saco": [112, 345], "barraca": [24, 240], "ninho": [15, 470], "arvore": [128, 180], "fruta": [130, 292]},
    ("p00", 1920, "vidro"): {"saco": [572, 305], "barraca": [490, 185], "ninho": None, "arvore": None},
    ("p00", 1920, "xcom"): {"saco": [580, 268], "barraca": [505, 172], "ninho": None, "arvore": None},
    ("p00", 390): {"saco": [40, 312], "barraca": None, "ninho": None, "arvore": None},
    ("q01", 1920): {"saco": [878, 290], "barraca": [690, 185], "ninho": [625, 560], "arvore": None, "tigela": [1165, 572]},
    ("q13", 1920): {"saco": [1060, 268], "barraca": [790, 170], "ninho": [845, 520], "arvore": None},
    ("r19", 390): {"saco": None, "barraca": [85, 262], "ninho": [110, 430], "arvore": None},
    ("q07", 390): {"saco": None, "barraca": [88, 262], "ninho": [85, 432], "arvore": None, "tigela": [285, 440]},
}


def ler_quadros(prefixo: str, pele: str, largura: int) -> dict:
    caminho = FUNDO / f"{prefixo}quadros_{pele}_{largura}.json"
    if not caminho.exists():
        raise FileNotFoundError(f"falta o arquivo de quadros {caminho} (rode o fonte/capturar_fundo.spec.ts)")
    d = json.loads(caminho.read_text(encoding="utf-8"))
    if d["erros"]:
        raise RuntimeError(f"a captura {caminho.name} teve erros na pagina: {d['erros']}")
    return d


def treinos_do_dia(log: list, tick: int) -> int:
    """os treinos ("tr") do registro no dia do jogo de agora (o dia = tick // 1440)"""
    return sum(1 for e in log if e[1] == "tr" and e[0] // 1440 == tick // 1440)


def main() -> None:
    saida = {"fonte": "gerar_dados.py, dos quadros em capturas_ux_ilha_aprovar/prancha_a/fundo", "estados": {}}
    for estado, (prefixo, por_largura) in ESTADOS.items():
        for pele in PELES:
            for chave, quadro in por_largura.items():
                if isinstance(chave, tuple):
                    if chave[0] != pele:
                        continue
                    largura = chave[1]
                else:
                    largura = chave
                d = ler_quadros(prefixo, pele, largura)
                achados = [q for q in d["quadros"] if q["nome"].startswith(quadro + "_")]
                if len(achados) != 1:
                    raise LookupError(f"quadro {quadro} de {prefixo}quadros_{pele}_{largura}: {len(achados)} achados")
                q = achados[0]
                if q["decisao"] is None:
                    raise ValueError(f"quadro {q['nome']} sem decisao do DigiBrain")
                maduras = sum(1 for c in q["comidas"] if c["situacao"] == "madura")
                podres = sum(1 for c in q["comidas"] if c["situacao"] == "podre")
                escolha = q["decisao"]["acao"]
                chance = next(c["chance"] for c in q["decisao"]["chances"] if c["acao"] == escolha)
                aprendido = {a["acao"]: a["desvio"] for a in q["aprendido"]}
                mao = MAO.get((quadro, largura, pele)) or MAO[(quadro, largura)]
                tigela = mao.get("tigela") or q["comedouroTela"]
                saida["estados"][f"{NOME_ESTADO.get(estado, estado)}|{pele}|{largura}"] = {
                    "fundo": f"{q['nome']}.png",
                    "semente": d["save"]["semente"], "tick": q["tick"],
                    "hora": f"{(q['tick'] % 1440) // 60:02d}:{q['tick'] % 60:02d}",
                    "acao": escolha, "regra": q["decisao"]["regra"], "chance": chance,
                    "chances": q["decisao"]["chances"],
                    "pet": q["petTela"], "pet_ret": q["ret"],
                    "tigela": tigela, "bola": q["bolaTela"],
                    "mao_ponteiro": q.get("dedo"), "pet_na_mao": q.get("petNaMao"),
                    "racao_madura": maduras, "racao_podre": podres,
                    "aprendido": aprendido, "aprendido_top": q["aprendido"],
                    "treinos_hoje": treinos_do_dia(d["save"]["log"], q["tick"]),
                    "treinou_alguma_vez": any(e[1] == "tr" for e in d["save"]["log"]),
                    "mao": mao,
                }
    (AQUI / "dados.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("dados.json:", len(saida["estados"]), "estados")


if __name__ == "__main__":
    main()
