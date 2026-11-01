"""A run da C1 da V3, o longe com lugares fixos (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 6, APROVADO pelo Matheus em
2026-10-30; docs/TAREFA_V2_LONGE_REGULAR.md). Pergunta: o M-MEM do cerebro modular ajuda no longe quando a racao volta a 3 lugares fixos
(o estilo `longe_fixo`, mundo.py)? As vidas sao as do orquestrador do prototipo (experiments/run_v2_digibrain_prototipo.py: o cenario do
MVP, os 4 donos, 14 dias, 16 interacoes por dia, o G1, o T-CENARIO-1, o G-MECANISMO e o credito por opcao em toda vida).

O desenho (A6.2 e A6.3): as celulas 4 donos x 2 lugares (`longe_fixo` e `longe`), os bracos M0, M2 e M3* (o "M3" de
SUBCHAVES_CONSERTO) com a `intencao_suspensa` desligada, K = 150 unidades (30 por base) nas bases 71101, 71202, 71303, 71404 e 71505, o
prefixo `digibrain_prototipo` (AD6-5): 150 x 24 = 3 600 vidas. A run roda uma vez, sem calibracao nem piloto.

A analise (A6.4 a A6.8), no `resultado.json`: o primario (M3* - M2 por episodio, so no `longe_fixo`, o IC95 pelo t sobre as 150 unidades),
as premissas (G-PESA da memoria e G-ELEGIVEL-EP), a classe de cada contraste (A6.6), a leitura de A6.7 e o descritivo de A6.8 (as taxas por
faixa de d0, as visitas ao lugar lembrado, as trocas de meta, as medidas da C5 e os outros), sem gate.

A trava (A6.10): o adendo 6 APROVADO no cabecalho (`exigir_adendo_aprovado`), a faixa 71101...71505 reservada em
`experiments/bancada/faixas.py`, so as bases, o K, os dias e o orcamento do adendo, no maximo 4 processos, e nenhuma gravacao por cima de
uma pasta que ja existe. Na fumaca (as sementes dos testes 101...505) a run roda sem a faixa e sem o K, com menos dias se a config pedir.

    python experiments/run_v2_longe_regular.py --config experiments/configs/v2_longe_regular/longe_regular.json --processos 4
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.metrics import JANELA_8_14, ic_t, janela_dias, quantil_t, viabilidade_do_corpo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = orq.PLANO
PREFIXO = orq.PREFIXO                                                                 # AD6-5
FASE = "longe_regular"
ADENDO = 6
BASES = (71101, 71202, 71303, 71404, 71505)                                           # A6.3 (LR-5)
K_POR_BASE = 30                                                                       # A6.3 (AD6-1): 150 unidades
FAIXA = (71101, 71505)
SAIDA = "artifacts_v2_digibrain_prototipo/longe_regular"
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA                             # A6.2
MAX_PROCESSOS = 4                                                                     # A6.9 (V3-D8)
DONOS = orq.DONOS
ESTILOS = ("longe_fixo", "longe")                                                     # A6.2
BRACOS = ("M0", "M2", "M3")                                                           # A6.2 (LR-4); o "M3" e o M3*
CELULAS = tuple((d, e) for d in DONOS for e in ESTILOS)
CHAVES_CONFIG = {"descricao", "plano", "fase", "unidades", "dias", "orcamento_por_dia"}
MARGEM = 0.022                                                                        # A6.5 (AD6-1), SEM FONTE: o "~ 0" (A6.6)
FOLGA_SIGMA, PODER_ALVO = 1.2, 0.8                                                    # A6.5
G_PESA_LIMIAR = orq.G_PESA["limiar"]                                                  # 0,01 (A6.4)
G_ELEGIVEL_EP = orq.G_ELEGIVEL_EP                                                     # 80 % das vidas do M3* com 3 episodios ou mais
LIMIAR_G1, RESSALVA_G1 = orq.LIMIAR_G1, orq.RESSALVA_G1                               # A6.4: o g1 como em A4.4.6
LIMIAR_CORPO = CONFIG_PADRAO.limiar_privacao                                          # AD6-4: o 0,15 da privacao
TIPOS_DE_META = {("comer", "cheiro"): "busca", ("comer", "comida"): "ida", ("explorar", "ponto"): "lugar_lembrado"}   # A6.8, item 3
MOTIVOS_FIM = ("meta", "trocou", "achou", "sumiu", "expirou", "desistiu")              # A6.8, item 3 e A6.14 (o "desistiu" da busca, DX-4)
FAIXAS_D0 = ("na_visao", "no_cheiro", "alem_do_cheiro")                               # A6.8, item 1
JANELAS_CORPO = ("vida", "dias_8_14")


# ================================================================== a config e a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_faixa_reservada() -> None:
    """a faixa 71101...71505 esta em FAIXAS_RESERVADAS (A6.3, A6.10); sem ela a run nao tem fonte para as sementes"""
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA[0]}...{FAIXA[1]} nao esta em FAIXAS_RESERVADAS (A6.3)")


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou 'longe_regular', que segue o adendo 6 a letra (A6.10): outra base, outro K, outros dias ou outro
    orcamento falham alto, e sementes fora da faixa e dos testes levantam SementeSemPlano"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo (AD6-5), o orcamento (A6.2) ou o K")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (A6.3)")
    exigir_faixa_reservada()
    orq.exigir_adendo_aprovado(_plano(), ADENDO)
    erros = []
    if cfg["dias"] != DIAS:
        erros.append(f"dias {cfg['dias']} (o plano: {DIAS})")
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != K_POR_BASE:
        erros.append(f"K por base {u['k']} (o plano: {K_POR_BASE})")
    if erros:
        raise ValueError(f"a {FASE} segue o adendo {ADENDO} a letra: {erros}")
    return FASE


# ================================================================== a vida
class MotorGravaCorpo(com_corpo(MotorMundo)):
    """O motor do mundo com o corpo, e nada mais: guarda os cinco estados do corpo no comeco de cada tick (o estado que a decisao do tick
    ve), para a C5 (A6.8, item 4). So le: o `_laco` de um tick de cada vez e o mesmo laco, na mesma ordem (o do grupo ja o chama assim),
    sem tocar em rng; a vida e o log saem byte a byte os do motor sem a gravacao (o G1 confere)."""

    def __init__(self, *a, **k) -> None:
        super().__init__(*a, **k)
        self.serie_corpo: list[tuple] = []

    def _laco(self, ticks: int):
        produzidas: list = []
        for _ in range(ticks):
            e = self._estado
            self.serie_corpo.append((e.tick, e.fome, e.higiene, e.energia, e.humor, e.saude))
            produzidas.extend(super()._laco(1))
        return produzidas


def viver(braco: str, dono: str, estilo: str, semente: int, dias: int, orcamento_por_dia: int):
    """uma vida: (o motor, o registro, as fabricas); o cerebro e o do conserto (SUBCHAVES_CONSERTO), o motor e o MotorGravaCorpo"""
    fp, _ = orq.fabricas(braco, dono, semente, dias, orcamento_por_dia, conserto=True)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, gl.BRACO_V11, semente))

    def fm(politica, cfg, s):
        return MotorGravaCorpo(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    registro = fp(CONFIG_PADRAO)
    d = DonoComLugar(criar_dono(dono), estilo, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    return motor, registro, (fp, fm)


def medidas_do_corpo(motor, registro, dias: int) -> dict:
    """A C5 (A6.8, item 4; AD6-4): a viabilidade do corpo por tick (digilab/metrics.py), na vida e nos dias 8 a 14. A serie tem um tick por
    minuto e, nos ticks das decisoes, e a mesma que o cerebro viu (conferido)."""
    serie = motor.serie_corpo
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    if len(serie) != dias * TICKS_POR_DIA or [s[0] for s in serie] != list(range(len(serie))):
        raise RuntimeError(f"a serie do corpo tem {len(serie)} ticks, nao os {dias * TICKS_POR_DIA} da vida, seguidos")
    for k, e in enumerate(registro.estados):
        if serie[k * passo][1:] != tuple(e[:5]):
            raise RuntimeError(f"o corpo do tick {k * passo} nao e o que o cerebro viu na decisao {k}")
    janelas = {"vida": janela_dias(1, dias), "dias_8_14": JANELA_8_14 if dias >= 14 else janela_dias(1, dias)}
    return {j: viabilidade_do_corpo(serie, w, LIMIAR_CORPO) for j, w in janelas.items()}


def trocas_de_meta(registro) -> dict:
    """A6.8, item 3 (a lição LP-2): por vida, os fins das intencoes por tipo (a busca pelo cheiro, a ida a uma comida vista, a ida ao lugar
    lembrado) e por motivo, e as trocas com o motivo: o reflexo do sono, o dormir pelo sorteio ou outra unidade (a vencedora). Com a
    `intencao_suspensa` desligada nenhuma intencao e suspensa nem retomada: um `retomou` ou um `n_susp` falha alto."""
    c = orq.cerebro_de(registro)
    if c.cd.intencao_suspensa:
        raise RuntimeError("a intencao_suspensa esta ligada (A6.2: a C1 roda com ela desligada)")
    fins = {t: {m: 0 for m in MOTIVOS_FIM} for t in TIPOS_DE_META.values()}
    trocas = {t: {"reflexo": 0, "dormir_sorteio": 0, "outra_unidade": 0, "por_vencedora": {}} for t in TIPOS_DE_META.values()}
    for k, m in enumerate(c.motivos):
        if m.get("retomou"):
            raise RuntimeError(f"decisao {k}: uma retomada com a intencao_suspensa desligada (LP-2)")
        for f in m["fins"]:
            if "n_susp" in f:
                raise RuntimeError(f"decisao {k}: uma intencao com n_susp com a intencao_suspensa desligada (LP-2)")
            t = TIPOS_DE_META.get(tuple(f["chave"][:2]))
            if t is None:
                continue
            if f["motivo"] not in MOTIVOS_FIM:
                raise RuntimeError(f"decisao {k}: o fim {f['motivo']!r} de uma intencao nao e dos conhecidos {MOTIVOS_FIM}")
            fins[t][f["motivo"]] += 1
            if f["motivo"] == "trocou":
                tr = trocas[t]
                if m["reflexo"]:
                    tr["reflexo"] += 1
                elif m["acao"] == "dormir":
                    tr["dormir_sorteio"] += 1
                else:
                    tr["outra_unidade"] += 1
                    v = "/".join(str(x) for x in m["escolha"][:2])
                    tr["por_vencedora"][v] = tr["por_vencedora"].get(v, 0) + 1
    return {"fins": fins, "trocas": trocas, "trocas_total": sum(fins[t]["trocou"] for t in fins)}


def _vida(cfg: dict, braco: str, dono: str, estilo: str, unidade: dict, pasta: str) -> dict:
    """uma vida: vivida, gravada, rejogada do disco (G1), conferida (as falhas altas) e medida, como no orquestrador do prototipo"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab = viver(braco, dono, estilo, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{estilo}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    med = orq.medidas(motor, registro, braco, cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{estilo}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": estilo,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": medidas_do_corpo(motor, registro, cfg["dias"]), "metas": trocas_de_meta(registro),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, estilo, unidade, pasta) for b in BRACOS for dono, estilo in CELULAS]


# ================================================================== a analise
def _celulas(estilo: str) -> tuple:
    return tuple((d, estilo) for d in DONOS)


def nivel(registros: list[dict], braco: str, medida, estilo: str) -> dict:
    """{(base, semente): a media da medida nas 4 celulas do estilo} (a unidade de A6.4)"""
    return orq.por_unidade(registros, braco, None, medida, _celulas(estilo))


def diferenca(registros: list[dict], a: str, b: str, medida, estilo: str) -> dict:
    """{(base, semente): a media, nas 4 celulas do estilo, de medida(a) - medida(b) no mesmo dono}"""
    return orq.por_unidade(registros, a, b, medida, _celulas(estilo))


def classe(ic: dict, margem: float = MARGEM) -> dict:
    """a classe de A6.6, na ordem: '~ 0' (o IC95 inteiro dentro de (-margem, +margem); com o sinal se ele tambem exclui o 0), '> 0', '< 0'
    ou 'indeterminado'"""
    lo, hi = ic["ic_inferior"], ic["ic_superior"]
    if lo is None:
        return {"classe": "indeterminado", "sinal": None, "motivo": ic["motivo"]}
    if lo > -margem and hi < margem:
        return {"classe": "≈ 0", "sinal": "+" if lo > 0 else ("-" if hi < 0 else None), "motivo": None}
    if lo > 0:
        return {"classe": "> 0", "sinal": None, "motivo": None}
    if hi < 0:
        return {"classe": "< 0", "sinal": None, "motivo": None}
    return {"classe": "indeterminado", "sinal": None, "motivo": None}


def estimativa(difs: dict, margem: float = MARGEM) -> dict:
    """o descritivo de um valor por unidade: a media, o dp e o IC95 pelo t (A4.4.6) sobre as unidades, com a classe de A6.6"""
    ic = ic_t([v for _, v in sorted(difs.items())])
    return {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic95": {"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"]},
            "classe": classe(ic, margem), "motivo": ic["motivo"]}


def margem_efetiva(dp: float | None, k: int) -> float | None:
    """o menor efeito com poder 0,8 pelo dp observado (A6.4, a formula de A6.5): delta = (t + z_0,8) x dp / raiz(K)"""
    if dp is None or k < 2:
        return None
    return (quantil_t(k - 1, 0.95) + statistics.NormalDist().inv_cdf(PODER_ALVO)) * dp / k ** 0.5


EPISODIO = lambda r: r["episodios_fome"]["taxa"]                       # noqa: E731
RACAO = lambda r: r["cadeia"]["taxa"]                                  # noqa: E731
RACAO_W = lambda r: r["cadeia_w"]["taxa"]                              # noqa: E731


def primario(registros: list[dict], boot: dict) -> dict:
    """A6.4: M3* - M2 por episodio, so nas 4 celulas do `longe_fixo`, o IC95 pelo t sobre as unidades; passa se o limite inferior > 0.
    Ao lado: o p unilateral, o g1 com a ressalva, o IC percentil do bootstrap (rotulado como na A4.10) e a margem efetiva."""
    difs = diferenca(registros, "M3", "M2", EPISODIO, "longe_fixo")
    c = orq.contraste_t(difs, boot)
    lo = c["ic95"]["ic_inferior"]
    ic = {"ic_inferior": lo, "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
    return {"contraste": "M3* - M2, taxa de fechamento por episodio, nas 4 celulas do longe_fixo", "passa": lo is not None and lo > 0,
            **c, "classe": classe(ic), "margem": MARGEM, "margem_efetiva": margem_efetiva(estimativa(difs)["dp"], c["n"])}


def premissas(registros: list[dict]) -> dict:
    """A6.4: a G-PESA da memoria (no M3*, nas 4 celulas do `longe_fixo`, o limite inferior do IC95 pelo t > 0,01) e a G-ELEGIVEL-EP (ao
    menos 80 % das vidas do M3* no `longe_fixo` com 3 episodios ou mais). Se uma falha, o primario e inconclusivo por premissa."""
    pesa = estimativa(nivel(registros, "M3", lambda r: r["influencia"]["memoria"], "longe_fixo"))
    pesa["passa"] = pesa["ic95"]["ic_inferior"] is not None and pesa["ic95"]["ic_inferior"] > G_PESA_LIMIAR
    pesa["limiar"] = G_PESA_LIMIAR
    vs = [r for r in registros if r["braco"] == "M3" and r["lugar"] == "longe_fixo"]
    frac = sum(1 for r in vs if r["episodios_fome"]["n"] >= G_ELEGIVEL_EP["episodios"]) / len(vs)
    elegivel = {"frac_vidas": frac, "vidas": len(vs), "limiar": G_ELEGIVEL_EP["frac_vidas"], "passa": frac >= G_ELEGIVEL_EP["frac_vidas"]}
    return {"G-PESA-memoria": pesa, "G-ELEGIVEL-EP": elegivel, "conclusivo": pesa["passa"] and elegivel["passa"]}


def leitura(prim: dict, prem: dict, sorteado: dict) -> dict:
    """A6.7, a tabela da seção 1.3 da tarefa e o complemento, na ordem (a primeira linha que serve). No `longe_fixo` o primario manda: '> 0'
    e o primario passar; senao a classe de A6.6. A L-3 so ganha tarefa com o primario '> 0' e o sorteado '≈ 0' (A6.12, C1-E2)."""
    fixo = "> 0" if prim["passa"] else prim["classe"]["classe"]
    sort = sorteado["classe"]["classe"]
    base = {"longe_fixo": fixo, "longe": sort}
    if not prem["conclusivo"]:
        return {**base, "linha": "inconclusivo por premissa (A6.4): a memoria nao pesou, ou os donos nao deram racao com fome: diagnosticar antes de ler",
                "l3_ganha_tarefa": False}
    if "indeterminado" in (fixo, sort):
        linha = "registrado como indeterminado; nada se decide com ele"
    elif fixo == "< 0":
        linha = "a memoria atrapalha mesmo com lugares fixos: contra a previsao"
    elif fixo == "> 0" and sort == "≈ 0":
        linha = "a falha do longe e do cenario: nao ha o que lembrar. O habito passa a ser lido tambem no longe com lugares fixos"
    elif fixo == "> 0" and sort == "< 0":
        linha = "a memoria ajuda com regularidade e atrapalha sem ela; o sorteado repete a 66xxx: a previsao '~ 0' do sorteado nao se confirma"
    elif fixo == "> 0" and sort == "> 0":
        linha = "a memoria ajuda ate sem regularidade, contra a previsao e contra a 66xxx"
    elif fixo == "≈ 0" and sort == "≈ 0":
        linha = "a memoria nao ajuda a distancia nem com regularidade; a causa fica na viagem e na decisao ou na percepcao"
    elif sort == "< 0":
        linha = "a memoria nao ajuda com regularidade e atrapalha sem ela"
    else:
        linha = "combinacao fora das linhas escritas em A6.7: registrada como esta; nada se decide com ela"
    return {**base, "linha": linha, "l3_ganha_tarefa": fixo == "> 0" and sort == "≈ 0",
            "ressalva_primario": prim["ressalva_assimetria"]}


# ------------------------------------------------------------------ o descritivo (A6.8; sem gate)
def _faixa(d0: int, g: dict) -> str:
    return "na_visao" if d0 <= g["raio_visao"] else ("no_cheiro" if d0 <= g["corte_d0"] else "alem_do_cheiro")


def faixas_d0(registros: list[dict]) -> dict:
    """A6.8, item 1: por estilo x braco x faixa de d0, os episodios (n), os fechados e a taxa (somas sobre as vidas); a diferenca
    `longe_fixo` - longe por faixa, em cada braco, por unidade (as somas das 4 vidas de cada estilo; a unidade sem episodio na faixa num dos
    estilos fica fora, contada) com a classe de A6.6. A ressalva da LP-2: a faixa depende do cerebro; so o M0 le sem ela."""
    g = orq.geometria()
    soma = {(e, b): {f: [0, 0] for f in FAIXAS_D0} for e in ESTILOS for b in BRACOS}
    por_u: dict = {}
    for r in registros:
        for _k, d0, _w, _fim, motivo in r["episodios_fome"]["episodios"]:
            f = _faixa(d0, g)
            for acum in (soma[(r["lugar"], r["braco"])][f], por_u.setdefault((r["braco"], r["lugar"], r["base"], r["semente"]),
                                                                              {x: [0, 0] for x in FAIXAS_D0})[f]):
                acum[0] += 1
                acum[1] += motivo == "fechou"
    tabela = {f"{e}|{b}": {f: {"n": n, "fechados": fe, "taxa": fe / n if n else None} for f, (n, fe) in soma[(e, b)].items()}
              for e in ESTILOS for b in BRACOS}
    unidades = sorted({(r["base"], r["semente"]) for r in registros})
    dif = {}
    for b in BRACOS:
        for f in FAIXAS_D0:
            difs, fora = {}, 0
            for u in unidades:
                x = por_u.get((b, "longe_fixo") + u, {}).get(f, [0, 0])
                y = por_u.get((b, "longe") + u, {}).get(f, [0, 0])
                if x[0] and y[0]:
                    difs[u] = x[1] / x[0] - y[1] / y[0]
                else:
                    fora += 1
            dif[f"{b}|{f}"] = {**estimativa(difs), "unidades_fora": fora}
    distancia_domina = all(v["classe"]["classe"] == "≈ 0" for v in dif.values() if v["n"] >= 2)
    return {"ressalva": "a faixa de d0 depende do cerebro (LP-2): a leitura entre estilos e primeiro a do M0; M2 e M3* saem com a ressalva",
            "por_estilo_braco_faixa": tabela, "longe_fixo_menos_longe": dif, "distancia_domina": distancia_domina}


def visitas(registros: list[dict]) -> dict:
    """A6.8, item 2: no M3*, por estilo, as visitas ao lugar lembrado, as vazias (a regra corrigida e a v1) e a fracao que acha a racao"""
    out = {}
    for e in ESTILOS:
        vs = [r for r in registros if r["braco"] == "M3" and r["lugar"] == e]
        v, z, z1 = (sum(r[k] for r in vs) for k in ("visitas_lugar_lembrado", "visitas_vazias", "visitas_vazias_v1"))
        out[e] = {"vidas": len(vs), "visitas": v, "vazias": z, "vazias_v1": z1, "frac_acha": (v - z) / v if v else None,
                  "frac_acha_v1": (v - z1) / v if v else None}
    return out


def _contrastes(registros: list[dict], medida, pares=(("M3", "M2"), ("M2", "M0"), ("M3", "M0"))) -> dict:
    return {f"{e}|{a} - {b}": estimativa(diferenca(registros, a, b, medida, e)) for e in ESTILOS for a, b in pares}


def _niveis(registros: list[dict], medida, bracos: tuple = BRACOS) -> dict:
    return {f"{e}|{b}": estimativa(nivel(registros, b, medida, e)) for e in ESTILOS for b in bracos}


def trocas(registros: list[dict]) -> dict:
    """A6.8, item 3: as trocas por vida (todas, e por tipo de meta), em nivel e nos contrastes M3* - M2 e M2 - M0, por estilo. So medidas
    da vida inteira entram em contraste; os subgrupos (o motivo da troca) saem so somados por braco e estilo, como leitura."""
    por_tipo = {t: _contrastes(registros, lambda r, t=t: r["metas"]["fins"][t]["trocou"], (("M3", "M2"), ("M2", "M0")))
                for t in TIPOS_DE_META.values()}
    motivos = {}
    for e in ESTILOS:
        for b in BRACOS:
            vs = [r["metas"] for r in registros if r["lugar"] == e and r["braco"] == b]
            motivos[f"{e}|{b}"] = {t: {**{m: sum(v["trocas"][t][m] for v in vs) for m in ("reflexo", "dormir_sorteio", "outra_unidade")},
                                       "fins": {m: sum(v["fins"][t][m] for v in vs) for m in MOTIVOS_FIM}}
                                   for t in TIPOS_DE_META.values()}
    return {"total": {"niveis": _niveis(registros, lambda r: r["metas"]["trocas_total"]),
                      "contrastes": _contrastes(registros, lambda r: r["metas"]["trocas_total"], (("M3", "M2"), ("M2", "M0")))},
            "por_tipo": por_tipo, "motivos_somados": motivos}


def corpo(registros: list[dict]) -> dict:
    """A6.8, item 4 (a C5; AD6-4): a fracao dos ticks com alguma variavel fora da faixa (< 0,15) e a menor necessidade (media e minimo
    por vida), na vida e nos dias 8 a 14: o nivel por braco e estilo e os contrastes M3* - M2 e M3* - M0, por estilo. Ao lado, a privacao de hoje."""
    out = {"limiar": LIMIAR_CORPO, "status": "DECIDIDA (AD6-4), SEM FONTE", "privacao_de_hoje": {
        "niveis": _niveis(registros, lambda r: r["privacao"])}}
    for j in JANELAS_CORPO:
        for m in ("fracao_fora", "menor_media", "menor_minimo"):
            f = lambda r, j=j, m=m: r["corpo"][j][m]          # noqa: E731
            out[f"{j}|{m}"] = {"niveis": _niveis(registros, f), "contrastes": _contrastes(registros, f, (("M3", "M2"), ("M3", "M0")))}
    return out


def outros(registros: list[dict]) -> dict:
    """A6.8, item 5: as taxas por episodio e por racao (com a W fixa e com a W(d)) por braco e estilo e os contrastes; o efeito da
    regularidade em cada braco (`longe_fixo` - longe, pareado por unidade); a G-PESA de cada modulo; os episodios por vida; a exaustao e a
    privacao; por dono, so a media"""
    regularidade = {}
    unidades = {}
    for b in BRACOS:
        a, c = nivel(registros, b, EPISODIO, "longe_fixo"), nivel(registros, b, EPISODIO, "longe")
        regularidade[b] = estimativa({u: a[u] - c[u] for u in sorted(set(a) & set(c))})
        unidades[b] = len(set(a) ^ set(c))
    modulos = ("incentivo", "habito", "memoria", "persistencia", "afeto", "aprendido")
    return {"sorteado_M3_menos_M2": estimativa(diferenca(registros, "M3", "M2", EPISODIO, "longe")),
            "episodio": {"niveis": _niveis(registros, EPISODIO), "contrastes": _contrastes(registros, EPISODIO)},
            "racao": {"niveis": _niveis(registros, RACAO), "contrastes": _contrastes(registros, RACAO)},
            "racao_w": {"niveis": _niveis(registros, RACAO_W), "contrastes": _contrastes(registros, RACAO_W)},
            "regularidade_fixo_menos_sorteado": {"por_braco": regularidade, "unidades_sem_par": unidades},
            "g_pesa_por_modulo": {m: _niveis(registros, lambda r, m=m: r["influencia"][m], ("M2", "M3")) for m in modulos},
            "episodios_por_vida": _niveis(registros, lambda r: r["episodios_fome"]["n"]),
            "exaustao": _niveis(registros, lambda r: r["exaustao"]), "privacao": _niveis(registros, lambda r: r["privacao"]),
            "por_dono": {f"{d}|{e}|{b}": statistics.fmean(v for v in (EPISODIO(r) for r in registros
                                                                      if r["dono"] == d and r["lugar"] == e and r["braco"] == b)
                                                          if v is not None)
                         for d in DONOS for e in ESTILOS for b in BRACOS
                         if any(EPISODIO(r) is not None for r in registros if r["dono"] == d and r["lugar"] == e and r["braco"] == b)}}


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    """a analise de A6.4 a A6.8, com a classe de cada contraste e a leitura"""
    prim, prem = primario(registros, boot), premissas(registros)
    sort = estimativa(diferenca(registros, "M3", "M2", EPISODIO, "longe"))
    return {"primario": prim, "premissas": prem, "sorteado": sort, "leitura": leitura(prim, prem, sort),
            "descritivo": {"faixas_d0": faixas_d0(registros), "visitas": visitas(registros), "trocas": trocas(registros),
                           "corpo": corpo(registros), "outros": outros(registros)},
            "nao_demonstra": ["que o modular supera o A", "prontidao do prototipo", "tamanho de efeito fora das condicoes da run"]}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (a maquina; V3-D8 e A6.9)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; A6.10)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS], "bracos": {b: orq.SUBCHAVES_CONSERTO[b] for b in BRACOS},
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    esperadas = len(unidades) * len(BRACOS) * len(CELULAS)
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas}")
    bv._gravar(pasta / "medidas.json", bv._dump({r["vida"]: r for r in sorted(registros, key=lambda r: r["vida"])}))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))       # a analise sai do artefato gravado
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos),
                 **analisar(list(lidos.values()))}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "resultado.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _imprimir_resumo(r: dict) -> None:
    """O resumo no console: ASCII puro (ensure_ascii), para nao quebrar num console cp1252 com '≈' na leitura; os artefatos gravados nao passam por aqui."""
    print(json.dumps({k: r[k] for k in ("modo", "vidas", "primario", "premissas", "sorteado", "leitura")}, indent=1, ensure_ascii=True,
                     default=str)[:4000])


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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_digibrain_prototipo/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    _imprimir_resumo(r)


if __name__ == "__main__":
    main()
