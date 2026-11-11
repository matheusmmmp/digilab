"""O orquestrador do adendo 2 do I7 da INDIVIDUALIDADE: historia ou sorteio (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md, secao 14,
DECIDIDO pelo Matheus em 2026-11-11, AD2-1 a AD2-7 pela recomendacao).

Cada pet novo (AD2-1: os bracos REL e REL+F, os donos atencioso, relapso e aleatorio, as sementes da faixa 88101...88505) tem a vida de
base vivida aqui (a `viver` da C4) e os ramos (14.2), todos pelo laco do `simular_vida_fisico`:
  - N, o nulo, com os gravadores ligados (14.3): o log tem de ser o da vida de base, byte a byte (G-AD2-0);
  - G, o gemeo: a rng de politica trocada no nascimento, como no I7;
  - E(t), o evento: um tapa no momento do dia t, como no I7;
  - R(t), o evento com o sorteio amarrado (AD2-2): o tapa, e cada `random()` da rng de politica com a chave (tick, ordem no tick) recebe o
    numero que o original gravou com a mesma chave; a chave sem par recebe um numero da rng
    `derivar_semente("individualidade-i7-amarrado", semente, braco, dono, t)`. As rngs do dono (a do laco e as do `DonoComLugar`) voltam,
    no comeco de cada passo, ao estado que o original tinha no mesmo passo (AD2-4; D-IND-I7c-1);
  - R°, o amarrado sem evento: tem de sair igual ao N, byte a byte, e sem chave sem par (G-AD2-1);
  - S(t), o deslocamento sozinho (AD2-3): no passo do momento, um `random()` da rng de politica jogado fora, sem tapa.
O A(t) e o E°(t) nao entram (AD2-5). Nada no `digilab/`, no `engine.py`, no cerebro nem no `simular_vida_fisico` muda: os gravadores e o
amarrado ficam aqui, em volta do motor e do dono, como o embrulho do ramo do I7.

As contas de cada ramo sao as do I7 (as do `digilab/metrics.py`, com a `fracao_amarrada` e a `trajetoria_janela` do adendo 2). O bootstrap,
a leitura (14.4) e os descritivos (14.5) ficam aqui. As conferencias G-AD2-0 a 4 falham alto (14.6), e cada ramo e vivido duas vezes
(AD2-6).

A trava (14 e 14.7): a run so roda com o cabecalho "APROVADO pelo Matheus", o adendo 2 DECIDIDO no cabecalho, a secao nova do registro
(`## 15. O registro do adendo 2`, uma vez), as bases e o K da AD2-1 dentro da faixa reservada do adendo, no maximo 4 processos e nada por
cima de uma pasta. A fumaca (as sementes dos testes, 101...505) segue o mesmo caminho.

    python experiments/run_v3_individualidade_i7_ad2.py --config experiments/configs/v3_individualidade/individualidade_i7_ad2.json --processos 4
"""
from __future__ import annotations

import argparse
import array
import gzip
import io
import json
import platform
import random
import sys
import tarfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import run_v3_individualidade_i5 as i5  # noqa: E402
import run_v3_individualidade_i7 as r7  # noqa: E402
import sondas_individualidade as so  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab import metrics as M  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PLANO = r7.PLANO
MARCA_ADENDO = "**O adendo 2 (seção 14) está DECIDIDO pelo Matheus"
TITULO_REGISTRO = "## 15. O registro do adendo 2"                                     # 14.7: a secao nova no fim
FASE = "individualidade-i7-ad2"
BASES = (88101, 88202, 88303, 88404, 88505)                                           # AD2-1
K_POR_BASE, PREFIXO, LUGAR = r7.K_POR_BASE, r7.PREFIXO, r7.LUGAR                       # K = 12, como no I2
FONTE_FAIXA = "INDIVIDUALIDADE, I7, adendo 2"                                         # a linha da faixa em experiments/bancada/faixas.py
BRACOS, DONOS = r7.BRACOS, r7.DONOS
DIAS, ORCAMENTO_POR_DIA, DECISOES_POR_DIA = r7.DIAS, r7.ORCAMENTO_POR_DIA, r7.DECISOES_POR_DIA
IDADES, JANELA = r7.IDADES, r7.JANELA
LIMIAR_GEMEO = r7.LIMIAR_GEMEO                                                        # IR-7
LIMIAR_SORTEIO, LIMIAR_HISTORIA = 0.2, 0.8                                            # AD2-7, PROPOSTOS, SEM FONTE
MAX_PROCESSOS = r7.MAX_PROCESSOS                                                      # V3-D8
BOOTSTRAP = r7.BOOTSTRAP
SAIDA = "artifacts_v3_individualidade_i7_ad2"
CHAVES_CONFIG = r7.CHAVES_CONFIG
RAMOS = ("E", "R", "S")                                                               # os perturbados (14.2)
TAPA = r7.TAPA


# ================================================================== a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_plano_decidido(texto: str) -> None:
    """o cabecalho APROVADO (a trava do I7), o adendo 2 DECIDIDO no cabecalho e a secao do registro do adendo (uma vez)"""
    r7.exigir_plano_aprovado(texto)
    linhas = texto.splitlines()
    if not any(x.startswith(MARCA_ADENDO) for x in linhas[:30]):
        raise RuntimeError("o plano do I7 sem o adendo 2 DECIDIDO no cabecalho: nenhuma vida")
    if sum(1 for x in linhas if x.startswith(TITULO_REGISTRO)) != 1:
        raise RuntimeError(f"o plano do I7 sem a secao {TITULO_REGISTRO!r} (o registro do adendo 2, 14.7): nenhuma vida")


def modo_da_config(cfg: dict, texto_plano: str | None = None) -> str:
    """'fumaca' (as sementes dos testes) ou a fase do adendo (a faixa da AD2-1; a trava); o resto falha alto"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    if cfg["vidas"] is not None:
        raise ValueError("o adendo 2 vive as proprias vidas de base: `vidas` e null")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento ou o K")
    if cfg["dias"] != DIAS:
        raise ValueError(f"dias {cfg['dias']}: o I7 vive {DIAS} dias")
    if cfg.get("plano") != PLANO:
        raise ValueError(f"plano {cfg.get('plano')!r}")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou as da AD2-1 {list(BASES)}")
    for b in bases:
        fonte = bv.na_faixa_reservada(b)
        if fonte is None or FONTE_FAIXA not in fonte:
            raise bv.SementeSemPlano(f"a base {b} fora da faixa reservada do adendo 2 ({FONTE_FAIXA!r} em experiments/bancada/faixas.py)")
    exigir_plano_decidido(_plano() if texto_plano is None else texto_plano)
    if u["k"] != K_POR_BASE:
        raise ValueError(f"a run segue o plano a letra: K {u['k']}")
    return FASE


# ================================================================== o sorteio amarrado (14.3)
_PROIBIDOS = ("getrandbits", "randbytes", "randrange", "randint", "choice", "choices", "sample", "shuffle", "uniform", "triangular",
              "gauss", "normalvariate", "lognormvariate", "expovariate", "vonmisesvariate", "gammavariate", "betavariate",
              "paretovariate", "weibullvariate", "binomialvariate")


class _SoRandom(random.Random):
    """a rng de politica do braco so usa `random()` (o M-ARB, `digilab/digibrain/arb.py`); qualquer outro metodo levanta erro (14.3). A chave
    de cada chamada e (o tick do motor, a ordem da chamada no tick)."""

    def __init__(self, caixa: dict) -> None:
        super().__init__(0)
        self.caixa = caixa
        self._tick: int | None = None
        self._ordem = 0

    def _chave(self) -> tuple[int, int]:
        t = self.caixa["motor"]._estado.tick
        if t != self._tick:
            self._tick, self._ordem = t, 0
        k = (t, self._ordem)
        self._ordem += 1
        return k


def _proibido(nome):
    def f(self, *a, **k):
        raise RuntimeError(f"o sorteio amarrado: a rng de politica chamou {nome}(), e o braco so usa random() (14.3)")
    return f


for _n in _PROIBIDOS:
    setattr(_SoRandom, _n, _proibido(_n))


class RngGravador(_SoRandom):
    """a rng de politica do N: o mesmo fluxo (o estado copiado da rng do motor), e cada numero gravado pela chave"""

    def __init__(self, caixa: dict, estado) -> None:
        super().__init__(caixa)
        self.setstate(estado)
        self.tabela: dict[tuple[int, int], float] = {}

    def random(self) -> float:
        k = self._chave()
        u = super().random()
        self.tabela[k] = u
        return u


class RngAmarrado(_SoRandom):
    """a rng de politica do R e do R°: o numero do original na mesma chave; a chave sem par, da rng propria (14.3)"""

    def __init__(self, caixa: dict, tabela: dict, semente_sem_par: int) -> None:
        super().__init__(caixa)
        self.tabela = tabela
        self.sem_par_rng = random.Random(semente_sem_par)
        self.par = 0
        self.sem_par = 0

    def random(self) -> float:
        k = self._chave()
        if k in self.tabela:
            self.par += 1
            return self.tabela[k]
        self.sem_par += 1
        return self.sem_par_rng.random()


def _comprimir(estado) -> tuple:
    versao, interno, gauss = estado
    return (versao, array.array("I", interno).tobytes(), gauss)


def _descomprimir(c: tuple) -> tuple:
    versao, dados, gauss = c
    a = array.array("I")
    a.frombytes(dados)
    return (versao, tuple(a), gauss)


if array.array("I").itemsize != 4:
    raise RuntimeError("o estado da rng comprimido pede o array 'I' de 4 bytes")


class DonoAmarravel(r7.DonoRamo):
    """o embrulho do ramo do I7 com as rngs do dono (a do laco, passada ao `decidir`, e as do `DonoComLugar`): no N, o estado de cada uma no
    comeco de cada passo e gravado; no R e no R°, ele volta ao do original no mesmo passo (AD2-4). Um passo cujo fim (o comeco do
    seguinte) nao bate com o do original conta como descasado (14.5)."""

    def __init__(self, interno, caixa, momento, perturbar, modo: str | None, tabela: dict | None = None) -> None:
        super().__init__(interno, caixa, momento, perturbar)
        self.modo, self.tabela = modo, tabela
        self.estados: dict[int, list] = {}
        self.passos = 0
        self.descasados = 0

    def _rngs(self, rng) -> list:
        out = [rng, self.interno._rng]
        if self.interno._rng_fixo is not None:
            out.append(self.interno._rng_fixo)
        return out

    def decidir(self, visao, rng):
        tick = visao.estado["tick"]
        rngs = self._rngs(rng)
        if self.modo == "gravar":
            self.estados[tick] = [_comprimir(r.getstate()) for r in rngs]
        elif self.modo == "amarrar":
            orig = self.tabela.get(tick)
            if orig is None or len(orig) != len(rngs):
                raise RuntimeError(f"o sorteio amarrado: o original nao tem o passo do tick {tick}")
            if self.passos > 0 and [_comprimir(r.getstate()) for r in rngs] != orig:
                self.descasados += 1
            self.passos += 1
            for r, s in zip(rngs, orig):
                r.setstate(_descomprimir(s))
        return super().decidir(visao, rng)


def viver_ramo(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int, momento: int | None = None, perturbar=None,
               rng_nascimento: int | None = None, gravar: bool = False, amarrar: dict | None = None) -> dict:
    """uma vida de um ramo pelo laco do dono (o N, o G, o E, o R, o R° e o S); `gravar` liga os gravadores (o N); `amarrar` e o
    {"pol", "dono", "sem_par"} do original (o R e o R°)"""
    if gravar and amarrar is not None:
        raise ValueError("um ramo grava ou amarra, nao os dois")
    fp, fm = i5.fabricas_vida(braco, dono, semente, dias, orcamento_por_dia)
    caixa: dict = {}
    base = r7._lendo_estado(fm, caixa, rng_nascimento)

    def fabrica(politica, cfg, s):
        m = base(politica, cfg, s)
        if gravar:
            m._rng_politica = RngGravador(caixa, m._rng_politica.getstate())
        elif amarrar is not None:
            m._rng_politica = RngAmarrado(caixa, amarrar["pol"], amarrar["sem_par"])
        caixa["rng_pol"] = m._rng_politica
        return m
    modo = "gravar" if gravar else ("amarrar" if amarrar is not None else None)
    d = DonoAmarravel(DonoComLugar(criar_dono(dono), LUGAR, semente, dono, orq.CM), caixa, momento, perturbar, modo,
                      None if amarrar is None else amarrar["dono"])
    motor, _ = simular_vida_fisico(d, fp(CONFIG_PADRAO), semente, dias, orcamento_por_dia * dias, dono, fabrica)
    out = {"log": motor.log.para_jsonl(), "decisoes": motor.decisoes_mundo, "estados": caixa["estados"], "aplicado": d.aplicado}
    if gravar:
        out["tabela_pol"], out["tabela_dono"] = caixa["rng_pol"].tabela, d.estados
    if amarrar is not None:
        r = caixa["rng_pol"]
        out["amarrado"] = {"par": r.par, "sem_par": r.sem_par, "passos": d.passos, "passos_descasados": d.descasados}
    return out


def _duas_vezes(fazer, rotulo: str) -> dict:
    """G-AD2-2 (AD2-6): o ramo vivido duas vezes da a mesma vida (o log, as decisoes, os estados, as tabelas e as contagens do amarrado)"""
    a, b = fazer(), fazer()
    for k in ("log", "decisoes", "estados", "tabela_pol", "tabela_dono", "amarrado"):
        if a.get(k) != b.get(k):
            raise RuntimeError(f"G-AD2-2: {rotulo} vivido duas vezes deu outra vida ({k})")
    return a


# ================================================================== os ramos de um pet
def tarefa_pet(braco: str, dono: str, unidade: dict, dias: int, orcamento_por_dia: int, idades: tuple = IDADES,
               janela: int = JANELA) -> dict:
    """a vida de base e todos os ramos de um pet, com as conferencias G-AD2-0 a 4; devolve o log de base, os perfis e as linhas do
    `ramos.jsonl`"""
    p0 = time.perf_counter()
    semente = unidade["semente"]
    rot = f"{braco}|{dono}|{semente}"
    custo: dict = {}

    def cronometrar(nome, fazer):
        t = time.perf_counter()
        r = fazer()
        custo[nome] = time.perf_counter() - t
        return r

    motor_base, *_ = cronometrar("base", lambda: ma.viver(braco, dono, LUGAR, semente, dias, orcamento_por_dia))
    texto = motor_base.log.para_jsonl()
    if r7._contar_tapas(texto):
        raise RuntimeError(f"{rot}: a vida de base tem tapa")
    # G-AD2-0: o N, com os gravadores, e a vida de base byte a byte, com 96 decisoes por dia
    n = cronometrar("N", lambda: _duas_vezes(lambda: viver_ramo(braco, dono, semente, dias, orcamento_por_dia, gravar=True), f"{rot} N"))
    if n["log"] != texto:
        raise bv.ReplayDivergiu(f"G-AD2-0: {rot}: o ramo N nao e a vida de base")
    if i5.decisoes_por_dia(n["decisoes"], dias) != [DECISOES_POR_DIA] * dias:
        raise RuntimeError(f"G-AD2-0: {rot}: as decisoes por dia nao sao {DECISOES_POR_DIA}")
    todos = list(range(1, dias + 1))
    fp, fm = i5.fabricas_vida(braco, dono, semente, dias, orcamento_por_dia)
    mot = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm)
    momentos = {dia + 1: tick for dia, tick in so.momentos(mot, dias)}

    def amarrar(t):
        return {"pol": n["tabela_pol"], "dono": n["tabela_dono"],
                "sem_par": derivar_semente("individualidade-i7-amarrado", semente, braco, dono, t)}

    g = cronometrar("G", lambda: _duas_vezes(lambda: viver_ramo(
        braco, dono, semente, dias, orcamento_por_dia, rng_nascimento=derivar_semente("individualidade-i7-gemeo", semente, braco, dono)),
        f"{rot} G"))
    # G-AD2-1: o R° (o amarrado sem evento) e o N byte a byte, sem chave sem par e sem passo descasado
    r0 = cronometrar("R0", lambda: _duas_vezes(lambda: viver_ramo(braco, dono, semente, dias, orcamento_por_dia, amarrar=amarrar(0)),
                                                 f"{rot} R°"))
    if r0["log"] != n["log"] or r0["decisoes"] != n["decisoes"] or r0["estados"] != n["estados"]:
        raise RuntimeError(f"G-AD2-1: {rot}: o R° nao e o N")
    if r0["amarrado"]["sem_par"] or r0["amarrado"]["passos_descasados"] or r0["amarrado"]["par"] != len(n["tabela_pol"]):
        raise RuntimeError(f"G-AD2-1: {rot}: o R° com chave sem par ou passo descasado: {r0['amarrado']}")
    vidas = {("N", None): n, ("G", None): g, ("R0", None): r0}
    sem_ramo = []
    for t in idades:
        m = momentos[t]
        if m is None:
            sem_ramo.append(t)
            continue

        def tapa(motor):
            motor.observar(TAPA)

        def jogar_fora(motor):
            motor._rng_politica.random()
        vidas[("E", t)] = cronometrar(f"E{t}", lambda: _duas_vezes(
            lambda: viver_ramo(braco, dono, semente, dias, orcamento_por_dia, m, tapa), f"{rot} E({t})"))
        vidas[("R", t)] = cronometrar(f"R{t}", lambda: _duas_vezes(
            lambda: viver_ramo(braco, dono, semente, dias, orcamento_por_dia, m, tapa, amarrar=amarrar(t)), f"{rot} R({t})"))
        vidas[("S", t)] = cronometrar(f"S{t}", lambda: _duas_vezes(
            lambda: viver_ramo(braco, dono, semente, dias, orcamento_por_dia, m, jogar_fora), f"{rot} S({t})"))
        pre = [d for d in n["decisoes"] if d["tick"] < m]
        for b in RAMOS:
            if vidas[(b, t)]["aplicado"] != 1:                              # G-AD2-4: a perturbacao uma vez
                raise RuntimeError(f"G-AD2-4: {rot} {b}({t}): a perturbacao foi aplicada {vidas[(b, t)]['aplicado']} vezes")
            if [d for d in vidas[(b, t)]["decisoes"] if d["tick"] < m] != pre:   # G-AD2-3: o prefixo
                raise RuntimeError(f"G-AD2-3: {rot} {b}({t}): as decisoes antes do momento nao sao as do original")
            tapas = r7._contar_tapas(vidas[(b, t)]["log"])
            if tapas != ([m] if b in ("E", "R") else []):
                raise RuntimeError(f"G-AD2-4: {rot} {b}({t}): os tapas do log sao {tapas}")
    perfis = {("N", None): r7._perfis(n["decisoes"], todos), ("G", None): r7._perfis(g["decisoes"], todos)}
    parciais = {}
    linhas = []
    for (b, t), v in sorted(vidas.items(), key=lambda kv: (kv[0][0], kv[0][1] or 0)):
        linha = {"braco": braco, "dono": dono, "semente": semente, "base": unidade["base"], "k": unidade["k"], "ramo": b, "idade": t,
                 "momento": None if t is None else momentos[t], "log_sha256": r7._sha(v["log"]),
                 "decisoes_sha256": r7._sha_decisoes(v["decisoes"]),
                 "estado_sha256": {str(d): r7._sha(json.dumps(e, sort_keys=True, default=str)) for d, e in sorted(v["estados"].items())},
                 "amarrado": v.get("amarrado"),
                 "conferencias": {"G-AD2-0": b == "N", "G-AD2-1": b == "R0", "G-AD2-2": True, "G-AD2-3": b in RAMOS,
                                  "G-AD2-4": b in RAMOS}}
        if t is not None:
            usados = [d for d in range(t + 1, t + janela + 1) if d <= dias]
            perfis[(b, t)] = r7._perfis(v["decisoes"], usados)
            parciais[(b, t)] = r7._perfis(v["decisoes"], [t], momentos[t])[t]
            for ref in ("N", "G"):
                parciais.setdefault((ref, t), r7._perfis(vidas[(ref, None)]["decisoes"], [t], momentos[t])[t])
            linha["estado"] = {str(d): M.distancia_estado(v["estados"][d], n["estados"][d]) for d in usados}
            linha["estado_gemeo"] = {str(d): M.distancia_estado(g["estados"][d], n["estados"][d]) for d in usados}
            linha["reencontro_ultimo_dia"] = M.reencontrou(v["decisoes"], n["decisoes"], dias)
            ev, ov = v["estados"][t], n["estados"][t]                     # 14.5: o M-ARB no fim do dia t
            linha["arb_fim_do_dia_t"] = {c: ev.get(f"arb.{c}") == ov.get(f"arb.{c}") for c in ("sorteios", "reflexos")}
        linhas.append(linha)
    custo["pet_parede"] = time.perf_counter() - p0
    return {"vida": rot, "braco": braco, "dono": dono, "semente": semente, "base": unidade["base"], "k": unidade["k"], "log_base": texto,
            "momentos": {str(t): momentos[t] for t in idades}, "sem_ramo": sem_ramo, "perfis": perfis, "parciais": parciais,
            "ramos": linhas, "custo": custo}


def tarefa(lote: list[tuple], dias: int, orcamento_por_dia: int) -> list[dict]:
    return [tarefa_pet(b, d, u, dias, orcamento_por_dia) for b, d, u in lote]


# ================================================================== a analise
def distancias_do_pet(p: dict, perfil: str, idades: tuple, janela: int, dias: int) -> dict:
    """as D de um pet num perfil (as do I7, para os ramos E, R e S)"""
    orig = r7._um_perfil(p["perfis"][("N", None)], perfil)
    gem = r7._um_perfil(p["perfis"][("G", None)], perfil)
    out = {"D": {}, "D0": {}, "DG0": {}, "DG": M.distancias_ramo(gem, orig, list(range(1, dias + 1)))}
    for t in idades:
        usados = [d for d in range(t + 1, t + janela + 1) if d <= dias]
        for b in RAMOS:
            if (b, t) not in p["perfis"]:
                continue
            out["D"][(b, t)] = M.distancias_ramo(r7._um_perfil(p["perfis"][(b, t)], perfil), orig, usados)
            ram, ori = p["parciais"][(b, t)].get(perfil), p["parciais"][("N", t)].get(perfil)
            out["D0"][(b, t)] = None if ram is None or ori is None else M.distancia_tv(ram, ori)
        if ("N", t) in p["parciais"]:
            gp, op = p["parciais"][("G", t)].get(perfil), p["parciais"][("N", t)].get(perfil)
            out["DG0"][t] = None if gp is None or op is None else M.distancia_tv(gp, op)
    return out


def agregados(pets: dict, braco: str, perfil: str, idades: tuple, janela: int, dias: int) -> dict:
    """as somas do I7 por semente e por dono, {chave: [soma do numerador, soma do denominador, pares]}, com as chaves (b, t, k) do E, do R,
    do S e do G (a regua crua) e as chaves ("rho", t, k) do rho, os pares (D_R, D_E) com os dois termos (14.4)"""
    out: dict = {}
    for (br, dono, s), p in sorted(pets.items()):
        if br != braco:
            continue
        x = distancias_do_pet(p, perfil, idades, janela, dias)
        alvo = out.setdefault(s, {"total": {}, "dono": {}})

        def somar(chave, a, g):
            if a is None or g is None:
                return
            for dest in (alvo["total"], alvo["dono"].setdefault(dono, {})):
                v = dest.setdefault(chave, [0.0, 0.0, 0])
                v[0] += a
                v[1] += g
                v[2] += 1
        for (b, t), por_dia in x["D"].items():
            for d, v in por_dia.items():
                somar((b, t, d - t), v, x["DG"].get(d))
            somar((b, t, 0), x["D0"][(b, t)], x["DG0"].get(t))
        for t in idades:
            for k in range(1, janela + 1):
                if t + k <= dias:
                    g = x["DG"].get(t + k)
                    somar(("G", t, k), g, g)
                    if ("R", t) in x["D"] and ("E", t) in x["D"]:
                        somar(("rho", t, k), x["D"][("R", t)].get(t + k), x["D"][("E", t)].get(t + k))
    return out


def todas_as_chaves(idades: tuple, janela: int) -> list[tuple]:
    return [(b, t, k) for b in RAMOS + ("G", "rho") for t in idades for k in range(0, janela + 1)]


def chaves_de(nome: str, idades: tuple, janela: int) -> list[tuple]:
    ks = range(1, janela + 1)
    if nome == "rho":
        return [("rho", t, k) for t in idades for k in ks]
    if nome.startswith("rho("):
        return [("rho", int(nome[4:-1]), k) for k in ks]
    return r7.chaves_de(nome, idades, janela)


def valor(nome: str, tot: dict, idades: tuple, janela: int) -> float | None:
    """as estatisticas do I7 (o `valor` dele) e o rho (14.4)"""
    if nome == "rho" or nome.startswith("rho("):
        vs = [tot[c] for c in chaves_de(nome, idades, janela) if c in tot and tot[c][2] > 0]
        return M.fracao_amarrada([(v[0], v[1]) for v in vs])
    return r7.valor(nome, tot, idades, janela)


def bootstrap(por: dict, nomes: list[str], rotulo: tuple, idades: tuple, janela: int, boot: int) -> dict:
    """o IC95 percentil, reamostrando as sementes com repeticao (3.6), com a rng `individualidade-i7-ad2-boot` (14.4)"""
    sementes = sorted(por)
    out = {}
    for nome in nomes:
        chaves = chaves_de(nome, idades, janela)
        rng = random.Random(derivar_semente("individualidade-i7-ad2-boot", *rotulo, nome))
        vs = []
        for _ in range(boot):
            amostra = [rng.choice(sementes) for _ in sementes]
            v = valor(nome, r7._somar_sementes(por, amostra, chaves), idades, janela)
            if v is not None:
                vs.append(v)
        out[nome] = r7._percentis(vs)
    return out


COM_IC = (["Phi_E({t})", "Phi_R({t})", "Phi_S({t})", "Phi0_E({t})", "Phi0_R({t})"],
          ["rho", "gamma_E", "gamma_R", "gamma_S", "gamma_cru_E", "gamma_cru_R", "gamma_cru_S", "gamma_cru_G",
           "Phi_E(todas)", "Phi_R(todas)", "Phi_S(todas)"])
SEM_IC = (["rho({t})", "Phi0_S({t})"], ["beta_E", "beta_R", "beta_S"])                 # so o ponto, no descritivo


def nomes_com_ic(idades: tuple) -> list[str]:
    return [n.format(t=t) for n in COM_IC[0] for t in idades] + COM_IC[1]


def nomes_todos(idades: tuple) -> list[str]:
    return nomes_com_ic(idades) + [n.format(t=t) for n in SEM_IC[0] for t in idades] + SEM_IC[1]


def pontos(por: dict, idades: tuple, janela: int, dono: str | None = None) -> dict:
    tot = r7._somar_sementes(por, sorted(por), todas_as_chaves(idades, janela), dono=dono)
    return {n: valor(n, tot, idades, janela) for n in nomes_todos(idades)}


def leitura(ic: dict, idades: tuple) -> dict:
    """as frases que a leitura pode escrever (14.4), pelos ICs de um braco num perfil"""
    acima, abaixo = r7._acima, r7._abaixo
    fr: dict = {}
    pegou_e = any(acima(ic.get(f"Phi0_E({t})"), 0) for t in idades)
    pegou_r = any(acima(ic.get(f"Phi0_R({t})"), 0) for t in idades)
    fr["condicao_do_evento"] = "o tapa mudou o dia em ao menos uma idade" if pegou_e else "o tapa nao mudou o dia"
    fr["condicao_do_amarrado"] = ("o tapa amarrado mudou o dia em ao menos uma idade" if pegou_r
                                  else "com o sorteio amarrado, o tapa nao mudou o dia")
    rho = ic.get("rho")
    if not pegou_e:
        h = "nenhuma hipotese se declara: o tapa nao mudou o dia"
    elif abaixo(rho, LIMIAR_SORTEIO):
        h = "H-SORT"
    elif acima(rho, LIMIAR_HISTORIA):
        h = "H-HIST"
    elif acima(rho, LIMIAR_SORTEIO) and abaixo(rho, LIMIAR_HISTORIA):
        h = "os dois pesam"
    else:
        h = "rho nao se separa do limiar nesta analise"
    fr["hipotese"] = h
    phis = [ic.get(f"Phi_S({t})") for t in idades]
    if all(acima(c, LIMIAR_GEMEO) for c in phis):
        fr["S"] = "deslocar o fluxo em um sorteio faz do pet um gemeo"
    elif all(abaixo(c, LIMIAR_GEMEO) for c in phis):
        fr["S"] = "deslocar o fluxo em um sorteio nao basta para um gemeo"
    else:
        fr["S"] = "nao se distingue do limiar nesta analise"
    if not pegou_r:
        fr["gamma_R"] = "com o sorteio amarrado, o tapa nao mudou o dia"
    else:
        r, c = ic.get("gamma_R"), ic.get("gamma_cru_R")
        if acima(r, 0):
            fr["gamma_R"] = "o efeito amarrado cresce com os dias" if acima(c, 0) else "a inclinacao vem da regua: o D_b cru nao se distingue de parado"
        elif abaixo(r, 0):
            fr["gamma_R"] = "o efeito amarrado some com os dias" if abaixo(c, 0) else "a inclinacao vem da regua: o D_b cru nao se distingue de parado"
        else:
            fr["gamma_R"] = "nao se distingue de zero nesta analise"
    return fr


def _fracoes(contagem: dict) -> dict:
    n = sum(contagem.values())
    return {"n": n, **{k: (v / n if n else None) for k, v in sorted(contagem.items())}}


def descritivo(pets: dict, por: dict, linhas_ramos: list[dict], braco: str, perfil: str, idades: tuple, janela: int, dias: int) -> dict:
    """os descritivos sem frase (14.5): por dono, a regua crua, o tudo ou nada do E e do R, a separacao pelo M-ARB, as chaves sem par e os
    passos descasados do R, o Phi^est e o reencontro"""
    out: dict = {"por_dono": {d: pontos(por, idades, janela, dono=d) for d in DONOS}}
    tot = r7._somar_sementes(por, sorted(por), todas_as_chaves(idades, janela))
    out["regua_crua"] = {f"{b}|{t}|{k}": {"soma_num": v[0], "soma_den": v[1], "pares": v[2]} for (b, t, k), v in sorted(tot.items())}
    traj: dict = {}
    contagens = {b: {"total": {}, "dono": {}} for b in ("E", "R")}
    for (br, dono, s), p in sorted(pets.items()):
        if br != braco:
            continue
        x = distancias_do_pet(p, perfil, idades, janela, dias)
        for (b, t), por_dia in x["D"].items():
            if b not in contagens:
                continue
            c = M.trajetoria_janela([por_dia[d] for d in sorted(por_dia)])
            traj[(b, dono, s, t)] = c
            if c is None:
                continue
            for dest in (contagens[b]["total"], contagens[b]["dono"].setdefault(dono, {})):
                dest[c] = dest.get(c, 0) + 1
    out["tudo_ou_nada"] = {b: {"total": _fracoes(v["total"]), "por_dono": {d: _fracoes(x) for d, x in sorted(v["dono"].items())}}
                           for b, v in contagens.items()}
    cruz: dict = {}
    for r in linhas_ramos:
        if r["braco"] != braco or r["ramo"] not in ("E", "R"):
            continue
        g = traj.get((r["ramo"], r["dono"], r["semente"], r["idade"]))
        a = r["arb_fim_do_dia_t"]
        chave = (f"{r['ramo']}|{g}|sorteios {'iguais' if a['sorteios'] else 'diferentes'}|"
                 f"reflexos {'iguais' if a['reflexos'] else 'diferentes'}")
        cruz[chave] = cruz.get(chave, 0) + 1
    out["separacao_pelo_arb"] = dict(sorted(cruz.items()))
    am: dict = {}
    for r in linhas_ramos:
        if r["braco"] == braco and r["ramo"] == "R":
            for dest in (am.setdefault("total", [0, 0, 0, 0]), am.setdefault(r["dono"], [0, 0, 0, 0])):
                x = r["amarrado"]
                dest[0] += x["sem_par"]
                dest[1] += x["par"] + x["sem_par"]
                dest[2] += x["passos_descasados"]
                dest[3] += x["passos"]
    out["amarrado_R"] = {k: {"fracao_sem_par": v[0] / v[1] if v[1] else None, "fracao_passos_descasados": v[2] / v[3] if v[3] else None}
                         for k, v in sorted(am.items())}
    est: dict = {}
    for r in linhas_ramos:
        if r["braco"] == braco and r["idade"] is not None:
            est.setdefault(f"{r['ramo']}|{r['idade']}", []).extend((r["estado"][d], r["estado_gemeo"][d]) for d in r["estado"])
    out["Phi_est"] = {k: M.razao_de_somas(v) for k, v in sorted(est.items())}
    out["reencontro_dia_final"] = {}
    for b in RAMOS:
        reenc = [r["reencontro_ultimo_dia"] for r in linhas_ramos if r["braco"] == braco and r["ramo"] == b]
        out["reencontro_dia_final"][b] = {"fracao": sum(reenc) / len(reenc) if reenc else None, "n": len(reenc)}
    return out


def analisar(pets: dict, linhas_ramos: list[dict], dias: int, idades: tuple = IDADES, janela: int = JANELA, boot: int = BOOTSTRAP) -> dict:
    out: dict = {"idades": list(idades), "janela": janela, "bootstrap": boot, "limiar_gemeo": LIMIAR_GEMEO,
                 "limiares_rho": [LIMIAR_SORTEIO, LIMIAR_HISTORIA], "por_braco": {},
                 "multiplicidade": "3 perfis x 2 bracos, sem correcao (14.4): plano de leitura, nao de gate"}
    nomes = nomes_com_ic(idades)
    for braco in BRACOS:
        bloco = out["por_braco"][braco] = {"por_perfil": {}}
        for perfil in M.PERFIS_HABITO:
            por = agregados(pets, braco, perfil, idades, janela, dias)
            ic = bootstrap(por, nomes, (braco, perfil), idades, janela, boot)
            bloco["por_perfil"][perfil] = {"ponto": pontos(por, idades, janela), "ic95": ic, "leitura": leitura(ic, idades),
                                           "descritivo": descritivo(pets, por, linhas_ramos, braco, perfil, idades, janela, dias)}
    return out


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None, boot: int = BOOTSTRAP) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python"] + [Path(sys.argv[0]).as_posix()] + sys.argv[1:]),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)),
            "orquestrador_i7_sha256": rc._sha_arquivo(RAIZ / "experiments" / "run_v3_individualidade_i7.py"),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "",
            "processos": processos, "unidades": unidades, "bracos": list(BRACOS), "donos": list(DONOS), "lugar": LUGAR, "bootstrap": boot,
            "idades": list(IDADES), "janela": JANELA,
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py")},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    lotes = [[(b, d, u)] for u in unidades for b in BRACOS for d in DONOS]
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (lote, cfg["dias"], cfg["orcamento_por_dia"])) for lote in lotes], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    if len(registros) != len(lotes):
        raise RuntimeError(f"{len(registros)} pets, eram {len(lotes)}")
    registros = sorted(registros, key=lambda r: r["vida"])
    with tarfile.open(pasta / "vidas.tar.gz", "w:gz") as tar:          # as vidas de base (14.1)
        for r in registros:
            dados = r["log_base"].encode("utf-8")
            info = tarfile.TarInfo(i5.nome_da_vida(r["braco"], r["dono"], r["semente"]))
            info.size = len(dados)
            tar.addfile(info, io.BytesIO(dados))
    with gzip.open(pasta / "perfis.jsonl.gz", "wt", encoding="utf-8", newline="\n") as f:
        for r in registros:
            for linha in r7.linhas_perfis(r):
                f.write(json.dumps(linha, sort_keys=True) + "\n")
    linhas_ramos = [linha for r in registros for linha in r["ramos"]]
    with (pasta / "ramos.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for linha in linhas_ramos:
            f.write(json.dumps(linha, sort_keys=True) + "\n")
    pets = r7.ler_perfis(pasta / "perfis.jsonl.gz")             # a analise sai do artefato gravado
    r7.conferir_lidos(pets, registros)
    lidas = [json.loads(x) for x in (pasta / "ramos.jsonl").read_text(encoding="utf-8").splitlines()]
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "pets": len(pets), **analisar(pets, lidas, cfg["dias"], boot=boot)}
    resultado["sem_ramo"] = {f"{r['braco']}|{r['dono']}|{r['semente']}": r["sem_ramo"] for r in registros if r["sem_ramo"]}
    bv._gravar(pasta / "analise.json", bv._dump(resultado))
    custos = [r["custo"]["pet_parede"] for r in registros]
    por_ramo: dict = {}
    for r in registros:
        for k, v in r["custo"].items():
            if k != "pet_parede":
                por_ramo.setdefault(k.rstrip("0123456789") or k, []).append(v)
    bv._gravar(pasta / "custo.json", bv._dump({"pets": len(custos), "parede_media_pet_s": sum(custos) / len(custos), "parede_max_pet_s": max(custos),
                                               "total_parede_s": meta["vidas_parede_s"],
                                               "por_ramo_media_s": {k: sum(v) / len(v) for k, v in sorted(por_ramo.items())},
                                               "nota": "cada ramo e vivido duas vezes (G-AD2-2); o tempo do ramo e o das duas; a base, uma"}))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("vidas.tar.gz", "perfis.jsonl.gz", "ramos.jsonl", "analise.json", "custo.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    if modo == "fumaca" and a.saida is None:
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA}/)")
    r = rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)
    res = r["resultado"]
    print(json.dumps({"modo": res["modo"], "pets": res["pets"], "custo_medio_pet_s": r["meta"]["vidas_parede_s"] / res["pets"],
                      "hipotese": {b: {p: x["leitura"]["hipotese"] for p, x in v["por_perfil"].items()} for b, v in res["por_braco"].items()}},
                     indent=1, ensure_ascii=True))


if __name__ == "__main__":
    main()
