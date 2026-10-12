"""Gabarito da quimica do corpo para a paridade Python x TS (G-PAR; docs/TAREFA_V2_CORPO_DRIVES.md, secao 12 e etapa 7 da secao 14).

So inteiros: a paridade e exata. O TS (etapa 7, do A) refaz cada caso e cada vida e confere igual, ate o sha256.

    python experiments/exportar_gabarito_corpo.py      # grava tests/gabaritos/corpo_quimica_python.json

O conteudo (versao 5):
- `taxas`: os numeros de hoje na escala C, ja inteiros (secao 4);
- `casos`: a quimica base, numa grade de estados com cada operacao (o tick, as acoes do dono e do pet, a bola, a fruta), o estado depois,
  o receptor de privacao e os receptores na escala S;
- `meia_vida` e `div_arred`: os passos inteiros da secao 3;
- `vidas`: 3 vidas de hoje em malha aberta (as acoes do pet e do dono forcadas, a sujeira e o sono lidos do Estado de hoje). A entrada de
  cada tick e um caractere (sono e sujeira), os eventos vao antes do tick em que acontecem, e o sha256 cobre q depois de cada operacao;
- `digestao` (orgao 1, secao 5): a mesma grade e as mesmas vidas com a digestao na taxa C (o estomago no fim de q), e o digerido de cada
  operacao; `digestao_lenta`: a grade com uma taxa menor, so para a paridade da reacao (nao e um valor da pesquisa);
- `vida` (orgao 2, secao 6): os limiares de estagio nas duracoes de hoje, uma grade de Vidas em volta dos limiares (o passo e o estagio
  antes e depois) e as mesmas vidas com a digestao e a Vida (os ticks em que o estagio muda);
- `mundo` (versao 3, CORPO-MUNDO): os estimulos do mundo fisico na mesma grade de estados, sem e com a digestao: a acao do pet com a
  MF-2 (`pet_mundo`), o andar (`andar`, deslocamento em subunidades e o custo da ConfigMundo) e as comidas do mapa (`consumo`: tipo,
  situacao e o efeito da fruta no humor). As secoes da versao 2 nao mudaram.
- `etapa6` (versao 4, CORPO-DRIVES): os drives novos e os gestos (secoes 7, 8 e 17), com a quimica, a digestao, a Vida e o mundo fisico
  (a curiosidade existe): os numeros da ConfigCorpo, uma grade de estados (os 13 quimicos e a janela do tedio) com cada operacao (o
  tick acordado e dormindo, o dono brincar, o carinho, o tapa, as quatro atividades e a novidade), o estado e a janela depois e os
  receptores; e uma sequencia longa de operacoes sorteadas num corpo so, com o sha256 de q e da janela depois de cada uma. O tapa vai
  como a acao do dono "tapa". As secoes da versao 3 nao mudaram.
- versao 5 (etapa 7, o corpo em TS): `config` (a ConfigCorpo padrao, campo a campo, para o espelho da web), `grafo` (a tabela unica e o
  relato de `corpo_grafo.checar` em cada combinacao de sub-chaves, com e sem o mundo fisico, e sem o medo da mao), `de_estado` (o corpo
  que nasce de tres Estados em cada combinacao: q, receptores, drives e para_dict) e `etapa6_mundo` (os estimulos do mundo fisico no
  corpo da etapa 6, na grade de estados da etapa 6, com a digestao e os drives lidos). As secoes da versao 4 nao mudaram.

- `banheiro` (versao 5, docs/TAREFA_V2_BANHEIRO.md, etapa 2): a vontade e o conforto (secao 3 e BN-6), com a etapa 6 inteira e o mundo
  fisico: os numeros da ConfigCorpo, uma grade de estados (os 15 quimicos, a janela do tedio e o resto da vontade) com cada operacao (o
  tick acordado e dormindo com 0 a 4 necessidades na regiao, a racao, o comer, a fruta e a racao do mapa, que passam pela digestao, o
  carinho com e sem susto, o aliviar e a necessidade no chao), o estado, a janela e o resto depois e os receptores; e uma sequencia longa
  de operacoes sorteadas num corpo so, com o sha256 de q, da janela e do resto depois de cada uma. As secoes da versao 4 nao mudaram.
- `metabolismo` (versao 5, como o banheiro; docs/TAREFA_V2_METABOLISMO.md, etapa 1): o combustivel e a reserva (secao 3), com a
  etapa 6 inteira e o mundo fisico: os numeros da ConfigCorpo; o grafo (a tabela com as reacoes inteiras: fracoes, o quimico lido, o lado e o limiar; e o
  relato) em quatro combinacoes; uma grade de estados (os 15 quimicos, a janela do tedio e o resto da conversao), com o combustivel e a
  reserva em volta dos limiares, com cada operacao (o tick acordado e dormindo, as racoes e o comer que passam pela digestao, as
  atividades e o andar), o estado, o resto e as contas depois; a mesma grade com a conversao 2/3 (o resto mordendo, so para a
  paridade); e uma sequencia longa de operacoes sorteadas num corpo so, com o sha256 de q, da janela, do resto e das contas. As secoes
  da versao 5 nao mudaram; a `config` ganhou os campos do metabolismo.
- `metabolismo_gasto` (o no `gasto_atividades`): a grade do metabolismo com o fator do gasto das atividades x 1/2 e x 2, e as taxas das
  atividades em cada um. A `config` ganhou os dois campos do fator; as outras secoes nao mudaram.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from dataclasses import replace  # noqa: E402

from digilab.config import (CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES, CONFIG_CORPO_METABOLISMO, CONFIG_DURACOES,  # noqa: E402
                            CONFIG_EVOLUCAO_PESQUISA, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigCorpo)
from digilab.corpo import (ATIVIDADES, Corpo, div_arred, grafo_do_corpo, limiares_estagio, passo_meia_vida, quimicos_de,  # noqa: E402
                           taxas_de, ticks_de_estagio)
from digilab.corpo_grafo import Grafo, checar  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import ACOES_PET_HOJE, AcaoPet, AcaoUsuario  # noqa: E402
from digilab.policy import PoliticaInstinto, efeito_da_acao_do_pet  # noqa: E402
from digilab.state import Estado, aplicar_acao_usuario, avancar_um_tick  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "corpo_quimica_python.json"
CC = ConfigCorpo(ligada=True)
CC_DIGESTAO = ConfigCorpo(ligada=True, digestao=True)
TAXA_LENTA = 1000                        # so para a paridade da reacao com a taxa mordendo (nao e valor de pesquisa)
CC_DIGESTAO_LENTA = ConfigCorpo(ligada=True, digestao=True, taxa_digestao=TAXA_LENTA)
CC_VIDA = ConfigCorpo(ligada=True, digestao=True, vida=True)
DURACOES = {"pesquisa": CONFIG_EVOLUCAO_PESQUISA, "canonica": CONFIG_DURACOES.cfg_evo("canonica")}
SEMENTE_CASOS = 20261007                 # so para sortear a grade de estados do gabarito (nao e semente de vida)
VIDAS = (("aleatorio", 101), ("relapso", 303), ("atencioso", 202))   # sementes dos testes
DIAS = 3
ORCAMENTO = 48
ACOES_DONO = (AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR, AcaoUsuario.ACARICIAR, AcaoUsuario.ELOGIAR,
              AcaoUsuario.REPREENDER)


def _q(corpo: Corpo) -> list[int]:
    return [corpo.q[n] for n in corpo.quimicos]


def _corpo(q: list[int], cc: ConfigCorpo) -> Corpo:
    return Corpo(dict(zip(quimicos_de(cc), q)), CONFIG_PADRAO, cc)


def _estados(rng: random.Random, cc: ConfigCorpo) -> list[list[int]]:
    """A grade de estados da quimica base; com a digestao, o estomago no fim (vazio, um pouco, muito)."""
    C = cc.escala
    t = taxas_de(CONFIG_PADRAO, cc)
    fixos = [[0] * 5, [C] * 5, [t.limiar_privacao, 0, 0, 0, 0], [t.limiar_privacao + 1, 0, 0, 0, 0],
             [0, t.limiar_privacao, 0, 0, C], [0, 0, t.limiar_privacao + 1, 0, 1], [90000, 0, 45000, 135000, 0]]
    base = fixos + [[rng.randrange(C + 1) for _ in range(5)] for _ in range(25)]
    if not cc.digestao:
        return base
    return [q + [a] for q in base[:12] for a in (0, 500, 202500)]       # os fixos e 5 sorteados, com o estomago em tres niveis


def _aplicar(c: Corpo, op: list) -> None:
    if op[0] == "passo":
        c.passo(Estado(tick=op[3], dormindo=bool(op[1]), sujeira=op[2]))
    elif op[0] == "dono":
        c.acao_dono(AcaoUsuario(op[1]))
    elif op[0] == "pet":
        c.acao_pet(AcaoPet(op[1]))
    elif op[0] == "bola":
        c.estimulo_bola(op[1])
    elif op[0] == "fruta":
        c.estimulo_fruta(op[1], op[2])
    elif op[0] == "pet_mundo":
        c.acao_pet(AcaoPet(op[1]), com_mundo=True)
    elif op[0] == "andar":
        c.estimulo_andar(op[1], op[2])
    elif op[0] == "consumo":
        c.estimulo_consumo_mundo(op[1], op[2], CONFIG_MUNDO_LIGADA, op[3])
    else:
        raise ValueError(f"operacao desconhecida: {op!r}")


def _ops_de_hoje() -> list[list]:
    ops = [["passo", dormindo, sujeira, tick] for dormindo in (0, 1) for sujeira in (0, 3) for tick in (600, 1400)]
    ops += [["dono", a.value] for a in ACOES_DONO] + [["pet", a.value] for a in ACOES_PET_HOJE]
    return ops + [["bola", 0.15], ["fruta", 0.10, -0.10], ["fruta", 0.10, 0.10], ["fruta", 0.10, 0.0]]


def _ops_do_mundo() -> list[list]:
    """os estimulos do mundo fisico (versao 3): a MF-2, o andar e as comidas do mapa, com os numeros da ConfigMundo"""
    cm = CONFIG_MUNDO_LIGADA
    ops = [["pet_mundo", a.value] for a in ACOES_PET_HOJE]
    ops += [["andar", d, cm.custo_energia_por_subunidade] for d in (0, 1, 37, 60, 128, 6000)]
    ops += [["consumo", "racao", "madura", 0.0], ["consumo", "racao", "podre", 0.0]]
    ops += [["consumo", f, sit, ef] for f in ("a", "b") for sit in ("madura", "podre") for ef in (-0.10, 0.0, 0.10)]
    return ops


def casos(cc: ConfigCorpo, ops: list[list] | None = None) -> list[dict]:
    rng = random.Random(SEMENTE_CASOS)
    out = []
    for q in _estados(rng, cc):
        for op in (ops if ops is not None else _ops_de_hoje()):
            c = _corpo(q, cc)
            _aplicar(c, op)
            rec = c.receptores()
            caso = {"q": q, "op": op, "q_depois": _q(c), "privacao": c.em_privacao(),
                    "receptores": [rec[d] for d in ("fome", "higiene", "energia", "humor", "saude")]}
            if cc.digestao:
                caso["digerido"] = c.digerido_total
                caso["digerido_no_tick"] = c.digerido_no_tick
                caso["descartado"] = c.descartado_total
            out.append(caso)
    return out


def casos_vida() -> list[dict]:
    """A Vida em volta de cada limiar de estagio (e no fim): um passo, com o estagio antes e depois, nas duas duracoes."""
    C, v = CC_VIDA.escala, CC_VIDA.vida_decaimento
    out = []
    for nome, cfg_evo in DURACOES.items():
        vidas = {C, v, v - 1, 1, 0}
        for lim in limiares_estagio(CC_VIDA, cfg_evo):
            vidas |= {lim - 1, lim, lim + 1, lim + v, lim + v - 1}
        for vida in sorted(vidas):
            c = Corpo({"fome": 90000, "desconforto": 0, "cansaco": 45000, "tristeza": 135000, "dano": 0, "alimento": 0, "vida": vida},
                      CONFIG_PADRAO, CC_VIDA, cfg_evo)
            antes = c.estagio()
            c.passo(Estado(tick=600))
            out.append({"duracao": nome, "vida": vida, "estagio": antes, "vida_depois": c.q["vida"], "estagio_depois": c.estagio()})
    return out


def meia_vida() -> list[list[int]]:
    ks = (CC.k_meia_vida_susto, CC.k_meia_vida_dor, CC.k_meia_vida_estresse)
    qs = (0, 1, 2, 100, 1023, 1024, 65535, 65536, 225000, CC.escala)
    return [[q, k, passo_meia_vida(q, k, CC.bits_meia_vida)] for k in ks for q in qs]


def divisoes() -> list[list[int]]:
    pares = [(n, d) for n in (-7, -5, -3, -1, 0, 1, 3, 5, 7, 450000 * 1024 - 1, 337500 * 1024) for d in (2, 3, 450000)]
    return [[n, d, div_arred(n, d)] for n, d in pares]


def vida_malha_aberta(dono: str, semente: int, cc: ConfigCorpo = CC) -> dict:
    """Uma vida de hoje rejogada em malha aberta, com o corpo ao lado. Devolve a entrada que o TS precisa e o que conferir."""
    cfg = CONFIG_PADRAO
    motor = simular_vida(dono, criar_dono(dono), PoliticaInstinto(cfg), semente, DIAS, ORCAMENTO).motor
    acoes_pet = dict(motor._acoes_pet)
    rng = random.Random(semente)               # a rng de ambiente do motor (engine.Motor: random.Random(semente))
    e = Estado()
    c = Corpo.de_estado(e, cfg, cc)
    q0 = _q(c)
    ticks, eventos, pontos = [], [], []
    estagios = [[0, c.estagio()]] if cc.vida else []
    h = hashlib.sha256()

    def marca() -> None:
        h.update((",".join(map(str, _q(c))) + ";").encode())

    for ev in motor.log:
        if ev.tipo == "avanco":
            for _ in range(int(ev.valor)):
                if e.tick in acoes_pet:
                    a = acoes_pet[e.tick]
                    e = efeito_da_acao_do_pet(e, a, cfg, cfg.intervalo_decisao_ticks)
                    c.acao_pet(a)
                    eventos.append([len(ticks), "pet", a.value])
                    marca()
                antes = e
                ticks.append(chr(ord("a") + 8 * int(antes.dormindo) + antes.sujeira))
                e = avancar_um_tick(e, cfg, rng)
                c.passo(antes)
                marca()
                if cc.vida and c.estagio() != estagios[-1][1]:
                    estagios.append([len(ticks), c.estagio()])
                if len(ticks) % 60 == 0:
                    pontos.append([len(ticks), _q(c)])
        elif ev.tipo == "acao_usuario":
            a = AcaoUsuario(ev.valor)
            e = aplicar_acao_usuario(e, a, cfg, rng)
            c.acao_dono(a)
            eventos.append([len(ticks), "dono", a.value])
            marca()
        else:
            raise ValueError(f"tipo de evento desconhecido no log: {ev.tipo!r}")
    if e != motor._estado:
        raise ValueError(f"{dono}@{semente}: a malha aberta nao reproduziu o Estado de hoje")
    out = {"dono": dono, "semente": semente, "q_inicial": q0, "tick_inicial": 0, "ticks": "".join(ticks), "eventos": eventos,
           "pontos": pontos, "q_final": _q(c), "sha256": h.hexdigest()}
    if cc.digestao:
        out["digerido_total"] = c.digerido_total
        out["descartado_total"] = c.descartado_total
    if cc.vida:
        out["estagios"] = estagios
    return out


# ------------------------------------------------------------------ etapa 6 (versao 4)

CC_E6 = CONFIG_CORPO_DRIVES
CAMPOS_E6 = ("tedio_sobe", "curiosidade_sobe", "solidao_sobe", "estresse_limiar", "estresse_divisor", "janela_tedio", "tedio_bola",
             "tedio_brincar", "tedio_explorar", "tedio_dono", "curiosidade_novidade", "curiosidade_max_novidades", "carinho_solidao",
             "carinho_estresse", "tapa_dor", "tapa_susto", "tapa_estresse", "medo_da_mao", "k_meia_vida_estresse", "k_meia_vida_dor",
             "k_meia_vida_susto")
RECEPTORES_E6 = ("fome", "higiene", "energia", "humor", "saude", "tedio", "curiosidade", "solidao", "estresse", "dor", "susto")


class _Tapa:
    """o AcaoUsuario.TAPA do A (etapa 6): o corpo o le pelo valor"""
    value = "tapa"


def _corpo_e6(q: list[int], janela: list[str]) -> Corpo:
    c = Corpo(dict(zip(quimicos_de(CC_E6, True), q)), CONFIG_PADRAO, CC_E6, com_mundo=True)
    c.janela_tedio = list(janela)
    return c


def _aplicar_e6(c: Corpo, op: list) -> None:
    if op[0] == "dono" and op[1] == "tapa":
        c.acao_dono(_Tapa())
    elif op[0] == "atividade":
        c.atividade(op[1])
    elif op[0] == "novidade":
        c.estimulo_novidade(op[1])
    else:
        _aplicar(c, op)


def _ops_e6() -> list[list]:
    ops = [["passo", dormindo, sujeira, tick] for dormindo in (0, 1) for sujeira in (0, 2) for tick in (600, 1400)]
    ops += [["dono", "brincar"], ["dono", "acariciar"], ["dono", "tapa"]]
    return ops + [["atividade", a] for a in ATIVIDADES] + [["novidade", n] for n in (0, 1, 2, 5)]


def _estados_e6(rng: random.Random) -> list[tuple[list[int], list[str]]]:
    C = CC_E6.escala
    n = len(quimicos_de(CC_E6, True))
    L = CC_E6.estresse_limiar
    fixos = [[0] * n, [C] * n, [L + 1] * 3 + [0] * (n - 3), [0] * 7 + [L, 0, L + 1000, 0, 90000, C // 2]]
    estados = [(q, []) for q in fixos]
    for _ in range(20):
        q = [rng.randrange(C + 1) for _ in range(n)]
        janela = [rng.choice(ATIVIDADES) for _ in range(rng.randrange(CC_E6.janela_tedio + 1))]
        estados.append((q, janela))
    return estados


def _caso_e6(c: Corpo) -> dict:
    rec = c.receptores()
    return {"q_depois": _q(c), "janela_depois": list(c.janela_tedio), "receptores": [rec[r] for r in RECEPTORES_E6]}


def etapa6() -> dict:
    rng = random.Random(SEMENTE_CASOS + 6)
    casos_e6 = []
    for q, janela in _estados_e6(rng):
        for op in _ops_e6():
            c = _corpo_e6(q, janela)
            _aplicar_e6(c, op)
            casos_e6.append({"q": q, "janela": janela, "op": op, **_caso_e6(c)})
    # a sequencia: um corpo so, do nascimento, 3000 operacoes sorteadas (o tick com o sono e a sujeira, e os estimulos)
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, CC_E6, com_mundo=True)
    ops, h = [], hashlib.sha256()
    tick = 0
    for _ in range(3000):
        if rng.random() < 0.7:
            op = ["passo", int(rng.random() < 0.3), rng.randrange(4), tick]
            tick += 1
        else:
            op = rng.choice(_ops_e6()[8:])
        _aplicar_e6(c, op)
        ops.append(op)
        h.update(json.dumps([_q(c), c.janela_tedio], separators=(",", ":")).encode())
    return {"quimicos": list(quimicos_de(CC_E6, True)), "config": {k: getattr(CC_E6, k) for k in CAMPOS_E6},
            "receptores": list(RECEPTORES_E6), "casos": casos_e6,
            "sequencia": {"ops": ops, "sha256": h.hexdigest(), "q_final": _q(c), "janela_final": list(c.janela_tedio)}}


# ------------------------------------------------------------------ versao 5 (etapa 7, o corpo em TS)

CHAVES_V5 = {
    "quimica": ConfigCorpo(ligada=True),
    "digestao": ConfigCorpo(ligada=True, digestao=True),
    "vida": ConfigCorpo(ligada=True, digestao=True, vida=True),
    "novos": ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True),
    "gestos": CC_E6,
    "gestos_sem_medo": ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True, gestos=True, medo_da_mao=0),
}
SUB_CHAVES = ("ligada", "digestao", "vida", "drives_novos", "gestos", "medo_da_mao")
ESTADOS_V5 = (Estado(), Estado(tick=5000, fome=0.5, higiene=0.25, energia=0.3, humor=0.9, saude=0.6),
              Estado(tick=50000, fome=0.0, higiene=1.0, energia=0.0, humor=0.0, saude=0.0))


def _tabela(g: Grafo) -> dict:
    return {"quimicos": [[q.nome, q.teto, q.descarte, q.receptor, q.leitura, q.meia_vida, q.k_meia_vida] for q in g.quimicos],
            "reacoes": [[r.nome, list(r.consome), list(r.produz), r.taxa] for r in g.reacoes],
            "emissores": [{"nome": e.nome, "gatilho": e.gatilho, "fase": e.fase, "efeitos": [list(x) for x in e.efeitos],
                           "le": [[le.quimico, le.num, le.den, le.sinal] for le in e.le], "limiar": e.limiar, "divisor": e.divisor,
                           "variavel": e.variavel} for e in g.emissores]}


def grafos() -> list[dict]:
    out = []
    for nome, cc in CHAVES_V5.items():
        for com_mundo in (False, True):
            g = grafo_do_corpo(CONFIG_PADRAO, cc, taxas_de(CONFIG_PADRAO, cc), com_mundo)
            out.append({"chaves": nome, "com_mundo": com_mundo, "config": {k: getattr(cc, k) for k in SUB_CHAVES},
                        "tabela": _tabela(g), "relato": checar(g)})
    return out


def de_estado() -> list[dict]:
    out = []
    for nome, cc in CHAVES_V5.items():
        for com_mundo in (False, True):
            for e in ESTADOS_V5:
                c = Corpo.de_estado(e, CONFIG_PADRAO, cc, com_mundo=com_mundo)
                out.append({"chaves": nome, "com_mundo": com_mundo, "config": {k: getattr(cc, k) for k in SUB_CHAVES},
                            "estado": {k: getattr(e, k) for k in ("tick", "fome", "higiene", "energia", "humor", "saude")},
                            "quimicos": list(c.quimicos), "q": _q(c), "receptores": c.receptores(), "drives": c.drives(),
                            "para_dict": c.para_dict()})
    return out


def etapa6_mundo() -> dict:
    rng = random.Random(SEMENTE_CASOS + 7)
    casos_m = []
    for q, janela in _estados_e6(rng):
        for op in _ops_do_mundo():
            c = _corpo_e6(q, janela)
            _aplicar_e6(c, op)
            casos_m.append({"q": q, "janela": janela, "op": op, **_caso_e6(c), "privacao": c.em_privacao(), "drives": c.drives(),
                            "digerido": c.digerido_total, "digerido_no_tick": c.digerido_no_tick, "descartado": c.descartado_total})
    return {"quimicos": list(quimicos_de(CC_E6, True)), "casos": casos_m}

CC_B = CONFIG_CORPO_BANHEIRO
CAMPOS_B = ("vontade_sobe", "vontade_digestao_num", "vontade_digestao_den", "vontade_limiar", "vontade_desconforto",
            "necessidade_desconforto", "necessidade_regiao", "necessidade_max_regiao", "conforto_carinho", "k_meia_vida_conforto")
RECEPTORES_B = RECEPTORES_E6 + ("vontade", "conforto")


def _corpo_b(q: list[int], janela: list[str], resto: int) -> Corpo:
    c = Corpo(dict(zip(quimicos_de(CC_B, True), q)), CONFIG_PADRAO, CC_B, com_mundo=True)
    c.janela_tedio = list(janela)
    c.resto_vontade = resto
    return c


def _aplicar_b(c: Corpo, op: list) -> None:
    if op[0] == "passo_nec":
        c.passo(Estado(tick=op[3], dormindo=bool(op[1]), sujeira=op[2]), necessidades=op[4])
    elif op[0] == "aliviar":
        c.estimulo_aliviar()
    elif op[0] == "necessidade":
        c.estimulo_necessidade()
    else:
        _aplicar_e6(c, op)


def _ops_b() -> list[list]:
    ops = [["passo_nec", dormindo, 0, tick, n] for dormindo in (0, 1) for tick in (600, 1400) for n in (0, 1, 4)]
    ops += [["dono", "alimentar"], ["dono", "acariciar"], ["dono", "tapa"], ["pet", "comer"], ["fruta", 0.15, -0.1],
            ["consumo", "racao", "madura", 0.0], ["aliviar"], ["necessidade"]]
    return ops


def _estados_b(rng: random.Random) -> list[tuple[list[int], list[str], int]]:
    C = CC_B.escala
    n = len(quimicos_de(CC_B, True))
    i_v = quimicos_de(CC_B, True).index("vontade")
    L = CC_B.vontade_limiar
    fixos = [[0] * n, [C] * n]
    for v in (L - CC_B.vontade_sobe, L - CC_B.vontade_sobe + 1, L, L + 1):
        q = [0] * n
        q[0] = C // 2
        q[i_v] = v
        fixos.append(q)
    estados = [(q, [], 0) for q in fixos]
    for _ in range(16):
        q = [rng.randrange(C + 1) for _ in range(n)]
        janela = [rng.choice(ATIVIDADES) for _ in range(rng.randrange(CC_B.janela_tedio + 1))]
        estados.append((q, janela, rng.randrange(CC_B.vontade_digestao_den)))
    return estados


def banheiro() -> dict:
    rng = random.Random(SEMENTE_CASOS + 7)
    casos_b = []
    for q, janela, resto in _estados_b(rng):
        for op in _ops_b():
            c = _corpo_b(q, janela, resto)
            _aplicar_b(c, op)
            rec = c.receptores()
            casos_b.append({"q": q, "janela": janela, "resto": resto, "op": op, "q_depois": _q(c), "janela_depois": list(c.janela_tedio),
                            "resto_depois": c.resto_vontade, "receptores": [rec[r] for r in RECEPTORES_B]})
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, CC_B, com_mundo=True)
    ops, h = [], hashlib.sha256()
    tick = 0
    for _ in range(3000):
        if rng.random() < 0.75:
            op = ["passo_nec", int(rng.random() < 0.3), rng.randrange(3), tick, rng.choice((0, 0, 0, 1, 2, 5))]
            tick += 1
        else:
            op = rng.choice(_ops_b()[12:] + [["atividade", a] for a in ATIVIDADES])
        _aplicar_b(c, op)
        ops.append(op)
        h.update(json.dumps([_q(c), c.janela_tedio, c.resto_vontade], separators=(",", ":")).encode())
    return {"quimicos": list(quimicos_de(CC_B, True)), "config": {k: getattr(CC_B, k) for k in CAMPOS_E6 + CAMPOS_B},
            "receptores": list(RECEPTORES_B), "receptores_falta_invertida": ["conforto"], "casos": casos_b,
            "sequencia": {"ops": ops, "sha256": h.hexdigest(), "q_final": _q(c), "janela_final": list(c.janela_tedio),
                          "resto_final": c.resto_vontade}}


# ------------------------------------------------------------------ o metabolismo (versao 5, como o banheiro)

CC_M = CONFIG_CORPO_METABOLISMO
CC_M_FRACAO = replace(CC_M, conversao_num=2, conversao_den=3)      # so para a paridade do resto (nao e valor de pesquisa)
CAMPOS_M = ("metabolismo", "combustivel_inicial", "reserva_inicial", "conversao_num", "conversao_den", "gasto_basal_acordado",
            "gasto_basal_dormindo", "armazenar_limiar", "armazenar_taxa", "mobilizar_limiar", "mobilizar_taxa", "falta_limiar",
            "falta_cansaco")
CHAVES_M = {
    "minimo": ConfigCorpo(ligada=True, digestao=True, metabolismo=True),
    "etapa6": CC_M,
    "banheiro": replace(CONFIG_CORPO_BANHEIRO, metabolismo=True),
    "fracao": CC_M_FRACAO,
}


def _tabela_m(g: Grafo) -> dict:
    t = _tabela(g)
    t["reacoes"] = [[r.nome, list(r.consome), list(r.produz), r.taxa, [list(f) for f in r.fracoes], r.le, r.lado, r.limiar]
                    for r in g.reacoes]
    return t


def _corpo_m(q: list[int], janela: list[str], resto: int, cc: ConfigCorpo) -> Corpo:
    c = Corpo(dict(zip(quimicos_de(cc, True), q)), CONFIG_PADRAO, cc, com_mundo=True)
    c.janela_tedio = list(janela)
    c.resto_combustivel = resto
    return c


def _ops_m() -> list[list]:
    cm = CONFIG_MUNDO_LIGADA
    ops = [["passo", dormindo, 0, tick] for dormindo in (0, 1) for tick in (600, 1400)]
    ops += [["dono", "alimentar"], ["dono", "brincar"], ["pet", "brincar"], ["pet", "explorar"], ["pet", "comer"], ["pet", "ocioso"],
            ["pet_mundo", "comer"], ["andar", 0, cm.custo_energia_por_subunidade], ["andar", 37, cm.custo_energia_por_subunidade],
            ["andar", 6000, cm.custo_energia_por_subunidade], ["consumo", "racao", "madura", 0.0], ["consumo", "a", "madura", -0.1],
            ["fruta", 0.15, 0.0]]
    return ops


def _estados_m(rng: random.Random, cc: ConfigCorpo) -> list[tuple[list[int], list[str], int]]:
    C = cc.escala
    nomes = quimicos_de(cc, True)
    n = len(nomes)
    i_c, i_r, i_a = nomes.index("combustivel"), nomes.index("reserva"), nomes.index("alimento")
    estados = [([0] * n, [], 0), ([C] * n, [], 0)]
    for comb in (cc.falta_limiar - 1, cc.falta_limiar, cc.mobilizar_limiar - 1, cc.mobilizar_limiar, cc.armazenar_limiar,
                 cc.armazenar_limiar + 1, cc.armazenar_limiar + 200, C - 100):
        for res in (0, 100, C // 4, C - 50):
            q = [C // 2] * 5 + [0] * (n - 5)
            q[i_c], q[i_r], q[i_a] = comb, res, 0
            estados.append((q, [], 0))
    for _ in range(12):
        q = [rng.randrange(C + 1) for _ in range(n)]
        janela = [rng.choice(ATIVIDADES) for _ in range(rng.randrange(cc.janela_tedio + 1))]
        estados.append((q, janela, rng.randrange(cc.conversao_den)))
    return estados


def _casos_m(cc: ConfigCorpo, rng: random.Random) -> list[dict]:
    out = []
    for q, janela, resto in _estados_m(rng, cc):
        for op in _ops_m():
            c = _corpo_m(q, janela, resto, cc)
            _aplicar_e6(c, op)
            out.append({"q": q, "janela": janela, "resto": resto, "op": op, "q_depois": _q(c), "janela_depois": list(c.janela_tedio),
                        "resto_depois": c.resto_combustivel, "contas": dict(c.contas_metabolismo)})
    return out


def metabolismo() -> dict:
    rng = random.Random(SEMENTE_CASOS + 8)
    grafos_m = []
    for nome, cc in CHAVES_M.items():
        for com_mundo in (False, True):
            g = grafo_do_corpo(CONFIG_PADRAO, cc, taxas_de(CONFIG_PADRAO, cc), com_mundo)
            grafos_m.append({"chaves": nome, "com_mundo": com_mundo, "tabela": _tabela_m(g), "relato": checar(g)})
    casos_m = _casos_m(CC_M, rng)
    casos_f = _casos_m(CC_M_FRACAO, rng)
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, CC_M, com_mundo=True)
    ops, h = [], hashlib.sha256()
    tick = 0
    for _ in range(3000):
        if rng.random() < 0.8:
            op = ["passo", int(rng.random() < 0.3), rng.randrange(3), tick]
            tick += 1
        else:
            op = rng.choice(_ops_m()[4:])
        _aplicar_e6(c, op)
        ops.append(op)
        h.update(json.dumps([_q(c), c.janela_tedio, c.resto_combustivel, c.contas_metabolismo], sort_keys=True,
                            separators=(",", ":")).encode())
    return {"quimicos": list(quimicos_de(CC_M, True)), "config": {k: getattr(CC_M, k) for k in CAMPOS_M},
            "config_fracao": {"conversao_num": CC_M_FRACAO.conversao_num, "conversao_den": CC_M_FRACAO.conversao_den},
            "grafo": grafos_m, "casos": casos_m, "casos_fracao": casos_f,
            "sequencia": {"ops": ops, "sha256": h.hexdigest(), "q_final": _q(c), "janela_final": list(c.janela_tedio),
                          "resto_final": c.resto_combustivel, "contas_final": dict(c.contas_metabolismo)}}


# o fator do gasto das atividades (o no `gasto_atividades`): os pontos do passo 0 que nao sao o padrao, so para a paridade
GASTOS_M = {"metade": (1, 2), "dobro": (2, 1)}


def metabolismo_gasto() -> dict:
    """a mesma grade do metabolismo com o gasto das atividades x 1/2 e x 2, e as taxas das atividades em cada um (rng propria: a secao
    `metabolismo` nao muda)"""
    rng = random.Random(SEMENTE_CASOS + 9)
    out = {}
    for nome, (num, den) in GASTOS_M.items():
        cc = replace(CC_M, gasto_atividades_num=num, gasto_atividades_den=den)
        t = taxas_de(CONFIG_PADRAO, cc)
        out[nome] = {"gasto_atividades_num": num, "gasto_atividades_den": den,
                     "pet": {a.value: d for a, d in t.pet.items()}, "dono_brincar": t.dono[AcaoUsuario.BRINCAR],
                     "casos": _casos_m(cc, rng)}
    return out


def gabarito() -> dict:
    t = taxas_de(CONFIG_PADRAO, CC)
    taxas = {k: v for k, v in vars(t).items() if k not in ("dono", "pet")}
    taxas["dono"] = {a.value: d for a, d in t.dono.items()}
    taxas["pet"] = {a.value: d for a, d in t.pet.items()}
    return {
        "versao": 5,
        "quimicos": list(quimicos_de(CC)),
        "escala": CC.escala,
        "escala_receptor": CC.escala_receptor,
        "bits_meia_vida": CC.bits_meia_vida,
        "codificacao_ticks": "chr(ord('a') + 8 * dormindo + sujeira) do Estado no comeco do tick; o tick absoluto e o indice",
        "taxas": taxas,
        "casos": casos(CC),
        "meia_vida": meia_vida(),
        "div_arred": divisoes(),
        "vidas": [vida_malha_aberta(d, s) for d, s in VIDAS],
        "digestao": {"quimicos": list(quimicos_de(CC_DIGESTAO)), "taxa_digestao": CC_DIGESTAO.taxa_digestao,
                     "casos": casos(CC_DIGESTAO), "vidas": [vida_malha_aberta(d, s, CC_DIGESTAO) for d, s in VIDAS]},
        "digestao_lenta": {"quimicos": list(quimicos_de(CC_DIGESTAO_LENTA)), "taxa_digestao": TAXA_LENTA,
                           "casos": casos(CC_DIGESTAO_LENTA)},
        "vida": {"quimicos": list(quimicos_de(CC_VIDA)), "vida_decaimento": CC_VIDA.vida_decaimento,
                 "ticks_de_estagio": {n: list(ticks_de_estagio(e)) for n, e in DURACOES.items()},
                 "limiares": {n: list(limiares_estagio(CC_VIDA, e)) for n, e in DURACOES.items()},
                 "casos": casos_vida(), "vidas": [vida_malha_aberta(d, s, CC_VIDA) for d, s in VIDAS]},
        "mundo": {"custo_andar_por_subunidade": CONFIG_MUNDO_LIGADA.custo_energia_por_subunidade,
                  "nutricao_fruta": CONFIG_MUNDO_LIGADA.nutricao_fruta, "efeito_podre": CONFIG_MUNDO_LIGADA.efeito_podre,
                  "casos": casos(CC, _ops_do_mundo()),
                  "digestao": {"quimicos": list(quimicos_de(CC_DIGESTAO)), "casos": casos(CC_DIGESTAO, _ops_do_mundo())}},
        "etapa6": etapa6(),
        "config": asdict(ConfigCorpo()),
        "grafo": grafos(),
        "de_estado": de_estado(),
        "etapa6_mundo": etapa6_mundo(),
        "banheiro": banheiro(),
        "metabolismo": metabolismo(),
        "metabolismo_gasto": metabolismo_gasto(),
    }


def texto() -> str:
    return json.dumps(gabarito(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def main() -> None:
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(texto(), encoding="utf-8", newline="\n")
    print(f"gravado {ARQUIVO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
