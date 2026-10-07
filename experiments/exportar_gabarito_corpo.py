"""Gabarito da quimica do corpo para a paridade Python x TS (G-PAR; docs/TAREFA_V2_CORPO_DRIVES.md, secao 12 e etapa 7 da secao 14).

So inteiros: a paridade e exata. O TS (etapa 7, do A) refaz cada caso e cada vida e confere igual, ate o sha256.

    python experiments/exportar_gabarito_corpo.py      # grava tests/gabaritos/corpo_quimica_python.json

O conteudo (versao 3):
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
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_DURACOES, CONFIG_EVOLUCAO_PESQUISA, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigCorpo  # noqa: E402
from digilab.corpo import (Corpo, div_arred, limiares_estagio, passo_meia_vida, quimicos_de, taxas_de,  # noqa: E402
                           ticks_de_estagio)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
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
    ops += [["dono", a.value] for a in ACOES_DONO] + [["pet", a.value] for a in AcaoPet]
    return ops + [["bola", 0.15], ["fruta", 0.10, -0.10], ["fruta", 0.10, 0.10], ["fruta", 0.10, 0.0]]


def _ops_do_mundo() -> list[list]:
    """os estimulos do mundo fisico (versao 3): a MF-2, o andar e as comidas do mapa, com os numeros da ConfigMundo"""
    cm = CONFIG_MUNDO_LIGADA
    ops = [["pet_mundo", a.value] for a in AcaoPet]
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


def gabarito() -> dict:
    t = taxas_de(CONFIG_PADRAO, CC)
    taxas = {k: v for k, v in vars(t).items() if k not in ("dono", "pet")}
    taxas["dono"] = {a.value: d for a, d in t.dono.items()}
    taxas["pet"] = {a.value: d for a, d in t.pet.items()}
    return {
        "versao": 3,
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
    }


def texto() -> str:
    return json.dumps(gabarito(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def main() -> None:
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(texto(), encoding="utf-8", newline="\n")
    print(f"gravado {ARQUIVO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
