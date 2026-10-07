"""Gabarito da quimica do corpo para a paridade Python x TS (G-PAR; docs/TAREFA_V2_CORPO_DRIVES.md, secao 12 e etapa 7 da secao 14).

So inteiros: a paridade e exata. O TS (etapa 7, do A) refaz cada caso e cada vida e confere igual, ate o sha256.

    python experiments/exportar_gabarito_corpo.py      # grava tests/gabaritos/corpo_quimica_python.json

O conteudo:
- `taxas`: os numeros de hoje na escala C, ja inteiros (secao 4);
- `casos`: uma grade de estados com cada operacao (o tick, as acoes do dono e do pet, a bola, a fruta), o estado depois, o receptor de
  privacao e os receptores na escala S;
- `meia_vida` e `div_arred`: os passos inteiros da secao 3;
- `vidas`: 3 vidas de hoje em malha aberta (as acoes do pet e do dono forcadas, a sujeira e o sono lidos do Estado de hoje). A entrada de
  cada tick e um caractere (sono e sujeira), os eventos vao antes do tick em que acontecem, e o sha256 cobre q depois de cada operacao.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_PADRAO, ConfigCorpo  # noqa: E402
from digilab.corpo import QUIMICOS, Corpo, div_arred, passo_meia_vida, taxas_de  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.policy import PoliticaInstinto, efeito_da_acao_do_pet  # noqa: E402
from digilab.state import Estado, aplicar_acao_usuario, avancar_um_tick  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "corpo_quimica_python.json"
CC = ConfigCorpo(ligada=True)
SEMENTE_CASOS = 20261007                 # so para sortear a grade de estados do gabarito (nao e semente de vida)
VIDAS = (("aleatorio", 101), ("relapso", 303), ("atencioso", 202))   # sementes dos testes
DIAS = 3
ORCAMENTO = 48
ACOES_DONO = (AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR, AcaoUsuario.ACARICIAR, AcaoUsuario.ELOGIAR,
              AcaoUsuario.REPREENDER)


def _q(corpo: Corpo) -> list[int]:
    return [corpo.q[n] for n in QUIMICOS]


def _corpo(q: list[int]) -> Corpo:
    return Corpo(dict(zip(QUIMICOS, q)), CONFIG_PADRAO, CC)


def _estados(rng: random.Random) -> list[list[int]]:
    C = CC.escala
    t = taxas_de(CONFIG_PADRAO, CC)
    fixos = [[0] * 5, [C] * 5, [t.limiar_privacao, 0, 0, 0, 0], [t.limiar_privacao + 1, 0, 0, 0, 0],
             [0, t.limiar_privacao, 0, 0, C], [0, 0, t.limiar_privacao + 1, 0, 1], [90000, 0, 45000, 135000, 0]]
    return fixos + [[rng.randrange(C + 1) for _ in range(5)] for _ in range(25)]


def casos() -> list[dict]:
    rng = random.Random(SEMENTE_CASOS)
    out = []
    for q in _estados(rng):
        ops = [["passo", dormindo, sujeira, tick] for dormindo in (0, 1) for sujeira in (0, 3) for tick in (600, 1400)]
        ops += [["dono", a.value] for a in ACOES_DONO] + [["pet", a.value] for a in AcaoPet]
        ops += [["bola", 0.15], ["fruta", 0.10, -0.10], ["fruta", 0.10, 0.10], ["fruta", 0.10, 0.0]]
        for op in ops:
            c = _corpo(q)
            if op[0] == "passo":
                c.passo(Estado(tick=op[3], dormindo=bool(op[1]), sujeira=op[2]))
            elif op[0] == "dono":
                c.acao_dono(AcaoUsuario(op[1]))
            elif op[0] == "pet":
                c.acao_pet(AcaoPet(op[1]))
            elif op[0] == "bola":
                c.estimulo_bola(op[1])
            else:
                c.estimulo_fruta(op[1], op[2])
            rec = c.receptores()
            out.append({"q": q, "op": op, "q_depois": _q(c), "privacao": c.em_privacao(),
                        "receptores": [rec[d] for d in ("fome", "higiene", "energia", "humor", "saude")]})
    return out


def meia_vida() -> list[list[int]]:
    ks = (CC.k_meia_vida_susto, CC.k_meia_vida_dor, CC.k_meia_vida_estresse)
    qs = (0, 1, 2, 100, 1023, 1024, 65535, 65536, 225000, CC.escala)
    return [[q, k, passo_meia_vida(q, k, CC.bits_meia_vida)] for k in ks for q in qs]


def divisoes() -> list[list[int]]:
    pares = [(n, d) for n in (-7, -5, -3, -1, 0, 1, 3, 5, 7, 450000 * 1024 - 1, 337500 * 1024) for d in (2, 3, 450000)]
    return [[n, d, div_arred(n, d)] for n, d in pares]


def vida_malha_aberta(dono: str, semente: int) -> dict:
    """Uma vida de hoje rejogada em malha aberta, com o corpo ao lado. Devolve a entrada que o TS precisa e o que conferir."""
    cfg = CONFIG_PADRAO
    motor = simular_vida(dono, criar_dono(dono), PoliticaInstinto(cfg), semente, DIAS, ORCAMENTO).motor
    acoes_pet = dict(motor._acoes_pet)
    rng = random.Random(semente)               # a rng de ambiente do motor (engine.Motor: random.Random(semente))
    e = Estado()
    c = Corpo.de_estado(e, cfg, CC)
    q0 = _q(c)
    ticks, eventos, pontos = [], [], []
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
    return {"dono": dono, "semente": semente, "q_inicial": q0, "tick_inicial": 0, "ticks": "".join(ticks), "eventos": eventos,
            "pontos": pontos, "q_final": _q(c), "sha256": h.hexdigest()}


def gabarito() -> dict:
    t = taxas_de(CONFIG_PADRAO, CC)
    taxas = {k: v for k, v in vars(t).items() if k not in ("dono", "pet")}
    taxas["dono"] = {a.value: d for a, d in t.dono.items()}
    taxas["pet"] = {a.value: d for a, d in t.pet.items()}
    return {
        "versao": 1,
        "quimicos": list(QUIMICOS),
        "escala": CC.escala,
        "escala_receptor": CC.escala_receptor,
        "bits_meia_vida": CC.bits_meia_vida,
        "codificacao_ticks": "chr(ord('a') + 8 * dormindo + sujeira) do Estado no comeco do tick; o tick absoluto e o indice",
        "taxas": taxas,
        "casos": casos(),
        "meia_vida": meia_vida(),
        "div_arred": divisoes(),
        "vidas": [vida_malha_aberta(d, s) for d, s in VIDAS],
    }


def texto() -> str:
    return json.dumps(gabarito(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def main() -> None:
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(texto(), encoding="utf-8", newline="\n")
    print(f"gravado {ARQUIVO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
