"""A etapa 0 da competicao entre as regras urgentes (V3-3/V3-4; docs/TAREFA_V2_V3_COMPETICAO.md, secoes 0 e 4): a disputa SOMBRA e a
G0-R1-PODE-APRENDER.

Medicao DESCRITIVA nas vidas do E0 (o A v11, 4 donos x as sementes dos testes, 14 dias), sem run de pesquisa. Nao muda o cerebro nem o
motor: embrulha o `agir` e o `_aplicar_sinal` da PoliticaLobos durante a medida, e os embrulhos so leem e chamam o original. As vidas sao
conferidas contra o gabarito gravado antes (`tests/gabaritos/competicao_vidas_de_hoje.json`, G2).

Em cada decisao (depois do `agir` de hoje, com as tabelas daquele momento):
  1. as regras que valem, refeitas da percepcao do motivo (`medir_v3_espaco_acoes.regras_que_valem`, conferida contra o instinto), e a
     primeira tem de ser a regra registrada (falha alto);
  2. a disputa decidida (CR-3, CR-4 da V3-4): com o `sono_exaustao`, nenhuma; senao as regras urgentes que valem (todas menos o tempo
     livre); as propostas sao a uniao das acoes delas, cada acao da regra mais urgente que a propoe. Abre so com duas acoes ou mais;
  3. numa decisao aberta, o peso de cada proposta pela tabela da regra dela (`_pesos_efetivos`, so leitura): o de hoje e o de nascimento
     (o termo do prior, com o piso). A regra do instinto (a primeira) tem o peso conferido contra o do motivo;
  4. para cada kappa da grade (CR-1: o kappa multiplica as propostas da regra do instinto): a P da acao do instinto e a massa de credito
     esperada da disputa, 2 x (1 - soma P^2) x |f|, com o |f| que a decisao recebeu hoje (o embrulho do `_aplicar_sinal`); e, com um u
     sombra de uma rng propria (`derivar_semente("sombra-r1", semente)`, que nao toca a rng da politica), se a disputa mudaria a acao.
A massa de hoje e 2 x (1 - P_a*) x |f| nas decisoes com escolha (a L1: a soma de |S 1[a=a*] - P_a| / S).

O kappa (CR-2, DECIDIDA): a menor potencia de 2 da grade com que a mediana da P da acao do instinto, nos pesos de nascimento, nas decisoes
abertas, e >= 0,9. A G0-R1-PODE-APRENDER (CR-7, DECIDIDA): no kappa da CR-2, a massa nova (as decisoes abertas, com os pesos de hoje) e >= 10%
da massa de hoje. Se nao for, a tarefa para antes de tocar em `digilab/`.

    python experiments/medir_competicao_etapa0.py      # grava artifacts_v2_v3/competicao_etapa0.json
"""
from __future__ import annotations

import json
import random
import statistics
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_competicao as gc  # noqa: E402
import medir_v3_espaco_acoes as v3m  # noqa: E402

from digilab.events import AcaoPet  # noqa: E402
from digilab.policies import lobos  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

ARQUIVO = RAIZ / "artifacts_v2_v3" / "competicao_etapa0.json"
KAPPAS = (1, 2, 4, 8, 16, 32)
P_INST_MIN = 0.9                 # CR-2, DECIDIDA em 2026-10-21 (SEM FONTE)
LIMIAR_G0 = 0.10                 # CR-7, DECIDIDA em 2026-10-21 (SEM FONTE)
URGENTES = tuple(r for r in v3m.ORDEM_INSTINTO if r != "tempo_livre")
ORDEM_ACOES = tuple(a.value for a in AcaoPet)


def propostas(valem: list, p: dict) -> dict | None:
    """CR-3 e a V3-4: acao -> a regra mais urgente que a propoe, na ordem das regras e, dentro delas, na do AcaoPet; None sem disputa (o
    sono_exaustao vale, menos de duas regras urgentes, ou menos de duas acoes)"""
    if "sono_exaustao" in valem:
        return None
    urgentes = [r for r in valem if r in URGENTES]
    if len(urgentes) < 2:
        return None
    prop: dict = {}
    for r in urgentes:
        for a in sorted(v3m.candidatos_da_regra(r, p), key=ORDEM_ACOES.index):
            prop.setdefault(a, r)
    return prop if len(prop) >= 2 else None


def _ps(pesos: list[float]) -> list[float]:
    total = 0.0
    for w in pesos:
        total = total + w
    return [w / total for w in pesos]


class _Estado:
    def __init__(self, semente: int) -> None:
        self.decisoes: list[dict] = []
        self.registros: dict = {}           # id(registro) -> (k, registro); a referencia impede o id de ser reusado
        self.f_abs: Counter = Counter()
        self.rng = random.Random(derivar_semente("sombra-r1", semente))


_ESTADOS: list = []


def _instalar(semente: int) -> dict:
    orig = {"agir": lobos.PoliticaLobos.agir, "_aplicar_sinal": lobos.PoliticaLobos._aplicar_sinal}

    def estado(cerebro) -> _Estado:
        s = cerebro.__dict__.get("_sombra_r1")
        if s is None:
            s = _Estado(semente)
            cerebro.__dict__["_sombra_r1"] = s
            _ESTADOS.append(s)
        return s

    def agir(self, obs, rng):
        acao = orig["agir"](self, obs, rng)
        s = estado(self)
        k = len(self.motivos) - 1
        m, reg = self.motivos[-1], self._registro_decisao
        if reg is None:
            raise RuntimeError("sombra: decisao sem registro (o v11 aprende)")
        s.registros[id(reg)] = (k, reg)
        p = m["percepcao"]
        valem = v3m.regras_que_valem(p)
        if valem[0] != m["regra"]:
            raise RuntimeError(f"sombra: as regras refeitas ({valem}) nao dao a regra registrada {m['regra']!r}")
        S = self._escala
        d = {"k": k, "regra": m["regra"], "n_cand": len(m["candidatos"]), "acao": m["acao"],
             "p_escolhida": reg["P"][reg["acao"]] / S, "aberta": False}
        prop = propostas(valem, p)
        if prop is not None:
            a_inst = m["acao"]
            r0 = m["regra"]
            if prop.get(a_inst) != r0 or len(m["candidatos"]) != 1:
                raise RuntimeError(f"sombra: a acao do instinto {a_inst} nao e a proposta unica da regra {r0}")
            x = self.percepcao(obs)
            hoje, nasc = {}, {}
            for r in sorted(set(prop.values()), key=URGENTES.index):
                cands = tuple(AcaoPet(a) for a in prop if prop[a] == r)
                c, w = self._pesos_efetivos(r, cands, x)
                for a in cands:
                    hoje[a.value] = w[a]
                    base = c["impulsos"][a] + c["memoria_emocao"][a]
                    nasc[a.value] = base if base >= self._piso else self._piso
            if hoje[a_inst] != m["pesos"][a_inst]:
                raise RuntimeError("sombra: o peso refeito da regra do instinto nao e o do motivo")
            ordem = list(prop)
            u = s.rng.random()
            por_kappa = {}
            for kappa in KAPPAS:
                linha = {}
                for nome, w in (("hoje", hoje), ("nascimento", nasc)):
                    q = [(kappa * w[a] if prop[a] == r0 else w[a]) for a in ordem]
                    P = _ps(q)
                    linha[nome] = {"p_inst": P[ordem.index(a_inst)], "soma_p2": sum(pi * pi for pi in P),
                                   "mudaria": ordem[lobos.sortear(q, u)] != a_inst}
                por_kappa[str(kappa)] = linha
            d.update({"aberta": True, "regras": sorted(set(prop.values()), key=URGENTES.index), "propostas": prop,
                      "pesos_hoje": hoje, "pesos_nascimento": nasc, "por_kappa": por_kappa})
        s.decisoes.append(d)
        return acao

    def _aplicar_sinal(self, registro, f_S, consequencia=False, alvos=None):
        s = estado(self)
        alvo = s.registros.get(id(registro))
        if alvo is None or alvo[1] is not registro:
            raise RuntimeError("sombra: credito para um registro que nao e de nenhuma decisao vista")
        s.f_abs[alvo[0]] += abs(f_S)
        return orig["_aplicar_sinal"](self, registro, f_S, consequencia, alvos)

    lobos.PoliticaLobos.agir = agir
    lobos.PoliticaLobos._aplicar_sinal = _aplicar_sinal
    return orig


def _desinstalar(orig: dict) -> None:
    lobos.PoliticaLobos.agir = orig["agir"]
    lobos.PoliticaLobos._aplicar_sinal = orig["_aplicar_sinal"]


def vida(args: tuple) -> dict:
    dono, semente = args
    _ESTADOS.clear()
    b = gc.bancada()
    orig = _instalar(semente)
    try:
        v = b.vida(gc.espec(dono, semente))
    finally:
        _desinstalar(orig)
    chave = f"v11|{dono}|{semente}"
    if gc.impressao(v.motor) != json.loads(gc.ARQUIVO.read_text(encoding="utf-8"))[chave]:
        raise RuntimeError(f"G2: a vida {chave} com a sombra nao e a do gabarito")
    if not _ESTADOS:
        raise RuntimeError(f"{chave}: nenhuma decisao vista")
    resumos = [(s.decisoes, dict(s.f_abs)) for s in _ESTADOS]
    if any(r != resumos[0] for r in resumos[1:]):
        raise RuntimeError(f"{chave}: a sombra da vida e a dos replays divergem")
    s = _ESTADOS[0]
    if len(s.decisoes) != len(v.motor.politica.motivos):
        raise RuntimeError(f"{chave}: {len(s.decisoes)} decisoes na sombra, {len(v.motor.politica.motivos)} no cerebro")
    for d in s.decisoes:
        d["f_abs"] = s.f_abs.get(d["k"], 0)
    return {"dono": dono, "semente": semente, "decisoes": s.decisoes}


def _mediana(xs: list):
    return statistics.median(xs) if xs else None


def resumir(decs: list[dict]) -> dict:
    n = len(decs)
    forcadas = [d for d in decs if d["n_cand"] == 1]
    abertas = [d for d in decs if d["aberta"]]
    f_total = sum(d["f_abs"] for d in decs)
    f_forcadas = sum(d["f_abs"] for d in forcadas)
    massa_hoje = sum(2 * (1 - d["p_escolhida"]) * d["f_abs"] for d in decs if d["n_cand"] > 1)
    out = {"decisoes": n, "frac_forcadas": len(forcadas) / n, "frac_abertas": len(abertas) / n,
           "frac_das_forcadas_que_abrem": len(abertas) / len(forcadas) if forcadas else None,
           "frac_forcadas_depois_da_abertura": (len(forcadas) - len(abertas)) / n,
           "abs_f": {"total": f_total, "forcadas": f_forcadas, "nas_abertas": sum(d["f_abs"] for d in abertas),
                     "frac_das_forcadas_nas_abertas": (sum(d["f_abs"] for d in abertas) / f_forcadas) if f_forcadas else None},
           "massa_hoje": massa_hoje, "por_kappa": {}}
    for kappa in KAPPAS:
        kk = str(kappa)
        linha = {}
        for nome in ("hoje", "nascimento"):
            nova = sum(2 * (1 - d["por_kappa"][kk][nome]["soma_p2"]) * d["f_abs"] for d in abertas)
            linha[nome] = {"mediana_p_inst": _mediana([d["por_kappa"][kk][nome]["p_inst"] for d in abertas]),
                           "massa_nova": nova, "massa_nova_sobre_hoje": nova / massa_hoje if massa_hoje else None,
                           "frac_abertas_que_mudariam": (sum(d["por_kappa"][kk][nome]["mudaria"] for d in abertas) / len(abertas))
                           if abertas else None}
        out["por_kappa"][kk] = linha
    return out


def analisar(vidas: list[dict]) -> dict:
    todas = [d for v in vidas for d in v["decisoes"]]
    geral = resumir(todas)
    kappa = next((k for k in KAPPAS if geral["por_kappa"][str(k)]["nascimento"]["mediana_p_inst"] is not None
                  and geral["por_kappa"][str(k)]["nascimento"]["mediana_p_inst"] >= P_INST_MIN), None)
    razao = None if kappa is None else geral["por_kappa"][str(kappa)]["hoje"]["massa_nova_sobre_hoje"]
    combos = Counter(tuple(d["regras"]) for d in todas if d["aberta"])
    return {"geral": geral,
            "kappa_cr2": kappa,
            "g0_r1_pode_aprender": {"limiar": LIMIAR_G0, "kappa": kappa, "massa_nova_sobre_hoje": razao,
                                    "passa": None if razao is None else razao >= LIMIAR_G0},
            "por_dono": {dono: resumir([d for v in vidas if v["dono"] == dono for d in v["decisoes"]]) for dono in gc.DONOS},
            "abertas_por_regras": {"+".join(c): n for c, n in sorted(combos.items(), key=lambda t: (-t[1], t[0]))}}


def main() -> dict:
    with ProcessPoolExecutor() as ex:
        vidas = list(ex.map(vida, [(d, s) for d in gc.DONOS for s in gc.SEMENTES]))
    out = {"versao": 1, "braco": "P1-c-tapa (v11)", "dias": gc.DIAS, "orcamento": gc.ORCAMENTO, "donos": list(gc.DONOS),
           "sementes": list(gc.SEMENTES), "kappas": list(KAPPAS), "p_inst_min": P_INST_MIN, "analise": analisar(vidas)}
    ARQUIVO.parent.mkdir(exist_ok=True)
    ARQUIVO.write_text(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return out


if __name__ == "__main__":
    r = main()["analise"]
    print(json.dumps({k: r[k] for k in ("kappa_cr2", "g0_r1_pode_aprender", "abertas_por_regras")}, indent=1, ensure_ascii=False))
    print(json.dumps(r["geral"], indent=1, ensure_ascii=False))
