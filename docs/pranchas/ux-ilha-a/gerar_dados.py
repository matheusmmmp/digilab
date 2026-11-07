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
ESTADOS = {
    "nada_tocado": ("d", {1920: "d04", 390: "d04"}),
    "etiqueta_aberta": ("d", {1920: "d04", 390: "d04"}),
    "fio_toque_pet": ("b", {("vidro", 1920): "b03", ("xcom", 1920): "b04", ("vidro", 390): "b04", ("xcom", 390): "b07"}),
    "indo_tigela": ("q", {1920: "q07", ("vidro", 390): "q11", ("xcom", 390): "q12"}),
    "toque_arvore": ("d", {1920: "d04", 390: "d04"}),
}
PELES = ("vidro", "xcom")

# as posicoes marcadas a mao na captura (o motor nao projeta os lugares nem os enfeites): por quadro e largura, iguais nas duas peles
# (a camera segue o pet, que esta no mesmo ponto nos dois quadros)
MAO = {
    ("d04", 1920): {"saco": [772, 352], "barraca": [150, 455], "ninho": [415, 640], "arvore": [716, 236], "tigela_vis": [1030, 652]},
    ("b03", 1920): {"saco": [565, 316], "barraca": None, "ninho": [200, 590], "arvore": [605, 255], "tigela_vis": [770, 590]},
    ("b04", 1920): {"saco": [565, 316], "barraca": None, "ninho": [200, 590], "arvore": [605, 255], "tigela_vis": [770, 590]},
    ("q07", 1920): {"saco": [1093, 300], "barraca": [610, 330], "ninho": [845, 520], "arvore": None, "tigela_vis": [1366, 518]},
    ("d04", 390): {"saco": [121, 338], "barraca": None, "ninho": [14, 470], "arvore": [72, 268], "tigela_vis": [220, 470]},
    ("b04", 390): {"saco": [36, 340], "barraca": None, "ninho": None, "arvore": [16, 270], "tigela_vis": [124, 462]},
    ("b07", 390): {"saco": [36, 340], "barraca": None, "ninho": None, "arvore": [16, 270], "tigela_vis": [124, 462]},
    # a 390, de noite, o balao do pet (o "26 %") fica sobre o saco: o selo do saco cede (pergunta I1-6)
    ("q11", 390): {"saco": None, "barraca": [42, 392], "ninho": [105, 425], "arvore": None, "tigela_vis": [303, 420]},
    ("q12", 390): {"saco": None, "barraca": [42, 392], "ninho": [105, 425], "arvore": None, "tigela_vis": [303, 420]},
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
                saida["estados"][f"{estado}|{pele}|{largura}"] = {
                    "fundo": f"{q['nome']}.png",
                    "semente": d["save"]["semente"], "tick": q["tick"],
                    "hora": f"{(q['tick'] % 1440) // 60:02d}:{q['tick'] % 60:02d}",
                    "acao": escolha, "regra": q["decisao"]["regra"], "chance": chance,
                    "chances": q["decisao"]["chances"],
                    "pet": q["petTela"], "pet_ret": q["ret"],
                    "tigela": q["comedouroTela"], "bola": q["bolaTela"],
                    "racao_madura": maduras, "racao_podre": podres,
                    "aprendido": aprendido, "aprendido_top": q["aprendido"],
                    "treinos_hoje": treinos_do_dia(d["save"]["log"], q["tick"]),
                    "treinou_alguma_vez": any(e[1] == "tr" for e in d["save"]["log"]),
                    "mao": MAO[(quadro, largura)],
                }
    (AQUI / "dados.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("dados.json:", len(saida["estados"]), "estados")


if __name__ == "__main__":
    main()
