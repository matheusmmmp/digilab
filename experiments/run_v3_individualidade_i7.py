"""O orquestrador do I7 da INDIVIDUALIDADE: o desenvolvimento contrafactual (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md, APROVADO em
2026-11-10, com o adendo 1 DECIDIDO).

Cada pet do I2 (IR-1: os bracos REL e REL+F, os donos atencioso, relapso e aleatorio, as sementes da faixa 85101...85505) e vivido de novo
pelo laco do `simular_vida_fisico`, com as fabricas da `viver` da C4, em ramos (2.2):
  - N, o nulo: o embrulho do ramo ligado e nada perturbado; o log tem de ser o do `vidas.tar.gz`, byte a byte (G-I7-0);
  - G, o gemeo: a rng de politica trocada no nascimento, `derivar_semente("individualidade-i7-gemeo", semente, braco, dono)`;
  - A(t), o acaso: a rng de politica trocada no momento do dia t, `derivar_semente("individualidade-i7-acaso", semente, braco, dono, t)`;
  - E(t), o evento: um tapa no momento do dia t (a rng de politica a mesma);
  - E°(t), a malha aberta (IR-5): o log do I2 com o tapa inserido no momento, rejogado (o dono repete os gestos do original).
O embrulho do ramo fica em volta do dono (`DonoRamo`): no passo do momento, aplica a perturbacao no motor e depois deixa o dono decidir.
Nada no `digilab/`, no `engine.py`, no cerebro nem no `simular_vida_fisico` muda. O estado interno do fim de cada dia (12.5) e lido por um
embrulho so de leitura do `_avancar` do motor.

As contas de cada ramo (os perfis do I5 por dia, a D_b(d), a razao contra o gemeo, as inclinacoes, a distancia do estado, o efeito comum e
o reencontro) sao as do `digilab/metrics.py` (secoes do I5 e do I7). O bootstrap sobre as sementes, os contrastes e a leitura (secoes 4, 7 e
12) ficam aqui. As conferencias G-I7-0 a 3 falham alto (secao 5).

A trava (secoes 0, 9 e 10 do plano): a run de pesquisa so roda com o cabecalho "APROVADO pelo Matheus", a secao nova do registro da analise
(`## 13. O registro da análise`, uma vez), o `vidas.tar.gz` do I2, as bases e o K do I2, no maximo 4 processos e nada por cima de uma
pasta. A fumaca (as sementes dos testes, 101...505) vive as proprias vidas de base (a `viver` da C4) e segue o mesmo caminho.

    python experiments/run_v3_individualidade_i7.py --config experiments/configs/v3_individualidade/individualidade_i7.json --processos 4
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import platform
import random
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import run_v3_individualidade as ri  # noqa: E402
import run_v3_individualidade_i5 as i5  # noqa: E402
import sondas_individualidade as so  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab import metrics as M  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md"
MARCA_APROVADO = ri.MARCA_APROVADO
TITULO_REGISTRO = "## 13. O registro da análise"                                      # secao 10 do plano: a secao nova no fim
FASE = "individualidade-i7"
VIDAS_I2 = i5.VIDAS_I2                                                                # IR-1
BASES, K_POR_BASE, PREFIXO, LUGAR = ri.BASES, ri.K_POR_BASE, ri.PREFIXO, ri.LUGAR     # as do I2
BRACOS = ri.BRACOS                                                                    # IR-2
DONOS = i5.DONOS                                                                      # o incoerente sai (D-IND-I2c-2)
DIAS, ORCAMENTO_POR_DIA = ri.DIAS, ri.ORCAMENTO_POR_DIA                               # 14 dias, 16 por dia
DECISOES_POR_DIA = i5.DECISOES_POR_DIA
IDADES = (2, 4, 6, 8, 10)                                                             # IR-3 (o dia 1 e o do nascimento)
JANELA = 4                                                                            # 3.2: os dias t+1 a t+4
LIMIAR_GEMEO = 0.8                                                                    # IR-7, PROPOSTO, SEM FONTE
MAX_PROCESSOS = ri.MAX_PROCESSOS                                                      # V3-D8
BOOTSTRAP = 2000                                                                      # 3.6
SAIDA = "artifacts_v3_individualidade_i7"
CHAVES_CONFIG = {"descricao", "fase", "plano", "vidas", "unidades", "dias", "orcamento_por_dia"}
RAMOS_PERTURBADOS = ("A", "E", "E0")                                                  # E0 e o E° (a malha aberta)
TAPA = AcaoUsuario.TAPA                                                               # IR-8


# ================================================================== a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_plano_aprovado(texto: str) -> None:
    """o cabecalho do plano tem a marca "APROVADO pelo Matheus" e a secao nova do registro da analise existe (uma vez)"""
    linhas = texto.splitlines()
    status = next((x for x in linhas[1:12] if x.startswith("**Status:")), None)
    if status is None or not status.startswith(MARCA_APROVADO):
        raise RuntimeError("o plano do I7 sem o status APROVADO pelo Matheus no cabecalho: nenhuma vida")
    if sum(1 for x in linhas if x.startswith(TITULO_REGISTRO)) != 1:
        raise RuntimeError(f"o plano do I7 sem a secao {TITULO_REGISTRO!r} (o registro da analise, secao 10): nenhuma vida")


def modo_da_config(cfg: dict, texto_plano: str | None = None) -> str:
    """'fumaca' (as sementes dos testes, as vidas de base feitas aqui) ou 'individualidade-i7' (as vidas do I2; a trava); o resto falha alto"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento ou o K")
    if cfg["dias"] != DIAS:
        raise ValueError(f"dias {cfg['dias']}: o I7 vive {DIAS} dias (a idade 10 com a janela de {JANELA} dias)")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if cfg["vidas"] is not None:
            raise ValueError("a fumaca vive as proprias vidas de base: `vidas` e null")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou as do I2 {list(BASES)} (IR-1)")
    exigir_plano_aprovado(_plano() if texto_plano is None else texto_plano)
    erros = [f"K {u['k']}"] if u["k"] != K_POR_BASE else []
    erros += [f"plano {cfg.get('plano')!r}"] if cfg.get("plano") != PLANO else []
    erros += [f"vidas {cfg.get('vidas')!r}"] if cfg.get("vidas") != VIDAS_I2 else []
    if erros:
        raise ValueError(f"a run segue o plano a letra: {erros}")
    return FASE


# ================================================================== os ramos
class DonoRamo:
    """O embrulho do ramo em volta do dono (2.2): no passo do momento (o tick do motor igual ao `momento`), aplica `perturbar(motor)` e depois
    deixa o dono decidir. Fora do momento, so repassa. O dono ve a visao calculada antes da perturbacao (a do passo; D-IND-I7a-1)."""

    def __init__(self, interno, caixa: dict, momento: int | None, perturbar) -> None:
        self.interno, self.caixa, self.momento, self.perturbar = interno, caixa, momento, perturbar
        self.aplicado = 0

    def decidir(self, visao, rng):
        if self.momento is not None and visao.estado["tick"] == self.momento:
            self.perturbar(self.caixa["motor"])
            self.aplicado += 1
        return self.interno.decidir(visao, rng)

    def __getattr__(self, nome):
        return getattr(self.interno, nome)


def _lendo_estado(fm, caixa: dict, rng_nascimento: int | None = None):
    """a fabrica do motor da vida, com (a) a rng de politica do nascimento trocada (o ramo G) e (b) o estado interno do cerebro lido no fim de
    cada dia, pelo `_avancar` do motor, so de leitura (12.5)"""
    def fabrica(politica, cfg, s):
        m = fm(politica, cfg, s)
        if rng_nascimento is not None:
            m._rng_politica = random.Random(rng_nascimento)
        caixa["motor"], caixa["estados"] = m, {}
        avancar = m._avancar

        def _avancar(ticks):
            r = avancar(ticks)
            tick = m._estado.tick
            if tick % M.TICKS_POR_DIA == 0 and tick > 0:
                c = orq.cerebro_de(m.politica)
                caixa["estados"][tick // M.TICKS_POR_DIA] = M.folhas_estado(json.loads(json.dumps(c.estado_interno()["modulos"], default=str)))
            return r
        m._avancar = _avancar
        return m
    return fabrica


def viver_ramo(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int, momento: int | None = None, perturbar=None,
               rng_nascimento: int | None = None) -> dict:
    """uma vida de um ramo pelo laco do dono (o N, o G, o A e o E); devolve o log, as decisoes, os estados do fim de cada dia e quantas vezes
    a perturbacao foi aplicada"""
    fp, fm = i5.fabricas_vida(braco, dono, semente, dias, orcamento_por_dia)
    caixa: dict = {}
    d = DonoRamo(DonoComLugar(criar_dono(dono), LUGAR, semente, dono, orq.CM), caixa, momento, perturbar)
    motor, _ = simular_vida_fisico(d, fp(CONFIG_PADRAO), semente, dias, orcamento_por_dia * dias, dono, _lendo_estado(fm, caixa, rng_nascimento))
    return {"log": motor.log.para_jsonl(), "decisoes": motor.decisoes_mundo, "estados": caixa["estados"], "aplicado": d.aplicado}


def log_com_tapa(texto: str, momento: int) -> str:
    """o log do original com o tapa no tick do momento, antes do primeiro evento desse tick (onde o embrulho do ramo E o poe: depois do
    avanco que chega ao momento e antes dos gestos do dono do passo)"""
    linhas = texto.splitlines()
    i = next((k for k, x in enumerate(linhas) if json.loads(x)["tick"] >= momento), None)
    if i is None:
        raise ValueError(f"o momento {momento} passa do fim do log")
    tapa = json.dumps({"tick": momento, "tipo": "acao_usuario", "valor": TAPA.value})
    return "\n".join(linhas[:i] + [tapa] + linhas[i:]) + ("\n" if texto.endswith("\n") else "")


def rejogar_ramo(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int, texto: str) -> dict:
    """o E° (a malha aberta): o log dado, rejogado; os mesmos campos da `viver_ramo`"""
    fp, fm = i5.fabricas_vida(braco, dono, semente, dias, orcamento_por_dia)
    caixa: dict = {}
    motor = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=_lendo_estado(fm, caixa))
    if motor.log.para_jsonl() != texto:
        raise bv.ReplayDivergiu(f"{braco}|{dono}|{semente}: o E° rejogado nao devolve o log dado")
    return {"log": texto, "decisoes": motor.decisoes_mundo, "estados": caixa["estados"], "aplicado": 1}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _sha_decisoes(decisoes: list[dict]) -> str:
    return _sha(json.dumps(decisoes, sort_keys=True))


def _duas_vezes(fazer, rotulo: str) -> dict:
    """G-I7-1 (IR-6): o ramo vivido duas vezes da o mesmo log e as mesmas decisoes"""
    a, b = fazer(), fazer()
    if a["log"] != b["log"] or a["decisoes"] != b["decisoes"] or a["estados"] != b["estados"]:
        raise RuntimeError(f"G-I7-1: {rotulo} vivido duas vezes deu outra vida")
    return a


def _perfis(decisoes: list[dict], dias: list[int], desde: int | None = None) -> dict:
    ds = decisoes if desde is None else [d for d in decisoes if d["tick"] >= desde]
    return {d: M.perfis_habito_dia(ds, d) for d in dias}


def _contar_tapas(texto: str) -> list[int]:
    return [e["tick"] for e in (json.loads(x) for x in texto.splitlines()) if e["tipo"] == "acao_usuario" and e["valor"] == TAPA.value]


def tarefa_pet(braco: str, dono: str, unidade: dict, texto: str, dias: int, orcamento_por_dia: int, idades: tuple = IDADES,
               janela: int = JANELA) -> dict:
    """todos os ramos de um pet, com as conferencias G-I7-0 a 3; devolve os perfis dos dias usados e as linhas do `ramos.jsonl`"""
    p0 = time.perf_counter()
    semente = unidade["semente"]
    rot = f"{braco}|{dono}|{semente}"
    custo: dict = {}

    def cronometrar(nome, fazer):
        t = time.perf_counter()
        r = fazer()
        custo[nome] = time.perf_counter() - t
        return r

    # N, o nulo (G-I7-0): o log do I2, byte a byte, e 96 decisoes por dia
    n = cronometrar("N", lambda: _duas_vezes(lambda: viver_ramo(braco, dono, semente, dias, orcamento_por_dia), f"{rot} N"))
    if n["log"] != texto:
        raise bv.ReplayDivergiu(f"G-I7-0: {rot}: o ramo N nao e o log do I2")
    if i5.decisoes_por_dia(n["decisoes"], dias) != [DECISOES_POR_DIA] * dias:
        raise RuntimeError(f"G-I7-0: {rot}: as decisoes por dia nao sao {DECISOES_POR_DIA}")
    if _contar_tapas(texto):
        raise RuntimeError(f"{rot}: a vida do I2 tem tapa (secao 0: nunca recebe)")
    todos = list(range(1, dias + 1))

    # o motor do original, para os momentos (a regra das sondas, 2.1): o replay do log
    fp, fm = i5.fabricas_vida(braco, dono, semente, dias, orcamento_por_dia)
    mot = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm)
    momentos = {dia + 1: tick for dia, tick in so.momentos(mot, dias)}

    g = cronometrar("G", lambda: _duas_vezes(lambda: viver_ramo(
        braco, dono, semente, dias, orcamento_por_dia, rng_nascimento=derivar_semente("individualidade-i7-gemeo", semente, braco, dono)),
        f"{rot} G"))
    vidas = {("N", None): n, ("G", None): g}
    sem_ramo = []
    for t in idades:
        m = momentos[t]
        if m is None:
            sem_ramo.append(t)
            continue
        rng_a = derivar_semente("individualidade-i7-acaso", semente, braco, dono, t)

        def troca(motor, rng_a=rng_a):
            motor._rng_politica = random.Random(rng_a)

        def tapa(motor):
            motor.observar(TAPA)
        vidas[("A", t)] = cronometrar(f"A{t}", lambda: _duas_vezes(lambda: viver_ramo(braco, dono, semente, dias, orcamento_por_dia, m, troca),
                                                                     f"{rot} A({t})"))
        vidas[("E", t)] = cronometrar(f"E{t}", lambda: _duas_vezes(lambda: viver_ramo(braco, dono, semente, dias, orcamento_por_dia, m, tapa),
                                                                     f"{rot} E({t})"))
        texto_e0 = log_com_tapa(texto, m)
        vidas[("E0", t)] = cronometrar(f"E0{t}", lambda: _duas_vezes(lambda: rejogar_ramo(braco, dono, semente, dias, orcamento_por_dia,
                                                                                            texto_e0), f"{rot} E°({t})"))
        for b in ("A", "E"):
            if vidas[(b, t)]["aplicado"] != 1:
                raise RuntimeError(f"{rot} {b}({t}): a perturbacao foi aplicada {vidas[(b, t)]['aplicado']} vezes")
        # G-I7-2: as decisoes antes do momento sao as do original
        pre = [d for d in n["decisoes"] if d["tick"] < m]
        for b in RAMOS_PERTURBADOS:
            if [d for d in vidas[(b, t)]["decisoes"] if d["tick"] < m] != pre:
                raise RuntimeError(f"G-I7-2: {rot} {b}({t}): as decisoes antes do momento nao sao as do original")
        # G-I7-3: um tapa a mais, no tick do momento; o log do E e o do E° iguais ao do original ate o tapa
        for b in ("E", "E0"):
            if _contar_tapas(vidas[(b, t)]["log"]) != [m]:
                raise RuntimeError(f"G-I7-3: {rot} {b}({t}): os tapas do log nao sao so o do momento {m}")
        linhas_e0 = texto_e0.splitlines()
        ate = next(i for i, x in enumerate(linhas_e0) if json.loads(x)["tipo"] == "acao_usuario" and json.loads(x)["valor"] == TAPA.value) + 1
        if vidas[("E", t)]["log"].splitlines()[:ate] != linhas_e0[:ate]:
            raise RuntimeError(f"G-I7-3: {rot} E({t}): o log ate o tapa nao e o do original com o tapa")

    # os perfis dos dias usados (2.3): o original e o G em todos os dias e no resto do dia t depois do momento; os ramos de t nos dias t+1
    # a t+janela e no resto do dia t
    perfis = {("N", None): _perfis(n["decisoes"], todos), ("G", None): _perfis(g["decisoes"], todos)}
    parciais = {}
    linhas = []
    for (b, t), v in sorted(vidas.items(), key=lambda kv: (kv[0][0], kv[0][1] or 0)):
        linha = {"braco": braco, "dono": dono, "semente": semente, "base": unidade["base"], "k": unidade["k"], "ramo": b, "idade": t,
                 "momento": None if t is None else momentos[t], "log_sha256": _sha(v["log"]), "decisoes_sha256": _sha_decisoes(v["decisoes"]),
                 "estado_sha256": {str(d): _sha(json.dumps(e, sort_keys=True, default=str)) for d, e in sorted(v["estados"].items())},
                 "conferencias": {"G-I7-0": b == "N", "G-I7-1": True, "G-I7-2": b in RAMOS_PERTURBADOS, "G-I7-3": b in ("E", "E0")}}
        if t is not None:
            usados = [d for d in range(t + 1, t + janela + 1) if d <= dias]
            perfis[(b, t)] = _perfis(v["decisoes"], usados)
            parciais[(b, t)] = _perfis(v["decisoes"], [t], momentos[t])[t]
            for ref in ("N", "G"):
                parciais.setdefault((ref, t), _perfis(vidas[(ref, None)]["decisoes"], [t], momentos[t])[t])
            linha["estado"] = {str(d): M.distancia_estado(v["estados"][d], n["estados"][d]) for d in usados}
            linha["estado_gemeo"] = {str(d): M.distancia_estado(g["estados"][d], n["estados"][d]) for d in usados}
            linha["reencontro_ultimo_dia"] = M.reencontrou(v["decisoes"], n["decisoes"], dias) if b == "E" else None
        linhas.append(linha)
    custo["pet_parede"] = time.perf_counter() - p0
    return {"vida": rot, "braco": braco, "dono": dono, "semente": semente, "base": unidade["base"], "k": unidade["k"],
            "momentos": {str(t): momentos[t] for t in idades}, "sem_ramo": sem_ramo, "perfis": perfis, "parciais": parciais,
            "ramos": linhas, "custo": custo}


def tarefa(lote: list[tuple], dias: int, orcamento_por_dia: int) -> list[dict]:
    return [tarefa_pet(b, d, u, texto, dias, orcamento_por_dia) for b, d, u, texto in lote]


def viver_fumaca(cfg: dict, unidades: list[dict], destino: Path) -> None:
    """a fumaca: as vidas de base da C4 com as sementes dos testes, num tar.gz como o do I2 (a do I5)"""
    i5.viver_fumaca(cfg, unidades, destino)


# ================================================================== o artefato dos perfis
def _esparso(contagens: list[int] | None) -> dict | None:
    return None if contagens is None else {str(i): c for i, c in enumerate(contagens) if c}


def _denso(esparso: dict | None, perfil: str) -> list[int] | None:
    if esparso is None:
        return None
    v = [0] * M.CAIXAS_HABITO[perfil]
    for i, c in esparso.items():
        v[int(i)] = c
    return v


def linhas_perfis(r: dict):
    """as linhas do `perfis.jsonl.gz` de um pet (6, D-IND-I7a-3): uma por (ramo, idade, dia, perfil), com as contagens esparsas; `parcial`
    marca o resto do dia t depois do momento"""
    base = {"braco": r["braco"], "dono": r["dono"], "semente": r["semente"]}
    for (b, t), por_dia in sorted(r["perfis"].items(), key=lambda kv: (kv[0][0], kv[0][1] or 0)):
        for dia, p in sorted(por_dia.items()):
            for perfil in M.PERFIS_HABITO:
                yield {**base, "ramo": b, "idade": t, "dia": dia, "parcial": False, "perfil": perfil,
                       "contagens": None if p is None else _esparso(p[perfil])}
    for (b, t), p in sorted(r["parciais"].items(), key=lambda kv: (kv[0][0], kv[0][1])):
        for perfil in M.PERFIS_HABITO:
            yield {**base, "ramo": b, "idade": t, "dia": t, "parcial": True, "perfil": perfil,
                   "contagens": None if p is None else _esparso(p[perfil])}


def ler_perfis(caminho: Path) -> dict:
    """{(braco, dono, semente): {"perfis": {(ramo, idade): {dia: {perfil: contagens}}}, "parciais": {(ramo, idade): {perfil: contagens}}}}"""
    pets: dict = {}
    with gzip.open(caminho, "rt", encoding="utf-8") as f:
        for linha in f:
            x = json.loads(linha)
            p = pets.setdefault((x["braco"], x["dono"], x["semente"]), {"perfis": {}, "parciais": {}})
            chave = (x["ramo"], x["idade"])
            dest = p["parciais"].setdefault(chave, {}) if x["parcial"] else p["perfis"].setdefault(chave, {}).setdefault(x["dia"], {})
            dest[x["perfil"]] = _denso(x["contagens"], x["perfil"])
    return pets


def _um_perfil(por_dia: dict, perfil: str) -> dict:
    """{dia: contagens ou None} de um perfil; um dia fora (None nos tres perfis) fica None"""
    out = {}
    for dia, ps in por_dia.items():
        v = ps.get(perfil)
        out[dia] = v
    return out


# ================================================================== a analise
def distancias_do_pet(p: dict, perfil: str, idades: tuple, janela: int, dias: int) -> dict:
    """as D de um pet num perfil: D[(b, t)][d] para b em A, E, E0 e d em t+1..t+janela; DG[d]; D0[(b, t)] (o dia t depois do momento)"""
    orig = _um_perfil(p["perfis"][("N", None)], perfil)
    gem = _um_perfil(p["perfis"][("G", None)], perfil)
    out = {"D": {}, "D0": {}, "DG0": {}, "DG": M.distancias_ramo(gem, orig, list(range(1, dias + 1)))}
    for t in idades:
        usados = [d for d in range(t + 1, t + janela + 1) if d <= dias]
        for b in RAMOS_PERTURBADOS:
            if (b, t) not in p["perfis"]:
                continue
            out["D"][(b, t)] = M.distancias_ramo(_um_perfil(p["perfis"][(b, t)], perfil), orig, usados)
            ram, ori = p["parciais"][(b, t)].get(perfil), p["parciais"][("N", t)].get(perfil)
            out["D0"][(b, t)] = None if ram is None or ori is None else M.distancia_tv(ram, ori)
        if ("N", t) in p["parciais"]:
            gp, op = p["parciais"][("G", t)].get(perfil), p["parciais"][("N", t)].get(perfil)
            out["DG0"][t] = None if gp is None or op is None else M.distancia_tv(gp, op)
    return out


def agregados(pets: dict, braco: str, perfil: str, idades: tuple, janela: int, dias: int) -> dict:
    """por semente (os tres donos juntos, 3.6) e por dono: as somas [soma D_b, soma D_G, pares] sobre os pares com os dois termos, por chave
    (b, t, k): k de 1 a janela sao os dias t+k; k = 0 e o resto do dia t depois do momento (o Phi0); b = "G" sao os pares (D_G, D_G), para a
    regua crua do gemeo (12.2)"""
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
    return out


def chaves_de(nome: str, idades: tuple, janela: int) -> list[tuple]:
    """as chaves que a estatistica `nome` soma (o bootstrap so soma essas)"""
    ks = range(1, janela + 1)
    if nome.startswith("Phi0_"):
        b, t = nome[5:].split("(")
        return [(b, int(t[:-1]), 0)]
    if nome.startswith("dPhi_E-E0("):
        t = nome[len("dPhi_E-E0("):-1]
        ts = idades if t == "todas" else (int(t),)
        return [(b, tt, k) for b in ("E", "E0") for tt in ts for k in ks]
    if nome.startswith("Phi_"):
        b, t = nome[4:].split("(")
        ts = idades if t[:-1] == "todas" else (int(t[:-1]),)
        return [(b, tt, k) for tt in ts for k in ks]
    b = nome.rsplit("_", 1)[1]
    return [(b, t, k) for t in idades for k in ks]


def valor(nome: str, tot: dict, idades: tuple, janela: int) -> float | None:
    """a estatistica `nome` (3.2 a 3.4, 12.2 e 12.3) a partir das somas {chave: [soma D_b, soma D_G, pares]}"""
    ks = list(range(1, janela + 1))

    def razao(chaves):
        vs = [tot[c] for c in chaves if c in tot and tot[c][2] > 0]
        den = sum(v[1] for v in vs)
        return None if not vs or den == 0 else sum(v[0] for v in vs) / den

    def cru(chaves):
        vs = [tot[c] for c in chaves if c in tot and tot[c][2] > 0]
        return sum(v[0] for v in vs) if vs else None

    def phi(b, t):
        return razao([(b, t, k) for k in ks])

    def dif(a, c):
        return None if a is None or c is None else a - c
    if nome.startswith("Phi0_"):
        b, t = nome[5:].split("(")
        return razao([(b, int(t[:-1]), 0)])
    if nome.startswith("dPhi_E-E0("):
        t = nome[len("dPhi_E-E0("):-1]
        ts = idades if t == "todas" else (int(t),)
        return dif(razao([("E", tt, k) for tt in ts for k in ks]), razao([("E0", tt, k) for tt in ts for k in ks]))
    if nome.startswith("Phi_"):
        b, t = nome[4:].split("(")
        ts = idades if t[:-1] == "todas" else (int(t[:-1]),)
        return razao([(b, tt, k) for tt in ts for k in ks])
    tipo, b = nome.rsplit("_", 1)
    if tipo == "gamma":
        return M.inclinacao_ou_none(ks, [razao([(b, t, k) for t in idades]) for k in ks])
    if tipo == "beta":
        return M.inclinacao_ou_none(list(idades), [phi(b, t) for t in idades])
    if tipo == "gamma_cru":
        return M.inclinacao_ou_none(ks, [cru([(b, t, k) for t in idades]) for k in ks])
    if tipo == "beta_cru":
        return M.inclinacao_ou_none(list(idades), [cru([(b, t, k) for k in ks]) for t in idades])
    if tipo in ("U1", "U2"):
        if not {2, 6, 10} <= set(idades):
            return None
        return dif(phi(b, 2 if tipo == "U1" else 10), phi(b, 6))
    raise KeyError(nome)


def _somar_sementes(por: dict, sementes: list, chaves: list[tuple], campo: str = "total", dono: str | None = None) -> dict:
    tot: dict = {}
    for s in sementes:
        fonte = por[s]["total"] if dono is None else por[s]["dono"].get(dono, {})
        for c in chaves:
            v = fonte.get(c)
            if v is not None:
                t = tot.setdefault(c, [0.0, 0.0, 0])
                t[0] += v[0]
                t[1] += v[1]
                t[2] += v[2]
    return tot


def todas_as_chaves(idades: tuple, janela: int) -> list[tuple]:
    return [(b, t, k) for b in RAMOS_PERTURBADOS + ("G",) for t in idades for k in range(0, janela + 1)]


def _percentis(valores: list[float]) -> list[float] | None:
    ic = ri._percentis(valores)
    return None if ic is None else list(ic)


def bootstrap(por: dict, nomes: list[str], rotulo: tuple, idades: tuple, janela: int, boot: int, contraste: dict | None = None) -> dict:
    """o IC95 percentil de cada estatistica, reamostrando as sementes com repeticao (3.6); a rng por (braco, perfil, medida). `contraste`:
    o outro braco (o REL), com as mesmas sementes reamostradas juntas (o REL+F - REL, secao 4)"""
    sementes = sorted(por)
    if contraste is not None and sorted(contraste) != sementes:
        raise ValueError("o contraste precisa das mesmas sementes nos dois bracos")
    out = {}
    for nome in nomes:
        chaves = chaves_de(nome, idades, janela)
        rng = random.Random(derivar_semente("individualidade-i7-boot", *rotulo, nome))
        vs = []
        for _ in range(boot):
            amostra = [rng.choice(sementes) for _ in sementes]
            v = valor(nome, _somar_sementes(por, amostra, chaves), idades, janela)
            if contraste is not None:
                w = valor(nome, _somar_sementes(contraste, amostra, chaves), idades, janela)
                v = None if v is None or w is None else v - w
            if v is not None:
                vs.append(v)
        out[nome] = _percentis(vs)
    return out


COM_IC = (["Phi_A({t})", "Phi_E({t})", "Phi_E0({t})", "Phi0_E({t})", "dPhi_E-E0({t})"],
          ["gamma_A", "gamma_E", "beta_A", "beta_E", "gamma_cru_A", "gamma_cru_E", "beta_cru_A", "beta_cru_E", "gamma_cru_G", "beta_cru_G",
           "U1_A", "U2_A", "U1_E", "U2_E", "Phi_E(todas)", "Phi_E0(todas)", "dPhi_E-E0(todas)"])
SEM_IC = (["Phi0_A({t})", "Phi0_E0({t})"], ["gamma_E0", "beta_E0", "Phi_A(todas)"])     # so o ponto, no descritivo
CONTRASTE_FACETAS = ("Phi_E(todas)", "gamma_E", "beta_E")                              # secao 4: o REL+F - REL


def nomes_com_ic(idades: tuple) -> list[str]:
    return [n.format(t=t) for n in COM_IC[0] for t in idades] + COM_IC[1]


def nomes_todos(idades: tuple) -> list[str]:
    return nomes_com_ic(idades) + [n.format(t=t) for n in SEM_IC[0] for t in idades] + SEM_IC[1]


def pontos(por: dict, idades: tuple, janela: int, dono: str | None = None) -> dict:
    tot = _somar_sementes(por, sorted(por), todas_as_chaves(idades, janela), dono=dono)
    return {n: valor(n, tot, idades, janela) for n in nomes_todos(idades)}


# ---------------------------------------------------------------- a leitura (7.2 e 12)
def _acima(ic, v) -> bool:
    return ic is not None and ic[0] > v


def _abaixo(ic, v) -> bool:
    return ic is not None and ic[1] < v


def forma_u(ic: dict, b: str) -> str | None:
    """12.3: 'U' se as duas diferencas tem o IC95 inteiro acima de 0, '∩' se inteiro abaixo; None fora disso"""
    a, c = ic.get(f"U1_{b}"), ic.get(f"U2_{b}")
    if _acima(a, 0) and _acima(c, 0):
        return "U"
    if _abaixo(a, 0) and _abaixo(c, 0):
        return "∩"
    return None


def leitura(ic: dict, idades: tuple) -> dict:
    """as frases que a leitura pode escrever (7.2, com o adendo 1: 12.1 a 12.3), pelos ICs de um braco num perfil"""
    fr: dict = {}
    pegou = any(_acima(ic.get(f"Phi0_E({t})"), 0) for t in idades)
    fr["condicao_do_evento"] = "o tapa mudou o dia em ao menos uma idade" if pegou else "o tapa nao mudou o dia"

    def inclinacao(nome, cru, sobe, desce):
        r, c = ic.get(nome), ic.get(cru)
        if _acima(r, 0):
            return sobe if _acima(c, 0) else "a inclinacao vem da regua: o D_b cru nao se distingue de parado"
        if _abaixo(r, 0):
            return desce if _abaixo(c, 0) else "a inclinacao vem da regua: o D_b cru nao se distingue de parado"
        return "nao se distingue de zero nesta analise"

    def gamma_passa(b, lado):
        r, c = ic.get(f"gamma_{b}"), ic.get(f"gamma_cru_{b}")
        return (_acima(r, 0) and _acima(c, 0)) if lado > 0 else (_abaixo(r, 0) and _abaixo(c, 0))

    def beta_passa(b, lado):
        if forma_u(ic, b) is not None:
            return False
        r, c = ic.get(f"beta_{b}"), ic.get(f"beta_cru_{b}")
        return (_acima(r, 0) and _acima(c, 0)) if lado > 0 else (_abaixo(r, 0) and _abaixo(c, 0))

    for b in ("A", "E"):
        if b == "E" and not pegou:
            fr["E"] = "o tapa nao mudou o dia"
            continue
        x = fr[b] = {}
        x["gamma"] = inclinacao(f"gamma_{b}", f"gamma_cru_{b}", "a diferenca cresce com os dias", "a diferenca some com os dias")
        u = forma_u(ic, b)
        if u is not None:
            x["beta"] = f"o afastamento muda com a idade sem ser em linha ({u})"
        else:
            x["beta"] = inclinacao(f"beta_{b}", f"beta_cru_{b}", "o tarde afasta mais que o cedo", "o cedo afasta mais que o tarde")
        x["idades"] = {}
        for t in idades:
            c = ic.get(f"Phi_{b}({t})")
            frases = []
            if _abaixo(c, 1):
                frases.append("a historia ate o dia t sobrevive a outro acaso" if b == "A" else "o ramo fica mais perto do original que um gemeo")
            if _acima(c, LIMIAR_GEMEO):
                frases.append("o ramo vira um gemeo")
            x["idades"][str(t)] = frases or ["nao se distingue de 1 nesta analise"]
    # as hipoteses (7.2 e 12.1); todas usam o E, e sem o tapa pegar nenhuma se declara
    h = "nenhuma das hipoteses descreve o perfil do braco sozinha"
    if not pegou:
        h = "nenhuma hipotese se declara: o tapa nao mudou o dia"
    else:
        ga_e = ic.get("gamma_E")
        trans = (_acima(ic.get(f"Phi_A({idades[0]})"), LIMIAR_GEMEO) and _abaixo(ic.get(f"Phi_A({idades[-1]})"), LIMIAR_GEMEO)
                 and beta_passa("A", -1) and not _acima(ga_e, 0))
        can = gamma_passa("E", -1) and all(_abaixo(ic.get(f"Phi_A({t})"), 1) for t in idades)
        amp = gamma_passa("E", +1) and beta_passa("E", -1)
        caos = (all(_acima(ic.get(f"Phi_A({t})"), LIMIAR_GEMEO) and _acima(ic.get(f"Phi_E({t})"), LIMIAR_GEMEO) for t in idades)
                and ga_e is not None and ga_e[0] <= 0 <= ga_e[1])
        if trans:
            h = "H-TRANS"
        elif can:
            h = "H-CAN"
        elif amp:
            h = "H-AMP"
        elif caos:
            h = "H-CAOS"
    fr["hipotese"] = h
    return fr


def descritivo(pets: dict, por: dict, linhas_ramos: list[dict], braco: str, perfil: str, idades: tuple, janela: int, dias: int) -> dict:
    """os descritivos sem IC (4 e 12.5): por dono, a regua crua por idade e dia, o estado interno contra o gemeo, o efeito comum do tapa e o
    reencontro"""
    out: dict = {"por_dono": {d: pontos(por, idades, janela, dono=d) for d in DONOS}}
    tot = _somar_sementes(por, sorted(por), todas_as_chaves(idades, janela))
    out["regua_crua"] = {f"{b}|{t}|{k}": {"soma_D_b": v[0], "soma_D_G": v[1], "pares": v[2]} for (b, t, k), v in sorted(tot.items())}
    # o estado interno contra o gemeo (12.5): Phi^est por ramo e idade (o estado nao depende do perfil; sai igual nos tres)
    est: dict = {}
    for r in linhas_ramos:
        if r["braco"] == braco and r["idade"] is not None:
            est.setdefault(f"{r['ramo']}|{r['idade']}", []).extend((r["estado"][d], r["estado_gemeo"][d]) for d in r["estado"])
    out["Phi_est"] = {k: M.razao_de_somas(v) for k, v in sorted(est.items())}
    out["efeito_comum_E"] = {}
    for t in idades:
        for d in range(t + 1, min(t + janela, dias) + 1):
            rs, os_ = [], []
            for (br, _, _), p in sorted(pets.items()):
                if br == braco and ("E", t) in p["perfis"]:
                    rs.append(p["perfis"][("E", t)][d].get(perfil))
                    os_.append(p["perfis"][("N", None)][d].get(perfil))
            out["efeito_comum_E"][f"{t}|{d}"] = M.efeito_comum(rs, os_)
    reenc = [r["reencontro_ultimo_dia"] for r in linhas_ramos if r["braco"] == braco and r["ramo"] == "E"]
    out["reencontro_dia_final_E"] = {"fracao": sum(reenc) / len(reenc) if reenc else None, "n": len(reenc)}
    return out


def analisar(pets: dict, linhas_ramos: list[dict], dias: int, idades: tuple = IDADES, janela: int = JANELA, boot: int = BOOTSTRAP) -> dict:
    out: dict = {"idades": list(idades), "janela": janela, "bootstrap": boot, "limiar_gemeo": LIMIAR_GEMEO, "por_braco": {}, "contrastes": {},
                 "multiplicidade": "3 perfis x 2 bracos, sem correcao (3.6): plano de leitura, nao de gate"}
    nomes = nomes_com_ic(idades)
    ag = {(b, p): agregados(pets, b, p, idades, janela, dias) for b in BRACOS for p in M.PERFIS_HABITO}
    for braco in BRACOS:
        bloco = out["por_braco"][braco] = {"por_perfil": {}}
        for perfil in M.PERFIS_HABITO:
            por = ag[(braco, perfil)]
            ic = bootstrap(por, nomes, (braco, perfil), idades, janela, boot)
            bloco["por_perfil"][perfil] = {"ponto": pontos(por, idades, janela), "ic95": ic, "leitura": leitura(ic, idades),
                                           "descritivo": descritivo(pets, por, linhas_ramos, braco, perfil, idades, janela, dias)}
    for perfil in M.PERFIS_HABITO:                    # as facetas, REL+F - REL (secao 4), com as mesmas sementes reamostradas juntas
        a, b = ag[("REL+F", perfil)], ag[("REL", perfil)]
        pa, pb = pontos(a, idades, janela), pontos(b, idades, janela)
        out["contrastes"][perfil] = {
            "REL+F-REL": {n: (None if pa[n] is None or pb[n] is None else pa[n] - pb[n]) for n in CONTRASTE_FACETAS},
            "ic95": bootstrap(a, list(CONTRASTE_FACETAS), ("REL+F-REL", perfil), idades, janela, boot, contraste=b)}
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
    if modo == "fumaca":
        vidas = pasta / "vidas_fumaca.tar.gz"
        viver_fumaca(cfg, unidades, vidas)
    else:
        vidas = RAIZ / cfg["vidas"]
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python"] + [Path(sys.argv[0]).as_posix()] + sys.argv[1:]),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "vidas": rc._relativo(vidas) if modo != "fumaca" else vidas.name,
            "vidas_sha256": rc._sha_arquivo(vidas), "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "",
            "processos": processos, "unidades": unidades, "bracos": list(BRACOS), "donos": list(DONOS), "lugar": LUGAR, "bootstrap": boot,
            "idades": list(IDADES), "janela": JANELA,
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py")},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    esperadas = [(b, d, u["semente"]) for u in unidades for b in BRACOS for d in DONOS]
    textos = i5.ler_vidas(vidas, esperadas)
    lotes = [[(b, d, u, textos[(b, d, u["semente"])])] for u in unidades for b in BRACOS for d in DONOS]
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (lote, cfg["dias"], cfg["orcamento_por_dia"])) for lote in lotes], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    if len(registros) != len(esperadas):
        raise RuntimeError(f"{len(registros)} pets, eram {len(esperadas)}")
    registros = sorted(registros, key=lambda r: r["vida"])
    with gzip.open(pasta / "perfis.jsonl.gz", "wt", encoding="utf-8", newline="\n") as f:
        for r in registros:
            for linha in linhas_perfis(r):
                f.write(json.dumps(linha, sort_keys=True) + "\n")
    linhas_ramos = [linha for r in registros for linha in r["ramos"]]
    with (pasta / "ramos.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for linha in linhas_ramos:
            f.write(json.dumps(linha, sort_keys=True) + "\n")
    pets = ler_perfis(pasta / "perfis.jsonl.gz")                 # a analise sai do artefato gravado
    conferir_lidos(pets, registros)
    lidas = [json.loads(x) for x in (pasta / "ramos.jsonl").read_text(encoding="utf-8").splitlines()]
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "pets": len(pets), **analisar(pets, lidas, cfg["dias"], boot=boot)}
    resultado["sem_ramo"] = {f"{r['braco']}|{r['dono']}|{r['semente']}": r["sem_ramo"] for r in registros if r["sem_ramo"]}
    bv._gravar(pasta / "analise.json", bv._dump(resultado))
    custos = [r["custo"]["pet_parede"] for r in registros]
    por_ramo: dict = {}
    for r in registros:
        for k, v in r["custo"].items():
            if k != "pet_parede":
                por_ramo.setdefault(_ramo_do_custo(k), []).append(v)
    bv._gravar(pasta / "custo.json", bv._dump({"pets": len(custos), "parede_media_pet_s": sum(custos) / len(custos), "parede_max_pet_s": max(custos),
                                               "total_parede_s": meta["vidas_parede_s"],
                                               "por_ramo_media_s": {k: sum(v) / len(v) for k, v in sorted(por_ramo.items())},
                                               "nota": "cada ramo e vivido duas vezes (G-I7-1); o tempo do ramo e o das duas"}))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("perfis.jsonl.gz", "ramos.jsonl", "analise.json", "custo.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _ramo_do_custo(chave: str) -> str:
    """o ramo de uma chave do custo ("N", "G", "A4", "E4", "E04" -> "N", "G", "A", "E", "E0")"""
    for ramo in ("E0", "A", "E"):
        if chave.startswith(ramo) and chave[len(ramo):].isdigit():
            return ramo
    return chave


def conferir_lidos(pets: dict, registros: list[dict]) -> None:
    """o `perfis.jsonl.gz` lido de volta e o que as vidas deram"""
    if len(pets) != len(registros):
        raise RuntimeError(f"perfis.jsonl.gz com {len(pets)} pets, eram {len(registros)}")
    for r in registros:
        p = pets[(r["braco"], r["dono"], r["semente"])]
        for chave, por_dia in r["perfis"].items():
            for dia, x in por_dia.items():
                lido = p["perfis"][chave][dia]
                if (x is None and any(v is not None for v in lido.values())) or (x is not None and lido != x):
                    raise RuntimeError(f"{r['vida']} {chave} dia {dia}: o perfis.jsonl.gz nao e o que a vida deu")
        for chave, x in r["parciais"].items():
            lido = p["parciais"][chave]
            if (x is None and any(v is not None for v in lido.values())) or (x is not None and lido != x):
                raise RuntimeError(f"{r['vida']} {chave} parcial: o perfis.jsonl.gz nao e o que a vida deu")


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
