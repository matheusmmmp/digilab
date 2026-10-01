"""Gabarito de paridade Python x web do vinculo (de hoje e da variante B; docs/PLANO_ANALISE_V2_VINCULO.md, secao 2).

Uma sequencia FIXA de chamadas ao Vinculo (decisao do pet com observacao e desejo; acao do dono; ajuste direto; amostra
de pausa; teto da sombria), sorteada de uma rng propria com semente fixa, passada por digilab/vinculo.py duas vezes: com
a ConfigVinculoSituacao desligada (o vinculo de hoje, pets v2-v9) e ligada (a variante B, pets v10). Grava o valor
depois de cada chamada e o estado final. O teste web (web/app/test/vinculo.test.ts) reproduz tudo em motor/vinculo.ts
e exige diferenca <= 1e-12.

So le digilab/: nada no pacote muda.

uso: python experiments/exportar_gabarito_vinculo.py [saida.json]
"""
from __future__ import annotations

import dataclasses
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_PADRAO, CONFIG_VINCULO, CONFIG_VINCULO_B_LIGADA, CONFIG_VINCULO_SITUACAO, TICKS_POR_DIA  # noqa: E402
from digilab.desejo import Desejo  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.policy import Observacao  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.vinculo import Vinculo  # noqa: E402

SAIDA = RAIZ / "web" / "app" / "test" / "gabaritos" / "vinculo_python.json"
SEMENTE = 20261001
N_PASSOS = 1500
ACOES_PET = [a.value for a in AcaoPet]
CUIDADOS = ["alimentar", "limpar", "brincar", "acariciar", "petisco", "levar_ao_banheiro", "tratar_lesao"]
FEEDBACK = ["elogiar", "repreender"]
VONTADES = ["comer", "brincar", "chamar_atencao", "explorar", "dormir"]


def sortear_ops(semente: int = SEMENTE, n: int = N_PASSOS) -> list[dict]:
    """as chamadas, independentes de qualquer motor: ticks de 15 em 15 (as vezes pulos), observacoes plausiveis com a
    hora coerente com o tick (a noite da situacao), desejo que muda de vez em quando, acoes do dono em rajadas"""
    rng = random.Random(derivar_semente("gabarito-vinculo", semente))
    ops: list[dict] = []
    tick, ref, acao_pet = 480, 0, None
    desejo = None
    for k in range(n):
        tick += 15 if rng.random() < 0.85 else 15 * rng.randrange(2, 40)
        hora = (tick % TICKS_POR_DIA) / TICKS_POR_DIA
        # fome e higiene com fases: o pet passa tempo em falta (situacao "1xx") e tempo cuidado
        base = 0.2 if (k // 60) % 3 == 0 else 0.75
        obs = [min(1.0, max(0.0, round(base + rng.uniform(-0.3, 0.3), 4))), min(1.0, max(0.0, round(base + rng.uniform(-0.3, 0.3), 4))),
               round(rng.random(), 4), round(rng.random(), 4), round(rng.uniform(0.5, 1.0), 4), rng.randrange(0, 6) / 5.0,
               1.0 if rng.random() < 0.3 else 0.0, hora]
        acao_pet = rng.choice(ACOES_PET)
        if rng.random() < 0.25:
            desejo = None if rng.random() < 0.4 else {"tipo": "vontade" if rng.random() < 0.8 else "necessidade",
                                                        "alvo": rng.choice(VONTADES), "tick": tick, "intensidade": round(rng.uniform(0.1, 1.0), 3)}
            ops.append({"op": "decisao", "tick": tick, "obs": obs, "acao": acao_pet, "desejo": desejo})
        else:
            ops.append({"op": "decisao", "tick": tick, "obs": obs, "acao": acao_pet, "desejo": None})
        if rng.random() < 0.55:
            for _ in range(rng.randrange(1, 4)):
                a = rng.choice(CUIDADOS) if rng.random() < 0.6 else rng.choice(FEEDBACK)
                ops.append({"op": "dono", "tick": tick, "acao": a, "acao_pet": acao_pet, "ref": ref})
                ref += 1
        if rng.random() < 0.03:
            ops.append({"op": "ajustar", "tick": tick, "componente": "forcar", "delta": -0.05, "ref": ref})
            ref += 1
        if rng.random() < 0.04:
            ops.append({"op": "amostra", "tick": tick, "componente": "pausa", "amostra": 1.0 if rng.random() < 0.7 else 0.0, "peso": 1.0})
        if k == int(n * 0.7):
            ops.append({"op": "limitar", "tick": tick, "teto": 0.6})
    return ops


def aplicar(ops: list[dict], ligada: bool) -> dict:
    v = Vinculo(CONFIG_VINCULO, CONFIG_VINCULO_B_LIGADA if ligada else CONFIG_VINCULO_SITUACAO)
    valores = []
    for o in ops:
        if o["op"] == "decisao":
            obs = Observacao(vetor_estado=tuple(o["obs"]), ticks_desde_cuidado=0, total_cuidados=0)
            d = o["desejo"]
            v.decisao(obs, AcaoPet(o["acao"]), o["tick"], Desejo(d["tick"], d["tipo"], d["alvo"], d["intensidade"]) if d else None)
        elif o["op"] == "dono":
            v.acao_dono(AcaoUsuario(o["acao"]), o["tick"], AcaoPet(o["acao_pet"]) if o["acao_pet"] else None, o["ref"])
        elif o["op"] == "ajustar":
            v.ajustar(o["tick"], o["componente"], o["delta"], o["ref"])
        elif o["op"] == "amostra":
            v._amostra(o["tick"], o["componente"], o["amostra"], o["peso"], None)
        elif o["op"] == "limitar":
            v.limitar(o["tick"], o["teto"], "sombria")
        else:
            raise ValueError(o["op"])
        valores.append(v.valor)
    comp = {}
    for _, _, c, _ in v.serie:
        comp[c] = comp.get(c, 0) + 1
    return {"valores": valores, "final": {"valor": v.valor, "pedidos_pendentes": list(v.pedidos),
                                          "vontades_pendentes": [[t, a.value] for t, a in v.vontades],
                                          "chaves_feedback": sorted(v.feedbacks), "n_amostras_por_componente": comp,
                                          "ultimo_ref_baixa": v.ultimo_ref_baixa, "teto": v.teto,
                                          "situacao_atual": v.situacao_atual}}


def gerar(semente: int = SEMENTE, n: int = N_PASSOS) -> dict:
    ops = sortear_ops(semente, n)
    return {"descricao": __doc__.splitlines()[0], "semente": semente, "n_ops": len(ops),
            "config": {"vinculo": dataclasses.asdict(CONFIG_VINCULO),
                       "situacao": {**dataclasses.asdict(CONFIG_VINCULO_B_LIGADA),
                                    "noite": [CONFIG_PADRAO.inicio_noite_tick, CONFIG_PADRAO.fim_noite_tick], "ticks_por_dia": TICKS_POR_DIA}},
            "ops": ops, "hoje": aplicar(ops, False), "b": aplicar(ops, True)}


def main(argv=None) -> int:
    saida = Path(argv[0]) if argv else SAIDA
    g = gerar()
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(g, ensure_ascii=False, indent=0, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{saida}: {g['n_ops']} chamadas; hoje {g['hoje']['final']['valor']:.6f} ({g['hoje']['final']['n_amostras_por_componente']}); "
          f"B {g['b']['final']['valor']:.6f} ({g['b']['final']['n_amostras_por_componente']}; {len(g['b']['final']['chaves_feedback'])} chaves)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
