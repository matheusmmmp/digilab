"""Gabaritos da voz propria para o jogo web (DESIGN_VOZ_PROPRIA, parte 4): o motor/historia.ts e a mentira do
motor.ts (pets v5) conferidos contra o Python.

    python experiments/exportar_gabaritos_voz.py      -> web/app/test/gabaritos/voz_python.json

historia: registros reais (artifacts_voz/rodada1/pets.jsonl, cortados em tres momentos) e os fatos que
  digilab/historia.py extrai, a selecao para uma fala (com e sem citados recentes) e 5 assuntos em rodizio.
mentira: uma grade de (sombria, sobrecarga, disciplina, impunes, acertos) -> honestidade, chance e a mostrada, e a
  tabela de desfechos da janela de fala (mentira ou verdade x bronca, petisco, elogio, prazo vencido).
Os numeros aleatorios do Python e da web sao outros (MT x mulberry32): a paridade e das regras, nao das vidas.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_EDUCACAO_LIGADA, CONFIG_MENTIRA_LIGADA  # noqa: E402
from digilab.educacao import fabricas_educacao  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.historia import RegistroVida, escolher_assunto, extrair, selecionar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

SAIDA = RAIZ / "web" / "app" / "test" / "gabaritos" / "voz_python.json"
PETS = RAIZ / "artifacts_voz" / "rodada1" / "pets.jsonl"
N_PETS = 8
CORTES = (3 * 1440, 8 * 1440, None)


def _reg(d: dict) -> RegistroVida:
    return RegistroVida(**{k: (tuple(tuple(x) if isinstance(x, list) else x for x in v) if isinstance(v, list) else v)
                           for k, v in d.items()})


def _para_ts(r: RegistroVida) -> dict:
    """nomes do TS (camelCase); janelas so com o que o extrator le"""
    return {"tickFinal": r.tick_final, "acoesDono": [list(x) for x in r.acoes_dono], "acoesPet": [list(x) for x in r.acoes_pet],
            "janelas": [{k: j[k] for k in ("tipo", "falso", "desfecho", "inicio", "fim")} for j in r.janelas],
            "sessoesTreino": [list(x) for x in r.sessoes_treino],
            "lutas": [{k: x[k] for k in ("tick", "rival", "resultado", "lesao")} for x in r.lutas],
            "evolucoes": [list(x) for x in r.evolucoes], "sombriaTick": r.sombria_tick,
            "filhoDeCruzamento": r.filho_de_cruzamento, "desvioPorAcao": [list(x) for x in r.desvio_por_acao]}


def historia() -> list[dict]:
    pets = [json.loads(x) for x in PETS.read_text(encoding="utf-8").splitlines() if x.strip()]
    casos = []
    for p in [p for p in pets if not p["morta"]][:N_PETS]:
        for corte in CORTES:
            r = _reg(p["registro"])
            if corte is not None:
                r = r.ate(corte)
            fatos = extrair(r)
            citados = [[f.chave] for f in fatos[:2]]
            dados: list[list[str]] = []
            for _ in range(5):
                a = escolher_assunto(fatos, dados)
                dados.append([] if a is None else [a.chave])
            casos.append({"pet": f"{p['braco']}@{p['ovo']}", "corte": corte, "registro": _para_ts(r),
                          "fatos": [f.para_dict() for f in fatos],
                          "selecao": [f.chave for f in selecionar(fatos)],
                          "citados": citados, "selecao_com_citados": [f.chave for f in selecionar(fatos, citados)],
                          "assuntos": dados})
    return casos


def _motor():
    fp, fm = fabricas_educacao(4242, "brasa", NEUTRO, ce=CONFIG_EDUCACAO_LIGADA, cm=CONFIG_MENTIRA_LIGADA)
    m = fm(fp(None), None, 4242)
    m.avancar(200)
    return m


def mentira() -> dict:
    grade = []
    for sombria in (False, True):
        for sobre in (0.0, 30.0, 80.0, 100.0):
            for disc in (0, 50, 100):
                for impunes in (0, 3, 20):
                    for acertos in (0, 3):
                        m = _motor()
                        m.sombria, m.treino.sobrecarga, m.disciplina = sombria, sobre, disc
                        m.mentiras_impunes, m.acertos_mentira = impunes, acertos
                        grade.append({"sombria": sombria, "sobrecarga": sobre, "disciplina": disc, "impunes": impunes,
                                      "acertos": acertos, "h": m.honestidade(), "p": m.chance_mentira(),
                                      "mostrada": m.honestidade_mostrada()})
    desfechos = []
    acoes = {"bronca": AcaoUsuario.REPREENDER, "petisco": AcaoUsuario.PETISCO, "elogio": AcaoUsuario.ELOGIAR,
             "carinho": AcaoUsuario.ACARICIAR, "prazo": None}
    for falso in (True, False):
        for nome, acao in acoes.items():
            m = _motor()
            m.disciplina, m.mentiras_impunes, m.acertos_mentira = 25, 1, 1
            t = m.estado()["tick"]
            m.janela = {"tipo": "fala", "pedido": "estado", "inicio": t, "prazo": t + 30, "falso": falso,
                        "contradiz_barras": falso, "gatilho": "teste", "honestidade": .5, "chance": .5}
            if acao is None:
                m.avancar(40)
                m.observar(AcaoUsuario.ACARICIAR)
            else:
                m.observar(acao)
            desfechos.append({"falso": falso, "acao": nome, "aberta": m.janela is not None,
                              "desfecho": m.historico_falas[-1]["desfecho"] if m.historico_falas else None,
                              "disciplina": m.disciplina, "impunes": m.mentiras_impunes, "acertos": m.acertos_mentira,
                              "bronca_injusta": m.contagem_mentira["broncas_injustas"]})
    return {"grade": grade, "desfechos": desfechos}


def main() -> int:
    d = {"versao": 1, "nota": __doc__.splitlines()[0], "historia": historia(), "mentira": mentira()}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{SAIDA}: {len(d['historia'])} casos de historia, {len(d['mentira']['grade'])} de mentira")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
