"""O prototipo do DigiBrain modular, a avaliacao (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, secoes 2 a 6 e 10; as PPM-1 a
PPM-9 DECIDIDAS em 2026-10-25). O cenario do MVP na bancada Python (secao 3): o corpo quimico do v11 (`com_corpo(MotorMundo)`, a
ConfigCorpo do braco P1-c-tapa), o mundo do produto (o layout padrao sem arvores, so a racao do dono; a PPM-3 permite a este
orquestrador o layout do MVP), o contrato da P4 desligado, o pet sozinho, os quatro donos da v1 so com o cuidado (o filtro sem_ensino
ao vivo, `simular_vida_fisico`) e o lugar da racao (`DonoComLugar`: comedouro, perto, longe), 14 dias, 16 interacoes por dia.

Os bracos (secao 2), a mesma semente e o mesmo mundo em todos; o cerebro so consome a rng de politica:
    M0       a chave ligada; p1, p2 e m_mem desligados; a persistencia ligada; g_apr = g0 (o inato sozinho)
    M1       M0 + p1                         M2   M1 + p2              M3   M2 + m_mem (o braco principal)
    M3-sp    M3 sem a persistencia           M4   M3 + modula_g_apr (a excitacao modula o g_apr)
    M4-emb   M4 com a excitacao de outra vida: a serie E da vida M4 da unidade seguinte da mesma base, na mesma celula (a ultima unidade
             usa a primeira)
    M4-con   M3 com o g_apr fixo na media do g_apr das vidas M4 do piloto (o adendo 2; no piloto e na fumaca, a das vidas M4 da propria
             run)
    A11      o A v11 (P1-c-tapa, o alvo padrao do motor): o baseline, so na avaliacao (secao 7)
As celulas: dono x lugar, 4 x 3 = 12. A unidade: `unidades_derivadas(bases, K, "digibrain_prototipo")`.

As fases (o campo "fase" da config; a faixa 63101...63505 para a calibracao e o piloto, a 64101...64505 para a avaliacao):
    calibracao  bases 63101 e 63202, K = 2, so o M3 (secao 6.1): os quatro criterios, uma rodada por run (no maximo tres, registradas)
    piloto      bases 63303 a 63505, K = 2, os 8 bracos do modular (secao 6.2): o efeito, as premissas, a media do g_apr do M4, o K pelo
                poder (secao 6.3) e o custo; exige o adendo 1 no plano. Os numeros nao sao evidencia
    avaliacao   bases 64101 a 64505, o K e o g_apr do M4-con do adendo 2, os 9 bracos, uma vez so (a run se recusa a gravar por cima)
Na fumaca (as sementes dos testes) as fases rodam sem a faixa nem os adendos, e com menos dias se a config pedir.

Os gates (secao 5.2; por unidade, a media das 12 celulas, salvo a G-ABLA-MEM, so no comedouro; o bootstrap agrupado por base, 10.000
reamostragens, semente 4242): o G-MVP (o limite inferior do IC95 da fracao de vidas do M3 com a cadeia >= 0,8); a familia G-ABLA (P1,
P2, MEM, PERS), pelo Holm a 0,05 sobre o `p_unilateral` (secao 5.2.1); a familia G-MOD (CON, EMB), idem; as premissas G-PESA e
G-ELEGIVEL (secao 5.3). Toda vida e gravada e rejogada do disco bit a bit (G1), e as falhas altas da secao 6.4 valem em toda vida.

    python experiments/run_v2_digibrain_prototipo.py --config experiments/configs/v2_digibrain_prototipo/piloto.json --processos 8
"""
from __future__ import annotations

import argparse
import json
import platform
import random
import statistics
import sys
import time
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import run_v2_calibracao_mundo as rc  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import (CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_MUNDO_MVP, CONFIG_PADRAO,  # noqa: E402
                            TICKS_POR_DIA, ConfigDigibrain, ConfigDigibrainInatos)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.metrics import (JANELA_8_14, MODULOS_SONDA, cadeia_comida_corpo, centro_temporal, contraste_pareado,  # noqa: E402
                             deficit_fome_energia, entropia_acoes, exaustao_nas_decisoes, falta_ao_comer, holm, ic_percentil,
                             influencia_por_modulo, intencoes_com_meta, janela_dias, media_absoluta, pesos_no_teto,
                             privacao_nas_decisoes, repeticao_apos_alivio)
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import ESTILOS_LUGAR, DonoComLugar, MotorMundo, reproduzir_mundo  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md"
PREFIXO = "digibrain_prototipo"                                      # secao 3 (PREFIXOS_UNIDADES)
CM = CONFIG_MUNDO_MVP                                                # o mundo do produto (PPM-3)
BASES = {"calibracao": (63101, 63202), "piloto": (63303, 63404, 63505), "avaliacao": (64101, 64202, 64303, 64404, 64505)}
K_FIXO = {"calibracao": 2, "piloto": 2}                              # secoes 6.1 e 6.2; o da avaliacao vem do adendo 2
SAIDA = {"calibracao": "artifacts_v2_digibrain_prototipo/calibracao", "piloto": "artifacts_v2_digibrain_prototipo/piloto",
         "avaliacao": "artifacts_v2_digibrain_prototipo/avaliacao"}
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")         # secao 3: as celulas, dono x lugar
LUGARES = ESTILOS_LUGAR                                              # comedouro, perto, longe
CELULAS = tuple((d, lugar) for d in DONOS for lugar in LUGARES)
DIAS, ORCAMENTO_POR_DIA = 14, 16                                     # secao 3
LIMIAR_PRIVACAO, LIMIAR_EXAUSTAO = 0.15, 0.25                        # secao 4 (o plano do corpo; o sono_exaustao)
SUBCHAVES = {"M0": {"p1": False, "p2": False, "m_mem": False}, "M1": {"p2": False, "m_mem": False}, "M2": {"m_mem": False}, "M3": {},
             "M3-sp": {"persistencia": False}, "M4": {"modula_g_apr": True},
             "M4-emb": {"modula_g_apr": True, "controle_g_apr": "embaralhado"}, "M4-con": {"controle_g_apr": "constante"}}
BRACOS_MODULAR = tuple(SUBCHAVES)
BRACOS = BRACOS_MODULAR + ("A11",)
BRACOS_DA_FASE = {"calibracao": ("M3",), "piloto": BRACOS_MODULAR, "avaliacao": BRACOS}
SEGUNDA_PASSADA = ("M4-emb", "M4-con")                               # dependem das vidas M4 (a serie E; a media do g_apr)
BOOTSTRAP = {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}
PODER = {"k_min": 4, "k_max": 10, "replicas": 2000, "reamostragens_internas": 1000, "alvo": 0.8, "alfa_abla": 0.0125,
         "alfa_mod": 0.025, "semente": 4242, "n_bases": 5}            # secao 6.3
HOLM = {"alfa": 0.05}
G_MVP = {"w_decisoes": 8, "fome_elegivel": 0.5, "taxa_vida": 0.5, "limiar": 0.8}             # PPM-4
G_ELEGIVEL = {"frac_vidas": 0.8, "racoes": 3}                                                # PPM-4
G_PESA = {"limiar": 0.01, "bracos": {"incentivo": "M1", "habito": "M2", "memoria": "M3", "persistencia": "M3"}}   # PPM-5
FAMILIA_ABLA = ("G-ABLA-P1", "G-ABLA-P2", "G-ABLA-MEM", "G-ABLA-PERS")
FAMILIA_MOD = ("G-MOD-CON", "G-MOD-EMB")
MODULO_DO_GATE = {"G-ABLA-P1": "incentivo", "G-ABLA-P2": "habito", "G-ABLA-MEM": "memoria", "G-ABLA-PERS": "persistencia"}
CHAVES_CONFIG = {"descricao", "plano", "fase", "unidades", "dias", "orcamento_por_dia", "bootstrap", "poder", "holm", "g_mvp",
                 "g_elegivel", "g_pesa", "rodada"}


# ================================================================== a config
def _sem_rodada(cfg: dict) -> set:
    return CHAVES_CONFIG - ({"rodada"} if cfg.get("fase") != "calibracao" else set())


def adendo_do_piloto() -> dict:
    """O K e o g_apr do M4-con da avaliacao: os do piloto (artifacts_v2_digibrain_prototipo/piloto/resultado.json), que o adendo 2 do plano
    registra num commit antes da avaliacao."""
    caminho = RAIZ / SAIDA["piloto"] / "resultado.json"
    if not caminho.exists():
        raise FileNotFoundError("a avaliacao precisa do piloto e do adendo 2 (secao 6.3): rode o piloto antes")
    if "## Adendo 2" not in (RAIZ / PLANO).read_text(encoding="utf-8"):
        raise RuntimeError("o adendo 2 (o K, o poder, as premissas do piloto, o valor do M4-con e o custo) nao esta no plano: commit antes")
    r = json.loads(caminho.read_text(encoding="utf-8"))
    return {"k": r["n"]["k"], "g_apr_m4_con": r["g_apr_m4"]["m4_con"]}


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou a fase ('calibracao', 'piloto', 'avaliacao'), que segue o plano a letra."""
    esperadas = _sem_rodada(cfg) - {"descricao"}
    faltam, sobram = esperadas - set(cfg), set(cfg) - _sem_rodada(cfg)
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    fase = cfg["fase"]
    if fase not in SAIDA:
        raise ValueError(f"fase {fase!r}: so {sorted(SAIDA)}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    erros = []
    if u.get("prefixo") != PREFIXO:
        erros.append("prefixo")
    if cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA:
        erros.append("orcamento (secao 3)")
    fumaca = set(bases) <= bv.SEMENTES_TESTE
    if (cfg["bootstrap"] != BOOTSTRAP or cfg["holm"] != HOLM or cfg["g_mvp"] != G_MVP or cfg["g_elegivel"] != G_ELEGIVEL
            or cfg["g_pesa"] != G_PESA):
        erros.append("bootstrap, holm, g_mvp, g_elegivel ou g_pesa (secoes 5 e 6)")
    if cfg["poder"] != PODER and not (fumaca and set(cfg["poder"]) == set(PODER)):
        erros.append("poder (secao 6.3; so a fumaca pode pedir menos replicas)")
    if fase == "calibracao" and cfg.get("rodada") not in (1, 2, 3):
        erros.append("rodada da calibracao: 1, 2 ou 3 (secao 6.1)")
    if erros:
        raise ValueError(f"config fora do plano: {erros}")
    outras = set().union(*(range(BASES[f][0], BASES[f][-1] + 1) for f in BASES if f != fase))
    if set(bases) & outras:
        raise bv.SementeSemPlano(f"a {fase} recusa as sementes das outras fases (secao 9)")
    if fumaca:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES[fase]:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES[fase])} ({fase}, secao 9)")
    if cfg["dias"] != DIAS:
        erros.append(f"dias {cfg['dias']} (o plano: {DIAS})")
    if fase == "piloto" and "## Adendo 1" not in (RAIZ / PLANO).read_text(encoding="utf-8"):
        raise RuntimeError("o piloto precisa do adendo 1 no plano (os valores de partida congelados, secao 6.1): commit antes")
    k = K_FIXO[fase] if fase in K_FIXO else adendo_do_piloto()["k"]
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != k:
        erros.append(f"K {u['k']} (o plano: {k})")
    if erros:
        raise ValueError(f"a {fase} segue o plano a letra: {erros}")
    return fase


# ================================================================== as vidas
_BANCADAS: dict = {}


def bancada(dias: int, orcamento_por_dia: int) -> bv.Bancada:
    """a bancada do v11 (o corpo do P1-c-tapa, o ponto do adendo 4): so a ConfigCorpo e o cerebro do A11 saem dela"""
    chave = (dias, orcamento_por_dia)
    if chave not in _BANCADAS:
        _BANCADAS[chave] = gl.bancada_v11(dias, orcamento_por_dia * dias)
    return _BANCADAS[chave]


def config_do_braco(braco: str, g_apr_con: int | None = None) -> ConfigDigibrain:
    if braco not in SUBCHAVES:
        raise ValueError(f"braco do modular {braco!r}: so {BRACOS_MODULAR}")
    extra = {"g_apr_constante": g_apr_con} if braco == "M4-con" else {}
    if braco == "M4-con" and (type(g_apr_con) is not int or g_apr_con <= 0):
        raise ValueError(f"o M4-con precisa do g_apr fixo (inteiro > 0): {g_apr_con!r}")
    return replace(CONFIG_DIGIBRAIN_LIGADA, **SUBCHAVES[braco], **extra)


class Registro:
    """Embrulho que so le: o estado de cada decisao (o da Observacao, no tick k x intervalo) e a falta da fome logo depois da
    consequencia no corpo (o gancho `consequencia_corpo`, que o A e o DigiBrain tem). Repassa todo o resto; nao toca em rng."""

    def __init__(self, interna, S: int) -> None:
        self._interna = interna
        self._S = S
        self.estados: list[tuple] = []
        self.falta_depois: list[int] = []

    def agir(self, obs, rng):
        v = obs.vetor_estado
        self.estados.append((v[0], v[1], v[2], v[3], v[4], self._S - obs.corpo.fome))
        return self._interna.agir(obs, rng)

    def consequencia_corpo(self, acao, ocorrido, obs_depois) -> None:
        self.falta_depois.append(self._S - obs_depois.corpo.fome)
        self._interna.consequencia_corpo(acao, ocorrido, obs_depois)

    def observar(self, transicao) -> None:
        self._interna.observar(transicao)

    def estado_interno(self) -> dict:
        return self._interna.estado_interno()

    def __getattr__(self, nome: str):
        interna = self.__dict__.get("_interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _tuplas(v):
    return tuple(_tuplas(x) for x in v) if isinstance(v, list) else v


def inatos_do_meta(meta: dict) -> ConfigDigibrainInatos:
    """os valores de partida de uma run, do meta.json dela (o JSON troca as tuplas por listas): para rejogar as vidas de uma rodada antiga
    da calibracao com os valores dela"""
    return ConfigDigibrainInatos(**{k: _tuplas(v) for k, v in meta["inatos"].items()})


def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int, serie_e: tuple | None = None,
             g_apr_con: int | None = None, inatos: ConfigDigibrainInatos | None = None):
    """(a fabrica do cerebro, a do motor) da vida: o motor e o mesmo em todo braco. `inatos` (so para rejogar uma rodada antiga): os
    valores daquela rodada; None, os de hoje (CONFIG_DIGIBRAIN_INATOS)"""
    b = bancada(dias, orcamento_por_dia)
    espec = bv.EspecVida(dono, gl.BRACO_V11, semente)
    cc = b.cfg_corpo_de(espec)

    def fm(politica, cfg, s):
        return com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc)

    if braco == "A11":
        def fp(cfg=None):
            return Registro(b.politica(espec, cfg or CONFIG_PADRAO), CONFIG_DIGIBRAIN_INATOS.escala)
    else:
        cd = config_do_braco(braco, g_apr_con)

        def fp(cfg=None):
            return Registro(DigiBrain(cfg or CONFIG_PADRAO, cd, CM, inatos=inatos, serie_e_doadora=serie_e), CONFIG_DIGIBRAIN_INATOS.escala)
    return fp, fm


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int, serie_e: tuple | None = None,
          g_apr_con: int | None = None):
    """uma vida: (o motor, o registro, as fabricas)"""
    fp, fm = fabricas(braco, dono, semente, dias, orcamento_por_dia, serie_e, g_apr_con)
    registro = fp(CONFIG_PADRAO)
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    return motor, registro, (fp, fm)


def conferir_replay(motor, fabricas_vida: tuple, semente: int, texto: str) -> None:
    """G1: a vida rejogada do log do disco, comparada bit a bit (o resumo do motor e o estado interno do cerebro)"""
    if texto != motor.log.para_jsonl():
        raise bv.ReplayDivergiu("o log do disco nao e o da vida")
    fp, fm = fabricas_vida
    r = reproduzir_mundo(LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm)
    if bv.resumo_motor(r) != bv.resumo_motor(motor):
        raise bv.ReplayDivergiu("log, estado, acoes ou rngs divergem no replay")
    if json.dumps(r.politica.estado_interno(), sort_keys=True) != json.dumps(motor.politica.estado_interno(), sort_keys=True):
        raise bv.ReplayDivergiu("o estado interno do cerebro diverge no replay")


def cerebro_de(registro: Registro):
    return registro._interna


def conferir_mecanismo(braco: str, registro: Registro, serie_e: tuple | None) -> None:
    """As falhas altas da secao 6.4, em toda vida do modular: com uma subchave desligada, o termo do modulo e 0 em toda decisao (o
    DigiBrain ja levanta erro decisao a decisao; aqui, o fim); o M0 com o desfecho, o habito e a memoria em 0 a vida inteira; o M4-emb leu
    a serie E inteira do doador; o reflexo do sono nunca sorteia."""
    c = cerebro_de(registro)
    cd = c.cd
    for m in c.motivos:
        if m["reflexo"] and (m["u"] is not None or m["acao"] != "dormir"):
            raise RuntimeError(f"{braco}: o reflexo do sono sorteou ou nao dormiu (decisao {m['k']})")
        for termo, ligada in (("incentivo", cd.p1), ("habito", cd.p2), ("memoria", cd.m_mem), ("persistencia", cd.persistencia)):
            if not ligada and any(u["termos"][termo] for u in m["unidades"]):
                raise RuntimeError(f"{braco}: o termo {termo!r} com a subchave desligada (decisao {m['k']})")
    if braco == "M0" and not (c.m.plast.desfecho_zero() and c.m.plast.habito_zero() and not c.m.mem.episodios):
        raise RuntimeError("M0: o desfecho, o habito ou a memoria sairam de 0")
    if braco == "M4-emb":
        if [m["afeto"]["e_usada"] for m in c.motivos] != list(serie_e[:len(c.motivos)]) or len(serie_e) != len(c.motivos):
            raise RuntimeError("M4-emb: a serie E usada nao e a do doador, decisao a decisao, inteira")


def _contexto_ganhou_fica(m: dict) -> tuple:
    c = m["contexto"]
    return (c["drive"], c["comida_vista"], c["noite"])


def medidas(motor, registro: Registro, braco: str, dias: int) -> dict:
    """As medidas da secao 4, pelas funcoes de metrics.py (o estado de cada decisao e o da Observacao; a decisao k no tick k x 15)."""
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    es = registro.estados
    if len(es) * passo != dias * TICKS_POR_DIA:
        raise RuntimeError(f"{len(es)} decisoes em {dias} dias: o relogio da decisao nao e k x {passo}")
    if len(registro.falta_depois) != len(es):
        raise RuntimeError("o gancho consequencia_corpo nao veio em toda decisao")
    janela = JANELA_8_14 if dias >= 14 else janela_dias(1, dias)
    vida = janela_dias(1, dias)
    ticks = [k * passo for k in range(len(es))]
    fe = [(t, e[0], e[2]) for t, e in zip(ticks, es)]
    # a cadeia comida -> corpo: as racoes postas pelo dono, a fome da primeira decisao em ou depois, e os consumos do pet
    entrada = motor.entrada_mundo                       # o relogio do mundo e o do pet mais a entrada (0 com um pet so)
    racoes = []
    for d in motor.deixadas:
        if d["tipo"] != "racao":
            continue
        t0 = d["tick"] - entrada
        k = -(-t0 // passo)
        racoes.append((d["id"], t0, es[k][0] if k < len(es) else None))
    consumos = []
    for c in motor.consumos_mundo:
        t = c["tick"] - entrada
        if t % passo:
            raise RuntimeError(f"consumo fora do tick de uma decisao: {t}")
        consumos.append((c["id"], t, c["tipo"], es[t // passo][5], registro.falta_depois[t // passo]))
    cadeia = cadeia_comida_corpo(racoes, consumos, dias, G_MVP["w_decisoes"] * passo, G_MVP["fome_elegivel"])
    out = {"d_fe": deficit_fome_energia(fe, janela)["d_fe"], "d_fe_vida": deficit_fome_energia(fe, vida)["d_fe"],
           "privacao": privacao_nas_decisoes([(t, e[0], e[1], e[2], e[3]) for t, e in zip(ticks, es)
                                              if janela[0] <= t < janela[1]], LIMIAR_PRIVACAO)["fracao_privacao"],
           "exaustao": exaustao_nas_decisoes([(t, e[2]) for t, e in zip(ticks, es)], janela, LIMIAR_EXAUSTAO)["frac"],
           "cadeia": {k: v for k, v in cadeia.items() if k != "latencias"},
           "latencia_media": statistics.fmean(cadeia["latencias"]) if cadeia["latencias"] else None,
           "acoes": dict(sorted(_contar(a.value for _, a in motor.acoes_recentes(10**9)).items()))}
    out["com_cadeia"] = None if cadeia["taxa"] is None else cadeia["taxa"] >= G_MVP["taxa_vida"]
    if braco == "A11":
        return out
    c = cerebro_de(registro)
    ms = c.motivos
    if len(ms) != len(es):
        raise RuntimeError("o registro do cerebro e o do motor com numeros de decisoes diferentes")
    S = c.S
    sondas = [(t, {mod: m["sondas"][f"{mod}_decidiu"] for mod in MODULOS_SONDA + ("aprendido",)}) for t, m in zip(ticks, ms)]
    infl = influencia_por_modulo(sondas, janela, MODULOS_SONDA + ("aprendido",))
    infl_vida = influencia_por_modulo(sondas, vida, MODULOS_SONDA + ("aprendido",))
    comer_racao = [(t, m["acao"] == "comer" and m["tipo_escolha"] == "racao", m["falta_fome"] / S) for t, m in zip(ticks, ms)]
    rep = [(t, _contexto_ganhou_fica(m), m["acao"], None if m["consequencia"] is None else m["consequencia"]["r"])
           for t, m in zip(ticks, ms)]
    intencoes = [(f["inicio"] * passo, bool(f["meta"])) for m in ms for f in m["fins"] if f["chave"][0] == "comer"]
    H = [v for linha in c.m.plast.H.values() for v in linha]
    fins = _contar(f["motivo"] for m in ms for f in m["fins"])
    episodios = c.m.mem.estado_interno()
    visitas = [m for m in ms if m["consequencia"] is not None and m["consequencia"]["episodio"] is not None
               and tuple(m["escolha"][:2]) == ("explorar", "ponto")]
    acoes_dia = [[m["acao"] for t, m in zip(ticks, ms) if t // TICKS_POR_DIA == d] for d in range(dias)]
    out.update({
        "influencia": infl["frac"], "influencia_vida": infl_vida["frac"], "influencia_por_dia": infl_vida["por_dia"],
        "falta_ao_comer": falta_ao_comer(comer_racao, janela)["media"],
        "repeticao": repeticao_apos_alivio(rep, janela),
        "intencoes_com_meta": intencoes_com_meta(intencoes, janela)["frac"],
        "pesos_no_teto": pesos_no_teto(H, c.inatos.h_max),
        "g_apr_media": statistics.fmean(m["afeto"]["g_apr"] for m in ms),
        "exploracao": sum(1 for m in ms if m["acao"] == "explorar") / len(ms),
        "entropia_dia": statistics.fmean(e for e in (entropia_acoes(a) for a in acoes_dia) if e is not None),
        "taxa_p1": media_absoluta([m["consequencia"]["p1"]["abs"] for m in ms if m["consequencia"] and m["consequencia"]["p1"]]),
        "taxa_p2": media_absoluta([cr["abs"] for m in ms for cr in m["creditos"] + (m["consequencia"] or {}).get("creditos", [])]),
        "fins": dict(sorted(fins.items())), "reflexos": sum(1 for m in ms if m["reflexo"]),
        "nada_a_fazer": sum(1 for m in ms if m["nada_a_fazer"]),
        "episodios": {"codificados": episodios["proximo_id"], "sairam": len(episodios["saidas"]),
                      "sairam_r_pos": sum(1 for s in episodios["saidas"] if s["r"] > 0), "no_fim": len(episodios["episodios"])},
        "visitas_lugar_lembrado": len(visitas),
        "visitas_vazias": sum(1 for m in visitas if m["consequencia"]["comeu"] is None)})
    return out


def _contar(xs) -> dict:
    out: dict = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return out


def _vida_gravada(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str, serie_e: tuple | None = None,
                  g_apr_con: int | None = None) -> dict:
    """uma vida: vivida, gravada, rejogada do disco (G1), conferida (as falhas altas) e medida"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab = viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"], serie_e, g_apr_con)
    nome = f"{braco}|{dono}|{lugar}|{unidade['semente']}"
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    if braco != "A11":
        conferir_mecanismo(braco, registro, serie_e)
    out = {"vida": nome, "braco": braco, "dono": dono, "lugar": lugar, "semente": unidade["semente"], "base": unidade["base"],
           "k": unidade["k"], **medidas(motor, registro, braco, cfg["dias"]),
           "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}
    if braco == "M4":
        out["serie_e"] = list(cerebro_de(registro).m.afeto.serie_e)
    return out


def tarefa_primeira(cfg: dict, unidade: dict, pasta: str, bracos: tuple) -> list[dict]:
    """as vidas de uma unidade dos bracos que nao dependem de outras vidas (todas as celulas)"""
    return [_vida_gravada(cfg, b, dono, lugar, unidade, pasta) for b in bracos for dono, lugar in CELULAS]


def tarefa_segunda(cfg: dict, unidade: dict, pasta: str, series: dict, g_apr_con: int) -> list[dict]:
    """o M4-emb (a serie E do doador de cada celula) e o M4-con (o g_apr fixo) de uma unidade"""
    out = []
    for dono, lugar in CELULAS:
        out.append(_vida_gravada(cfg, "M4-emb", dono, lugar, unidade, pasta, serie_e=tuple(series[(dono, lugar)])))
        out.append(_vida_gravada(cfg, "M4-con", dono, lugar, unidade, pasta, g_apr_con=g_apr_con))
    return out


def doadores(unidades: list[dict]) -> dict:
    """a unidade doadora de cada unidade (secao 2): a seguinte da mesma base, e a ultima usa a primeira"""
    por_base: dict = {}
    for u in unidades:
        por_base.setdefault(u["base"], []).append(u)
    out = {}
    for us in por_base.values():
        us = sorted(us, key=lambda u: u["k"])
        for i, u in enumerate(us):
            out[u["semente"]] = us[(i + 1) % len(us)]["semente"]
    return out


# ================================================================== a analise (funcoes puras)
def _idx(registros: list[dict]) -> dict:
    idx = {}
    for r in registros:
        chave = (r["semente"], r["dono"], r["lugar"], r["braco"])
        if chave in idx:
            raise RuntimeError(f"vida repetida: {chave}")
        idx[chave] = r
    return idx


def _ler(medida):
    if callable(medida):
        return medida
    return lambda r: r[medida]


def por_unidade(registros: list[dict], braco_a: str, braco_b: str | None, medida, celulas=CELULAS) -> dict:
    """{(base, semente): a media nas celulas de medida(a) - medida(b)} (b None: o nivel de a). As celulas com valor None num dos bracos
    ficam fora; a unidade sem celula com valor fica fora (a familia nao encolhe: o contraste sai sem p)."""
    ler, idx = _ler(medida), _idx(registros)
    out = {}
    for s, base in sorted({(r["semente"], r["base"]) for r in registros}):
        ds = []
        for dono, lugar in celulas:
            a = idx.get((s, dono, lugar, braco_a))
            if a is None:
                raise RuntimeError(f"unidade {s}, celula {dono}/{lugar}: falta o {braco_a}")
            va = ler(a)
            if braco_b is None:
                if va is not None:
                    ds.append(va)
                continue
            b = idx.get((s, dono, lugar, braco_b))
            if b is None:
                raise RuntimeError(f"unidade {s}, celula {dono}/{lugar}: falta o {braco_b}")
            vb = ler(b)
            if va is not None and vb is not None:
                ds.append(va - vb)
        if ds:
            out[(base, s)] = sum(ds) / len(ds)
    return out


def contraste(difs: dict, boot: dict) -> dict:
    """o contraste_pareado agrupado por base (secao 5.2.1): {base: [as unidades dela]}"""
    grupos: dict = {}
    for (base, _), d in sorted(difs.items()):
        grupos.setdefault(base, []).append(d)
    return contraste_pareado(grupos, boot["reamostragens"], boot["semente"])


CELULAS_COMEDOURO = tuple(c for c in CELULAS if c[1] == "comedouro")
CONTRASTES_ABLA = {"G-ABLA-P1": ("M0", "M1", "falta_ao_comer", CELULAS), "G-ABLA-P2": ("M2", "M1", lambda r: r["repeticao"]["indice"], CELULAS),
                   "G-ABLA-MEM": ("M3", "M2", lambda r: r["cadeia"]["taxa"], CELULAS_COMEDOURO),
                   "G-ABLA-PERS": ("M3", "M3-sp", "intencoes_com_meta", CELULAS)}
CONTRASTES_MOD = {"G-MOD-CON": ("M4-con", "M4", "d_fe", CELULAS), "G-MOD-EMB": ("M4-emb", "M4", "d_fe", CELULAS)}


def g_pesa(registros: list[dict], boot: dict, cfg_pesa: dict) -> dict:
    """a premissa por modulo (secao 5.3): no braco em que o modulo entra, a fracao das decisoes (dias 8 a 14) com `<modulo>_decidiu`; o
    limite inferior do IC95 > 0,01"""
    out = {}
    for mod, braco in cfg_pesa["bracos"].items():
        r = contraste(por_unidade(registros, braco, None, lambda x, mod=mod: x["influencia"][mod]), boot)
        out[mod] = {"braco": braco, **r, "passa": r["ic95"] is not None and r["ic95"]["ic_inferior"] > cfg_pesa["limiar"]}
    return out


def familia(registros: list[dict], contrastes: dict, boot: dict, alfa: float) -> dict:
    """os contrastes de uma familia, orientados (positivo = a direcao da espec), com o Holm sobre o p_unilateral (secao 5.2.1); o IC95 so
    descritivo"""
    out = {}
    for nome, (a, b, med, celulas) in contrastes.items():
        out[nome] = {"contraste": f"{med if isinstance(med, str) else 'medida'}({a}) - ({b})", "celulas": len(celulas),
                     **contraste(por_unidade(registros, a, b, med, celulas), boot)}
    h = holm({n: out[n]["p_unilateral"] for n in contrastes}, alfa)
    for n in contrastes:
        out[n]["holm"] = h[n]
        out[n]["passa"] = h[n]["rejeita"]
    return out


def fracao_com_cadeia(registros: list[dict], braco: str = "M3") -> dict:
    """{(base, semente): a fracao das vidas (celulas) com a cadeia}, so as vidas com racao elegivel; e as vidas sem elegivel"""
    fr = por_unidade(registros, braco, None, lambda r: None if r["com_cadeia"] is None else float(r["com_cadeia"]))
    sem = sum(1 for r in registros if r["braco"] == braco and r["com_cadeia"] is None)
    return {"por_unidade": fr, "vidas_sem_elegivel": sem}


def g_mvp(registros: list[dict], boot: dict, cfg_mvp: dict) -> dict:
    fc = fracao_com_cadeia(registros)
    r = contraste(fc["por_unidade"], boot)
    return {"medida": "a fracao de vidas do M3 com a taxa de fechamento >= 0,5 (media das celulas por unidade)", **r,
            "vidas_sem_elegivel": fc["vidas_sem_elegivel"], "limiar": cfg_mvp["limiar"],
            "passa": r["ic95"] is not None and r["ic95"]["ic_inferior"] >= cfg_mvp["limiar"]}


def g_elegivel(registros: list[dict], cfg_el: dict) -> dict:
    vs = [r for r in registros if r["braco"] == "M3"]
    frac = sum(1 for r in vs if r["cadeia"]["elegiveis"] >= cfg_el["racoes"]) / len(vs)
    return {"frac_vidas": frac, "vidas": len(vs), "passa": frac >= cfg_el["frac_vidas"]}


def comparacao_com_o_a(registros: list[dict], boot: dict) -> dict:
    """a comparacao descritiva com o A (secao 7, o D6): M3 - A11 e M0 - A11, sem Holm e sem margem"""
    meds = {"d_fe": "d_fe", "privacao": "privacao", "refeicoes_por_dia": lambda r: r["cadeia"]["refeicoes_por_dia"],
            "taxa": lambda r: r["cadeia"]["taxa"], "com_cadeia": lambda r: None if r["com_cadeia"] is None else float(r["com_cadeia"])}
    return {f"{b} - A11": {n: contraste(por_unidade(registros, b, "A11", m), boot) for n, m in meds.items()} for b in ("M3", "M0")}


def leitura_d2(registros: list[dict], boot: dict) -> dict:
    """D-2 (secao 8): centro_temporal(habito) - centro_temporal(memoria) no M3, por unidade; positiva e a ordem prevista. Sem gate."""
    def dif(r):
        h, m = (centro_temporal([0.0 if f is None else f for f in r["influencia_por_dia"][x]]) for x in ("habito", "memoria"))
        return None if h is None or m is None else h - m
    por_lugar = {lugar: contraste(por_unidade(registros, "M3", None, dif, tuple(c for c in CELULAS if c[1] == lugar)), boot)
                 for lugar in LUGARES}
    return {"habito_menos_memoria": contraste(por_unidade(registros, "M3", None, dif), boot), "por_lugar": por_lugar}


def leitura_d1(registros: list[dict], boot: dict) -> dict:
    """D-1 (secao 8): M4 - M4-con na exploracao (a fracao e a entropia das acoes por dia) e na taxa de aprendizado (|delta d| e |delta H|),
    cada diferenca pelo desvio padrao das unidades do M4-con. Sem gate."""
    out = {}
    for nome in ("exploracao", "entropia_dia", "taxa_p1", "taxa_p2"):
        difs = por_unidade(registros, "M4", "M4-con", nome)
        nivel = list(por_unidade(registros, "M4-con", None, nome).values())
        dp = statistics.stdev(nivel) if len(nivel) > 1 else None
        padr = {k: v / dp for k, v in difs.items()} if dp else {}
        out[nome] = {"bruto": contraste(difs, boot), "dp_m4_con": dp, "padronizado": contraste(padr, boot) if padr else None}
    return out


def descritivos(registros: list[dict]) -> dict:
    out = {}
    for b in sorted({r["braco"] for r in registros}):
        rs = [r for r in registros if r["braco"] == b]
        out[b] = {"d_fe": statistics.fmean(r["d_fe"] for r in rs), "privacao": statistics.fmean(r["privacao"] for r in rs),
                  "exaustao": statistics.fmean(r["exaustao"] for r in rs),
                  "refeicoes_por_dia": statistics.fmean(r["cadeia"]["refeicoes_por_dia"] for r in rs),
                  "por_celula": {f"{d}|{lugar}": {"d_fe": statistics.fmean(r["d_fe"] for r in rs if r["dono"] == d and r["lugar"] == lugar)}
                                 for d, lugar in CELULAS}}
        if b != "A11":
            out[b]["influencia"] = {m: statistics.fmean(r["influencia"][m] for r in rs) for m in rs[0]["influencia"]}
            out[b]["fins"] = _somar(r["fins"] for r in rs)
            out[b]["visitas_lugar_lembrado"] = sum(r["visitas_lugar_lembrado"] for r in rs)
            out[b]["visitas_vazias"] = sum(r["visitas_vazias"] for r in rs)
            out[b]["episodios_sairam"] = sum(r["episodios"]["sairam"] for r in rs)
            out[b]["pesos_no_teto"] = statistics.fmean(r["pesos_no_teto"] for r in rs)
    return out


def _somar(dicts) -> dict:
    out: dict = {}
    for d in dicts:
        for k, v in d.items():
            out[k] = out.get(k, 0) + v
    return dict(sorted(out.items()))


def leitura(mecanismo_passa: bool, mvp: dict, elegivel: dict, abla: dict, pesa: dict) -> str:
    """a tabela da secao 5.5 (a G-MOD e lida a parte)"""
    if not mecanismo_passa:
        return "falha de implementacao (D1): o G-MECANISMO nao passa"
    if not elegivel["passa"]:
        return "G-MVP inconclusivo por premissa (G-ELEGIVEL): os donos quase nao deram racao com o pet com fome"
    inconclusivos = [g for g in FAMILIA_ABLA if not pesa[MODULO_DO_GATE[g]]["passa"]]
    todos = all(abla[g]["passa"] for g in FAMILIA_ABLA) and not inconclusivos
    if mvp["passa"]:
        if todos:
            return "o modular vai a comida pelos proprios modulos, e cada um pesa no sentido previsto (na pesquisa Python)"
        return ("o produto funciona na pesquisa Python; os modulos que nao pesaram vao ao diagnostico da fiacao (D2): "
                + ", ".join(g for g in FAMILIA_ABLA if not abla[g]["passa"] or g in inconclusivos))
    return "o G-MVP falha: com o oraculo passando, a aprendizagem nao chega la (D4), falha de implementacao ou de calibracao"


CELULA_DUPLICADA = ("incoerente", "comedouro")    # com o sem_ensino, a vida e byte a byte a do atencioso no comedouro (adendo 2)
CELULAS_11 = tuple(c for c in CELULAS if c != CELULA_DUPLICADA)


def descritivo_11_celulas(registros: list[dict], cfg: dict) -> dict:
    """a leitura com 11 celulas, sem a duplicata do comedouro (a decisao do Matheus no fim do adendo 2): os mesmos contrastes, premissas e
    a fracao do G-MVP sobre as mesmas vidas, so sem a celula incoerente/comedouro. So descritiva: sem Holm, sem "passa", sem gate."""
    boot = cfg["bootstrap"]
    fc = por_unidade(registros, "M3", None, lambda r: None if r["com_cadeia"] is None else float(r["com_cadeia"]), CELULAS_11)
    contrastes = {}
    for nome, (a, b, med, celulas) in {**CONTRASTES_ABLA, **CONTRASTES_MOD}.items():
        cs = tuple(c for c in celulas if c != CELULA_DUPLICADA)
        contrastes[nome] = {"celulas": len(cs), **contraste(por_unidade(registros, a, b, med, cs), boot)}
    pesa = {mod: {"braco": braco, **contraste(por_unidade(registros, braco, None, lambda x, mod=mod: x["influencia"][mod], CELULAS_11),
                                               boot)}
            for mod, braco in cfg["g_pesa"]["bracos"].items()}
    m3 = [r for r in registros if r["braco"] == "M3" and (r["dono"], r["lugar"]) != CELULA_DUPLICADA]
    return {"aviso": "descritivo, sem gate: a analise principal e a das 12 celulas (decisao do Matheus, 2026-10-26)",
            "fora": list(CELULA_DUPLICADA), "celulas": len(CELULAS_11), "G-MVP": contraste(fc, boot), "contrastes": contrastes,
            "G-PESA": pesa, "G-ELEGIVEL": {"frac_vidas": sum(1 for r in m3 if r["cadeia"]["elegiveis"] >= cfg["g_elegivel"]["racoes"])
                                                         / len(m3), "vidas": len(m3)}}


def analisar(registros: list[dict], cfg: dict, mecanismo_passa: bool = True) -> dict:
    """a avaliacao (secao 5): os gates, as premissas e as leituras; o A11, se veio, so descritivo"""
    boot, alfa = cfg["bootstrap"], cfg["holm"]["alfa"]
    abla = familia(registros, CONTRASTES_ABLA, boot, alfa)
    pesa = g_pesa(registros, boot, cfg["g_pesa"])
    for g in FAMILIA_ABLA:
        abla[g]["premissa_g_pesa"] = pesa[MODULO_DO_GATE[g]]["passa"]
        abla[g]["leitura"] = ("inconclusivo por premissa: o modulo nao pesa" if not abla[g]["premissa_g_pesa"]
                              else ("passa" if abla[g]["passa"] else "nao passa"))
    mod = familia(registros, CONTRASTES_MOD, boot, alfa)
    mvp, el = g_mvp(registros, boot, cfg["g_mvp"]), g_elegivel(registros, cfg["g_elegivel"])
    out = {"G-MVP": mvp, "G-ELEGIVEL": el, "G-ABLA": abla, "G-PESA": pesa, "G-MOD": mod, "holm_alfa": alfa,
           "leitura": leitura(mecanismo_passa, mvp, el, abla, pesa), "D-2": leitura_d2(registros, boot), "D-1": leitura_d1(registros, boot),
           "descritivos": descritivos(registros), "descritivo_11_celulas": descritivo_11_celulas(registros, cfg)}
    if any(r["braco"] == "A11" for r in registros):
        out["comparacao_com_o_a"] = comparacao_com_o_a(registros, boot)
    return out


# ------------------------------------------------------------------ o piloto: o poder e o K (secao 6.3)
def _p_bootstrap(somas: list[float], contagens: list[int], reamostragens: int, rng: random.Random) -> float:
    """o p unilateral do bootstrap agrupado por base (a conta do `contraste_pareado`, pela soma e a contagem de cada base): a fracao das
    medias reamostradas <= 0"""
    n = len(somas)
    abaixo = 0
    for _ in range(reamostragens):
        s, c = 0.0, 0
        for _ in range(n):
            i = rng.randrange(n)
            s += somas[i]
            c += contagens[i]
        abaixo += s / c <= 0.0
    return abaixo / reamostragens


def _ic_inferior(somas: list[float], contagens: list[int], reamostragens: int, rng: random.Random) -> float:
    n = len(somas)
    medias = []
    for _ in range(reamostragens):
        s, c = 0.0, 0
        for _ in range(n):
            i = rng.randrange(n)
            s += somas[i]
            c += contagens[i]
        medias.append(s / c)
    return ic_percentil(medias, 0.95)[0]


def poder_por_k(unidades: list[dict], planos: dict, k: int, poder: dict, alfas: dict, mvp_plano: float | None) -> dict:
    """o poder de cada contraste num K (secao 6.3): `unidades` = [{contraste: a diferenca da unidade}], cada diferenca centrada e
    deslocada para o efeito de planejamento dela (as diferencas da mesma unidade juntas, a correlacao fica); K x n_bases unidades por
    replica, divididas em n_bases bases de K; o teste da replica e o p unilateral do bootstrap agrupado por base (as reamostragens
    internas); o poder e a fracao das replicas com p <= alfa. O G-MVP: o limite inferior do IC95 >= o limiar."""
    rng = random.Random(derivar_semente("poder-digibrain", poder["semente"], k))
    medias = {c: statistics.fmean(u[c] for u in unidades if u.get(c) is not None) for c in planos}
    n_bases = poder["n_bases"]
    acertos = {c: 0 for c in planos}
    acertos_mvp, conjunto = 0, 0
    for _ in range(poder["replicas"]):
        sorteadas = [unidades[rng.randrange(len(unidades))] for _ in range(k * n_bases)]
        rejeita = {}
        for c, efeito in planos.items():
            somas, cont = [], []
            for b in range(n_bases):
                vs = [u[c] - medias[c] + efeito for u in sorteadas[b * k:(b + 1) * k] if u.get(c) is not None]
                if vs:
                    somas.append(sum(vs))
                    cont.append(len(vs))
            p = _p_bootstrap(somas, cont, poder["reamostragens_internas"], rng) if len(somas) >= 2 else 1.0
            rejeita[c] = p <= alfas[c]
            acertos[c] += rejeita[c]
        conjunto += all(rejeita[c] for c in planos if c in FAMILIA_ABLA)
        if mvp_plano is not None:
            somas, cont = [], []
            media_mvp = statistics.fmean(u["G-MVP"] for u in unidades)
            for b in range(n_bases):
                vs = [u["G-MVP"] - media_mvp + mvp_plano for u in sorteadas[b * k:(b + 1) * k]]
                somas.append(sum(vs))
                cont.append(len(vs))
            acertos_mvp += _ic_inferior(somas, cont, poder["reamostragens_internas"], rng) >= G_MVP["limiar"]
    r = poder["replicas"]
    return {"k": k, "n": k * n_bases, "poder": {c: acertos[c] / r for c in planos},
            "poder_mvp": None if mvp_plano is None else acertos_mvp / r, "poder_conjunto_abla": conjunto / r}


def analisar_piloto(registros: list[dict], cfg: dict) -> dict:
    """o piloto (secoes 6.2 e 6.3): os contrastes so como relato, as premissas, a media do g_apr do M4 (o valor do M4-con), o K pelo poder
    e o custo. Nenhum numero dele e evidencia."""
    boot, poder = cfg["bootstrap"], cfg["poder"]
    abla = familia(registros, CONTRASTES_ABLA, boot, cfg["holm"]["alfa"])
    mod = familia(registros, CONTRASTES_MOD, boot, cfg["holm"]["alfa"])
    difs = {n: por_unidade(registros, a, b, med, cel) for n, (a, b, med, cel) in {**CONTRASTES_ABLA, **CONTRASTES_MOD}.items()}
    fc = fracao_com_cadeia(registros)["por_unidade"]
    chaves = sorted({k for d in difs.values() for k in d} | set(fc))
    unidades = [{**{n: difs[n].get(k) for n in difs}, "G-MVP": fc.get(k)} for k in chaves]
    planos, fora = {}, {}
    for n in FAMILIA_ABLA + FAMILIA_MOD:
        vs = [v for v in difs[n].values()]
        if not vs:
            fora[n] = "sem valor no piloto"
            continue
        efeito = statistics.fmean(vs) / 2
        if efeito <= 0:
            fora[n] = "o efeito do piloto tem o sinal contrario ao previsto (ou e 0): fora da conta do K"
            continue
        planos[n] = efeito
    mvp_frac = statistics.fmean(v for v in fc.values()) if fc else None
    mvp_plano = None if mvp_frac is None or mvp_frac <= G_MVP["limiar"] else G_MVP["limiar"] + (mvp_frac - G_MVP["limiar"]) / 2
    alfas = {n: poder["alfa_abla"] if n in FAMILIA_ABLA else poder["alfa_mod"] for n in planos}
    unidades_com_mvp = [u for u in unidades if u["G-MVP"] is not None] if mvp_plano is not None else unidades
    tabela = [poder_por_k(unidades_com_mvp, planos, k, poder, alfas, mvp_plano) for k in range(poder["k_min"], poder["k_max"] + 1)]
    no_k = [c for c in planos if c in FAMILIA_ABLA]

    def chega(t):
        return all(t["poder"][c] >= poder["alvo"] for c in no_k) and (t["poder_mvp"] is None or t["poder_mvp"] >= poder["alvo"])
    escolhido = next((t for t in tabela if chega(t)), tabela[-1])
    m4 = [r["g_apr_media"] for r in registros if r["braco"] == "M4"]
    return {"contrastes_so_relato": {"G-ABLA": abla, "G-MOD": mod}, "premissas": {"G-PESA": g_pesa(registros, boot, cfg["g_pesa"]),
                                                                              "G-ELEGIVEL": g_elegivel(registros, cfg["g_elegivel"])},
            "G-MVP_piloto": {"fracao": mvp_frac, "plano": mvp_plano, "fora_do_k": mvp_plano is None},
            "n": {"k": escolhido["k"], "chega_ao_alvo": chega(escolhido), "planos": planos, "fora_do_k": fora, "tabela": tabela},
            "g_apr_m4": {"media": statistics.fmean(m4) if m4 else None, "m4_con": round(statistics.fmean(m4)) if m4 else None},
            "descritivos": descritivos(registros),
            "aviso": "o piloto serve so para o efeito, as premissas, o valor do M4-con, o K e o custo (secao 6.2): nenhum numero e evidencia"}


def analisar_calibracao(registros: list[dict], cfg: dict) -> dict:
    """a calibracao (secao 6.1), so o M3: o T-CADEIA-1 (o oraculo, conferido pelo teste), a taxa de fechamento na mediana das vidas >= 0,5,
    nenhum H no teto e a G-PESA de cada modulo do M3 com a fracao >= 0,01"""
    vs = [r for r in registros if r["braco"] == "M3"]
    taxas = [r["cadeia"]["taxa"] for r in vs if r["cadeia"]["taxa"] is not None]
    mediana = statistics.median(taxas) if taxas else None
    teto = max(r["pesos_no_teto"] for r in vs)
    pesa = {m: statistics.fmean(r["influencia"][m] for r in vs) for m in ("incentivo", "habito", "memoria", "persistencia")}
    criterios = {"taxa_mediana": {"valor": mediana, "passa": mediana is not None and mediana >= 0.5},
                 "pesos_no_teto": {"valor": teto, "passa": teto == 0},
                 "g_pesa": {m: {"valor": v, "passa": v >= cfg["g_pesa"]["limiar"]} for m, v in pesa.items()}}
    fecha = criterios["taxa_mediana"]["passa"] and criterios["pesos_no_teto"]["passa"] and all(x["passa"] for x in criterios["g_pesa"].values())
    return {"rodada": cfg.get("rodada"), "criterios": criterios, "fecha": fecha, "descritivos": descritivos(registros),
            "aviso": "o T-CADEIA-1 e conferido por tests/test_digibrain_vidas.py antes da run; os bracos da ablacao nao sao olhados"}


def custo(registros: list[dict], k: int | None, n_bases: int) -> dict:
    por = {b: statistics.fmean(r["custo"]["vida_cpu"] for r in registros if r["braco"] == b) for b in sorted({r["braco"] for r in registros})}
    por_unidade_cpu = sum(por.values()) * len(CELULAS)
    return {"cpu_por_vida": por, "cpu_por_unidade": por_unidade_cpu,
            "avaliacao_estimada": None if k is None else {"k": k, "vidas": n_bases * k * len(CELULAS) * len(BRACOS),
                                                         "cpu_s": n_bases * k * por_unidade_cpu * len(BRACOS) / max(1, len(por))}}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    modo = modo_da_config(cfg)
    fase = cfg["fase"]
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (secao 6.4)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    meta = {"modo": modo, "fase": fase, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "git_head": rc._git("rev-parse", "HEAD"),
            "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos, "unidades": unidades,
            "bracos": {b: (None if b == "A11" else SUBCHAVES[b]) for b in BRACOS_DA_FASE[fase]},
            "inatos": json.loads(json.dumps(CONFIG_DIGIBRAIN_INATOS.__dict__)),
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    g_apr_con = None
    if fase == "avaliacao" and modo == "avaliacao":
        ad = adendo_do_piloto()
        g_apr_con = ad["g_apr_m4_con"]
        meta["adendo_2"] = ad
        meta["piloto_resultado_sha256"] = rc._sha_arquivo(RAIZ / SAIDA["piloto"] / "resultado.json")
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    primeira = tuple(b for b in BRACOS_DA_FASE[fase] if b not in SEGUNDA_PASSADA)
    saidas = rc._executar([(tarefa_primeira, (cfg, u, str(pasta), primeira)) for u in unidades], processos)
    registros = [r for s in saidas for r in s]
    if any(b in BRACOS_DA_FASE[fase] for b in SEGUNDA_PASSADA):
        series = {(r["semente"], r["dono"], r["lugar"]): r["serie_e"] for r in registros if r["braco"] == "M4"}
        if g_apr_con is None:                       # o piloto e a fumaca: a media do g_apr das vidas M4 da propria run
            g_apr_con = round(statistics.fmean(r["g_apr_media"] for r in registros if r["braco"] == "M4"))
        meta["g_apr_m4_con"] = g_apr_con
        doa = doadores(unidades)
        tarefas = [(tarefa_segunda, (cfg, u, str(pasta), {(d, lugar): series[(doa[u["semente"]], d, lugar)] for d, lugar in CELULAS},
                                     g_apr_con)) for u in unidades]
        registros += [r for s in rc._executar(tarefas, processos) for r in s]
    for r in registros:
        r.pop("serie_e", None)
    meta["vidas_parede_s"] = time.perf_counter() - t0
    n_bases = len(cfg["unidades"]["bases"])
    if fase == "calibracao":
        resultado = {"modo": modo, "fase": fase, "plano": PLANO, **analisar_calibracao(registros, cfg)}
    elif fase == "piloto":
        resultado = {"modo": modo, "fase": fase, "plano": PLANO, **analisar_piloto(registros, cfg)}
        resultado["custo"] = custo(registros, resultado["n"]["k"], len(BASES["avaliacao"]))
    else:
        resultado = {"modo": modo, "fase": fase, "plano": PLANO, **analisar(registros, cfg), "custo": custo(registros, None, n_bases)}
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    bv._gravar(pasta / "medidas.json", bv._dump({r["vida"]: r for r in sorted(registros, key=lambda r: r["vida"])}))
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_digibrain_prototipo/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA[cfg["fase"]]
    if cfg["fase"] == "calibracao" and a.saida is None:
        saida = saida / f"rodada_{cfg['rodada']}"
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    print(json.dumps({k: v for k, v in r.items() if k not in ("descritivos", "D-1", "D-2")}, indent=1, ensure_ascii=False,
                     default=str)[:4000])


if __name__ == "__main__":
    main()
