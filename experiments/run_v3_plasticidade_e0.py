"""PLASTICIDADE_EVOLUIDA, o E0: o teste de sensibilidade dos numeros do aprendizado (docs/TAREFA_V3_PLASTICIDADE_EVOLUIDA.md, APROVADA pelo
Matheus em 2026-11-21, D-PE-1 a D-PE-6). E uma triagem, nao uma run confirmatoria: nada confirmatorio sai daqui.

Pergunta (secao 2): algum numero do aprendizado, mexido sozinho, muda o bem-estar do pet ou o valor de aprender?

As 25 configs (PE-3): a de hoje e cada um dos 12 genes (campos inteiros da `ConfigDigibrainInatos`) na metade e no dobro, um por vez,
cortado nos limites que a config valida. Os dois bracos de cada config (PE-2), nas mesmas sementes: o APRENDE (como hoje) e o CONGELADO
(as subchaves `p1` e `p2` da `ConfigDigibrain` desligadas: o desfecho e o habito ficam em 0). O pet (PE-4) e o v38 do Python, o da
PET_VIVO e da V1-a (`experiments/pv2.py`, `fabricas(..., v38=True)`): este orquestrador monta as mesmas pecas com os inatos da config e
a `ConfigDigibrain` do braco, e confere em toda vida da config de hoje no APRENDE que o log e o do `pv2.viver("HOJE", ..., v38=True)`,
byte a byte. As celulas: os donos atencioso e relapso x os tres lugares da V1-a (comedouro, longe, longe_fixo). 10 unidades, 14 dias:
25 x 2 x 6 x 10 = 3 000 vidas. O `beta_e`, o `g_min` e o `g_max` sairam da lista por decisao do Matheus em 2026-11-21 (D-PE-7): sao
inertes no pet v38, que tem a `modula_g_apr` desligada (o `g_apr` e o `g0`).

As medidas (secao 2), pelo `digilab/metrics.py`: o "Tempo bem" (dias 1 a 14) do APRENDE; o valor do aprendizado (APRENDE - CONGELADO,
pareado por unidade); os contrastes contra a config de hoje com o IC95 pelo t (`sensibilidade_um_por_vez`); ao lado, a saude e a
exaustao dos dias 8 a 14 e a fracao `aprendido_decidiu` das sondas (dias 1 a 14). A leitura da secao 3, escrita antes, e descritiva:
nao ha gate. O resultado diz quantos contrastes passariam por acaso.

As conferencias de cada vida, que falham alto: o replay pelo log (G1), o T-CENARIO-1, as do mecanismo (o termo de uma subchave desligada
e 0 em toda decisao), o pet da vida (os inatos da config, a `ConfigDigibrain` do braco e as chaves do v38) e, no CONGELADO, o desfecho
e o habito em 0 no fim da vida.

A trava: a run se recusa sem o "APROVADO pelo Matheus" na tarefa, com a faixa de sementes pendente ou fora de FAIXAS_RESERVADAS, fora
das 10 bases, com a pasta de saida existente, sem o `tools/pre_run.py` e sem disco. A fumaca (as sementes dos testes, e um subconjunto
das configs se a config pedir) so serve ao custo: nenhuma medida dela e lida.

  python experiments/run_v3_plasticidade_e0.py --config experiments/configs/v3_plasticidade_e0/run.json --processos 4
  python experiments/run_v3_plasticidade_e0.py --config experiments/configs/v3_plasticidade_e0/fumaca.json --saida <pasta>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import pre_run  # noqa: E402
import pv2  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_corpo_c4 as C4  # noqa: E402
import run_v3_pet_vivo_ra as ra  # noqa: E402
import run_v3_valuation as V  # noqa: E402
from bancada.faixas import FAIXAS_QUEIMADAS, FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import (CONFIG_LANCE_DONO_LIGADA, CONFIG_PADRAO, CONFIG_SONO_SEGURA_LIGADA, TICKS_POR_DIA,  # noqa: E402
                            ConfigCritico, ConfigDigibrain, ConfigDigibrainInatos, inatos_e1)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = "docs/TAREFA_V3_PLASTICIDADE_EVOLUIDA.md"            # a leitura escrita antes esta na secao 3 da tarefa
ORQUESTRADOR = "experiments/run_v3_plasticidade_e0.py"
STATUS = "**Status: APROVADO pelo Matheus"
FASE = "plasticidade_e0"
SAIDA = "artifacts_v3_plasticidade/e0"
PREFIXO = orq.PREFIXO
PENDENTE = "PENDENTE"                                         # PE-5: a faixa vem da coordenadora, antes da run
N_BASES = 10                                                  # PE-4 e PE-5: 10 unidades, uma por base
K_POR_BASE = 1
DIAS = 14
ORCAMENTO_POR_DIA = orq.ORCAMENTO_POR_DIA
MAX_PROCESSOS = 4                                             # V3-D8
DONOS = ("atencioso", "relapso")                              # PE-4
LUGARES = C4.LUGARES                                          # os tres lugares da V1-a: comedouro, longe, longe_fixo
CELULAS = tuple((d, lugar) for d in DONOS for lugar in LUGARES)
APRENDE, CONGELADO = "APRENDE", "CONGELADO"
BRACOS = (APRENDE, CONGELADO)
SUBCHAVES_CONGELADO = {"p1": False, "p2": False}              # PE-2
HOJE = "hoje"
FATORES = ("metade", "dobro")                                 # PE-3; PROPOSTOS, SEM FONTE
# os 12 genes (secao 2, PE-3; PROPOSTOS, SEM FONTE), por grupo; todos sao campos inteiros da ConfigDigibrainInatos. O `beta_e`, o
# `g_min` e o `g_max` sairam em 2026-11-21 (D-PE-7, "Sim, tira os tres"): inertes no pet v38, com a `modula_g_apr` desligada
GRUPOS = {"a plasticidade": ("eta_d", "eta_h", "h_max"),
          "o incentivo": ("c_g", "g_max_incentivo"),
          "o ganho do aprendizado": ("g0",),
          "os pesos dos termos": ("w_pers", "w_mem", "w_lem"),
          "a disputa": ("tau_hab", "epsilon", "lambda_sono")}
GENES = tuple(g for grupo in GRUPOS.values() for g in grupo)
DISPUTA = frozenset(GRUPOS["a disputa"])
INATOS_V38 = inatos_e1()
PASSO_CEREBRO = 15                                            # o piso das constantes de tempo que a ConfigDigibrainInatos valida
NIVEL = 0.95                                                  # secao 3: o IC95 do contraste pareado
CHAVES_CONFIG = {"descricao", "fase", "plano", "dias", "orcamento_por_dia", "faixa", "unidades", "configs"}
OPCIONAIS = {"descricao", "configs"}
MEDIDA = "tempo_bem"
AO_LADO = ("saude_8_14", "exaustao_8_14", "aprendido_decidiu", "entropia_bits", "entropia_frac_baixa", "credito_dormir")
ENTROPIA = "entropia_bits"                                    # PE-10 (secao 9.2): o descritivo da entropia da decisao
PREVISAO_ENTROPIA = ("escrita antes de calcular (secao 9.2, D-RB-13): os genes da disputa (epsilon, tau_hab) mexem na entropia do "
                     "sorteio; os da plasticidade mexem pouco. E descritiva")
L_ESTRUTURAL = "estrutural: os numeros do aprendizado nao decidem"
L_BUSCAR = "ha por onde buscar"
L_REFLEXOS = "a busca afinaria os reflexos, nao o aprendizado"
L_FORA = "fora da tabela da secao 3: volta ao Matheus como esta"
L_SEM_IC = "sem leitura: falta o IC de algum contraste"
SEGUE = {L_ESTRUTURAL: "a busca (E1) nao se abre; a aposta fica no pet que pensa",
         L_BUSCAR: "o plano do E1 (a busca do nivel A), com os genes que mexeram",
         L_REFLEXOS: "a busca nao se abre como plasticidade; o achado vai para a frente do corpo",
         L_FORA: "nenhum passo previsto: a tabela e o caso vao ao Matheus",
         L_SEM_IC: "nenhum passo: o resultado nao tem o que a regra le"}
NAO_DIZ = ["nada sobre interacoes entre genes: o E0 mexe um por vez",
           "nada sobre donos e lugares fora das seis celulas",
           "nada confirmatorio: e uma triagem, com 10 unidades",
           "nada sobre o jogo: nenhum numero da config muda, e o pet e o v38 do Python"]


class E0Divergiu(RuntimeError):
    """uma conferencia de uma vida falhou, ou a analise ficou sem o que a regra le"""


class GeneSemMexer(ValueError):
    """os limites da config nao deixam o gene sair do valor de hoje"""


# ================================================================== as 25 configs
def limites(gene: str, inatos: ConfigDigibrainInatos) -> tuple[int | None, int | None]:
    """(o minimo, o maximo) que a `ConfigDigibrainInatos.__post_init__` aceita para o gene, com os outros campos como estao; None e sem
    limite daquele lado. A propria config confere depois (o `replace` valida): uma tabela errada aqui falha alto"""
    if gene not in GENES:
        raise KeyError(f"gene {gene!r}: so {GENES}")
    return {"g0": (inatos.g_min, inatos.g_max), "h_max": (1, None),
            "tau_hab": (PASSO_CEREBRO, None), "w_lem": (0, None)}.get(gene, (None, None))


def _pedido(valor: int, fator: str) -> int:
    """a metade (arredondada para baixo, em inteiros) ou o dobro do valor de hoje"""
    if fator not in FATORES:
        raise ValueError(f"fator {fator!r}: so {FATORES}")
    return valor // 2 if fator == "metade" else valor * 2


def montar_configs(inatos: ConfigDigibrainInatos | None = None) -> dict:
    """nome -> a config do E0: a de hoje e cada gene na metade e no dobro, um por vez, cortado nos limites. Falha alto (GeneSemMexer) se
    o corte devolver o valor de hoje: a config repetiria a de hoje em silencio"""
    base = inatos or INATOS_V38
    out = {HOJE: {"nome": HOJE, "gene": None, "fator": None, "valor_hoje": None, "pedido": None, "valor": None, "cortado": False,
                  "inatos": base}}
    for gene in GENES:
        hoje = getattr(base, gene)
        if type(hoje) is not int:
            raise TypeError(f"o gene {gene} nao e um campo inteiro: {hoje!r}")
        lo, hi = limites(gene, base)
        for fator in FATORES:
            pedido = _pedido(hoje, fator)
            valor = pedido if lo is None else max(lo, pedido)
            valor = valor if hi is None else min(hi, valor)
            if valor == hoje:
                raise GeneSemMexer(f"{gene} na {fator if fator == 'metade' else 'no ' + fator}: os limites {(lo, hi)} deixam o valor em {hoje}")
            nome = f"{gene}_{fator}"
            out[nome] = {"nome": nome, "gene": gene, "fator": fator, "valor_hoje": hoje, "pedido": pedido, "valor": valor,
                         "cortado": valor != pedido, "inatos": replace(base, **{gene: valor})}
    return out


CONFIGS = montar_configs()
N_VIDAS = len(CONFIGS) * len(BRACOS) * len(CELULAS) * N_BASES * K_POR_BASE      # 3 000


def descricao_das_configs(configs: dict | None = None) -> list[dict]:
    """as configs sem o registro dos inatos (para o meta e o resultado)"""
    return [{k: v for k, v in c.items() if k != "inatos"} for c in (configs or CONFIGS).values()]


def config_digibrain(braco: str) -> ConfigDigibrain:
    """a ConfigDigibrain do braco: a do pet v38 (o REL das fases do conserto) e, no CONGELADO, a mesma com o `p1` e o `p2` desligados"""
    if braco not in BRACOS:
        raise ValueError(f"braco {braco!r}: so {BRACOS}")
    cd = orq.config_do_braco("REL", None, True)
    return cd if braco == APRENDE else replace(cd, **SUBCHAVES_CONGELADO)


# ================================================================== as vidas
def fabricas(config: str, braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int,
             critico: ConfigCritico | None = None) -> tuple:
    """(a fabrica do cerebro, a do motor) do pet v38 da PET_VIVO (`pv2.fabricas("HOJE", ..., v38=True)`), com os inatos da config e a
    ConfigDigibrain do braco. Na config de hoje e no APRENDE a vida e, byte a byte, a do `pv2.viver("HOJE", ..., v38=True)` (teste, e a
    conferencia C-HOJE de toda vida dessas). `critico` (o C0, secao 9.1): a ConfigCritico do cerebro; None, a vida de hoje"""
    kw = {} if critico is None else {"cfg_critico": critico}
    inatos = CONFIGS[config]["inatos"]
    cd = config_digibrain(braco)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, gl.BRACO_V11, semente))

    def fm(politica, cfg, s):
        return com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc,
                                     cfg_lance_dono=CONFIG_LANCE_DONO_LIGADA)

    def fp(cfg=None):
        registro = orq.Registro(DigiBrain(cfg or CONFIG_PADRAO, cd, orq.CM, semente=semente, inatos=inatos,
                                          cfg_sono=CONFIG_SONO_SEGURA_LIGADA, cfg_lance=CONFIG_LANCE_DONO_LIGADA,
                                          cfg_equilibrio=pv2.EQUILIBRIO_V38, **kw), inatos.escala)
        pv2.bebe_pelas_decisoes(orq.cerebro_de(registro))     # na fabrica, para o replay ter o mesmo bebe (como no pv2)
        return registro

    return fp, fm


def viver(config: str, braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int = ORCAMENTO_POR_DIA,
          critico: ConfigCritico | None = None) -> tuple:
    """uma vida: (o motor, o registro, as fabricas)"""
    fp, fm = fabricas(config, braco, dono, semente, dias, orcamento_por_dia, critico)
    registro = fp(CONFIG_PADRAO)
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    return motor, registro, (fp, fm)


def conferir_vida(config: str, braco: str, motor, registro, critico: ConfigCritico | None = None) -> None:
    """o pet da vida e o v38 com os inatos da config e a ConfigDigibrain do braco; no CONGELADO, o desfecho e o habito em 0; o critico
    so esta no cerebro se a vida o pediu (falha alto)"""
    c = orq.cerebro_de(registro)
    nome = f"{config}/{braco}"
    esperado = critico if critico is not None and critico.ligada else None
    if c.cr != esperado or c.m.plast.cr != esperado or any(("critico" in m) != (esperado is not None) for m in c.motivos):
        raise E0Divergiu(f"{nome}: o critico do cerebro nao e o da vida ({esperado!r})")
    erros = [n for n, ok in (("os inatos da config", c.inatos == CONFIGS[config]["inatos"]), ("a ConfigDigibrain do braco", c.cd == config_digibrain(braco)),
                             ("o sono que segura ligado", c.m.arb.sono == CONFIG_SONO_SEGURA_LIGADA),
                             ("o lance no cerebro", c.cl == CONFIG_LANCE_DONO_LIGADA), ("o lance no motor", motor.cld == CONFIG_LANCE_DONO_LIGADA),
                             ("o equilibrio do cuidado", c.ceq == pv2.EQUILIBRIO_V38)) if not ok]
    if erros:
        raise E0Divergiu(f"{nome}: o pet da vida nao e o da config ({', '.join(erros)})")
    orq.conferir_mecanismo("REL", registro, None)             # o termo de uma subchave desligada e 0 em toda decisao
    plast = c.m.plast
    if braco == CONGELADO and not (plast.desfecho_zero() and plast.habito_zero() and plast.creditos == 0):
        raise E0Divergiu(f"{nome}: o desfecho ou o habito sairam de 0 com o p1 e o p2 desligados")


def medir(dias: int, motor, registro) -> dict:
    """as medidas de uma vida (secao 2), pelas funcoes do metrics.py: o estado de cada decisao e o da Observacao, a decisao k no tick
    k x passo"""
    c = orq.cerebro_de(registro)
    passo, es, ms = CONFIG_PADRAO.intervalo_decisao_ticks, registro.estados, c.motivos
    if len(es) * passo != dias * TICKS_POR_DIA or len(ms) != len(es):
        raise E0Divergiu(f"{len(es)} estados e {len(ms)} motivos em {dias} dias: o relogio da decisao nao e k x {passo}")
    ticks = [k * passo for k in range(len(es))]
    vida = met.janela_dias(1, dias)
    janela = met.JANELA_8_14 if dias >= 14 else vida          # na fumaca curta, a vida toda (a regra do `orq.medidas`)
    tb = met.tempo_bem_nas_decisoes([(t, e[0], e[1], e[2]) for t, e in zip(ticks, es)], vida, orq.LIMIAR_PRIVACAO, orq.LIMIAR_EXAUSTAO)
    sondas = [(t, {"aprendido": m["sondas"]["aprendido_decidiu"]}) for t, m in zip(ticks, ms)]
    H = [v for linha in c.m.plast.H.values() for v in linha]
    # PE-10 (secao 9.2): a entropia do sorteio, do motivo do M-ARB; e para onde vai o credito do habito (secao 9.1)
    h = met.entropia_do_sorteio([None if m["u"] is None else [u["w"] for u in m["unidades"]] for m in ms])
    creditos = [cr for m in ms for cr in m["creditos"] + (m["consequencia"] or {}).get("creditos", []) + m.get("critico", {}).get("fechados", [])]
    cred = met.credito_do_habito_por_linha(creditos)
    return {"entropia_bits": h["media_bits"], "entropia_frac_baixa": h["frac_abaixo"], "frac_sorteio": h["frac_sorteio"],
            "credito_dormir": cred["frac_abs"], "credito_dormir_n": cred["frac_n"], "credito_abs": cred["abs"],
            "tempo_bem": tb["frac"], "privacao_vida": tb["frac_privacao"], "exaustao_vida": tb["frac_exaustao"], "decisoes": tb["n"],
            "saude_8_14": met.saude_nas_decisoes([(t, e[4]) for t, e in zip(ticks, es)], janela)["media"],
            "exaustao_8_14": met.exaustao_nas_decisoes([(t, e[2]) for t, e in zip(ticks, es)], janela, orq.LIMIAR_EXAUSTAO)["frac"],
            "aprendido_decidiu": met.influencia_por_modulo(sondas, vida, ("aprendido",))["frac"]["aprendido"],
            "reflexos": sum(1 for m in ms if m["reflexo"]), "habito_abs": sum(abs(v) for v in H), "creditos_p2": c.m.plast.creditos,
            "habito_no_teto": met.pesos_no_teto(H, c.inatos.h_max)}


def assinatura_da_vida(motor, registro) -> str:
    """o sha256 do que a vida produziu: o resumo do motor (o log, o estado final, as acoes do pet e as rngs), o estado de cada decisao
    e o estado interno do cerebro. O log sozinho nao distingue as vidas: ele so tem as acoes do dono e o tempo, e o dono simulado nao
    le o pet"""
    texto = json.dumps([repr(bv.resumo_motor(motor)), registro.estados, motor.politica.estado_interno()], sort_keys=True)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _vida(cfg: dict, config: str, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    c0, p0 = time.process_time(), time.perf_counter()
    semente = unidade["semente"]
    nome = f"{config}|{braco}|{dono}|{lugar}|{semente}"
    motor, registro, fab = viver(config, braco, dono, lugar, semente, cfg["dias"], cfg["orcamento_por_dia"])
    texto = motor.log.para_jsonl()
    arquivo = Path(pasta) / "vidas" / config / braco / f"{dono}_{lugar}_{semente}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(texto, encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, semente, arquivo.read_text(encoding="utf-8"))          # G1
    orq.conferir_cenario(motor, registro)
    conferir_vida(config, braco, motor, registro)
    if config == HOJE and braco == APRENDE:                                                # C-HOJE
        hoje, registro_hoje, _ = pv2.viver("HOJE", dono, lugar, semente, cfg["dias"], cfg["orcamento_por_dia"], v38=True)
        if hoje.log.para_jsonl() != texto or assinatura_da_vida(hoje, registro_hoje) != assinatura_da_vida(motor, registro):
            raise E0Divergiu(f"C-HOJE, {nome}: a config de hoje no APRENDE nao e o pet v38 de hoje")
    out = {"vida": nome, "config": config, "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": unidade["base"],
           "k": unidade["k"], **medir(cfg["dias"], motor, registro), "log_sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
           "vida_sha256": assinatura_da_vida(motor, registro)}
    out["custo"] = {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}
    return json.loads(json.dumps(out))


def tarefa(cfg: dict, config: str, unidade: dict, pasta: str) -> list[dict]:
    """uma config numa unidade: os dois bracos nas seis celulas (12 vidas)"""
    return [_vida(cfg, config, braco, dono, lugar, unidade, pasta) for braco in BRACOS for dono, lugar in CELULAS]


# ================================================================== a analise (secoes 2 e 3 da tarefa, escritas antes)
def _media_das_celulas(valores: list, com_none: bool):
    if not com_none:
        return sum(valores) / len(valores)
    vs = [v for v in valores if v is not None]
    return None if not vs else sum(vs) / len(vs)


def por_unidade(registros: list[dict], medida: str, configs, com_none: bool = False) -> dict:
    """config -> braco -> semente -> a media da medida nas seis celulas; falha alto com vida repetida ou faltando. `com_none` (so nos
    descritivos ao lado): a celula sem valor (o CONGELADO nao tem credito) fica fora da media, e a unidade sem nenhuma fica None"""
    idx: dict = {}
    for r in registros:
        chave = (r["config"], r["braco"], r["semente"], r["dono"], r["lugar"])
        if chave in idx:
            raise E0Divergiu(f"vida repetida: {chave}")
        idx[chave] = r[medida]
    sementes = sorted({r["semente"] for r in registros})
    if len(idx) != len(configs) * len(BRACOS) * len(sementes) * len(CELULAS):
        raise E0Divergiu(f"{len(idx)} vidas: cada config tem {len(BRACOS)} bracos x {len(sementes)} unidades x {len(CELULAS)} celulas")
    out = {}
    for config in configs:
        out[config] = {b: {s: _media_das_celulas([idx[(config, b, s, d, lugar)] for d, lugar in CELULAS], com_none) for s in sementes}
                       for b in BRACOS}
    return out


def iguais_a_hoje(registros: list[dict], configs) -> dict:
    """config -> braco -> quantas vidas saem iguais (a `vida_sha256`) a da config de hoje na mesma celula, unidade e braco, e de quantas.
    Um gene com todas as vidas iguais nos dois fatores nao chega a nenhuma decisao do pet: e inerte nesta montagem (descritivo)"""
    idx = {(r["config"], r["braco"], r["semente"], r["dono"], r["lugar"]): r["vida_sha256"] for r in registros}
    out = {}
    for config in configs:
        if config == HOJE:
            continue
        out[config] = {}
        for b in BRACOS:
            chaves = [k for k in idx if k[0] == config and k[1] == b]
            out[config][b] = {"vidas": len(chaves), "iguais": sum(1 for k in chaves if idx[k] == idx[(HOJE, *k[1:])])}
    return out


def genes_inertes(iguais: dict, configs: dict) -> list[str]:
    """os genes em que toda vida do APRENDE, na metade e no dobro, sai igual a da config de hoje"""
    return [g for g in GENES if (ns := [n for n, c in configs.items() if c["gene"] == g])
            and all(iguais[n][APRENDE]["iguais"] == iguais[n][APRENDE]["vidas"] for n in ns)]


def tabela_dos_genes(resumo: dict, configs: dict) -> list[dict]:
    """secao 3: os genes ordenados pelo efeito, o maior |contraste| contra a config de hoje (no nivel do APRENDE ou no valor do
    aprendizado, na metade ou no dobro); no empate, a ordem da secao 2"""
    linhas = []
    for gene in GENES:
        nomes = [n for n, c in configs.items() if c["gene"] == gene]
        if not nomes:
            continue
        por_config = {}
        for n in nomes:
            r = resumo["configs"][n]
            por_config[configs[n]["fator"]] = {"config": n, "valor_do_gene": configs[n]["valor"], "tempo_bem": r["aprende"]["media"],
                                               "valor_do_aprendizado": r["valor"]["media"],
                                               "contraste_aprende": r["contraste_aprende"], "contraste_valor": r["contraste_valor"]}
        efeito = max(abs(x[f]["media"]) for x in por_config.values() for f in ("contraste_aprende", "contraste_valor"))
        linhas.append({"gene": gene, "grupo": next(g for g, gs in GRUPOS.items() if gene in gs), "valor_hoje": configs[nomes[0]]["valor_hoje"],
                       "efeito": efeito, "fora_de_zero": sorted(f"{fator}:{f}" for fator, x in por_config.items()
                                                                for f in ("contraste_aprende", "contraste_valor") if x[f]["fora_de_zero"]),
                       **por_config})
    return sorted(linhas, key=lambda x: (-x["efeito"], GENES.index(x["gene"])))


def ler(resumo: dict, configs: dict) -> dict:
    """a leitura da secao 3, na ordem da tabela; descritiva, sem gate. "Alem do ruido": o IC95 do contraste pareado contra a config de
    hoje nao contem 0. "O valor do aprendizado fica acima de 0": o IC95 do valor (APRENDE - CONGELADO) da config esta todo acima de 0.
    A ressalva do acaso: com poucos contrastes fora de zero (ate o esperado por acaso, arredondado para cima), um gene isolado nao e achado"""
    rs = resumo["configs"]
    genes = {n: c["gene"] for n, c in configs.items() if c["gene"] is not None}
    if any(rs[n][f]["fora_de_zero"] is None for n in genes for f in ("contraste_aprende", "contraste_valor")) \
            or any(r["valor"]["ic_inferior"] is None for r in rs.values()):
        return {"leitura": L_SEM_IC, "segue": SEGUE[L_SEM_IC], "nota": "menos de 2 unidades"}
    mexem_bem = sorted({g for n, g in genes.items() if rs[n]["contraste_aprende"]["fora_de_zero"]}, key=GENES.index)
    mexem_valor = sorted({g for n, g in genes.items() if rs[n]["contraste_valor"]["fora_de_zero"]}, key=GENES.index)
    acima = [n for n, r in rs.items() if r["valor"]["ic_inferior"] > 0.0]
    mexem = set(mexem_bem) | set(mexem_valor)
    nota = None
    if not mexem:
        leitura = L_ESTRUTURAL
    elif mexem_valor and acima:
        leitura = L_BUSCAR
    elif mexem <= DISPUTA and not acima:
        leitura = L_REFLEXOS
    else:
        leitura = L_FORA
        nota = ("um gene fora da disputa mexe e o valor do aprendizado nao fica acima de 0 em nenhuma config" if not acima else
                "o valor do aprendizado fica acima de 0 em alguma config, mas nenhum gene muda o valor do aprendizado")
    acaso = resumo["acaso"]
    teto = math.ceil(acaso["esperados_por_acaso_por_familia"])
    return {"leitura": leitura, "segue": SEGUE[leitura], "nota": nota, "genes_que_mexem_no_tempo_bem": mexem_bem,
            "genes_que_mexem_no_valor_do_aprendizado": mexem_valor, "configs_com_o_valor_acima_de_0": acima,
            "so_a_disputa": bool(mexem) and mexem <= DISPUTA,
            "acaso": {**acaso, "ressalva": {f: 0 < n <= teto for f, n in acaso["fora_de_zero"].items()},
                      "texto": f"com {acaso['contrastes_por_familia']} contrastes por familia e o IC95, cerca de "
                               f"{acaso['esperados_por_acaso_por_familia']:.1f} saem fora de zero por acaso em cada familia; com ate {teto}, "
                               "um gene isolado nao e tratado como achado"}}


def analisar(registros: list[dict], configs: dict | None = None) -> dict:
    configs = configs or CONFIGS
    if HOJE not in configs:
        raise E0Divergiu("a analise precisa da config de hoje")
    resumo = met.sensibilidade_um_por_vez(por_unidade(registros, MEDIDA, configs), HOJE, APRENDE, CONGELADO, NIVEL)
    ao_lado = {}
    for m in AO_LADO:
        pu = por_unidade(registros, m, configs, com_none=True)
        for config, bracos in pu.items():
            ao_lado.setdefault(config, {})[m] = {b: _media_das_celulas(list(v.values()), True) for b, v in bracos.items()}
    # PE-10: a entropia do sorteio de cada config contra a de hoje, pareada por unidade (descritivo; None se alguma unidade nao sorteou)
    pu = por_unidade(registros, ENTROPIA, configs, com_none=True)
    tem = all(v is not None for bracos in pu.values() for por in bracos.values() for v in por.values())
    entropia = {"previsao": PREVISAO_ENTROPIA, "limiar_bits": met.LIMIAR_ENTROPIA_BAIXA,
                "sensibilidade": met.sensibilidade_um_por_vez(pu, HOJE, APRENDE, CONGELADO, NIVEL) if tem else None}
    iguais = iguais_a_hoje(registros, configs)
    return {"medida": MEDIDA, "unidades": resumo["unidades"], "celulas": [list(c) for c in CELULAS],
            "configs": descricao_das_configs(configs), "sensibilidade": resumo, "ao_lado": ao_lado,
            "iguais_a_hoje": iguais, "genes_inertes": genes_inertes(iguais, configs),
            "genes_pelo_efeito": tabela_dos_genes(resumo, configs), "leitura": ler(resumo, configs), "entropia": entropia,
            "nao_diz": NAO_DIZ}


# ================================================================== a trava e a run
def exigir_aprovado(plano: str) -> None:
    linhas = [x for x in plano.splitlines() if x.startswith("**Status:")]
    if not linhas or not linhas[0].startswith(STATUS):
        raise RuntimeError(f"{PLANO} nao esta APROVADO pelo Matheus: {linhas[:1] or 'sem a linha do status'}")


def configs_da_run(cfg: dict) -> dict:
    """as configs que a run vive: as 25, ou, so na fumaca, as que a config nomeia (sempre com a de hoje)"""
    nomes = cfg.get("configs")
    if nomes is None:
        return CONFIGS
    if type(nomes) is not list or HOJE not in nomes or len(set(nomes)) != len(nomes) or set(nomes) - set(CONFIGS):
        raise ValueError(f"configs {nomes!r}: nomes do E0, sem repetir, com {HOJE!r}")
    return {n: CONFIGS[n] for n in CONFIGS if n in nomes}


def modo_da_config(cfg: dict, fase: str = FASE) -> str:
    """`fase`: a do E0, ou a de outra triagem da tarefa com a mesma trava (o C0, `run_v3_plasticidade_c0.py`)"""
    faltam, sobram = (CHAVES_CONFIG - OPCIONAIS) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != fase:
        raise ValueError(f"fase {cfg['fase']!r}: so {fase!r}")
    u = cfg["unidades"]
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora da tarefa: o prefixo, o orcamento ou o K")
    bases = list(u["bases"])
    configs_da_run(cfg)
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    faixa = cfg["faixa"]
    if faixa == PENDENTE or not bases:
        raise bv.SementeSemPlano("a faixa de sementes do E0 esta pendente (PE-5): a coordenadora reserva a faixa em FAIXAS_RESERVADAS, e a "
                                 "config recebe a faixa e as 10 bases antes da run")
    if type(faixa) is not list or len(faixa) != 2 or any(type(x) is not int for x in faixa) or faixa[0] > faixa[1]:
        raise ValueError(f"faixa {faixa!r}: [primeira, ultima], inteiros")
    lo, hi = faixa
    if any(type(b) is not int for b in bases) or len(bases) != N_BASES or len(set(bases)) != N_BASES or not all(lo <= b <= hi for b in bases):
        raise bv.SementeSemPlano(f"bases fora da tarefa: {N_BASES} bases distintas dentro da faixa {lo}...{hi} (PE-5)")
    if any(qlo <= b <= qhi for b in bases for qlo, qhi, _ in FAIXAS_QUEIMADAS):
        raise bv.SementeSemPlano("base numa faixa queimada: faixa queimada nao volta")
    if not any((rlo, rhi) == (lo, hi) for rlo, rhi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {(lo, hi)} nao esta em FAIXAS_RESERVADAS (PE-5)")
    exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    erros = [m for m, ok in ((f"dias {cfg['dias']} (a tarefa: {DIAS})", cfg["dias"] == DIAS), (f"plano {cfg.get('plano')!r}", cfg.get("plano") == PLANO),
                             (f"K por base {u['k']} (a tarefa: {K_POR_BASE})", u["k"] == K_POR_BASE),
                             ("um subconjunto das configs so vale na fumaca", "configs" not in cfg)) if not ok]
    if erros:
        raise ValueError(f"a run segue a tarefa a letra: {erros}")
    return fase


def projecao_h(custos: dict, processos: int = MAX_PROCESSOS) -> float:
    """a projecao de parede da run inteira (as 3 000 vidas), pelo custo medio por vida dos registros (a fumaca)"""
    por_vida = sum(c["vida_parede"] for c in custos.values()) / len(custos)
    return N_VIDAS * por_vida / processos / 3600


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    configs = configs_da_run(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez)")
    livre = ra.exigir_disco(RAIZ)
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None, "python": platform.python_version(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "pv2_sha256": rc._sha_arquivo(Path(pv2.__file__)),
            "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS], "bracos": {b: vars(config_digibrain(b)) for b in BRACOS},
            "configs": descricao_das_configs(configs), "genes": {g: list(gs) for g, gs in GRUPOS.items()}, "faixa": cfg["faixa"],
            "pet": {"inatos": "inatos_e1(), com o gene da config", "sono_segura": vars(CONFIG_SONO_SEGURA_LIGADA),
                    "lance_dono": vars(CONFIG_LANCE_DONO_LIGADA), "equilibrio": vars(pv2.EQUILIBRIO_V38), "bebe": "pv2.bebe_pelas_decisoes"},
            "nivel": NIVEL, "disco_livre_gb": livre,
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py", "corpo.py",
                                                                         "motor_corpo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, n, u, str(pasta))) for u in unidades for n in configs], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    esperadas = len(unidades) * len(configs) * len(BRACOS) * len(CELULAS)
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas}")
    registros.sort(key=lambda r: r["vida"])
    custos = {r["vida"]: r.pop("custo") for r in registros}            # o relogio fora do medidas.json
    bv._gravar(pasta / "medidas.json", bv._dump(registros))
    bv._gravar(pasta / "custos.json", bv._dump(custos))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    if modo == "fumaca":                                      # a fumaca so serve ao custo: nenhuma medida dela e lida
        resultado = {"modo": modo, "fase": FASE, "vidas": len(lidos), "configs": list(configs), "conferencias": "passam"}
    else:
        resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "vidas": len(lidos), **analisar(lidos, configs)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    V.tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    meta["pasta_crua_apagada"] = {"vidas": C4.conferir_e_apagar(pasta / "vidas", pasta / "vidas.tar.gz")}
    meta["custo"] = {"vida_parede_media_s": sum(c["vida_parede"] for c in custos.values()) / len(custos),
                     "vida_cpu_media_s": sum(c["vida_cpu"] for c in custos.values()) / len(custos),
                     "projecao_parede_h_4_processos": projecao_h(custos), "vidas_da_run": N_VIDAS}
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "custos.json", "resultado.json", "vidas.tar.gz")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _resumo(r: dict) -> str:
    """o resumo no console, ASCII puro"""
    res = r["resultado"]
    if res["modo"] == "fumaca":
        return json.dumps({**res, "custo": r["meta"]["custo"]}, indent=1, ensure_ascii=True, default=str)
    return json.dumps({"vidas": res["vidas"], "leitura": res["leitura"],
                       "genes_pelo_efeito": [{k: g[k] for k in ("gene", "efeito", "fora_de_zero")} for g in res["genes_pelo_efeito"]]},
                      indent=1, ensure_ascii=True, default=str)


def main() -> None:
    ap_ = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap_.add_argument("--config", required=True)
    ap_.add_argument("--saida", default=None)
    ap_.add_argument("--processos", type=int, default=1)
    a = ap_.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    pre_run.exigir(ORQUESTRADOR, a.config, a.processos)       # tambem na fumaca: ela vive vidas, e a maquina leva uma carga por vez
    if modo == "fumaca" and a.saida is None:
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)))


if __name__ == "__main__":
    main()
