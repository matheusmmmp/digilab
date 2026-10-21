"""A etapa 0 do credito por canal (docs/TAREFA_V2_V3_CREDITO_CANAL.md, secao 5): o gabarito das vidas de hoje (G2), gravado antes da
medicao das tabelas sombra."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import gabarito_credito_canal as gc  # noqa: E402

from digilab.policies.lobos import atualizar_fruta  # noqa: E402


def test_as_vidas_de_hoje_sao_as_do_gabarito():
    """G2: as vidas do T1 do J5 (P1 e P1-plan, sementes dos testes) saem iguais ao gabarito gravado antes da etapa 0"""
    gravado = json.loads(gc.ARQUIVO.read_text(encoding="utf-8"))
    assert gc.gerar() == gravado


def _sorteios(rng, n, classes, S):
    for _ in range(n):
        p = [rng.randrange(1, S) for _ in classes]
        tot = sum(p)
        P = {c: v * S // tot for c, v in zip(classes, p)}
        sub = {"candidatos": tuple(classes), "acao": rng.choice(classes), "X": {c: S for c in classes}, "P": P,
               "W": {c: rng.randrange(S // 2, 4 * S) for c in classes}}
        canais = {"fome": rng.randrange(-900, 900), "energia": rng.randrange(-300, 300), "humor": rng.randrange(-900, 900),
                  "gosto": rng.randrange(-300, 900)}
        yield sub, canais


def test_os_grupos_somam_o_escalar_sem_teto_e_divergem_com_ele():
    """a secao 0 da tarefa, com sinais sinteticos: pela regra da L1 (linear no sinal), os grupos sem corte somam a tabela escalar a menos
    de uma unidade por grupo e por credito; com um teto que se atinge, a soma dos grupos (a C1) e outra coisa"""
    import random
    import medir_credito_canal_etapa0 as m
    S, passo, classes = 1024, 512, ["comida:a", "comida:b", "comida:racao"]
    n = 400
    dif, andou = {}, {}
    for teto in (1 << 40, S // 4):
        rng = random.Random(11)
        esc, prior = {c: 64 for c in classes}, {c: 64 for c in classes}
        zero = {c: 0 for c in classes}
        gr = {"humor": dict(zero), "gosto": dict(zero), "nutricao": dict(prior)}
        pg = {"humor": zero, "gosto": zero, "nutricao": prior}
        for sub, canais in _sorteios(rng, n, classes, S):
            f_g = {g: 0 for g in m.GRUPOS}
            for c, f in canais.items():
                f_g[m.grupo_do_canal(c)] += f
            atualizar_fruta(esc, prior, sub, sum(canais.values()), passo, teto, S)
            for g in m.GRUPOS:
                atualizar_fruta(gr[g], pg[g], sub, f_g[g], passo, teto, S)
        dif[teto] = max(abs(sum(gr[g][c] for g in m.GRUPOS) - esc[c]) for c in classes)
        andou[teto] = max(abs(esc[c] - 64) for c in classes)
    sem, com = 1 << 40, S // 4
    assert dif[sem] <= n * len(m.GRUPOS)                  # o limite do arredondamento
    assert dif[sem] * 10 < andou[sem]                     # e pequeno perto do que a tabela andou
    assert dif[com] > 10 * dif[sem]                       # com o teto atingido, o teto por grupo muda o peso


def test_o_artefato_se_refaz_igual():
    """a etapa 0: as sombras nao mudam a vida (o G2 e conferido dentro da medida, falha alto), e o artefato se refaz igual"""
    import medir_credito_canal_etapa0 as m
    gravado = json.loads(m.ARQUIVO.read_text(encoding="utf-8"))
    m.main()
    assert json.loads(m.ARQUIVO.read_text(encoding="utf-8")) == gravado
    a = gravado["analise"]
    assert a["linearidade"]["dentro_do_arredondamento"]
    assert a["cl"]["teto"] == 16384                                        # o ponto T3 do J5: 16 S
    assert all(v == 0 for v in a["cortes_no_teto"].values())               # nenhum peso de comer chega ao teto
    assert a["g0_pode_mudar"]["passa"] is False                            # a C1 nao tem o que mudar nestas vidas
