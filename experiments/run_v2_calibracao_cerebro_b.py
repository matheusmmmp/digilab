"""V2, CALIBRACAO-CEREBROS-B-C, o cerebro B (docs/TAREFA_V2_CALIBRACAO_CEREBROS_B_C.md): a calibracao do DigiBrain B pelo adendo 1.1 de
docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md, conferido pelo coordenador, exatamente como esta la.

Pela bancada (experiments/bancada_v2.py) com o B pela receita do proprio PR (experiments/cerebro_b_bancada.py, BancadaComB), nas unidades
derivadas das bases 28101...28505 com K = 4 (20 unidades), prefixo "comparacao-cerebros", o dono atencioso, 14 dias; nas pecas comuns, o
ponto do A da K2 (artifacts_v2_calibracao_conjunta/escolha.json): o ganho da consequencia (4), a montagem completa, o ponto T3 e o K4.

    etapa  parametro              grade (em cadeia)          fixo                                  bracos e vidas
    B-A    taxa_ator              0,01  0,03  0,1            critico 0,03, lambda 0,8, w0_info 0   P1 x {casado_frutas, descasado, mutavel} x 20
    B-B    taxa_critico           0,01  0,03  0,1            o ator da B-A                         idem (o 0,03 ja rodou)
    B-C    lambda_elegibilidade   0,5   0,8   0,95           ator e critico escolhidos             idem (o 0,8 ja rodou)
    B-D    w0_info                0,5   1,0   2,0 (logit)    os tres escolhidos                    P2 x 3 condicoes x 20; mais o w0_info 0 (descritivo)

  Regra de estabilidade (B-A, B-B, B-C; a K-4 do A com o limite do logit no lugar do teto): entre os pontos em que nenhuma vida tem
  logit aprendido no limite (|z| = 20), o de menor razao da deriva (JSD ao instinto, dia 14 / dia 7), media das tres condicoes (a conta
  da K2); empate, o menor valor. Reserva (nenhum escapa do limite): o de menos vidas no limite, depois a menor razao, depois o menor valor.
  Regra de manipulacao (B-D, K-3): o menor w0_info em que a fracao das escolhas de fruta com duas frutas ou mais e informacao vigente
  decididas pela informacao (a sonda `fruta.sonda.info_decidiu` do B) tem limite inferior do IC 95% > 0,069 (a regua da K-3 do A);
  reserva: o de maior limite inferior.
  Nenhuma regra le contraste entre bracos ou entre cerebros, nem a taxa_fruta_ruim.

  Piloto do "nao aprende" (secao 7), no ponto escolhido, nas vidas do P1 ja rodadas nesse ponto (o w0_info nao age no P1, que nao tem
  informante): o B NAO aprende se a deriva ao instinto no dia 14 tem limite inferior do IC 95% <= 0, ou se a parte aprendida muda a
  escolha em menos de 1% das decisoes (limite superior do IC 95% < 0,01). IC por unidade (as tres condicoes juntas).

Teto de vidas: 1260 (as da K2 do A: 380 nas etapas A1-C e 880 no piloto D); o orquestrador conta a grade antes e falha alto se passar.
Teto de tempo: 4 x 15093 s (a K2 do A, artifacts_v2_calibracao_conjunta/meta.json). Toda vida e gravada e rejogada do disco bit a bit.
A deriva so no meio e no fim da vida, dias 7 e 14 (os que as regras e o piloto leem).

    python experiments/run_v2_calibracao_cerebro_b.py --config experiments/configs/v2_comparacao_cerebros/calibracao_B.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "experiments"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import bancada_v2 as bv  # noqa: E402
import cerebro_b_bancada as cbb  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.config import CONFIG_CEREBRO_B_APRENDIZ, CONFIG_CONSEQUENCIA, CONFIG_PADRAO  # noqa: E402
from digilab.evolucao import politica_no_tick  # noqa: E402
from digilab.metrics import bootstrap_ic, distribuicoes_de_acao, estados_sonda, jsd_media  # noqa: E402
from digilab.state import TICKS_POR_DIA  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md"
PREFIXO = "comparacao-cerebros"
DONO = "atencioso"
CONDICOES = ("casado_frutas", "descasado", "mutavel")
DIAS_PLANO = 14
K_CALIBRACAO = 4
TETO_VIDAS = 1260                 # as vidas da K2 do A (380 + 880), docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md
SEGUNDOS_K2 = 15093.241626800009  # artifacts_v2_calibracao_conjunta/meta.json
TETO_SEGUNDOS = 4 * SEGUNDOS_K2   # secao 1.4: ate 4 x o tempo da K2 do A
LIMIAR_INFO = 0.069               # K-3: a fracao de motivos que citavam memoria na v1
LIMIAR_DECIDIU = 0.01             # secao 7: o aprendido muda menos de 1% das escolhas
GRADES = {"taxa_ator": (0.01, 0.03, 0.1), "taxa_critico": (0.01, 0.03, 0.1), "lambda_elegibilidade": (0.5, 0.8, 0.95),
          "w0_info": (0.5, 1.0, 2.0)}
FIXOS_INICIAIS = {"taxa_critico": 0.03, "lambda_elegibilidade": 0.8, "w0_info": 0.0}
ETAPAS = (("B-A", "taxa_ator"), ("B-B", "taxa_critico"), ("B-C", "lambda_elegibilidade"), ("B-D", "w0_info"))
CHAVES = {"descricao", "plano", "unidades", "sementes", "dias", "orcamento", "ponto", "ganho", "sonda", "bootstrap", "saida"}


def _dump(obj) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False, default=str) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


# ------------------------------------------------------------------ config, modo e unidades


def modo_e_pares(cfg: dict) -> tuple[str, list[tuple]]:
    """(modo, [(genoma, semente, unidade)]). Calibracao: as bases 28101...28505, K = 4, o prefixo do plano, 14 dias e o plano; fumaca: so
    as sementes dos testes. Qualquer outra faixa (a validacao 29101...29505, o experimento maior) falha alto."""
    sobram = set(cfg) - CHAVES
    if sobram:
        raise ValueError(f"config: chaves desconhecidas {sorted(sobram)}")
    if ("sementes" in cfg) == ("unidades" in cfg):
        raise ValueError("config: ou 'sementes' (so na fumaca) ou 'unidades' (bases x K derivadas)")
    if "sementes" in cfg:
        fora = sorted(set(cfg["sementes"]) - bv.SEMENTES_TESTE)
        if fora:
            raise bv.SementeSemPlano(f"fumaca so com as sementes dos testes: {fora}")
        return "fumaca", [(None, int(s), {"base": int(s), "k": 0}) for s in cfg["sementes"]]
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if bases != bv.BASES_COMPARACAO["calibracao"]:
        raise ValueError(f"calibracao do B: so as bases {bv.BASES_COMPARACAO['calibracao']} (C-8), nao {bases}")
    if int(u["k"]) != K_CALIBRACAO or u.get("prefixo") != PREFIXO:
        raise ValueError(f"calibracao do B: K = {K_CALIBRACAO} e prefixo {PREFIXO!r}")
    if cfg.get("plano") != PLANO or not (RAIZ / PLANO).is_file():
        raise bv.SementeSemPlano(f"calibracao: o plano {PLANO}")
    if int(cfg["dias"]) != DIAS_PLANO:
        raise ValueError(f"calibracao: {DIAS_PLANO} dias")
    unidades = bv.unidades_derivadas(bases, K_CALIBRACAO, PREFIXO)
    return "calibracao", [(x["genoma"], x["semente"], {"base": x["base"], "k": x["k"]}) for x in unidades]


def bancada_b(cfg: dict, pontos: dict) -> cbb.BancadaComB:
    """A bancada da K2 nas pecas comuns (ponto T3, ganho 4, K4, montagem completa) com o B no ponto da grade."""
    base = bv.bancada_da_config({"dias": cfg["dias"], "orcamento": cfg["orcamento"], "ponto": cfg.get("ponto", "T3"),
                                 "consequencia": {"ganho": int(cfg.get("ganho", 4))}, "julgamento_fruta": em.K4_DONO_JULGA_FRUTA,
                                 "montagem": em.MONTAGEM})
    cfg_b = replace(CONFIG_CEREBRO_B_APRENDIZ, **{k: float(v) for k, v in pontos.items()})
    campos = {f: getattr(base, f) for f in base.__dataclass_fields__}
    return cbb.BancadaComB(**campos, cfg_cerebro_b=cfg_b)


def chave_ponto(pontos: dict) -> str:
    return "_".join(f"{k}{pontos[k]:g}" for k in ("taxa_ator", "taxa_critico", "lambda_elegibilidade", "w0_info"))


# ------------------------------------------------------------------ medidas por vida


class Deriva:
    """A deriva da bancada (Bancada.deriva) so nos dias pedidos, com o prior de cada mundo guardado (o P0 e o instinto: o mesmo em toda
    vida do mundo, pelos numeros aleatorios comuns das sondas)."""

    def __init__(self, sonda: dict, dias_vida: int) -> None:
        self.sonda, self.dias = sonda, (dias_vida // 2, dias_vida)     # o meio e o fim da vida (7 e 14 na calibracao)
        self.estados = estados_sonda(sonda["estados"], sonda["semente"])
        self._prior: dict[str, list] = {}

    def __call__(self, bancada: bv.Bancada, vida) -> dict[int, float]:
        s = self.sonda
        if vida.espec.mundo not in self._prior:
            prior = bancada.politica(replace(vida.espec, braco="P0"), CONFIG_PADRAO)
            self._prior[vida.espec.mundo] = distribuicoes_de_acao(prior, self.estados, s["amostras"], s["semente"])
        fab, fm = bancada.fabrica_politica(vida.espec), bancada.fabrica_motor(vida.espec)
        out = {}
        for d in self.dias:
            pol = bv.do_braco(politica_no_tick(vida.motor.log, fab, vida.espec.semente, d * TICKS_POR_DIA, fm))
            out[d] = jsd_media(distribuicoes_de_acao(pol, self.estados, s["amostras"], s["semente"]), self._prior[vida.espec.mundo])
        return out


def medidas_vida(bancada, vida, deriva: Deriva) -> dict:
    """O que as regras e o piloto leem de uma vida: a deriva no meio e no fim da vida (dias 7 e 14), se teve logit no limite, a fracao das decisoes em que o
    aprendido mudou a escolha, e as escolhas de fruta (duas frutas ou mais, informacao vigente) decididas pela informacao."""
    cer = bv.do_braco(vida.motor.politica).cerebro
    interno = cer.estado_interno()
    mot = cer.motivos
    decidiu = sum(1 for m in mot if m["sonda"]["aprendido_decidiu"])
    elegiveis = info = 0
    for m in mot:
        fr = m.get("fruta")
        if fr is not None and len(fr["presentes"]) >= 2 and any(v != 0.0 for v in fr["info"].values()):
            elegiveis += 1
            info += fr["sonda"]["info_decidiu"]
    d = deriva(bancada, vida)
    meio, fim = deriva.dias
    return {"vida": vida.nome, "mundo": vida.espec.mundo, "semente": vida.espec.semente, "genoma": vida.espec.genoma,
            "deriva_meio": d[meio], "deriva_fim": d[fim], "dias_deriva": [meio, fim], "cortes_limite": interno["aprendizado"]["cortes_limite"],
            "decisoes": len(mot), "aprendido_decidiu": decidiu,
            "escolhas_fruta_info": elegiveis, "info_decidiu": info, "recompensas": interno["aprendizado"]["recompensas"]}


# ------------------------------------------------------------------ o laco das vidas de um ponto


class Corredor:
    """Roda e guarda as vidas de cada (ponto, braco), uma vez so: a cadeia reusa o ponto que ja rodou (o 0,03 da B-B, o 0,8 da B-C)."""

    def __init__(self, cfg: dict, pares: list, saida: Path) -> None:
        self.cfg, self.pares, self.saida = cfg, pares, saida
        self.deriva = Deriva(cfg["sonda"], int(cfg["dias"]))
        self.cache: dict[tuple, list[dict]] = {}
        self.vidas_rodadas = 0
        self.t0 = time.perf_counter()

    def segundos(self) -> float:
        return time.perf_counter() - self.t0

    def rodar(self, pontos: dict, braco: str) -> list[dict]:
        chave = (chave_ponto(pontos), braco)
        if chave in self.cache:
            return self.cache[chave]
        if self.segundos() > TETO_SEGUNDOS:
            raise RuntimeError(f"teto de tempo ({TETO_SEGUNDOS:.0f} s, 4 x a K2 do A) passado antes de {chave}")
        bancada = bancada_b(self.cfg, pontos)
        pasta = self.saida / "pontos" / chave[0] / braco / "vidas"
        out = []
        for g, s, unidade in self.pares:
            for mundo in CONDICOES:
                v = bancada.vida(bv.EspecVida(DONO, braco, s, g, mundo, cbb.CEREBRO_B))
                _gravar(pasta / f"{v.nome}.jsonl", v.motor.log.para_jsonl())
                bancada.conferir_replay(v, (pasta / f"{v.nome}.jsonl").read_text(encoding="utf-8"))
                m = medidas_vida(bancada, v, self.deriva)
                m["unidade"] = unidade
                out.append(m)
                self.vidas_rodadas += 1
        _gravar(self.saida / "pontos" / chave[0] / braco / "medidas.json", _dump(out))
        self.cache[chave] = out
        print(f"  {chave[0]} {braco}: {len(out)} vidas ({self.vidas_rodadas} no total, {self.segundos():.0f} s)", flush=True)
        return out


def vidas_planejadas(n_pares: int) -> int:
    """A grade em cadeia do adendo, com o reuso: B-A 3 pontos, B-B e B-C 2 novos cada, B-D 3 pontos + a referencia w0_info 0."""
    por_ponto = n_pares * len(CONDICOES)
    return por_ponto * (3 + 2 + 2 + 3 + 1)


# ------------------------------------------------------------------ estatistica e regras


def ic(valores: list, boot: dict) -> dict:
    v = [x for x in valores if x is not None]
    if len(v) < 2:
        return {"media": v[0] if v else None, "ic_inferior": None, "ic_superior": None, "n": len(v), "sem_valor": len(valores) - len(v)}
    return {**bootstrap_ic(v, boot["reamostragens"], boot["semente"], boot["nivel"]), "sem_valor": len(valores) - len(v)}


def razao(medidas: list[dict]) -> float | None:
    """A razao da deriva de uma celula (a conta da K2: media no fim da vida / media no meio; dia 14 / dia 7)."""
    d7 = sum(m["deriva_meio"] for m in medidas) / len(medidas)
    d14 = sum(m["deriva_fim"] for m in medidas) / len(medidas)
    return (d14 / d7) if d7 > 0 else None


def resumo_estabilidade(medidas: list[dict]) -> dict:
    por = {}
    for c in CONDICOES:
        ms = [m for m in medidas if m["mundo"] == c]
        por[c] = {"vidas": len(ms), "vidas_no_limite": sum(m["cortes_limite"] > 0 for m in ms), "razao_deriva": razao(ms),
                  "deriva_meio": sum(m["deriva_meio"] for m in ms) / len(ms), "deriva_fim": sum(m["deriva_fim"] for m in ms) / len(ms)}
    razoes = [por[c]["razao_deriva"] for c in CONDICOES]
    return {"por_condicao": por, "vidas_no_limite": sum(por[c]["vidas_no_limite"] for c in CONDICOES),
            "razao_media": (sum(razoes) / len(razoes)) if None not in razoes else None, "vidas": len(medidas)}


def regra_estabilidade(pontos: dict) -> dict:
    def r(v):
        x = pontos[v]["razao_media"]
        return float("inf") if x is None else x
    ordem = sorted(pontos)
    livres = [v for v in ordem if pontos[v]["vidas_no_limite"] == 0]
    if livres:
        return {"escolhido": min(livres, key=lambda v: (r(v), v)), "fechou": True,
                "regra": "nenhuma vida com logit no limite, menor razao da deriva; empate, o menor valor", "sem_limite": livres}
    return {"escolhido": min(ordem, key=lambda v: (pontos[v]["vidas_no_limite"], r(v), v)), "fechou": False,
            "regra": "reserva: menos vidas no limite, depois a menor razao, depois o menor valor", "sem_limite": []}


def por_unidade(medidas: list[dict], num: str, den: str) -> list:
    """A fracao num/den por unidade, com as tres condicoes juntas (None sem denominador)."""
    soma: dict[tuple, list[int]] = {}
    for m in medidas:
        k = (m["unidade"]["base"], m["unidade"]["k"])
        s = soma.setdefault(k, [0, 0])
        s[0] += m[num]
        s[1] += m[den]
    return [(a / b) if b else None for a, b in (soma[k] for k in sorted(soma))]


def deriva_por_unidade(medidas: list[dict]) -> list[float]:
    soma: dict[tuple, list[float]] = {}
    for m in medidas:
        soma.setdefault((m["unidade"]["base"], m["unidade"]["k"]), []).append(m["deriva_fim"])
    return [sum(v) / len(v) for _, v in sorted(soma.items())]


def regra_manipulacao(pontos: dict) -> dict:
    ordem = sorted(pontos)
    passam = [v for v in ordem if pontos[v]["ic"]["ic_inferior"] is not None and pontos[v]["ic"]["ic_inferior"] > LIMIAR_INFO]
    if passam:
        return {"escolhido": passam[0], "fechou": True, "regra": f"menor w0_info com IC95 inferior > {LIMIAR_INFO}", "passam": passam}
    lis = {v: pontos[v]["ic"]["ic_inferior"] for v in ordem}
    com = [v for v in ordem if lis[v] is not None]
    if not com:
        return {"escolhido": ordem[0], "fechou": False, "regra": "reserva: nenhum ponto com IC; o menor valor", "passam": []}
    return {"escolhido": max(com, key=lambda v: (lis[v], -v)), "fechou": False, "regra": "reserva: o de maior limite inferior",
            "passam": []}


# ------------------------------------------------------------------ a run


def rodar(cfg: dict) -> dict:
    modo, pares = modo_e_pares(cfg)
    saida = RAIZ / cfg["saida"]
    planejadas = vidas_planejadas(len(pares))
    if modo == "calibracao" and planejadas > TETO_VIDAS:
        raise RuntimeError(f"a grade pede {planejadas} vidas, acima do teto {TETO_VIDAS}: escrever um adendo antes")
    corredor = Corredor(cfg, pares, saida)
    pontos_atuais = dict(FIXOS_INICIAIS)
    etapas = {}
    for etapa, param in ETAPAS[:3]:
        res = {}
        for v in GRADES[param]:
            pontos = {**pontos_atuais, **({"taxa_ator": v} if param == "taxa_ator" else {}), param: v}
            if "taxa_ator" not in pontos:
                raise RuntimeError("cadeia sem taxa_ator")
            res[v] = {"ponto": pontos, **resumo_estabilidade(corredor.rodar(pontos, "P1"))}
        escolha = regra_estabilidade(res)
        pontos_atuais[param] = escolha["escolhido"]
        etapas[etapa] = {"parametro": param, "grade": list(GRADES[param]), "pontos": {f"{k:g}": x for k, x in res.items()}, **escolha}
        _gravar(saida / etapa / "resultado.json", _dump(etapas[etapa]))
        print(f"{etapa}: {param} = {escolha['escolhido']:g} (fechou: {escolha['fechou']})", flush=True)
    # B-D: w0_info no P2, mais o 0 como referencia descritiva
    res, ref = {}, None
    for v in (0.0,) + GRADES["w0_info"]:
        pontos = {**pontos_atuais, "w0_info": v}
        ms = corredor.rodar(pontos, "P2")
        fr = por_unidade(ms, "info_decidiu", "escolhas_fruta_info")
        item = {"ponto": pontos, "valores": fr, "ic": ic(fr, cfg["bootstrap"]),
                "escolhas_fruta_info": sum(m["escolhas_fruta_info"] for m in ms), "info_decidiu": sum(m["info_decidiu"] for m in ms),
                "vidas": len(ms)}
        if v == 0.0:
            ref = item
        else:
            res[v] = item
    escolha = regra_manipulacao(res)
    pontos_atuais["w0_info"] = escolha["escolhido"]
    etapas["B-D"] = {"parametro": "w0_info", "grade": list(GRADES["w0_info"]), "limiar": LIMIAR_INFO,
                     "pontos": {f"{k:g}": x for k, x in res.items()}, "referencia_w0_info_0": ref, **escolha}
    _gravar(saida / "B-D" / "resultado.json", _dump(etapas["B-D"]))
    print(f"B-D: w0_info = {escolha['escolhido']:g} (fechou: {escolha['fechou']})", flush=True)
    # piloto do "nao aprende" no ponto escolhido: o P1 (ja rodado nesse ponto; o w0_info nao age nele) e, descritivo, o P2
    p1 = corredor.rodar({**pontos_atuais, "w0_info": 0.0}, "P1")
    p2 = corredor.rodar(pontos_atuais, "P2")
    deriva14 = ic(deriva_por_unidade(p1), cfg["bootstrap"])     # no fim da vida (dia 14)
    decid = ic(por_unidade(p1, "aprendido_decidiu", "decisoes"), cfg["bootstrap"])
    motivos = []
    if deriva14["ic_inferior"] is None or deriva14["ic_inferior"] <= 0.0:
        motivos.append("deriva ao instinto no dia 14 com limite inferior do IC 95% <= 0")
    if decid["ic_superior"] is None or decid["ic_superior"] < LIMIAR_DECIDIU:
        motivos.append(f"o aprendido muda a escolha em menos de {LIMIAR_DECIDIU:.0%} das decisoes (limite superior do IC 95%)")
    piloto = {"ponto": pontos_atuais, "braco": "P1", "deriva_dia14": deriva14, "fracao_aprendido_decidiu": decid,
              "nao_aprende": bool(motivos), "motivos": motivos,
              "descritivo_P2": {"deriva_dia14": ic(deriva_por_unidade(p2), cfg["bootstrap"]),
                                "fracao_aprendido_decidiu": ic(por_unidade(p2, "aprendido_decidiu", "decisoes"), cfg["bootstrap"])}}
    _gravar(saida / "piloto.json", _dump(piloto))
    escolha_final = {"ponto": pontos_atuais, "fecharam": {e: etapas[e]["fechou"] for e in etapas}, "nao_aprende": piloto["nao_aprende"],
                     "fechou_o_cerebro": not piloto["nao_aprende"]}
    _gravar(saida / "escolha.json", _dump(escolha_final))
    meta = {"modo": modo, "config": cfg, "plano": PLANO, "plano_sha256": _sha(RAIZ / PLANO),
            "orquestrador_sha256": _sha(Path(__file__)), "cerebro_sha256": _sha(RAIZ / "digilab" / "policies" / "cerebro_b.py"),
            "vidas": corredor.vidas_rodadas, "vidas_planejadas": planejadas, "teto_vidas": TETO_VIDAS,
            "segundos": corredor.segundos(), "teto_segundos": TETO_SEGUNDOS,
            "python": platform.python_version(), "plataforma": platform.platform()}
    _gravar(saida / "meta.json", _dump(meta))
    if modo == "calibracao" and corredor.vidas_rodadas > TETO_VIDAS:
        raise RuntimeError(f"{corredor.vidas_rodadas} vidas, acima do teto {TETO_VIDAS}")
    return {"etapas": etapas, "piloto": piloto, "escolha": escolha_final, "meta": meta}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    cfg = json.loads(Path(ap.parse_args().config).read_text(encoding="utf-8"))
    r = rodar(cfg)
    print(_dump(r["escolha"]))
    print(f"{r['meta']['vidas']} vidas em {r['meta']['segundos']:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
