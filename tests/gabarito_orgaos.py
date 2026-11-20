"""Gabarito das vidas de hoje para o G2 dos orgaos do olfato e do ouvido (docs/TAREFA_V2_DOIS_PETS.md, etapa 8b; docs/futuro/dois_pets.md,
secao 5.6; DP-13 e DP-14): gravado com o codigo da main ANTES de mexer no corpo, no grafo e no motor do corpo. Com a ConfigOlfato e a
ConfigOuvido desligadas, tudo aqui tem de sair igual, byte a byte.

Tres partes:
- **as vidas de um pet** no mundo fisico (`simular_vida_mundo`, layout padrao, o dono atencioso perto com a bola de vez em quando), com o
  corpo da quimica, a etapa 6 inteira e a etapa 6 com o metabolismo, o instinto do mundo e os lobos aprendendo com a chave do corpo, sementes
  101 e 202. Confere a impressao do gabarito dos dois pets e, decisao a decisao, as leituras da `PercepcaoCorpo` nos campos de hoje (um espiao
  na politica);
- **os grupos de dois pets** com o corpo da etapa 6 (o B entrando no dia 0 e no dia 1), o resumo do grupo, o registro e cada pet;
- **o corpo sozinho**: a tabela do grafo (os campos de hoje) e o relato do `checar` em cada combinacao de sub-chaves, com e sem o mundo
  fisico, e uma sequencia de estimulos e ticks com os receptores e o `para_dict` a cada passo.

    python tests/gabarito_orgaos.py      # grava tests/gabaritos/orgaos_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_dois_pets as gdp  # noqa: E402

from digilab.config import (CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES, CONFIG_CORPO_METABOLISMO, CONFIG_GRUPO_LIGADA,  # noqa: E402
                            CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigCorpo)
from digilab.corpo import Corpo, grafo_do_corpo, taxas_de  # noqa: E402
from digilab.corpo_grafo import checar  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, simular_vida_mundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.state import Estado  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "orgaos_vidas_de_hoje.json"
DIAS = 3
SEMENTES = (101, 202)                                   # so as dos testes
CM = CONFIG_MUNDO_LIGADA
CORPOS = {"quimica": ConfigCorpo(ligada=True, digestao=True, vida=True), "drives": CONFIG_CORPO_DRIVES,
          "metabolismo": CONFIG_CORPO_METABOLISMO}
CEREBROS = ("instinto", "lobos")
MotorMundoCorpo = com_corpo(MotorMundo)
# os campos da PercepcaoCorpo de hoje: o espiao le so estes (um campo novo, desligado, fica None e nao entra aqui)
CAMPOS_HOJE = ("fome", "higiene", "energia", "humor", "saude", "tedio", "curiosidade", "solidao", "estresse", "dor", "susto", "vontade",
               "conforto")
# o corpo sozinho: as combinacoes de sub-chaves (cada uma exige a anterior)
COMBOS = {"ligada": ConfigCorpo(ligada=True), "quimica": CORPOS["quimica"], "drives": CONFIG_CORPO_DRIVES,
          "banheiro": CONFIG_CORPO_BANHEIRO, "metabolismo": CONFIG_CORPO_METABOLISMO}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def _texto(x) -> str:
    return json.dumps(x, sort_keys=True, default=repr)


class Espiao:
    """Embrulho que so le: anota as leituras da `PercepcaoCorpo` de cada decisao (os campos de hoje) e repassa todo o resto."""

    def __init__(self, politica) -> None:
        self._p = politica
        self.leituras: list = []

    def agir(self, obs, rng):
        pc = obs.corpo
        self.leituras.append(None if pc is None else [getattr(pc, c) for c in CAMPOS_HOJE])
        return self._p.agir(obs, rng)

    def __getattr__(self, nome):
        return getattr(self._p, nome)


def politica(cerebro: str, corpo: str):
    if cerebro == "instinto":
        return PoliticaInstintoMundo(CONFIG_PADRAO)
    return PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=CM, cfg_corpo=CORPOS[corpo])


def fabrica_motor(corpo: str):
    cc = CORPOS[corpo]
    return lambda p, cfg, s, **kw: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc, **kw)  # noqa: E731


def vida(corpo: str, cerebro: str, semente: int) -> dict:
    esp = Espiao(politica(cerebro, corpo))
    dono = gdp.DonoComBolaPerto(DonoComLugar(criar_dono("atencioso"), "perto", semente, "atencioso", CM))
    v = simular_vida_mundo("atencioso", dono, esp, semente, DIAS, 16 * DIAS, fabrica_motor(corpo), rotulo_dono="atencioso")
    d = gdp.impressao(v.motor, v.interacoes)
    d["leituras"] = _sha(_texto(esp.leituras))
    d["decisoes"] = len(esp.leituras)
    return d


def casos_vidas():
    for corpo in CORPOS:
        for cerebro in CEREBROS:
            for s in SEMENTES:
                yield f"vida|{corpo}|{cerebro}|{s}", (corpo, cerebro, s)


def grupo(cerebro: str, entrada_b: int, semente: int) -> dict:
    pets = []
    for ident, entrada, dono, lugar in (("A", 0, "atencioso", "perto"), ("B", entrada_b, "aleatorio", "longe")):
        s = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)[ident]
        fp = (lambda cfg=None: politica(cerebro, "drives"))
        d = DonoComLugar(criar_dono(dono), lugar, s, dono, CM)
        pets.append(PetDoGrupo(ident, entrada, fp, fabrica_motor("drives"), d, dono, cerebro))
    g = simular_grupo(CM, semente, pets, DIAS)
    return {"resumo": _sha(_texto(g.resumo())), "registro": _sha(g.registro.para_jsonl()),
            "pets": {i: gdp.impressao(m) for i, m in sorted(g.motores.items())}}


def casos_grupos():
    for cerebro in CEREBROS:
        for entrada_b in (0, 1440):
            for s in SEMENTES:
                yield f"grupo|{cerebro}|{entrada_b}|{s}", (cerebro, entrada_b, s)


def tabela(g) -> dict:
    """a tabela do grafo, nos campos de hoje (um campo novo com o padrao nao entra)"""
    return {"quimicos": [[q.nome, q.teto, q.descarte, q.receptor, q.leitura, q.meia_vida, q.k_meia_vida] for q in g.quimicos],
            "reacoes": [[r.nome, list(r.consome), list(r.produz), r.taxa, [list(f) for f in r.fracoes], r.le, r.lado, r.limiar]
                        for r in g.reacoes],
            "emissores": [[e.nome, e.gatilho, e.fase, [list(x) for x in e.efeitos],
                           [[le.quimico, le.num, le.den, le.sinal] for le in e.le], e.limiar, e.divisor, e.variavel]
                          for e in g.emissores]}


def sequencia(cc: ConfigCorpo, com_mundo: bool) -> list:
    """estimulos e ticks sorteados (rng propria), com os receptores e o `para_dict` a cada passo"""
    rng = random.Random(8101)
    corpo = Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=com_mundo)
    saida = []
    for i in range(600):
        k = rng.randrange(6)
        if k == 0:
            corpo.acao_dono(rng.choice([AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR, AcaoUsuario.ACARICIAR]))
        elif k == 1:
            corpo.acao_pet(rng.choice([AcaoPet.BRINCAR, AcaoPet.EXPLORAR, AcaoPet.COMER]), com_mundo=com_mundo)
        elif k == 2 and com_mundo:
            corpo.estimulo_andar(rng.randrange(0, 61), CM.custo_energia_por_subunidade)
        else:
            corpo.passo(Estado(tick=i, dormindo=rng.random() < 0.3, sujeira=rng.randrange(3)))
        saida.append([corpo.receptores(), corpo.para_dict()])
    return saida


def casos_corpo():
    for nome in COMBOS:
        for com_mundo in (False, True):
            yield f"corpo|{nome}|{com_mundo}", (nome, com_mundo)


def corpo_de_hoje(nome: str, com_mundo: bool) -> dict:
    cc = COMBOS[nome]
    g = grafo_do_corpo(CONFIG_PADRAO, cc, taxas_de(CONFIG_PADRAO, cc), com_mundo)
    return {"tabela": _sha(_texto(tabela(g))), "relato": _sha(_texto(checar(g))), "sequencia": _sha(_texto(sequencia(cc, com_mundo)))}


def gerar() -> dict:
    g = {}
    for chave, caso in casos_vidas():
        g[chave] = vida(*caso)
    for chave, caso in casos_grupos():
        g[chave] = grupo(*caso)
    for chave, caso in casos_corpo():
        g[chave] = corpo_de_hoje(*caso)
    return g


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} casos")
