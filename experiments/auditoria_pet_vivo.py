"""A auditoria da escolha (0b) e a medida de "age pelo estado" (0c) da PET_VIVO (docs/PLANO_ANALISE_V3_PET_VIVO.md; APROVADO em 2026-11-08,
repassado pelo Gerente da V3, D-PV0-7). So leitura: nenhuma vida nova, nenhuma semente, nenhuma faixa. O motor, o `engine.py`, o corpo e os
cerebros nao mudam: a leitura de cada decisao entra embrulhando, na instancia do cerebro, o `Impulso.unidades` (como o coletor da D-C1-3
embrulha o `agir`), e as contas refeitas sao puras, sobre copias rasas das entradas da decisao.

As duas fontes (secao 2, PV-0-2 a PV-0-4):
  - **a C4** (o REL e o SEM nas 12 celulas, 4 800 vidas): os logs do `vidas.tar.gz` da pasta da run (`--pasta-c4`, so lida), rejogados com o
    codigo do `a287ba2` numa worktree destacada (`--codigo`). Os processos desse replay importam o `digilab` do `a287ba2`; as contas do
    `digilab/metrics.py` de hoje entram neles pelo pacote `digilab_hoje` (o mesmo diretorio `digilab/` desta arvore, sob outro nome, para os
    dois pacotes nao colidirem);
  - **a AN0** (os gabaritos da LM0 e as duas vidas dos fins com os inatos de hoje): as vidas refeitas no codigo de hoje (as sementes dos
    testes), conferidas contra o gabarito decisao a decisao.

As conferencias que falham alto (secao 2.3): o codigo da C4 (os sha256 do `meta.json`, pela `conferir_codigo` da D-C1-3), a fonte (os
sha256 da pasta e dos gabaritos), o G1 de cada vida (o log, as medidas da C4 ou o motivo do gabarito iguais) e o G1 com o contrafactual
ligado (a mesma vida sai igual com e sem ele: a C4 pela conferencia das medidas, que roda com ele ligado; a AN0 pelo gabarito, idem).

O contrafactual A-4 (secao 4.4, PV-0-5 e PV-0-6) roda so na subamostra (os k de 0 a 7 de cada base da C4, e toda a AN0), com Delta = S/4
na falta de cada receptor presente, e cinco variantes por receptor: `todo` (tudo o que sai da falta refeito), `z` (so a urgencia no z),
`incentivo` (so a percepcao do corpo do P1), `g_exp` (so o ganho da exploracao) e `reflexo` (so o reflexo do sono).

    git worktree add --detach <pasta> a287ba2
    python experiments/auditoria_pet_vivo.py --codigo <pasta> --processos 4        # a auditoria inteira, UMA vez (a vez da maquina)
    python experiments/auditoria_pet_vivo.py --medir-tempo                          # so o tempo do A-4 nas sementes dos testes (sem medida)
grava artifacts_v3_pet_vivo/auditoria/auditoria.json e auditoria_vidas.json.gz (o `--medir-tempo` grava so tempo_a4.json)
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib
import importlib.util
import json
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "experiments") not in sys.path:
    sys.path.insert(0, str(RAIZ / "experiments"))

PASTA_C4_PADRAO = Path(r"D:\Trab\digilab\v3-memoria-run\artifacts_v2_digibrain_prototipo\memoria_autobio\run")
PASTA_C4_GIT = RAIZ / "artifacts_v2_digibrain_prototipo" / "memoria_autobio" / "run"      # a reserva (D-PV0-1), com os mesmos sha256
SAIDA = RAIZ / "artifacts_v3_pet_vivo" / "auditoria"
COMMIT_DA_C4 = "a287ba20fafdc1fbbf9be7100f89d9c90f466948"
SHA_C4 = {                                                                  # secao 2.2, conferidos com o sha256sum em 2026-11-07
    "meta.json": "6315784c4290ddfcfa3a373ca2ae14165f164581a2f184dd9210446441213a18",
    "resultado.json": "6f8c91d8e2b857194de1de00145a4da817efca76eb882bcd2d090dd3101cd6d3",
    "medidas.json.gz": "8b48d0a234afc69adfaf72d150d0d4317d4f7dd9abfa7fc2e49908a6758fd93b",
    "vidas.tar.gz": "aa0c398716bf9b285889c3e3f490f9d3538b41d1135d9ee3b788fd28cfa50aed",
}
PASTA_GAB = RAIZ / "web" / "app" / "test" / "gabaritos"
GABARITOS = ("digibrain_modular_comedouro.json.gz", "digibrain_modular_longe_fixo.json.gz", "digibrain_modular_fins.json.gz")
BRACOS_C4 = ("REL", "SEM")
LUGARES_C4 = ("longe_fixo", "comedouro", "longe")
VIDAS_C4 = 4800                                                             # 200 unidades x 4 donos x 3 lugares x 2 bracos
K_SUBAMOSTRA = 8                                                            # PV-0-5: os k de 0 a 7 de cada base
MAX_PROCESSOS = 4                                                           # V3-D8
COMPORTAMENTOS = ("ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar")
IDX = {b: i for i, b in enumerate(COMPORTAMENTOS)}
VARIANTES = ("todo", "z", "incentivo", "g_exp", "reflexo")
GRUPOS_Z = {"vies": ("vies",), "contexto": ("noite", "dormindo", "sem_cuidado", "comida_vista", "sem_comida", "bola_vista"),
            "estado": ("F", "V", "E")}                                       # o resto (u_*, fome_sem_comida, cuidado_humor) e o "corpo"
TERMOS_A1 = ("inato", "prox", "nov", "incentivo", "habito", "memoria", "persistencia", "lembranca", "faceta", "exploracao")
QUANTIS = (0.1, 0.5, 0.9)
ROTULO = ("auditoria da escolha (0b) e medida de age pelo estado (0c) da PET_VIVO: so leitura, sem vida nova e sem semente; pos hoc, "
          "descritiva e geradora de hipotese (secao 6 do plano)")
CASAS = 9


# ================================================================== as contas de hoje, sob outro nome
def metricas():
    """o `digilab/metrics.py` desta arvore, carregado como `digilab_hoje.metrics`: o processo do replay da C4 ja tem o `digilab` do
    `a287ba2`, e os dois nao podem ter o mesmo nome. Os imports do pacote sao relativos, entao o pacote inteiro carrega sob o nome novo"""
    if "digilab_hoje.metrics" in sys.modules:
        return sys.modules["digilab_hoje.metrics"]
    if "digilab_hoje" not in sys.modules:
        spec = importlib.util.spec_from_file_location("digilab_hoje", RAIZ / "digilab" / "__init__.py",
                                                      submodule_search_locations=[str(RAIZ / "digilab")])
        mod = importlib.util.module_from_spec(spec)
        sys.modules["digilab_hoje"] = mod
        spec.loader.exec_module(mod)
    met = importlib.import_module("digilab_hoje.metrics")
    if Path(met.__file__).resolve() != (RAIZ / "digilab" / "metrics.py").resolve():
        raise RuntimeError(f"digilab_hoje.metrics veio de {met.__file__}")
    return met


def _sha(caminho: Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def _r(x):
    return None if x is None else round(x, CASAS)


# ================================================================== a leitura de cada decisao (o embrulho do Impulso.unidades)
class Leitor:
    """embrulha o `impulso.unidades` da instancia do cerebro e guarda, por decisao, a leitura pura dela (as unidades com os pesos, o z
    por grupo, o reflexo e, com `contrafactual`, os pesos por comportamento de cada variante do A-4). Nao toca em rng nem em estado: so
    chama funcoes puras do proprio cerebro (o `Impulso.unidades` sobre copias rasas, o `Arbitragem.pesos`, o `Arbitragem.reflexo`, o
    `Afeto.urgencia`). O G1 confere isso (secao 2.3)"""

    def __init__(self, cerebro, comum, contrafactual: bool) -> None:
        m = cerebro.m
        self.m, self.comum, self.cf = m, comum, contrafactual
        cd = cerebro.cd
        if getattr(cd, "redecidir_evento", False) or getattr(cd, "fala_unidades", False) or getattr(cd, "passeio", False):
            raise RuntimeError("PET_VIVO: a leitura supoe o sorteio sem escolha segurada, sem as unidades de fala e sem o passeio")
        self.p = m.arb.p
        self.S = self.p.escala
        self.delta = self.S // 4                                            # PV-0-6
        self.orig = m.impulso.unidades
        self.registros: list[dict] = []
        self.t_cf = 0.0                                                     # o tempo de parede so do contrafactual (o relato da secao 8)
        m.impulso.unidades = self.unidades

    def soltar(self) -> None:
        del self.m.impulso.unidades

    # ---------------------------------------------------------------- as contas puras do proprio cerebro
    def _g_exp(self, falta: dict, urg: dict) -> int:
        """a conta do `Afeto.ler` (o `g_exp`), refeita com a falta e as urgencias dadas"""
        p, S, mul, clamp = self.p, self.S, self.comum.mul, self.comum.clamp
        return clamp(p.e0 + mul(p.beta_t, falta.get("tedio", 0), S) - mul(p.beta_u, max(urg.values()), S), 0, p.e_max)

    def _W(self, unidades: list[dict], g_exp: int, reflexo: bool) -> list[int]:
        """os pesos por comportamento da decisao: o reflexo e o nada a fazer viram um peso so (o dormir, o ocioso)"""
        n = len(COMPORTAMENTOS)
        if reflexo:
            return [1 if b == "dormir" else 0 for b in COMPORTAMENTOS]
        w = self.m.arb.pesos([x["a"] for x in unidades], g_exp)
        if sum(w) <= 0:
            return [1 if b == "ocioso" else 0 for b in COMPORTAMENTOS]
        out = [0] * n
        for x, wi in zip(unidades, w):
            out[IDX[x["acao"]]] += wi
        return out

    def _pc_com_falta(self, pc, r: str, falta_nova: int, falta_velha: int):
        """a PercepcaoCorpo com a falta de r trocada: a leitura anda no sentido da falta (S - leitura nos drives de hoje, a propria leitura
        nos novos); confere pela `falta_receptor` do cerebro, ou falha alto"""
        from dataclasses import replace
        v = getattr(pc, r)
        for nova in (v + (falta_nova - falta_velha), v - (falta_nova - falta_velha)):
            if 0 <= nova <= self.S:
                pc2 = replace(pc, **{r: nova})
                if self.comum.falta_receptor(pc2, r, self.S) == falta_nova:
                    return pc2
        raise RuntimeError(f"PET_VIVO: nao achei a leitura de {r} com a falta {falta_nova}")

    def _grupos(self, linha: list[int], z: list[int]) -> dict:
        """a soma de mul(W[j], z_j) por grupo de caracteristicas (vies, corpo, contexto, estado)"""
        mul, S = self.comum.mul, self.S
        out = {"vies": 0, "corpo": 0, "contexto": 0, "estado": 0}
        for c, wj, zj in zip(self.comum.CARACTERISTICAS, linha, z):
            if not wj:
                continue
            g = next((k for k, cs in GRUPOS_Z.items() if c in cs), "corpo")
            out[g] += mul(wj, zj, S)
        return out

    # ---------------------------------------------------------------- o embrulho
    def unidades(self, sens, afeto, ctx, plast, memoria, drives, lembranca=None, facetas=None):
        unidades, z = self.orig(sens, afeto, ctx, plast, memoria, drives, lembranca, facetas)
        m = self.m
        reflexo = m.arb.reflexo(sens)
        w = m.arb.pesos([x["a"] for x in unidades], afeto["g_exp"])
        inato_b = {b: self._grupos(m.impulso.w0[b], z) for b in COMPORTAMENTOS}
        H = getattr(plast, "H", None)
        habito_b = {b: (self._grupos(H[b], z) if H is not None and b in H else None) for b in COMPORTAMENTOS}
        reg = {"minuto": sens["minuto"], "reflexo": reflexo, "energia": sens["leitura"]["energia"], "urgencias": dict(afeto["urgencias"]),
               "comida_vista": sens["conjuncoes"]["comida_vista"] > 0, "g_exp": afeto["g_exp"],
               "unidades": [{"b": IDX[x["acao"]], "chave": self.comum.chave_json(x["chave"]), "tipo": x["tipo"], "termos": dict(x["termos"]),
                             "soma": x["soma"], "a": x["a"], "w": wi} for x, wi in zip(unidades, w)],
               "inato": {b: v for b, v in inato_b.items()}, "habito": habito_b,
               "W": self._W(unidades, afeto["g_exp"], reflexo)}
        if self.cf:
            t = time.perf_counter()
            reg["cf"] = self._contrafactual(sens, afeto, ctx, plast, memoria, drives, lembranca, facetas, unidades, reflexo)
            self.t_cf += time.perf_counter() - t
        self.registros.append(reg)
        return unidades, z

    def _contrafactual(self, sens, afeto, ctx, plast, memoria, drives, lembranca, facetas, unidades, reflexo) -> dict:
        """{r: {variante: (W com falta + Delta, W com falta - Delta)}} (secao 4.4)"""
        m, S = self.m, self.S
        falta, urg = sens["falta"], afeto["urgencias"]
        out = {}
        for r in sorted(falta):
            par = {v: [] for v in VARIANTES}
            for sinal in (1, -1):
                f2 = min(S, max(0, falta[r] + sinal * self.delta))
                falta2 = {**falta, r: f2}
                urg2 = {**urg, r: m.afeto.urgencia(f2)}
                g2 = self._g_exp(falta2, urg2)
                pc2 = self._pc_com_falta(sens["pc"], r, f2, falta[r]) if f2 != falta[r] else sens["pc"]
                leit2 = {**sens["leitura"], r: getattr(pc2, r)}
                sens_todo = {**sens, "falta": falta2, "leitura": leit2, "pc": pc2}
                reflexo2 = m.arb.reflexo(sens_todo)
                u_todo, _ = self.orig(sens_todo, {**afeto, "urgencias": urg2, "g_exp": g2}, ctx, plast, memoria, drives, lembranca, facetas)
                u_z, _ = self.orig(sens, {**afeto, "urgencias": urg2}, ctx, plast, memoria, drives, lembranca, facetas)
                u_inc, _ = self.orig({**sens, "pc": pc2}, afeto, ctx, plast, memoria, drives, lembranca, facetas)
                par["todo"].append(self._W(u_todo, g2, reflexo2))
                par["z"].append(self._W(u_z, afeto["g_exp"], reflexo))
                par["incentivo"].append(self._W(u_inc, afeto["g_exp"], reflexo))
                par["g_exp"].append(self._W(unidades, g2, reflexo))
                par["reflexo"].append(self._W(unidades, afeto["g_exp"], reflexo2))
            out[r] = {v: tuple(par[v]) for v in VARIANTES}
        return out


def comum_do_pacote(pacote: str) -> object:
    """as funcoes puras do cerebro da fonte (o `_comum`, a `falta_receptor` e as caracteristicas do z), do pacote importado como `digilab`"""
    from types import SimpleNamespace
    c = importlib.import_module(f"{pacote}.digibrain._comum")
    lobos = importlib.import_module(f"{pacote}.policies.lobos")
    cfg = importlib.import_module(f"{pacote}.config")
    return SimpleNamespace(mul=c.mul, clamp=c.clamp, phi=c.phi, chave_json=c.chave_json, falta_receptor=lobos.falta_receptor,
                           CARACTERISTICAS=cfg.CARACTERISTICAS_DIGIBRAIN)


# ================================================================== a reducao de uma vida (com as contas do metrics.py de hoje)
def _sem_termo(leitor_p, comum, unidades: list[dict], termo: str, g_exp: int, arb) -> list[int]:
    """os pesos por comportamento sem um termo (A-1): a ativacao phi(soma - t), como as sondas; sem a `memoria`, a unidade do lugar
    lembrado sai inteira (ela so existe pela memoria); sem a `exploracao`, w = a"""
    a_max = leitor_p.a_max
    if termo == "exploracao":
        w = [x["a"] if x["a"] > 0 else 0 for x in unidades]
    else:
        ativ = [0 if (termo == "memoria" and x["tipo"] == "ponto") else comum.phi(x["soma"] - x["termos"].get(termo, 0), a_max)
                for x in unidades]
        w = arb.pesos(ativ, g_exp)
    out = [0] * len(COMPORTAMENTOS)
    for x, wi in zip(unidades, w):
        out[x["b"]] += wi
    return out if sum(out) > 0 else [1 if b == "ocioso" else 0 for b in COMPORTAMENTOS]


def reduzir(met, comum, arb, registros: list[dict], motivos: list[dict], cf: bool) -> dict:
    """as medidas A-1 a A-4 de uma vida (secao 4), com as contas do `digilab/metrics.py` de hoje. `registros` e `motivos` sao da mesma
    decisao, na mesma ordem"""
    if len(registros) != len(motivos):
        raise RuntimeError(f"PET_VIVO: {len(registros)} leituras e {len(motivos)} motivos")
    S = arb.p.escala
    lam = arb.p.lambda_sono
    nb = len(COMPORTAMENTOS)
    soma_p = [0.0] * nb
    soma_p1 = [0.0] * nb
    soma_pmu = [0.0] * nb
    soma_pa = [0.0] * nb
    ativas_soma = [0] * nb
    ativas_max = [0] * nb
    ativas_hist = {b: {} for b in COMPORTAMENTOS}
    tv_p1, tv_pa1, entropias = [], [], []
    troca_p, troca_p1 = [], []
    escolhas = [0] * nb
    partes = {"escolhida": {t: [] for t in TERMOS_A1}, "rival_forte": {t: [] for t in TERMOS_A1},
              "rivais_ponderadas": {t: [] for t in TERMOS_A1}}
    tv_sem = {t: [] for t in TERMOS_A1}
    portas_inato = {g: [] for g in ("vies", "corpo", "contexto", "estado", "tipo")}
    portas_habito = {g: [] for g in ("vies", "corpo", "contexto", "estado")}
    corpo_no_inato = []
    sondas: dict = {}
    n_eleg = 0
    # A-3
    n_dec = len(registros)
    reflexos = 0
    por_hora = {"decisoes": [0] * 24, "reflexos": [0] * 24}
    dormir_reflexo = dormir_sorteio = 0
    p_dormir = []
    reflexo_por_pouco = quase_reflexo = reflexo_e_fome = 0
    r_dormir = {"n": 0, "soma_r": 0, "r_diferente_de_0": 0}
    # o alivio (os canais por comportamento) e o ramo 2 da HP
    canais: dict = {}
    hp2: dict = {}
    # A-4
    a4: dict = {}
    rv = {"soma": 0.0, "n": 0}
    for reg, mot in zip(registros, motivos):
        hora = (reg["minuto"] // 60) % 24
        por_hora["decisoes"][hora] += 1
        cons = mot["consequencia"]
        b_mot = mot["acao"]
        if cons is not None:
            for r, c in cons["canais"].items():
                s = canais.setdefault((b_mot, r), [0, 0])
                s[0] += c
                s[1] += 1
        if b_mot == "dormir" and cons is not None:
            r_dormir["n"] += 1
            r_dormir["soma_r"] += cons["r"]
            r_dormir["r_diferente_de_0"] += cons["r"] != 0
        if reg["reflexo"] != mot["reflexo"]:
            raise RuntimeError("PET_VIVO: o reflexo da leitura nao e o do motivo")
        if reg["reflexo"]:
            reflexos += 1
            por_hora["reflexos"][hora] += 1
            dormir_reflexo += 1
            if reg["energia"] >= lam - S // 16:
                reflexo_por_pouco += 1
            if reg["urgencias"].get("fome", 0) >= S // 2:
                reflexo_e_fome += 1
        else:
            if reg["energia"] < lam + S // 16:
                quase_reflexo += 1
            if b_mot == "dormir":
                dormir_sorteio += 1
        if cf and "cf" in reg:
            for r, variantes in reg["cf"].items():
                for v, (wm, wn) in variantes.items():
                    s = a4.setdefault(r, {}).setdefault(v, {"n": 0, "soma_tv": 0.0, "movido_para": [0.0] * nb, "delta": [0.0] * nb})
                    d, tv = met.diferenca_e_tv(wm, wn)
                    s["n"] += 1
                    s["soma_tv"] += tv
                    for i, x in enumerate(d):
                        s["delta"][i] += x
                        if x > 0:
                            s["movido_para"][i] += x
                if r == "fome" and reg["comida_vista"] and not reg["reflexo"]:
                    wm, wn = variantes["todo"]
                    rv["soma"] += met.diferenca_de_distribuicao(wm, wn)[IDX["comer"]]
                    rv["n"] += 1
        if reg["reflexo"]:
            continue
        # ---- a decisao com sorteio (ou com um candidato so, ou o nada a fazer): A-1 e A-2
        n_eleg += 1
        us = reg["unidades"]
        W = reg["W"]
        pares = [(x["b"], x["w"]) for x in us]
        W1 = met.maximo_por_comportamento(pares, nb) if sum(W) == sum(x["w"] for x in us) else W
        Wmu = met.media_inteira_por_comportamento(pares, nb) if sum(W) == sum(x["w"] for x in us) else W
        pares_a = [(x["b"], x["a"] if x["a"] > 0 else 0) for x in us]
        Wa = met.pesos_por_comportamento(pares_a, nb)
        Wa = Wa if sum(Wa) > 0 else W
        Wa1 = met.maximo_por_comportamento(pares_a, nb) if sum(met.pesos_por_comportamento(pares_a, nb)) > 0 else W
        for acc, vec in ((soma_p, W), (soma_p1, W1), (soma_pmu, Wmu), (soma_pa, Wa)):
            for i, x in enumerate(met.distribuicao(vec)):
                acc[i] += x
        tv_p1.append(met.distancia_tv(W, W1))
        tv_pa1.append(met.distancia_tv(Wa, Wa1))
        entropias.append(met.entropia_bits(W))
        ativ = met.unidades_ativas_por_comportamento(pares, nb)
        for i, n in enumerate(ativ):
            ativas_soma[i] += n
            ativas_max[i] = max(ativas_max[i], n)
            h = ativas_hist[COMPORTAMENTOS[i]]
            h[str(n)] = h.get(str(n), 0) + 1
        esc = mot["escolha"]
        i_esc = next((j for j, x in enumerate(us) if x["chave"] == esc), None)
        if i_esc is None:
            raise RuntimeError(f"PET_VIVO: a escolha {esc} nao esta entre as unidades da decisao {mot['k']}")
        escolhas[us[i_esc]["b"]] += 1
        intencao = mot["estado"]["I"]
        if intencao is not None:
            j = next((j for j, x in enumerate(us) if x["chave"] == intencao), None)
            T = sum(x["w"] for x in us)
            p_unid = (us[j]["w"] / T) if (j is not None and T > 0) else 0.0
            troca_p.append(1.0 - p_unid)
            b_int = IDX[intencao[0]]
            troca_p1.append(1.0 - met.distribuicao(W1)[b_int])
        # A-1: as partes de cada termo (com a exploracao) na escolhida e nas rivais
        def termos_de(x):
            t = {k: x["termos"].get(k, 0) for k in TERMOS_A1 if k != "exploracao"}
            t["exploracao"] = x["w"] - x["a"] if x["a"] > 0 else 0
            return t
        pe = met.partes_absolutas(termos_de(us[i_esc]))
        for t in TERMOS_A1:
            partes["escolhida"][t].append(pe[t])
        rivais = [j for j, x in enumerate(us) if j != i_esc and x["w"] > 0]
        if rivais:
            jf = max(rivais, key=lambda j: (us[j]["w"], -j))
            pf = met.partes_absolutas(termos_de(us[jf]))
            tot = sum(us[j]["w"] for j in rivais)
            pp = {t: 0.0 for t in TERMOS_A1}
            for j in rivais:
                pj = met.partes_absolutas(termos_de(us[j]))
                for t in TERMOS_A1:
                    pp[t] += pj[t] * us[j]["w"] / tot
            for t in TERMOS_A1:
                partes["rival_forte"][t].append(pf[t])
                partes["rivais_ponderadas"][t].append(pp[t])
        for t in TERMOS_A1:
            if t != "exploracao" and not any(t in x["termos"] for x in us):
                continue
            tv_sem[t].append(met.distancia_tv(W, _sem_termo(arb.p, comum, us, t, reg["g_exp"], arb)))
        # o inato e o habito da escolhida por porta
        b_esc = COMPORTAMENTOS[us[i_esc]["b"]]
        gi = dict(reg["inato"][b_esc])
        gi["tipo"] = us[i_esc]["termos"]["inato"] - sum(reg["inato"][b_esc].values())
        pi = met.partes_absolutas(gi)
        for g in portas_inato:
            portas_inato[g].append(pi[g])
        corpo_no_inato.append(pi["corpo"])
        if reg["habito"][b_esc] is not None:
            ph = met.partes_absolutas(reg["habito"][b_esc])
            for g in portas_habito:
                portas_habito[g].append(ph[g])
        for k, v in mot["sondas"].items():
            if k.endswith("_decidiu"):
                sondas[k] = sondas.get(k, 0) + bool(v)
        p_dormir.append(met.distribuicao(W)[IDX["dormir"]])
        # o ramo 2 da HP: com a urgencia de r >= S/2, a vantagem da vencedora sobre a melhor unidade de cada outro comportamento
        melhor = {}
        for x in us:
            if x["w"] > 0 and (x["b"] not in melhor or x["w"] > melhor[x["b"]]["w"]):
                melhor[x["b"]] = x
        x_win = us[i_esc]
        for r, u in sorted(reg["urgencias"].items()):
            if u < S // 2:
                continue
            for b, xb in melhor.items():
                if b == x_win["b"]:
                    continue
                dw = x_win["w"] - xb["w"]
                if dw <= 0:
                    continue
                gw, gb = reg["inato"][COMPORTAMENTOS[x_win["b"]]], reg["inato"][COMPORTAMENTOS[b]]
                parte = (gw["vies"] + gw["contexto"] - gb["vies"] - gb["contexto"]) / dw
                s = hp2.setdefault(f"{r}|{COMPORTAMENTOS[b]}", [0, 0])
                s[0] += 1
                s[1] += parte > 0.5
    media = lambda xs: (sum(xs) / len(xs)) if xs else None      # noqa: E731
    out = {
        "decisoes": n_dec, "elegiveis": n_eleg,
        "A1": {"partes": {q: {t: {"media": _r(media(v)), "quantis": [_r(x) for x in met.quantis(v, QUANTIS)] if v else None}
                              for t, v in d.items()} for q, d in partes.items()},
               "tv_sem_termo": {t: _r(media(v)) for t, v in tv_sem.items()},
               "portas_inato": {g: _r(media(v)) for g, v in portas_inato.items()},
               "portas_habito": {g: _r(media(v)) for g, v in portas_habito.items()},
               "corpo_no_inato_mediana": _r(met.mediana(corpo_no_inato)),
               "sondas": {k: _r(v / n_eleg) for k, v in sorted(sondas.items())} if n_eleg else {}},
        "A2": {"ativas_media": {b: _r(ativas_soma[i] / n_eleg) if n_eleg else None for i, b in enumerate(COMPORTAMENTOS)},
               "ativas_max": dict(zip(COMPORTAMENTOS, ativas_max)), "ativas_hist": ativas_hist,
               "soma_p": dict(zip(COMPORTAMENTOS, map(_r, soma_p))), "soma_p1": dict(zip(COMPORTAMENTOS, map(_r, soma_p1))),
               "soma_pmu": dict(zip(COMPORTAMENTOS, map(_r, soma_pmu))), "soma_pa": dict(zip(COMPORTAMENTOS, map(_r, soma_pa))),
               "tv_p_p1_media": _r(media(tv_p1)), "tv_p_p1_mediana": _r(met.mediana(tv_p1)),
               "tv_sem_exploracao_media": _r(media(tv_pa1)),
               "troca_p": _r(media(troca_p)), "troca_p1": _r(media(troca_p1)),
               "escolhas": dict(zip(COMPORTAMENTOS, escolhas)), "entropia_media": _r(media(entropias))},
        "A3": {"reflexos": reflexos, "fracao_reflexo": _r(reflexos / n_dec) if n_dec else None, "por_hora": por_hora,
               "dormir_reflexo": dormir_reflexo, "dormir_sorteio": dormir_sorteio, "p_dormir_media_no_sorteio": _r(media(p_dormir)),
               "reflexo_por_pouco": reflexo_por_pouco, "quase_reflexo": quase_reflexo, "reflexo_com_fome_urgente": reflexo_e_fome,
               "r_do_dormir": r_dormir},
        "canais": {f"{b}|{r}": _r(s[0] / s[1]) for (b, r), s in sorted(canais.items()) if s[1]},
        "hp2": dict(sorted(hp2.items())),
    }
    if cf:
        out["A4"] = {r: {v: {"n": s["n"], "S": _r(s["soma_tv"] / s["n"]) if s["n"] else None, "soma_tv": _r(s["soma_tv"]),
                              "movido_para": dict(zip(COMPORTAMENTOS, map(_r, s["movido_para"]))),
                              "delta": dict(zip(COMPORTAMENTOS, map(_r, s["delta"])))}
                          for v, s in sorted(d.items())} for r, d in sorted(a4.items())}
        out["RV"] = {"n": rv["n"], "media": _r(rv["soma"] / rv["n"]) if rv["n"] else None}
    return out


# ================================================================== a C4 (o replay no a287ba2)
_NS: dict = {}


def _ns_c4(codigo: str):
    if codigo not in _NS:
        import descritivo_dc13_rel as drel
        ns = drel.carregar(Path(codigo))
        _NS[codigo] = (drel, ns, comum_do_pacote("digilab"))
    return _NS[codigo]


def rejogar_c4(tarefa: tuple) -> dict:
    """uma vida da C4: o replay do log (a `viver` da C4, com o coletor da D-C1-3 e o Leitor), o G1 das medidas e a reducao"""
    codigo, gravada, arquivo, dias, orcamento, cf = tarefa
    drel, ns, comum = _ns_c4(codigo)
    met = metricas()
    ma, lr, orq = ns.ma, ns.lr, ns.orq
    braco, dono, semente = gravada["braco"], gravada["dono"], gravada["semente"]
    texto = Path(arquivo).read_text(encoding="utf-8")
    fp, _ = orq.fabricas(braco, dono, semente, dias, orcamento, conserto=True)
    cc = orq.bancada(dias, orcamento).cfg_corpo_de(ma.bv.EspecVida(dono, ma.gl.BRACO_V11, semente))
    categorias: dict = {}
    episodios: dict = {}
    feito = []

    def fp_leitor(cfg):
        registro = fp(cfg)
        drel._instalar_coletor(ns, registro, categorias, episodios)
        feito.append((registro, Leitor(orq.cerebro_de(registro), comum, cf)))
        return registro

    def fm(politica, cfg, s):
        return lr.MotorGravaCorpo(politica, cfg, s, ma.NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    t0 = time.perf_counter()
    motor = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), fp_leitor, semente=semente, fabrica_motor=fm)
    registro, leitor = feito[0]
    cerebro = orq.cerebro_de(registro)
    del cerebro.agir
    leitor.soltar()
    if motor.log.para_jsonl() != texto:
        raise orq.bv.ReplayDivergiu(f"{arquivo}: o log rejogado nao e o do disco")
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    ma.conferir_memoria(braco, cerebro)
    fins = ma.conferir_fins(braco, registro)
    refeita = {"vida": gravada["vida"], "braco": braco, "dono": dono, "lugar": gravada["lugar"], "semente": semente, "base": gravada["base"],
               "k": gravada["k"], **orq.medidas(motor, registro, braco, dias, True),
               "corpo": lr.medidas_do_corpo(motor, registro, dias), "fins_conferidos": fins,
               "memoria": ma.medidas_memoria(registro, dias, categorias)}
    sem_custo = {k: v for k, v in gravada.items() if k != "custo"}
    if json.dumps(refeita, sort_keys=True) != json.dumps(sem_custo, sort_keys=True):
        raise RuntimeError(f"G1 da auditoria: a vida {gravada['vida']} nao refaz as medidas gravadas (contrafactual {cf})")
    t_replay = time.perf_counter() - t0
    t1 = time.perf_counter()
    red = reduzir(met, comum, cerebro.m.arb, leitor.registros, cerebro.motivos, cf)
    t_red = time.perf_counter() - t1
    return {"fonte": "C4", "vida": gravada["vida"], "braco": braco, "dono": dono, "lugar": gravada["lugar"], "base": gravada["base"],
            "k": gravada["k"], "semente": semente, "contrafactual": cf, "log_sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
            "parede_s": {"replay": t_replay, "contrafactual": leitor.t_cf, "reducao": t_red, "total": time.perf_counter() - t0}, **red}


# ================================================================== a AN0 (as vidas dos gabaritos, no codigo de hoje)
def vidas_an0() -> list[tuple]:
    """(arquivo, dono, lugar, semente, inatos) das vidas da AN0 com os inatos de hoje: as 8 da LM0 e as 2 dos fins sem ajuste (D-PV0C-1)"""
    import exportar_gabarito_digibrain_modular as gab
    out = [(f"{gab.PREFIXO}{lg}.json.gz", d, lg, s, {}) for lg in gab.LUGARES for d in gab.DONOS for s in gab.SEMENTES]
    out += [(gab.ARQUIVO_FINS, d, lg, s, aj) for d, lg, s, aj in gab.VIDAS_FINS if not aj]
    return out


def rejogar_an0(tarefa: tuple) -> dict:
    """uma vida da AN0: a vida refeita no codigo de hoje com o Leitor, o G1 contra o gabarito (cada motivo, o log e o estado) e a reducao"""
    arquivo, dono, lugar, semente, inatos, cf, gabarito = tarefa
    import exportar_gabarito_digibrain_modular as gab
    from bancada.regras_mundo import simular_vida_fisico
    from digilab.config import CONFIG_PADRAO
    from digilab.donos import criar_dono
    from digilab.mundo import DonoComLugar
    met = metricas()
    comum = comum_do_pacote("digilab")
    orq = gab.orq
    t0 = time.perf_counter()
    fp, fm = orq.fabricas(gab.BRACO, dono, semente, gab.DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
    registro = fp(CONFIG_PADRAO)
    cerebro = orq.cerebro_de(registro)
    leitor = Leitor(cerebro, comum, cf)
    try:
        d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
        motor, _ = simular_vida_fisico(d, registro, semente, gab.DIAS, orq.ORCAMENTO_POR_DIA * gab.DIAS, dono, fm)
    finally:
        leitor.soltar()
    log = hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest()
    estado = hashlib.sha256(gab._texto(gab.paraj(cerebro.estado_interno())).encode("utf-8")).hexdigest()
    motivos = [gab.paraj(x) for x in cerebro.motivos]
    if log != gabarito["log"] and log != gabarito.get("log_sha256"):
        raise RuntimeError(f"G1 da AN0: o log de {dono}/{lugar}/{semente} nao e o do gabarito (contrafactual {cf})")
    if estado != gabarito["estado"]:
        raise RuntimeError(f"G1 da AN0: o estado de {dono}/{lugar}/{semente} nao e o do gabarito (contrafactual {cf})")
    if [x["motivo"] for x in gabarito["decisoes"]] != motivos:
        raise RuntimeError(f"G1 da AN0: os motivos de {dono}/{lugar}/{semente} nao sao os do gabarito (contrafactual {cf})")
    t_replay = time.perf_counter() - t0
    t1 = time.perf_counter()
    red = reduzir(met, comum, cerebro.m.arb, leitor.registros, motivos, cf)
    t_red = time.perf_counter() - t1
    return {"fonte": "AN0", "vida": f"{arquivo}|{dono}|{lugar}|{semente}", "braco": "REL", "dono": dono, "lugar": lugar,
            "base": None, "k": None, "semente": semente, "contrafactual": cf, "log_sha256": log,
            "parede_s": {"replay": t_replay, "contrafactual": leitor.t_cf, "reducao": t_red, "total": time.perf_counter() - t0}, **red}


def gabaritos() -> dict:
    """{(arquivo, dono, lugar, semente): a vida gravada}, com o sha256 de cada arquivo"""
    out, shas = {}, {}
    for nome in GABARITOS:
        dados = (PASTA_GAB / nome).read_bytes()
        shas[nome] = hashlib.sha256(dados).hexdigest()
        for v in json.loads(gzip.decompress(dados))["vidas"]:
            out[(nome, v["dono"], v["lugar"], v["semente"])] = v
    return {"vidas": out, "sha256": shas}


# ================================================================== a leitura (secao 5), as contas por grupo
def _unidade(v: dict):
    return (v["base"], v["semente"]) if v["fonte"] == "C4" else v["vida"]


def _media_por_unidade(vidas: list[dict], f) -> list[float]:
    """o valor por unidade (base, semente) com a media dos donos (a C4, secao 3); na AN0, a vida e a unidade"""
    por: dict = {}
    for v in vidas:
        x = f(v)
        if x is not None:
            por.setdefault(_unidade(v), []).append(x)
    return [sum(xs) / len(xs) for _, xs in sorted(por.items(), key=lambda kv: repr(kv[0]))]


def ler_grupo(met, vidas: list[dict]) -> dict:
    """as contas da regra da secao 5 num grupo (fonte, braco, lugar): a tabela do alivio, S_r, C_r, a SE-C, a RV, e as tres hipoteses"""
    nb = len(COMPORTAMENTOS)
    canais: dict = {}
    for v in vidas:
        for chave, x in v["canais"].items():
            b, r = chave.split("|")
            canais.setdefault((b, r), []).append(x)
    tab = met.tabela_do_alivio(canais)
    receptores = sorted({r for _, r in canais})
    alivio = {r: [b for b in COMPORTAMENTOS if tab.get((b, r), {}).get("alivia")] for r in receptores if r != "susto"}
    # A-2 no grupo
    soma_p = [sum(v["A2"]["soma_p"][b] for v in vidas) for b in COMPORTAMENTOS]
    soma_p1 = [sum(v["A2"]["soma_p1"][b] for v in vidas) for b in COMPORTAMENTOS]
    rho = dict(zip(COMPORTAMENTOS, map(_r, met.inflacao(soma_p, soma_p1))))
    ativas = {b: _r(sum(v["A2"]["ativas_media"][b] * v["elegiveis"] for v in vidas) / max(1, sum(v["elegiveis"] for v in vidas)))
              for b in COMPORTAMENTOS}
    mais = max(("explorar", "comer"), key=lambda b: (ativas[b] or 0))
    tv_mediana = met.mediana([v["A2"]["tv_p_p1_media"] for v in vidas if v["A2"]["tv_p_p1_media"] is not None])
    ha = tv_mediana is not None and tv_mediana >= 0.10 and (rho[mais] or 0) >= 1.25
    # A-3
    fr_reflexo = sum(v["A3"]["reflexos"] for v in vidas) / max(1, sum(v["decisoes"] for v in vidas))
    corpo_mediana = met.mediana([v["A1"]["corpo_no_inato_mediana"] for v in vidas if v["A1"]["corpo_no_inato_mediana"] is not None])
    out = {"vidas": len(vidas), "unidades": len({_unidade(v) for v in vidas}),
           "alivio": {f"{b}|{r}": {k: (_r(x) if isinstance(x, float) else x) for k, x in d.items()} for (b, r), d in sorted(tab.items())},
           "A_r": alivio, "rho": rho, "ativas_media": ativas, "mais_unidades": mais, "tv_p_p1_mediana_das_vidas": _r(tv_mediana),
           "fracao_reflexo": _r(fr_reflexo), "reflexo_acima_de_um_terco": fr_reflexo > 1 / 3,
           "corpo_no_inato_mediana_das_vidas": _r(corpo_mediana),
           "HA": {"aponta": ha, "tv_mediana": _r(tv_mediana), "rho_do_comportamento_com_mais_unidades": rho[mais], "cortes": [0.10, 1.25]}}
    com_a4 = [v for v in vidas if "A4" in v]
    if not com_a4:
        out["HC"] = out["HP"] = {"aponta": None, "nota": "sem o contrafactual neste grupo"}
        return out
    por_r = {}
    for r, A in sorted(alivio.items()):
        def S_r(v, var="todo", r=r):
            s = v["A4"].get(r, {}).get(var)
            return None if not s or not s["n"] else s["soma_tv"] / s["n"]

        def mov(v, r=r, A=tuple(A)):
            s = v["A4"].get(r, {}).get("todo")
            return None if not s or not s["n"] else met.sensibilidade_coerente(s["movido_para"], A, s["n"])

        def dp_alivio(v, r=r, A=tuple(A)):
            s = v["A4"].get(r, {}).get("todo")
            return None if not s or not s["n"] or not A else sum(s["delta"][b] for b in A) / s["n"]

        soma_tv = sum(v["A4"][r]["todo"]["soma_tv"] for v in com_a4 if r in v["A4"])
        movido = {b: sum(v["A4"][r]["todo"]["movido_para"][b] for v in com_a4 if r in v["A4"]) for b in COMPORTAMENTOS}
        ic_dp = met.ic_t(_media_por_unidade(com_a4, dp_alivio))
        ic_sc = met.ic_t(_media_por_unidade(com_a4, mov))
        por_r[r] = {"A_r": A, "S_mediana_das_vidas": _r(met.mediana([x for x in (S_r(v) for v in com_a4) if x is not None])),
                    "S_portas": {var: _r(met.mediana([x for x in (S_r(v, var) for v in com_a4) if x is not None])) for var in VARIANTES},
                    "C": _r(met.coerencia(movido, A, soma_tv)),
                    "S_vezes_C": {k: _r(x) if isinstance(x, float) else x for k, x in ic_sc.items()},
                    "dP_alivio": {k: _r(x) if isinstance(x, float) else x for k, x in ic_dp.items()},
                    "hp2": None}
        n_hp2 = [0, 0]
        for v in vidas:
            for b in A:
                s = v["hp2"].get(f"{r}|{b}")
                if s:
                    n_hp2[0] += s[0]
                    n_hp2[1] += s[1]
        por_r[r]["hp2"] = {"n": n_hp2[0], "fracao_vies_contexto_acima_de_meio": _r(n_hp2[1] / n_hp2[0]) if n_hp2[0] else None}
    se_vidas = []
    for v in com_a4:
        valores = {}
        for r, A in alivio.items():
            s = v["A4"].get(r, {}).get("todo")
            valores[r] = None if not s or not s["n"] else met.sensibilidade_coerente(s["movido_para"], A, s["n"])
        se_vidas.append((v, met.se_c(valores)))
    ic_se = met.ic_t(_media_por_unidade_vals(se_vidas))
    rv = met.ic_t(_media_por_unidade(com_a4, lambda v: v["RV"]["media"]))
    com_A = [r for r, A in alivio.items() if A]
    hc_baixos = [r for r in com_A if por_r[r]["dP_alivio"]["ic_superior"] is not None and por_r[r]["dP_alivio"]["ic_superior"] < 0.05]
    hc = len(hc_baixos) >= 6 and corpo_mediana is not None and corpo_mediana < 1 / 3
    sens = [r for r in com_A if (por_r[r]["S_mediana_das_vidas"] or 0) >= 0.05]
    incoerentes = [r for r in sens if por_r[r]["C"] is not None and por_r[r]["C"] < 0.5]
    hp_a = len(sens) >= 6 and len(incoerentes) * 2 >= len(sens)
    hp_b = [r for r in com_A if (por_r[r]["hp2"]["fracao_vies_contexto_acima_de_meio"] or 0) > 0.5]
    out.update({
        "A4": por_r,
        "SE_C": {k: _r(x) if isinstance(x, float) else x for k, x in ic_se.items()},
        "RV": {k: _r(x) if isinstance(x, float) else x for k, x in rv.items()},
        "entropia_media": _r(sum(v["A2"]["entropia_media"] for v in com_a4 if v["A2"]["entropia_media"] is not None) / len(com_a4)),
        "receptores_com_A_r": com_A,
        "HC": {"aponta": hc, "receptores_com_dP_alivio_baixo": hc_baixos, "corpo_no_inato_mediana": _r(corpo_mediana),
               "cortes": ["6 receptores", 0.05, "1/3"]},
        "HP": {"aponta": hp_a or bool(hp_b), "ramo_1": hp_a, "receptores_sensiveis": sens, "incoerentes": incoerentes,
               "ramo_2_receptores": hp_b, "cortes": ["6 receptores", 0.05, 0.5, "metade", "1/2 da diferenca de w"]},
    })
    return out


def _media_por_unidade_vals(pares: list[tuple]) -> list[float]:
    por: dict = {}
    for v, x in pares:
        if x is not None:
            por.setdefault(_unidade(v), []).append(x)
    return [sum(xs) / len(xs) for _, xs in sorted(por.items(), key=lambda kv: repr(kv[0]))]


def linha_da_leitura(g: dict) -> dict:
    """a linha da secao 5 num grupo: as hipoteses que apontam; mistura com duas ou mais; indeterminado com nenhuma"""
    apontam = [h for h in ("HA", "HC", "HP") if g.get(h, {}).get("aponta")]
    if not apontam:
        linha = "indeterminado"
    elif len(apontam) == 1:
        linha = f"aponta para {apontam[0]}"
    else:
        linha = "mistura: " + " + ".join(apontam)
    return {"linha": linha, "apontam": apontam,
            "aviso_reflexo": "o reflexo decide mais de 1/3 das decisoes" if g.get("reflexo_acima_de_um_terco") else None}


# ================================================================== o principal
def subamostra(v: dict) -> bool:
    return v["k"] < K_SUBAMOSTRA


def ler_fontes_c4(pasta: Path) -> dict:
    shas = {}
    for nome, esperado in SHA_C4.items():
        s = _sha(pasta / nome)
        if s != esperado:
            raise RuntimeError(f"{pasta / nome} nao e o da C4 (sha256 {s})")
        shas[nome] = s
    return shas


def principal(codigo: Path, pasta_c4: Path, processos: int, saida: Path = SAIDA) -> dict:
    if (saida / "auditoria.json").exists():
        raise FileExistsError(f"{saida / 'auditoria.json'} ja existe: a auditoria roda uma vez (secao 9)")
    if not 1 <= processos <= MAX_PROCESSOS:
        raise SystemExit(f"de 1 a {MAX_PROCESSOS} processos (V3-D8)")
    import descritivo_dc13_longe_fixo as dc
    import descritivo_dc13_rel as drel
    fontes = ler_fontes_c4(pasta_c4)
    meta = json.loads((pasta_c4 / "meta.json").read_text(encoding="utf-8"))
    codigo_ok = drel.conferir_codigo(codigo, meta)                      # antes de importar uma linha do pacote do a287ba2
    medidas, sha_medidas = drel.carregar_medidas(pasta_c4 / "medidas.json.gz", meta)
    fontes["medidas.json"] = sha_medidas
    alvo = sorted((v for v in medidas.values() if v["braco"] in BRACOS_C4 and v["lugar"] in LUGARES_C4), key=lambda v: v["vida"])
    if len(alvo) != VIDAS_C4:
        raise RuntimeError(f"{len(alvo)} vidas do REL e do SEM no medidas.json; o plano pede {VIDAS_C4}")
    gab = gabaritos()
    fontes["gabaritos"] = gab["sha256"]
    met = metricas()
    t0 = time.time()
    cfg = meta["config"]
    vidas: list[dict] = []
    with tempfile.TemporaryDirectory() as tmp:
        logs = dc.extrair_logs(pasta_c4 / "vidas.tar.gz", alvo, Path(tmp))
        tarefas = [(str(codigo), v, str(logs[v["vida"]]), cfg["dias"], cfg["orcamento_por_dia"], subamostra(v)) for v in alvo]
        with ProcessPoolExecutor(max_workers=processos) as pool:     # sempre em processos proprios: o digilab do a287ba2 fica neles
            vidas += list(pool.map(rejogar_c4, tarefas, chunksize=4))
    t_c4 = time.time() - t0
    t1 = time.time()
    tarefas_an0 = [(*x, True, gab["vidas"][(x[0], x[1], x[2], x[3])]) for x in vidas_an0()]
    with ProcessPoolExecutor(max_workers=processos) as pool:
        vidas += list(pool.map(rejogar_an0, tarefas_an0))
    t_an0 = time.time() - t1
    grupos: dict = {}
    for v in vidas:
        grupos.setdefault(f"{v['fonte']}|{v['braco']}|{v['lugar']}", []).append(v)
    leitura = {}
    for chave in sorted(grupos):
        g = ler_grupo(met, grupos[chave])
        g["leitura"] = linha_da_leitura(g)
        leitura[chave] = g
    out = {"rotulo": ROTULO, "plano": "docs/PLANO_ANALISE_V3_PET_VIVO.md (APROVADO em 2026-11-08, repassado pelo Gerente da V3)",
           "fontes_sha256": fontes, "pasta_c4": str(pasta_c4), "commit_da_c4": meta["git_head"], "codigo_c4": codigo_ok,
           "scripts": {"experiments/auditoria_pet_vivo.py": _sha(Path(__file__)), "digilab/metrics.py": _sha(RAIZ / "digilab" / "metrics.py")},
           "subamostra": f"o contrafactual nos k < {K_SUBAMOSTRA} de cada base da C4 e em toda a AN0 (PV-0-5)",
           "vidas": {"C4": sum(v["fonte"] == "C4" for v in vidas), "AN0": sum(v["fonte"] == "AN0" for v in vidas),
                     "com_contrafactual": sum(v["contrafactual"] for v in vidas)},
           "parede_s": {"C4": t_c4, "AN0": t_an0}, "processos": processos, "grupos": leitura}
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "auditoria.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    texto = json.dumps(sorted(vidas, key=lambda v: (v["fonte"], v["vida"])), ensure_ascii=False, sort_keys=True)
    (saida / "auditoria_vidas.json.gz").write_bytes(gzip.compress(texto.encode("utf-8"), compresslevel=9, mtime=0))
    return out


def medir_tempo(saida: Path = SAIDA, vidas: int = 2, repeticoes: int = 3, codigo: Path | None = None, pasta_c4: Path = PASTA_C4_PADRAO) -> dict:
    """o tempo do contrafactual A-4 nas sementes dos testes (a fumaca da secao 8): as primeiras `vidas` da AN0 com o contrafactual, cada uma
    `repeticoes` vezes, com o minimo de cada parte (o replay sem a leitura do A-4, o contrafactual e a reducao), e a projecao para a
    auditoria. Com `codigo` (a worktree do a287ba2), tambem uma vida da C4 (o REL no `longe_fixo`, a primeira de k = 0), as mesmas
    `repeticoes` vezes num processo proprio, depois de uma rodada que so aquece (a primeira compila o bytecode da worktree). **Nenhuma
    medida da auditoria e gravada nem impressa:** so o tempo"""
    gab = gabaritos()
    linhas = []
    for x in vidas_an0()[:vidas]:
        g = gab["vidas"][(x[0], x[1], x[2], x[3])]
        rodadas = [rejogar_an0((*x, True, g))["parede_s"] for _ in range(repeticoes)]
        n = len(g["decisoes"])
        cf = min(r["contrafactual"] for r in rodadas)
        resto = min(r["replay"] - r["contrafactual"] for r in rodadas)
        red = min(r["reducao"] for r in rodadas)
        linhas.append({"vida": f"{x[0]}|{x[1]}|{x[2]}|{x[3]}", "decisoes": n, "rodadas_s": rodadas,
                       "a4_por_decisao_s": cf / n, "vida_sem_a4_por_decisao_s": resto / n, "reducao_por_decisao_s": red / n})
    a4 = max(x["a4_por_decisao_s"] for x in linhas)                       # a pior vida, para nao subestimar
    resto = max(x["vida_sem_a4_por_decisao_s"] for x in linhas)
    red = max(x["reducao_por_decisao_s"] for x in linhas)
    dec_c4 = 14 * 96                                                     # 14 dias x 96 decisoes (secao 8)
    replay_c4 = 3.15                                                     # o CPU por vida da C4 (A11.8), o replay sem leitura
    h = lambda s: s / MAX_PROCESSOS / 3600                               # noqa: E731
    proj = {"decisoes_por_vida_c4": dec_c4,
            "a4_por_vida_s": a4 * dec_c4, "reducao_por_vida_s": red * dec_c4, "vida_sem_a4_por_vida_s": resto * dec_c4,
            "a4_960_vidas_h": h(960 * a4 * dec_c4),
            "auditoria_inteira_h": h(4800 * (replay_c4 + red * dec_c4) + 960 * a4 * dec_c4),
            "auditoria_inteira_com_a_vida_medida_h": h(4800 * (resto + red) * dec_c4 + 960 * a4 * dec_c4),
            "nota": ("o tempo por decisao e o de parede (o process_time mede errado nesta maquina, D-PV0C-7), o minimo de "
                     f"{repeticoes} rodadas por vida e o pior das {vidas} vidas, na AN0 (codigo de hoje, 4 dias). A C4 roda o codigo do "
                     "a287ba2, de custo parecido mas nao medido aqui. A auditoria inteira soma o replay da C4 (3,15 s por vida, A11.8, ou a "
                     "vida medida aqui), a reducao das 4 800 vidas e o contrafactual das 960, com 4 processos")}
    c4 = None
    if codigo is not None:
        c4 = _tempo_c4(Path(codigo), Path(pasta_c4), repeticoes)
        proj["c4_medida"] = {"replay_sem_a4_s": c4["replay_sem_a4_s"], "a4_s": c4["a4_s"], "reducao_s": c4["reducao_s"],
                             "auditoria_inteira_h": h(4800 * (c4["replay_sem_a4_s"] + c4["reducao_s"]) + 960 * c4["a4_s"]),
                             "nota": ("uma vida da C4 no codigo do a287ba2 (1 344 decisoes), o minimo das rodadas depois do aquecimento; a "
                                      "reducao com o contrafactual vale como teto para as 4 800 vidas")}
    pior = max([proj["auditoria_inteira_h"], proj["auditoria_inteira_com_a_vida_medida_h"]]
               + ([proj["c4_medida"]["auditoria_inteira_h"]] if c4 else []))
    out = {"rotulo": "o tempo do A-4 nas sementes dos testes (secao 8 do plano): so o tempo, nenhuma medida", "vidas": linhas,
           "c4": c4, "projecao": proj, "corte_h": 8, "pior_projecao_h": pior, "passa_do_corte": pior > 8}
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "tempo_a4.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return out


def _tempo_c4(codigo: Path, pasta_c4: Path, repeticoes: int) -> dict:
    """o tempo de uma vida da C4 com o contrafactual (so o tempo; o resto da saida e descartado)"""
    import descritivo_dc13_longe_fixo as dc
    import descritivo_dc13_rel as drel
    ler_fontes_c4(pasta_c4)
    meta = json.loads((pasta_c4 / "meta.json").read_text(encoding="utf-8"))
    drel.conferir_codigo(codigo, meta)
    medidas, _ = drel.carregar_medidas(pasta_c4 / "medidas.json.gz", meta)
    vida = sorted((v for v in medidas.values() if v["braco"] == "REL" and v["lugar"] == "longe_fixo" and v["k"] == 0),
                  key=lambda v: v["vida"])[0]
    cfg = meta["config"]
    with tempfile.TemporaryDirectory() as tmp:
        logs = dc.extrair_logs(pasta_c4 / "vidas.tar.gz", [vida], Path(tmp))
        tarefa = (str(codigo), vida, str(logs[vida["vida"]]), cfg["dias"], cfg["orcamento_por_dia"], True)
        with ProcessPoolExecutor(max_workers=1) as pool:
            rodadas = [pool.submit(rejogar_c4, tarefa).result()["parede_s"] for _ in range(repeticoes + 1)][1:]
    return {"vida": vida["vida"], "decisoes": 14 * 96, "rodadas_s": rodadas,
            "replay_sem_a4_s": min(r["replay"] - r["contrafactual"] for r in rodadas),
            "a4_s": min(r["contrafactual"] for r in rodadas), "reducao_s": min(r["reducao"] for r in rodadas)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--codigo", type=Path, help="a worktree destacada do a287ba2")
    ap.add_argument("--pasta-c4", type=Path, default=PASTA_C4_PADRAO, help="a pasta da run da C4 (so lida)")
    ap.add_argument("--processos", type=int, default=1)
    ap.add_argument("--medir-tempo", action="store_true", help="so o tempo do A-4 nas sementes dos testes")
    a = ap.parse_args(argv)
    if a.medir_tempo:
        out = medir_tempo(codigo=None if a.codigo is None else a.codigo.resolve(), pasta_c4=a.pasta_c4)
        print(json.dumps({"pior_projecao_h": out["pior_projecao_h"], "passa_do_corte": out["passa_do_corte"]}, indent=1))
        return 0
    if a.codigo is None:
        ap.error("--codigo e obrigatorio para a auditoria")
    principal(a.codigo.resolve(), a.pasta_c4, a.processos)
    print(f"gravado: {SAIDA / 'auditoria.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
