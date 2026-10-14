"""O custo em pesos de cada receptor dos orgaos do Olfato e da Audicao como entrada do cerebro (docs/TAREFA_V2_DOIS_PETS.md, etapa 8b;
docs/futuro/dois_pets.md, secao 5.6; o teto e por plano, ate 2000: docs/DECISAO_V2_TETO_PESOS.md, TP-1 e TP-2).

O cerebro A ainda nao le os receptores dos orgaos. Se lesse, cada um entraria como as entradas novas do corpo (CORPO, etapa 5): so nas
regras de tempo livre (`lobos.REGRAS_ENTRADAS_CORPO`), um peso por (regra, acao candidata, receptor), prior 0. O custo de um receptor e o
numero de pares (regra, acao) dessas regras no cerebro montado; aqui ele sai do proprio cerebro (`_prior`), nao de uma conta a parte.

A rede de si (`digilab/rede_de_si.py`) le TODOS os receptores presentes da PercepcaoCorpo, entao com os orgaos ligados ela os pega sozinha:
o custo dela sai de `rede_de_si.n_pesos(R)`, com R os receptores do corpo mais os dos orgaos.

So montagem de cerebros, sem vida e sem semente.

    python experiments/custo_orgaos.py      # grava artifacts_v2_dois_pets/custo_orgaos.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402

from digilab.config import (CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, CONFIG_REDE_DE_SI,  # noqa: E402
                            LIMITE_TETO_PESOS_PLANO, ConfigBanheiro, ConfigCorpo, ConfigOlfato, ConfigOuvido)
from digilab.corpo import Corpo, orgaos_de  # noqa: E402
from digilab.policies.lobos import REGRAS_ENTRADAS_CORPO, PoliticaLobos  # noqa: E402
from digilab.rede_de_si import n_pesos as n_pesos_rede  # noqa: E402
from digilab.state import Estado  # noqa: E402

ARQUIVO = RAIZ / "artifacts_v2_dois_pets" / "custo_orgaos.json"
TETO_PADRAO = 1000
QUIMICA = ConfigCorpo(ligada=True, digestao=True, vida=True)
METABOLISMO = replace(QUIMICA, metabolismo=True)
# o ponto da K2 (a config da calibracao dos dois pets) e o que a bancada do grupo acrescenta (Bancada.bancada_grupo)
K2 = {"memoria_ganho": 512, "w0_pedido": 256, "w0_info": 256, "maximo_pesos": LIMITE_TETO_PESOS_PLANO}
GRUPO = {"alvo_aprendido": True, "entradas_sociais": True, "modelo_outros": True, "presenca_fruta_mundo": True}

# os cerebros: (nome, o que e, campos da ConfigLobos por cima do T3, a ConfigCorpo, a ConfigBanheiro ou None)
CEREBROS = (
    ("dois_pets_degrau1", "o cerebro A da calibracao dos dois pets (o ponto da K2, o alvo aprendido, as entradas sociais, o modelo dos "
     "outros e a presenca da fruta) com o corpo da quimica", GRUPO, QUIMICA, None),
    ("pet_que_pensa_p1", "o P1 do pet que pensa (o alvo aprendido, a presenca da fruta e as classes por arvore) com a quimica e o "
     "metabolismo", {"alvo_aprendido": True, "presenca_fruta_mundo": True, "alvo_por_arvore": True}, METABOLISMO, None),
    ("mundo_etapa6", "o P1 do mundo fisico com o corpo da etapa 6 (os drives novos e os gestos)", {}, CONFIG_CORPO_DRIVES, None),
    ("mundo_banheiro", "o P1 do mundo fisico com o corpo e o banheiro", {}, CONFIG_CORPO_BANHEIRO, ConfigBanheiro(ligada=True)),
)

# os conjuntos de orgaos: (nome, ConfigOlfato, ConfigOuvido)
ORGAOS = (
    ("olfato_comida_1", ConfigOlfato(ligada=True, narinas=1, comida=True), None),
    ("olfato_comida_2", ConfigOlfato(ligada=True, narinas=2, comida=True), None),
    ("olfato_outro_2", ConfigOlfato(ligada=True, narinas=2, outro_pet=True), None),
    ("olfato_2", ConfigOlfato(ligada=True, narinas=2, comida=True, outro_pet=True), None),
    ("ouvido_1", None, ConfigOuvido(ligada=True, ouvidos=1)),
    ("ouvido_2", None, ConfigOuvido(ligada=True, ouvidos=2)),
    ("dp13_dp14", ConfigOlfato(ligada=True, narinas=2, comida=True, outro_pet=True), ConfigOuvido(ligada=True, ouvidos=2)),
)


def cerebro(troca: dict, cc: ConfigCorpo, cbh: ConfigBanheiro | None) -> PoliticaLobos:
    cl = replace(bv.cfg_lobos_do_ponto("T3", K2), **troca)
    kw = {"cfg_banheiro": cbh} if cbh is not None else {}
    return PoliticaLobos(CONFIG_PADRAO, cl, cfg_mundo=CONFIG_MUNDO_LIGADA, cfg_corpo=cc, **kw)


def pares_tempo_livre(b: PoliticaLobos) -> dict[str, int]:
    """os pares (regra, acao candidata) das regras de tempo livre no cerebro montado: o custo de uma entrada nova do corpo"""
    return {r: len(b._prior[r]) for r in REGRAS_ENTRADAS_CORPO if r in b._prior}


def receptores_do_corpo(cc: ConfigCorpo) -> int:
    return len(Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=True).receptores())


def _sha(caminho: str) -> str:
    return hashlib.sha256((RAIZ / caminho).read_bytes()).hexdigest()


def medir() -> dict:
    cerebros = {}
    for nome, descricao, troca, cc, cbh in CEREBROS:
        b = cerebro(troca, cc, cbh)
        pares = pares_tempo_livre(b)
        por_receptor = sum(pares.values())
        n, R = b.n_pesos(), receptores_do_corpo(cc)
        conjuntos = {}
        for nome_o, co, cv in ORGAOS:
            k = len(orgaos_de(co, cv))
            total = n + k * por_receptor
            rede = n_pesos_rede(R + k, CONFIG_REDE_DE_SI)
            conjuntos[nome_o] = {"receptores": k, "custo": k * por_receptor, "total": total,
                                 "cabe_no_padrao": total < TETO_PADRAO, "cabe_no_teto_do_plano": total < LIMITE_TETO_PESOS_PLANO,
                                 "rede_de_si": {"receptores": R + k, "pesos": rede, "cabe": rede < CONFIG_REDE_DE_SI.maximo_pesos}}
        cerebros[nome] = {"descricao": descricao, "pesos_sem_orgao": n, "pares_tempo_livre": pares, "custo_por_receptor": por_receptor,
                          "receptores_do_corpo": R, "rede_de_si_sem_orgao": n_pesos_rede(R, CONFIG_REDE_DE_SI), "conjuntos": conjuntos}
    return {"descricao": __doc__.strip().splitlines()[0], "teto_padrao": TETO_PADRAO, "teto_do_plano": LIMITE_TETO_PESOS_PLANO,
            "teto_rede_de_si": CONFIG_REDE_DE_SI.maximo_pesos,
            "conjuntos": {n: [o.receptor for o in orgaos_de(co, cv)] for n, co, cv in ORGAOS}, "cerebros": cerebros,
            "codigo": {c: _sha(c) for c in ("digilab/policies/lobos.py", "digilab/corpo.py", "digilab/rede_de_si.py",
                                             "experiments/custo_orgaos.py")}}


if __name__ == "__main__":
    d = medir()
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for nome, c in d["cerebros"].items():
        print(nome, c["pesos_sem_orgao"], "por receptor", c["custo_por_receptor"], c["pares_tempo_livre"], "R", c["receptores_do_corpo"])
        for n, x in c["conjuntos"].items():
            print("   ", n, x["receptores"], x["custo"], x["total"], "rede", x["rede_de_si"]["pesos"])
