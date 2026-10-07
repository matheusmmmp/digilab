"""V2, COMPARACAO-A-C: o piloto, o adendo de tamanho e a validacao da comparacao dos cerebros A x C (docs/TAREFA_V2_COMPARACAO_A_C.md;
plano docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md, secoes 2 a 8, adendos 1 e 2). O B nao roda: saiu por "nao aprende" (secao 7; decisao de
2026-10-06 no REGISTRO_DESVIOS).

Quem compara, cada um no seu ponto, lidos dos artefatos (nada se escolhe aqui):
    A  os lobos no ponto da K2 (artifacts_v2_calibracao_conjunta/escolha.json): T3, g, w0_info, w0_pedido, ganho; canais ligados, K4,
       montagem completa (o cerebro A da validacao unica, a mesma bancada do experimento maior);
    C  o Fly-like no ponto da calibracao dele (artifacts_v2_comparacao_cerebros/calibracao_C/escolha.json): passo, teto, w0_info; o mesmo
       ganho do A (a fonte do sinal e comum, C-1). O C nao le a montagem (as pecas do A; ele tem a arquitetura dele) nem a chave dos
       canais (no C sao a arquitetura). O mundo e o dono sao os mesmos para os dois, o K4 incluido (o dono do P3 julga a fruta).

Por unidade (genoma, semente) e por condicao (casado_frutas, descasado, mutavel), o dono atencioso (secao 1.2):
    P0                         comum (o aprendizado desligado e o instinto byte a byte nos dois: contrato 1.1)
    A e C em P1, P2, P2e, P3   modo fechado (secao 2): cada cerebro vive a propria vida
    o so cuidado               o acoplado sem_ensino de P2, P2e e P3, de cada cerebro (o G5 contra o acoplado do proprio cerebro)
    a mesma experiencia        o C no registro do P1 do A (filtro nenhum), no descasado e no mutavel (modo acoplado, secao 2), com a
                               divergencia por dia entre a politica do C e a do A nas sondas
Toda vida e gravada e rejogada do disco bit a bit (Bancada.conferir_replay); o replay das medidas tambem confere.

Analise (secoes 3 a 5): a familia CC-1 e CC-2 (C - A no P1; taxa_fruta_ruim final no descasado, depois da troca no mutavel), Holm de dois,
bilateral, alfa 0,05, empate pelo IC 90% dentro de +-delta (o delta do adendo 2 do experimento maior); os secundarios da secao 4 sem o B
(C - A nos outros bracos e no casado), descritivos; a legibilidade (a sonda do aprendido: a parte aprendida mudou a escolha, com o mesmo
u), a deriva, o custo e a divergencia acoplada, descritivos com IC; as predicoes do experimento maior por cerebro, descritivas; e a tabela
do M6 (secao 5), preenchida ate onde os dados deixam. No piloto, o tamanho de amostra (secao 6.3, com o alfa de Holm de dois: alfa / 2).

Modos pelas bases das unidades: fumaca (sementes dos testes), piloto (28101...28505, K = 4) e validacao (29101...29505, K do adendo 2,
uma vez: com resumo.json na pasta, recusa). As do experimento maior (30101...30505 e a queimada 15101...15505) nunca.

    python experiments/run_v2_comparacao_cerebros.py --config experiments/configs/v2_comparacao_cerebros/piloto_ac.json
"""
from __future__ import annotations

import argparse
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

import bancada_v2 as bv  # noqa: E402
import cerebro_c_bancada as cbc  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.config import CONFIG_CEREBRO_C_APRENDIZ, CONFIG_CONSEQUENCIA, CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.evolucao import politica_no_tick  # noqa: E402
from digilab.metrics import (_medias_bootstrap_agrupadas, bootstrap_ic, contraste_pareado, dentro_da_margem,  # noqa: E402
                             distribuicoes_de_acao, estados_sonda, holm, jsd_media, tamanho_amostra)
from digilab.motivo import _motivo_lobos_decisao  # noqa: E402
from digilab.policies.lobos import sortear  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md"
TAREFA = "docs/TAREFA_V2_COMPARACAO_A_C.md"
ESCOLHA_A = "artifacts_v2_calibracao_conjunta/escolha.json"
ESCOLHA_C = "artifacts_v2_comparacao_cerebros/calibracao_C/escolha.json"
CONFIG_EXPERIMENTO_MAIOR = "experiments/configs/v2_experimento_maior/validacao.json"   # o delta do adendo 2 de la (secao 4)
PREFIXO = "comparacao-cerebros"
DONO = "atencioso"
MUNDOS = ("casado_frutas", "descasado", "mutavel")
BRACOS = ("P1", "P2", "P2e", "P3")
COM_DONO = ("P2", "P2e", "P3")                       # os bracos com o so cuidado acoplado (secao 1.2)
FILTRO_SO_CUIDADO = "sem_ensino"
MESMA_EXPERIENCIA = ("descasado", "mutavel")         # o C no registro do P1 do A (secao 6.3, custo: "descasado e mutavel")
CEREBROS = {"A": "lobos", "C": cbc.CEREBRO_C}
JANELA = {"casado_frutas": "final", "descasado": "final", "mutavel": "depois_da_troca"}   # secao 3: a primaria por condicao
PRIMARIOS = {"CC-1": ("P1", "descasado"), "CC-2": ("P1", "mutavel")}
NAO_TESTAVEIS = {"CB-1": "nao testavel: o B nao fecha (secao 7, 'nao aprende')",
                 "CB-2": "nao testavel: o B nao fecha (secao 7, 'nao aprende')"}
ALFA = 0.05
PODER = 0.8
LIMIAR_LEGIBILIDADE = 0.05      # secao 5, passo 2: empate com |diferenca| < 0,05 (PROPOSTO) ou IC 95% contendo 0
LIMIAR_CUSTO = 0.20             # secao 5, passo 4: empate com diferenca < 20% (PROPOSTO)
REPLICAS_PODER = 2000
CHAVES = {"descricao", "plano", "unidades", "dias", "orcamento", "sonda", "bootstrap", "delta", "simulacao", "adendo", "saida"}


class ValidacaoJaFeita(RuntimeError):
    """A validacao roda uma vez (secao 8): a pasta ja tem o resumo."""


def _dump(obj) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False, default=repr) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _ler(caminho: str) -> dict:
    return json.loads((RAIZ / caminho).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ os pontos e a bancada


def ponto_a() -> dict:
    return dict(_ler(ESCOLHA_A)["ponto"])


def ponto_c() -> dict:
    e = _ler(ESCOLHA_C)
    if not e.get("cerebro_fecha") or e.get("nao_aprende"):
        raise RuntimeError(f"{ESCOLHA_C}: o C nao fechou; a comparacao nao roda com ele")
    return dict(e["ponto"])


def delta_do_experimento_maior() -> float:
    return float(_ler(CONFIG_EXPERIMENTO_MAIOR)["delta"])


class BancadaAC(cbc.BancadaComC):
    """A bancada do experimento maior (montagem completa, K4, canais) com o C a mais. A montagem e do cerebro A: para o C o braco e o
    proprio braco (sem as pecas do A), como na BancadaComC; assim as medidas do N6 (memoria do A) nunca leem o C."""

    def braco(self, espec: bv.EspecVida) -> bv.Braco:
        if espec.cerebro == cbc.CEREBRO_C:
            return bv.braco_de(espec.braco)
        return super().braco(espec)


def config_do_a(cfg: dict) -> dict:
    """A config da bancada do A, a mesma chave a chave da do experimento maior (config_da_bancada): ponto T3, as pecas da K2, os canais,
    o K4 e a montagem completa."""
    a = ponto_a()
    return {"dias": int(cfg["dias"]), "orcamento": int(cfg["orcamento"]), "ponto": "T3",
            "lobos": {"memoria_ganho": int(a["g"]), "w0_pedido": int(a["w0_pedido"]), "w0_info": int(a["w0_info"])},
            "consequencia": {"ganho": int(a["ganho"]), "canais_ligados": True}, "julgamento_fruta": em.K4_DONO_JULGA_FRUTA,
            "montagem": em.MONTAGEM}


def bancada_da_config(cfg: dict) -> BancadaAC:
    a, c = ponto_a(), ponto_c()
    if int(c["ganho"]) != int(a["ganho"]):
        raise ValueError(f"o ganho do C ({c['ganho']}) nao e o do A ({a['ganho']}): a fonte do sinal e comum (C-1)")
    base = bv.bancada_da_config(config_do_a(cfg))
    cc = replace(CONFIG_CEREBRO_C_APRENDIZ, passo=int(c["passo"]), teto=int(c["teto"]), w0_info=int(c["w0_info"]))
    return BancadaAC(**{f: getattr(base, f) for f in base.__dataclass_fields__}, cfg_cerebro_c=cc)


# ------------------------------------------------------------------ config, modo e unidades


def modo_e_unidades(cfg: dict) -> tuple[str, list[dict]]:
    faltam = {"plano", "unidades", "dias", "orcamento", "sonda", "bootstrap"} - set(cfg)
    sobram = set(cfg) - CHAVES
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["plano"] != PLANO or not (RAIZ / PLANO).is_file():
        raise bv.SementeSemPlano(f"o plano da comparacao e {PLANO}, nao {cfg['plano']!r}")
    u = cfg["unidades"]
    if set(u) != {"bases", "k", "prefixo"} or u["prefixo"] != PREFIXO:
        raise ValueError(f"unidades: {{'bases', 'k', 'prefixo': {PREFIXO!r}}} (secao 6.2), nao {u}")
    bases = tuple(int(b) for b in u["bases"])
    if set(bases) <= bv.SEMENTES_TESTE:
        modo = "fumaca"
    elif bases == bv.BASES_COMPARACAO["calibracao"]:
        modo = "piloto"
    elif bases == bv.BASES_COMPARACAO["validacao"]:
        modo = "validacao"
    else:
        raise bv.SementeSemPlano(f"bases {bases}: so as dos testes, {bv.BASES_COMPARACAO['calibracao']} (piloto) ou "
                                 f"{bv.BASES_COMPARACAO['validacao']} (validacao)")
    if modo == "piloto" and int(u["k"]) != 4:
        raise ValueError("o piloto e o da calibracao: K = 4 por base, 20 unidades (secao 6.2)")
    if modo != "fumaca" and int(cfg["dias"]) != em.DIAS_PLANO:
        raise ValueError(f"vida de {cfg['dias']} dias: o plano e de {em.DIAS_PLANO}")
    if modo != "fumaca" and float(cfg.get("delta", -1)) != delta_do_experimento_maior():
        raise ValueError("o delta e o do adendo 2 do experimento maior (secao 4), lido de " + CONFIG_EXPERIMENTO_MAIOR)
    if modo == "validacao":
        if cfg.get("adendo") != 2 or "## Adendo 2" not in (RAIZ / PLANO).read_text(encoding="utf-8"):
            raise ValueError("a validacao precisa do adendo 2 do plano commitado antes (campo 'adendo': 2)")
    unidades = bv.unidades_derivadas(bases, int(u["k"]), PREFIXO)
    for un in unidades:
        for x in (un["semente"], un["genoma"]):
            if any(ini <= x <= fim for ini, fim, _ in bv.FAIXAS_QUEIMADAS):
                raise bv.SementeSemPlano(f"unidade {un} cai numa faixa queimada")
    return modo, unidades


# ------------------------------------------------------------------ o que se le de cada vida


def legibilidade_a(cerebro) -> dict:
    """A sonda do aprendido do A (contrato 1.1): a escolha com a parte aprendida zerada e o mesmo u e o sorteio com os pesos do prior (o
    lobo de impulsos), a regra do motivo honesto (motivo._motivo_lobos_decisao); decisao com um candidato so, o impulso decidiu. Ao lado,
    as decisoes do aprendido que viram fator (o G4 da L1). A sonda e o diagnostico do motivo tem de concordar (falha alto)."""
    dec = apr = multi = apr_multi = fator = 0
    for k, m in enumerate(cerebro.motivos):
        dec += 1
        if m["u"] is None:
            continue
        multi += 1
        cands = m["candidatos"]
        decidiu = cands[sortear([m["contribuicoes"]["impulsos"][a] for a in cands], m["u"])] != m["acao"]
        mot, diag = _motivo_lobos_decisao(m, k * CONFIG_PADRAO.intervalo_decisao_ticks, None)
        if diag["valor_decidiu"] != decidiu:
            raise RuntimeError(f"decisao {k}: a sonda do aprendido e o motivo divergem")
        apr += decidiu
        apr_multi += decidiu
        fator += decidiu and bool(mot.fatores)
    return {"decisoes": dec, "aprendido_decidiu": apr, "decisoes_com_escolha": multi, "aprendido_decidiu_com_escolha": apr_multi,
            "aprendido_com_fator": fator}


def legibilidade_c(cerebro) -> dict:
    """A sonda do aprendido do C (`motivos[k]["sonda"]`, contrato 1.1). O C nao tem a expressao do motivo (fator): fica None."""
    dec = apr = multi = apr_multi = 0
    for m in cerebro.motivos:
        dec += 1
        d = bool(m["sonda"]["aprendido_decidiu"])
        apr += d
        if m["u"] is not None:
            multi += 1
            apr_multi += d
        elif d:
            raise RuntimeError("o aprendido decidiu uma decisao com um candidato so")
    return {"decisoes": dec, "aprendido_decidiu": apr, "decisoes_com_escolha": multi, "aprendido_decidiu_com_escolha": apr_multi,
            "aprendido_com_fator": None}


def custo(vida: bv.VidaBancada, segundos: float, dias: int) -> dict:
    """Secao 3: CPU por decisao (o tempo de Bancada.vida, sem o replay; maquina no meta), bytes de log por dia e o estado interno sem
    os motivos (o que o pet guarda: os pesos), em bytes de JSON, e os parametros aprendiveis."""
    cerebro = bv.do_braco(vida.motor.politica).cerebro
    interno = vida.motor.politica.estado_interno()
    sem_motivos = {k: v for k, v in interno.items() if k != "motivos"}
    decisoes = len(cerebro.motivos)
    return {"segundos_vida": segundos, "decisoes": decisoes, "us_por_decisao": 1e6 * segundos / decisoes if decisoes else None,
            "bytes_log_por_dia": len(vida.motor.log.para_jsonl().encode("utf-8")) / dias,
            "bytes_estado_sem_motivos": len(json.dumps(sem_motivos, sort_keys=True).encode("utf-8")),
            "parametros_aprendiveis": cerebro.n_pesos()}


def divergencia_acoplada(bancada: BancadaAC, vida_a: bv.VidaBancada, vida_c: bv.VidaBancada, sonda: dict) -> list[float]:
    """Secao 3: no acoplado da mesma experiencia, a JSD (bits) entre a politica do C e a do A no fim de cada dia, nas mesmas sondas da
    deriva. Os dois rejogam o mesmo registro (o log do C e o do P1 do A: filtro nenhum)."""
    if vida_c.motor.log.para_jsonl() != vida_a.motor.log.para_jsonl():
        raise RuntimeError("o acoplado da mesma experiencia tem de ter o registro do P1 do A")
    estados = estados_sonda(sonda["estados"], sonda["semente"])
    serie = []
    for d in range(1, bancada.dias + 1):
        pols = [bv.do_braco(politica_no_tick(v.motor.log, bancada.fabrica_politica(v.espec), v.espec.semente, d * TICKS_POR_DIA,
                                             bancada.fabrica_motor(v.espec))) for v in (vida_a, vida_c)]
        dist = [distribuicoes_de_acao(p, estados, sonda["amostras"], sonda["semente"]) for p in pols]
        serie.append(jsd_media(dist[1], dist[0]))
    return serie


def acoplar_no_c(bancada: BancadaAC, origem: bv.VidaBancada) -> bv.VidaBancada:
    """O C no registro do P1 do A (secao 2, modo acoplado, filtro nenhum): o mesmo braco, o cerebro trocado. Bancada.acoplar guarda o
    cerebro da origem; aqui so ele muda, e a vida e conferida pelo replay como toda outra."""
    if origem.espec.cerebro != "lobos" or origem.espec.braco != "P1" or origem.origem is not None:
        raise ValueError("o acoplado da mesma experiencia e o C no registro de um P1 do A")
    espec = replace(origem.espec, cerebro=cbc.CEREBRO_C)
    m = bancada.rejogar(origem.motor.log, espec)
    vida = bv.VidaBancada(espec, m, bv.contar_acoes(origem.motor.log)[0], origem=origem.nome, origem_braco="P1-A", filtro="nenhum")
    bancada.conferir_replay(vida)
    return vida


# ------------------------------------------------------------------ as vidas


def rodar_vidas(cfg: dict, bancada: BancadaAC, unidades: list[dict], pasta: Path, log=print) -> dict:
    """Todas as vidas, unidade por unidade (os motores saem da memoria ao fim da unidade). Devolve {rotulo da vida: medidas}."""
    dias, sonda = int(cfg["dias"]), cfg["sonda"]
    medidas, t0 = {}, time.perf_counter()

    def guardar(v: bv.VidaBancada, rotulo: str, cer: str, un: dict, piso=None, taxa_p0=None, segundos=None) -> dict:
        nome = f"{rotulo.replace(':', '-').replace('<', '~de-')}~{v.espec.mundo}@{v.espec.semente}"
        caminho = pasta / "vidas" / f"{nome}.jsonl"
        _gravar(caminho, v.motor.log.para_jsonl())
        bancada.conferir_replay(v, caminho.read_text(encoding="utf-8"))
        m = bancada.medir(v, sonda, piso, taxa_p0)
        cerebro = bv.do_braco(v.motor.politica).cerebro
        m.update({"rotulo": rotulo, "cerebro_ac": cer, "unidade": {k: un[k] for k in ("base", "k", "semente", "genoma")},
                  "legibilidade": legibilidade_c(cerebro) if v.espec.cerebro == cbc.CEREBRO_C else legibilidade_a(cerebro)})
        if segundos is not None:
            m["custo"] = custo(v, segundos, dias)
        if nome in medidas:
            raise RuntimeError(f"vida repetida: {nome}")
        medidas[nome] = m
        return m

    for i, un in enumerate(unidades):
        g, s = un["genoma"], un["semente"]
        for mundo in MUNDOS:
            p0 = bancada.vida(bv.EspecVida(DONO, "P0", s, g, mundo))
            m0 = guardar(p0, "P0", "comum", un)
            piso, taxa_p0 = m0["acerto_total"], m0["frutas"]["taxa_fruta_ruim"]["total"]["taxa"]
            p1_a = None
            for letra, cer in CEREBROS.items():
                for braco in BRACOS:
                    t = time.perf_counter()
                    v = bancada.vida(bv.EspecVida(DONO, braco, s, g, mundo, cer))
                    seg = time.perf_counter() - t
                    guardar(v, f"{letra}:{braco}", letra, un, piso, taxa_p0, seg)
                    if braco in COM_DONO:
                        guardar(bancada.acoplar(v, braco, FILTRO_SO_CUIDADO), f"{letra}:{braco}<{FILTRO_SO_CUIDADO}", letra, un,
                                piso, taxa_p0)
                    if letra == "A" and braco == "P1":
                        p1_a = v
            if mundo in MESMA_EXPERIENCIA:
                c_em_a = acoplar_no_c(bancada, p1_a)
                m = guardar(c_em_a, "C<A:P1", "C", un, piso, taxa_p0)
                m["divergencia_acoplada"] = divergencia_acoplada(bancada, p1_a, c_em_a, sonda)
        log(f"[{i + 1}/{len(unidades)}] unidade {s}: {len(medidas)} vidas, {time.perf_counter() - t0:.0f} s")
    return {"medidas": medidas, "segundos": time.perf_counter() - t0}


# ------------------------------------------------------------------ a analise (pura sobre as medidas)


def indice(medidas: dict) -> dict:
    """(rotulo, mundo, (genoma, semente)) -> medidas da vida."""
    idx = {}
    for m in medidas.values():
        chave = (m["rotulo"], m["mundo"], (m["genoma"], m["semente"]))
        if chave in idx:
            raise ValueError(f"vida repetida: {chave}")
        idx[chave] = m
    return idx


def p_bilateral(grupos: dict, boot: dict) -> float | None:
    """O p bilateral do bootstrap (a mesma reamostragem do contraste_pareado): 2 x a menor cauda, no maximo 1."""
    gs = [list(map(float, v)) for _, v in sorted(grupos.items(), key=lambda kv: repr(kv[0])) if len(v)]
    if len(gs) < 2:
        return None
    medias = _medias_bootstrap_agrupadas(gs, boot["reamostragens"], boot["semente"])
    r = len(medias)
    return min(1.0, 2.0 * min(sum(1 for x in medias if x <= 0.0), sum(1 for x in medias if x >= 0.0)) / r)


def contraste_c_menos_a(idx: dict, unidades: list[dict], braco: str, mundo: str, medida: str, boot: dict) -> dict:
    """C - A pareado por unidade (secao 4), bilateral; negativo = o C come menos a fruta ruim."""
    d = em.diferencas(idx, unidades, mundo, medida, f"C:{braco}", f"A:{braco}")
    r = contraste_pareado(d["grupos"], boot["reamostragens"], boot["semente"])
    return {"d": f"C:{braco} - A:{braco}", "braco": braco, "mundo": mundo, "medida": medida, **r,
            "p_bilateral": p_bilateral(d["grupos"], boot), "sem_valor": d["sem_valor"],
            "valores": {str(k): v for k, v in d["grupos"].items()}}


def leitura(c: dict, rejeita: bool | None, delta: float | None) -> str:
    """Secao 4: empate quando o IC 90% fica dentro de (-delta, +delta) (a margem de relevancia, antes do teste); fora dela, C melhor ou A
    melhor quando a diferenca passa (com Holm nos primarios; sem Holm, nos secundarios, pelo IC 95% inteiro de um lado, descritivo);
    senao, inconclusivo."""
    if c["media"] is None:
        return "sem valor"
    if dentro_da_margem(c["ic90"], delta):
        return "empate"
    if rejeita is None:
        lado = c["ic95"] is not None and (c["ic95"]["ic_superior"] < 0.0 or c["ic95"]["ic_inferior"] > 0.0)
    else:
        lado = rejeita
    if lado:
        return "C melhor" if c["media"] < 0.0 else "A melhor"
    return "inconclusivo"


def ic(valores: list, boot: dict) -> dict:
    v = [x for x in valores if x is not None]
    if len(v) < 2:
        return {"media": v[0] if v else None, "ic_inferior": None, "ic_superior": None, "n": len(v), "sem_valor": len(valores) - len(v)}
    return {**bootstrap_ic(v, boot["reamostragens"], boot["semente"], boot["nivel"]), "sem_valor": len(valores) - len(v)}


def _unidade(u: dict) -> tuple:
    return (u["genoma"], u["semente"])


def fracao_legivel(idx: dict, unidades: list[dict], rotulo: str, mundos, chave: str = "aprendido_decidiu",
                   base: str = "decisoes") -> list:
    """Por unidade: a fracao das decisoes (dos mundos dados, somadas) em que a parte aprendida mudou a escolha."""
    out = []
    for u in unidades:
        ms = [idx[(rotulo, mu, _unidade(u))]["legibilidade"] for mu in mundos]
        if any(m[chave] is None for m in ms):
            out.append(None)
            continue
        n = sum(m[base] for m in ms)
        out.append(sum(m[chave] for m in ms) / n if n else None)
    return out


def legibilidade(idx, unidades, boot) -> dict:
    """Secao 5, passo 2: P1 descasado, a fracao decidida pelo aprendido (a sonda, a mesma regra nos dois), com IC; C - A pareado. Ao
    lado (descritivo): as decisoes com escolha (mais de um candidato), o G4 com fator do A, as tres condicoes e os outros bracos."""
    out = {"por_cerebro": {}, "descritivo": {}}
    for letra in CEREBROS:
        out["por_cerebro"][letra] = ic(fracao_legivel(idx, unidades, f"{letra}:P1", ("descasado",)), boot)
        desc = {}
        for braco in BRACOS:
            desc[braco] = {mu: ic(fracao_legivel(idx, unidades, f"{letra}:{braco}", (mu,)), boot) for mu in MUNDOS}
        desc["P1_com_escolha_descasado"] = ic(fracao_legivel(idx, unidades, f"{letra}:P1", ("descasado",),
                                                             "aprendido_decidiu_com_escolha", "decisoes_com_escolha"), boot)
        if letra == "A":
            desc["P1_com_fator_descasado"] = ic(fracao_legivel(idx, unidades, "A:P1", ("descasado",), "aprendido_com_fator"), boot)
        out["descritivo"][letra] = desc
    fa = fracao_legivel(idx, unidades, "A:P1", ("descasado",))
    fc = fracao_legivel(idx, unidades, "C:P1", ("descasado",))
    grupos = {}
    for u, a, c in zip(unidades, fa, fc):
        if a is not None and c is not None:
            grupos.setdefault(u["semente"], []).append(c - a)
    d = contraste_pareado(grupos, boot["reamostragens"], boot["semente"])
    empate = d["media"] is None or abs(d["media"]) < LIMIAR_LEGIBILIDADE or (
        d["ic95"] is not None and d["ic95"]["ic_inferior"] <= 0.0 <= d["ic95"]["ic_superior"])
    out["c_menos_a"] = {**d, "empate": empate, "limiar": LIMIAR_LEGIBILIDADE,
                        "vence": None if empate else ("C" if d["media"] > 0 else "A")}
    return out


def deriva(idx, unidades, dias: int, boot) -> dict:
    """Secao 3: JSD ao instinto no fim de cada dia, por cerebro, P1 (as tres condicoes juntas por unidade) e a razao dia 14 / dia 7."""
    out = {}
    meio = dias // 2
    for letra in CEREBROS:
        por_dia = []
        for d in range(dias):
            por_dia.append(ic([sum(idx[(f"{letra}:P1", mu, _unidade(u))]["custo_da_plasticidade"]["deriva_por_dia"][d] for mu in MUNDOS)
                               / len(MUNDOS) for u in unidades], boot))
        fim, meio_v = por_dia[-1]["media"], por_dia[meio - 1]["media"] if meio else None
        out[letra] = {"por_dia": por_dia, "razao_fim_meio": (fim / meio_v) if fim is not None and meio_v else None}
    return out


def custos(medidas: dict, boot) -> dict:
    """Secao 3 e passo 4 do M6: por cerebro, nas vidas fechadas (P1 a P3 nas tres condicoes), a media por unidade do CPU por decisao e dos
    bytes de log por dia; a diferenca relativa C / A - 1 e o empate abaixo de 20%."""
    out = {}
    for letra in CEREBROS:
        ms = [m for m in medidas.values() if m["cerebro_ac"] == letra and "custo" in m]
        por_u: dict = {}
        for m in ms:
            por_u.setdefault(m["semente"], []).append(m["custo"])
        out[letra] = {k: ic([sum(c[k] for c in cs) / len(cs) for _, cs in sorted(por_u.items())], boot)
                      for k in ("us_por_decisao", "bytes_log_por_dia", "bytes_estado_sem_motivos")}
        out[letra]["parametros_aprendiveis"] = sorted({m["custo"]["parametros_aprendiveis"] for m in ms})
        out[letra]["vidas"] = len(ms)
    rel = {}
    for k in ("us_por_decisao", "bytes_log_por_dia"):
        a, c = out["A"][k]["media"], out["C"][k]["media"]
        rel[k] = {"c_sobre_a_menos_1": (c / a - 1.0) if a and c is not None else None}
        rel[k]["empate"] = rel[k]["c_sobre_a_menos_1"] is not None and abs(rel[k]["c_sobre_a_menos_1"]) < LIMIAR_CUSTO
        rel[k]["vence"] = None if rel[k]["empate"] or rel[k]["c_sobre_a_menos_1"] is None else (
            "C" if rel[k]["c_sobre_a_menos_1"] < 0 else "A")
    out["relativo"] = rel
    return out


def divergencias(medidas: dict, dias: int, boot) -> dict:
    out = {}
    for mu in MESMA_EXPERIENCIA:
        ms = sorted((m for m in medidas.values() if m["rotulo"] == "C<A:P1" and m["mundo"] == mu), key=lambda m: m["semente"])
        out[mu] = {"por_dia": [ic([m["divergencia_acoplada"][d] for m in ms], boot) for d in range(dias)], "unidades": len(ms)}
    return out


def so_cuidado(idx, unidades, boot) -> dict:
    """O canal de cuidado (G5, secao 3), descritivo: por cerebro e braco com dono, original - o proprio so cuidado acoplado, no tempo
    fora de privacao e na saude media (as tres condicoes)."""
    out = {}
    for letra in CEREBROS:
        for braco in COM_DONO:
            for medida in ("fracao_fora_de_privacao", "saude_media"):
                for mu in MUNDOS:
                    grupos = {}
                    for u in unidades:
                        a = idx[(f"{letra}:{braco}", mu, _unidade(u))][medida]
                        b = idx[(f"{letra}:{braco}<{FILTRO_SO_CUIDADO}", mu, _unidade(u))][medida]
                        grupos.setdefault(u["semente"], []).append(a - b)
                    out[f"{letra}:{braco}/{medida}/{mu}"] = contraste_pareado(grupos, boot["reamostragens"], boot["semente"])
    return out


def predicoes_por_cerebro(idx, unidades, boot, delta) -> dict:
    """Secao 3: as predicoes do experimento maior por cerebro, descritivas (os contrastes primarios dele e a equivalencia da 5, com o
    Holm de seis so como leitura; as do A que valem sao as da validacao unica)."""
    out = {}
    for letra in CEREBROS:
        sub = {}
        for (rot, mu, ku), m in idx.items():
            if rot == "P0":
                sub[("P0", mu, ku)] = m
            elif rot.startswith(f"{letra}:") and "<" not in rot:
                sub[(rot.split(":", 1)[1], mu, ku)] = m
        cs = {c.nome: em.calcular_contraste(sub, unidades, c, boot) for c in em.PRIMARIOS}
        h = holm({k: c["p_unilateral"] for k, c in cs.items()}, ALFA)
        eq = em.calcular_contraste(sub, unidades, em.EQUIVALENCIA, boot)
        out[letra] = {"primarios": {k: {"media": c["media"], "ic95": c["ic95"], "p_unilateral": c["p_unilateral"],
                                        "holm_rejeita": h[k]["rejeita"], "d": c["d"], "sem_valor": len(c["sem_valor"])}
                                    for k, c in cs.items()},
                      "p5_equivalencia": {"media": eq["media"], "ic90": eq["ic90"], "dentro_de_delta": dentro_da_margem(eq["ic90"], delta)}}
    return out


PILOTO_C = "artifacts_v2_comparacao_cerebros/calibracao_C/piloto.json"


def conferencia_calibracao_c(idx: dict, unidades: list[dict], boot: dict, dias: int) -> dict:
    """A tarefa pede reaproveitar as vidas do C da calibracao se a config for a mesma. As vidas ficaram fora do git (so os resumos); o
    piloto as refaz e confere que sao as mesmas: o "nao aprende" do C (P1, as tres condicoes, a conta de run_v2_calibracao_cerebro_c)
    tem de dar os numeros gravados em calibracao_C/piloto.json, com o mesmo bootstrap."""
    gravado = _ler(PILOTO_C)
    der, frac = [], []
    for u in sorted(unidades, key=lambda x: x["semente"]):          # a ordem da calibracao (_por_unidade: por semente)
        ms = [idx[("C:P1", mu, _unidade(u))] for mu in MUNDOS]
        der.append(sum(m["custo_da_plasticidade"]["deriva_por_dia"][dias - 1] for m in ms) / len(ms))
        frac.append(sum(m["legibilidade"]["aprendido_decidiu"] for m in ms) / sum(m["legibilidade"]["decisoes"] for m in ms))
    agora = {"deriva_dia_final": ic(der, boot), "fracao_aprendido_decidiu": ic(frac, boot)}
    iguais = all(agora[k][x] == gravado[k][x] for k in agora for x in ("media", "ic_inferior", "ic_superior"))
    return {"agora": agora, "gravado": {k: gravado[k] for k in agora}, "iguais": iguais}


def tamanho(primarios: dict, delta: float, simulacao: dict | None) -> dict:
    """Secao 6.3 com a familia de dois (adendo 2): N = ((z_{1-alfa'/2} + z_0,8) sigma_d / delta)^2, alfa' = alfa / 2 (o passo mais
    exigente do Holm de dois), bilateral; a conta unilateral da tamanho_amostra com alfa' / 2 e a mesma. Conferencia pelo poder simulado
    (bootstrap das unidades centradas em delta, o teste t no mesmo alfa' / 2). N da validacao = o maior, ao multiplo de 5."""
    alfa_lado = ALFA / len(primarios) / 2.0
    out, ns = {}, []
    for nome, c in primarios.items():
        vs = [x for g in c["valores"].values() for x in g]
        if len(vs) < 2:
            out[nome] = {"sigma_d": None, "n": None, "motivo": "menos de 2 unidades com valor"}
            continue
        m = sum(vs) / len(vs)
        sigma = math.sqrt(sum((x - m) ** 2 for x in vs) / (len(vs) - 1))
        n = tamanho_amostra(sigma, delta, alfa_lado, PODER, 5)
        out[nome] = {"sigma_d": sigma, "sigma2_d": sigma ** 2, "media_d": m, "unidades": len(vs), "n_formula": n}
        ns.append(n)
        if simulacao is not None:
            sim = em.n_simulado(vs, delta, alfa_lado, PODER, simulacao["replicas"], simulacao["semente"])
            out[nome].update({"n_simulado": sim["n"], "poder_no_n_simulado": sim["poder"], "motivo_simulado": sim.get("motivo")})
            if sim["n"] is not None:
                ns.append(sim["n"])
    n_val = max(ns) if ns else None
    return {"por_contraste": out, "alfa_familia": ALFA, "alfa_passo_bilateral": ALFA / len(primarios), "alfa_por_lado": alfa_lado,
            "poder": PODER, "delta": delta, "n_validacao": n_val, "k_validacao": None if n_val is None else n_val // 5,
            "regra": "o maior entre a formula e o N simulado de cada contraste, ao multiplo de 5"}


def tabela_m6(prim: dict, leg: dict, cst: dict) -> list[dict]:
    """Secao 5, aplicada de cima para baixo: um cerebro so passa ao passo seguinte se empatar com o melhor no passo atual. Preenchida ate
    onde os dados deixam; a escolha e do Matheus."""
    linhas, decidido = [], None
    linhas.append({"passo": 0, "criterio": "admissao", "A": "fecha (K2)", "C": "fecha (calibracao C, piloto: aprende)",
                   "B": "nao fecha: nao aprende (piloto da calibracao B)", "resultado": "A e C seguem"})
    leituras = [prim[k]["leitura_m6"] for k in PRIMARIOS]
    if all(x == "empate" for x in leituras):
        r1 = "empate"
    elif {"C melhor"} >= set(leituras) - {"empate"} and "C melhor" in leituras:
        r1, decidido = "C vence", "C"
    elif {"A melhor"} >= set(leituras) - {"empate"} and "A melhor" in leituras:
        r1, decidido = "A vence", "A"
    else:
        r1, decidido = "conflito entre CC-1 e CC-2 (um de cada lado): o Matheus le", "?"
    linhas.append({"passo": 1, "criterio": "desempenho (CC-1, CC-2)", **{k: prim[k]["leitura_m6"] for k in PRIMARIOS},
                   "resultado": r1})
    if decidido is None:
        lc = leg["c_menos_a"]
        r2 = "empate" if lc["empate"] else f"{lc['vence']} vence"
        decidido = None if lc["empate"] else lc["vence"]
        linhas.append({"passo": 2, "criterio": "legibilidade (P1 descasado)", "A": leg["por_cerebro"]["A"]["media"],
                       "C": leg["por_cerebro"]["C"]["media"], "c_menos_a": lc["media"], "resultado": r2})
    if decidido is None:
        linhas.append({"passo": 3, "criterio": "determinismo inteiro e porte", "A": "pesos inteiros, sem funcao transcendental",
                       "C": "pesos inteiros, sem funcao transcendental", "resultado": "empate (dois cerebros inteiros)"})
        rel = cst["relativo"]
        emp = rel["us_por_decisao"]["empate"] and rel["bytes_log_por_dia"]["empate"]
        venc = {rel[k]["vence"] for k in ("us_por_decisao", "bytes_log_por_dia")} - {None}
        if emp:
            r4 = "empate"
        elif len(venc) == 1:
            r4 = f"{venc.pop()} vence"
            decidido = r4[0]
        else:
            r4 = "conflito entre CPU e log: o Matheus le"
            decidido = "?"
        linhas.append({"passo": 4, "criterio": "custo", "us_por_decisao_c_sobre_a_menos_1": rel["us_por_decisao"]["c_sobre_a_menos_1"],
                       "bytes_log_por_dia_c_sobre_a_menos_1": rel["bytes_log_por_dia"]["c_sobre_a_menos_1"], "resultado": r4})
    if decidido is None:
        linhas.append({"passo": 5, "criterio": "desempate final", "resultado": "o A"})
        decidido = "A"
    linhas.append({"recomendacao": decidido})
    return linhas


def analisar(medidas: dict, unidades: list[dict], cfg: dict, modo: str) -> dict:
    boot, dias = cfg["bootstrap"], int(cfg["dias"])
    delta = float(cfg["delta"]) if "delta" in cfg else None
    idx = indice(medidas)
    prim = {k: contraste_c_menos_a(idx, unidades, b, mu, JANELA[mu], boot) for k, (b, mu) in PRIMARIOS.items()}
    h = holm({k: c["p_bilateral"] for k, c in prim.items()}, ALFA)
    for k, c in prim.items():
        c["holm"] = h[k]
        c["leitura"] = leitura(c, h[k]["rejeita"], delta)
        # M6, passo 1: empate quando o IC 90% fica dentro de +-delta OU a diferenca nao passa no Holm
        c["leitura_m6"] = c["leitura"] if c["leitura"] in ("C melhor", "A melhor") else "empate"
    sec = {}
    for b in BRACOS:
        for mu in MUNDOS:
            if (b, mu) in PRIMARIOS.values():
                continue
            c = contraste_c_menos_a(idx, unidades, b, mu, JANELA[mu], boot)
            c["leitura"] = leitura(c, None, delta)
            sec[f"{b}/{mu}"] = c
    for b in BRACOS:
        c = contraste_c_menos_a(idx, unidades, b, "descasado", "consumos_ate_metade", boot)
        c["leitura"] = "descritivo"
        sec[f"{b}/descasado/consumos_ate_metade"] = c
    leg = legibilidade(idx, unidades, boot)
    cst = custos(medidas, boot)
    out = {"modo": modo, "delta": delta, "alfa": ALFA, "unidades": len(unidades),
           "primarios": prim, "nao_testaveis": NAO_TESTAVEIS, "secundarios": sec, "legibilidade": leg,
           "deriva": deriva(idx, unidades, dias, boot), "custo": cst, "divergencia_acoplada": divergencias(medidas, dias, boot),
           "so_cuidado": so_cuidado(idx, unidades, boot), "predicoes_por_cerebro": predicoes_por_cerebro(idx, unidades, boot, delta),
           "m6": tabela_m6(prim, leg, cst)}
    if modo != "validacao" and delta:
        out["tamanho_amostra"] = tamanho(prim, delta, cfg.get("simulacao"))
    if modo == "piloto":
        out["conferencia_calibracao_c"] = conferencia_calibracao_c(idx, unidades, boot, dias)
    return out


# ------------------------------------------------------------------ rodar


def vidas_por_unidade() -> int:
    return len(MUNDOS) * (1 + len(CEREBROS) * (len(BRACOS) + len(COM_DONO))) + len(MESMA_EXPERIENCIA)


def rodar(cfg: dict, pasta: Path | None = None, log=print, reanalisar: bool = False) -> dict:
    """As vidas e a analise. Com `reanalisar`, a analise de novo sobre o medidas.json gravado na pasta (sem rodar vida; o tempo e o da
    run gravada no resumo); na validacao, so a analise, nunca as vidas de novo."""
    modo, unidades = modo_e_unidades(cfg)
    pasta = Path(pasta or cfg["saida"])
    bancada = bancada_da_config(cfg)
    if reanalisar:
        r = {"medidas": json.loads((pasta / "medidas.json").read_text(encoding="utf-8")),
             "segundos": json.loads((pasta / "resumo.json").read_text(encoding="utf-8"))["segundos"]}
    else:
        if modo == "validacao" and (pasta / "resumo.json").exists():
            raise ValidacaoJaFeita(f"{pasta}: a validacao ja rodou (secao 8: uma vez)")
        r = rodar_vidas(cfg, bancada, unidades, pasta, log)
    a = analisar(r["medidas"], unidades, cfg, modo)
    seg_unidade = r["segundos"] / len(unidades)
    a["tempo"] = {"segundos": r["segundos"], "vidas": len(r["medidas"]), "vidas_por_unidade": vidas_por_unidade(),
                  "segundos_por_unidade": seg_unidade}
    if "tamanho_amostra" in a and a["tamanho_amostra"]["n_validacao"]:
        a["tempo"]["horas_validacao_estimadas"] = seg_unidade * a["tamanho_amostra"]["n_validacao"] / 3600.0
    if not reanalisar:
        _gravar(pasta / "medidas.json", _dump(r["medidas"]))
    _gravar(pasta / "analise.json", _dump(a))
    resumo = {"modo": modo, "unidades": len(unidades), "vidas": len(r["medidas"]), "segundos": r["segundos"],
              "primarios": {k: {x: c[x] for x in ("d", "media", "ic95", "ic90", "p_bilateral", "leitura", "leitura_m6")}
                            | {"holm_rejeita": c["holm"]["rejeita"], "p_ajustado": c["holm"].get("p_ajustado")}
                            for k, c in a["primarios"].items()},
              "legibilidade": {k: a["legibilidade"]["por_cerebro"][k]["media"] for k in CEREBROS},
              "m6": a["m6"], "tamanho_amostra": a.get("tamanho_amostra"), "tempo": a["tempo"],
              "conferencia_calibracao_c_iguais": a.get("conferencia_calibracao_c", {}).get("iguais")}
    _gravar(pasta / "resumo.json", _dump(resumo))
    _gravar(pasta / "meta.json", _dump({
        "config": cfg, "modo": modo, "plano": PLANO, "plano_sha256": bv._sha(RAIZ / PLANO), "tarefa": TAREFA,
        "ponto_a": ponto_a(), "ponto_c": ponto_c(), "config_bancada_a": config_do_a(cfg),
        "cfg_cerebro_c": bancada.cfg_cerebro_c.__dict__, "cfg_lobos": bancada.cfg_lobos.__dict__,
        "orquestrador_sha256": bv._sha(Path(__file__)), "bancada_sha256": bv._sha(RAIZ / "experiments" / "bancada_v2.py"),
        "lobos_sha256": bv._sha(RAIZ / "digilab" / "policies" / "lobos.py"),
        "cerebro_c_sha256": bv._sha(RAIZ / "digilab" / "policies" / "cerebro_c.py"),
        "metrics_sha256": bv._sha(RAIZ / "digilab" / "metrics.py"), "engine_sha256": bv.meta({})["engine_sha256"],
        "python": platform.python_version(), "plataforma": platform.platform(), "processador": platform.processor()}))
    return {"modo": modo, "unidades": unidades, "medidas": r["medidas"], "analise": a, "resumo": resumo}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="comparacao dos cerebros A x C (docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida")
    ap.add_argument("--reanalisar", action="store_true", help="so a analise, sobre o medidas.json gravado")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    r = rodar(cfg, Path(a.saida) if a.saida else None, log=lambda s: print(s, flush=True), reanalisar=a.reanalisar)
    print(_dump(r["resumo"]["primarios"]))
    print("M6:", _dump(r["resumo"]["m6"]))
    if r["resumo"].get("tamanho_amostra"):
        print("tamanho:", _dump(r["resumo"]["tamanho_amostra"]), "tempo:", _dump(r["resumo"]["tempo"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
