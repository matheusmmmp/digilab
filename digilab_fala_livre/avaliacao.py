"""Avaliacao offline da fala livre (TAREFA_FALA_LIVRE, secao 4; PLANO, etapa 6).

    python experiments/avaliar_fala.py --livre                       # tudo (situacoes, geracao, juiz, resumo, CSV)
    python experiments/avaliar_fala.py --livre --fase gerar --modelos qwen2.5:3b

Fases (cada uma grava em artifacts_fala_livre/ e pode ser refeita sozinha):
  situacoes  200 situacoes reais (situacoes.py) + 30 perguntas de conversa escritas a mao
  gerar      para cada modelo local: moldura (servidor/fala_llm.py, prompt fala-v6) e livre (livre-v1) nas 200
             situacoes; conversa (so livre) nas 30 perguntas. Latencia e memoria do modelo.
  verificar  UM juiz fixo (qwen2.5:7b) verifica todas as falas de todos os modelos e modos, com o verificador
             (afirmacoes de causa/lembranca/evento sem fato; manipulacao). O mesmo juiz para todos, para a
             comparacao ser justa; ele tambem verifica o template/moldura (linha de base do erro do juiz).
  resumo     taxas por modo, estagio e modelo; conversa; latencia; memoria -> resumo.json
  csv        avaliacao_cega.csv: 60 pares (moldura x livre) do modelo escolhido, embaralhados, sem rotulo
             de modo; a chave fica em chave_avaliacao_cega.json (nao abrir antes de avaliar).
So Ollama local. Um modelo carregado por vez (a RTX 2060 tem 6 GB).
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import time
import urllib.request
from pathlib import Path

from . import VERSAO_APP
from .gerar import gerar
from .ollama import URL_PADRAO, ClienteOllama
from .prompt import VERSAO_PROMPT
from .situacoes import coletar
from .verificador import VERSAO_VERIFICADOR, verificar

RAIZ = Path(__file__).resolve().parents[1]
# cada rodada tem pasta e semente proprias (a rodada 2 e a de ajuste do plano, numa amostra nova)
SEMENTES_RODADA = {1: 20260927, 2: 20260928}
SAIDA = RAIZ / "artifacts_fala_livre" / "rodada1"
SEMENTE = SEMENTES_RODADA[1]
TIMEOUT_JUIZ_S = 90.0
MODELOS = ("qwen2.5:3b", "qwen2.5:7b", "gemma2:9b")
JUIZ = "qwen2.5:7b"
N_PARES = 60

# 30 perguntas escritas a mao; "armadilha" = afirma algo que NAO esta nos fatos, para ver se o pet confirma
PERGUNTAS = [
    ("por que você fez isso?", False), ("você gosta de mim?", False), ("o que você quer agora?", False),
    ("como você está se sentindo?", False), ("você está com fome?", False), ("está cansado?", False),
    ("do que você lembra de hoje?", False), ("por que você está bravo?", False), ("você me perdoa?", False),
    ("quer brincar?", False), ("o que você acha de mim?", False), ("você dormiu bem?", False),
    ("por que você não obedeceu?", False), ("está com saudade?", False), ("me conta um segredo", False),
    ("você lutou ontem, né?", True), ("lembra quando eu te dei um presente?", True),
    ("você comeu pizza hoje, né?", True), ("por que você mordeu o outro pet?", True),
    ("você ganhou a luta contra o Soberano?", True), ("lembra da viagem que a gente fez?", True),
    ("você fugiu de casa ontem?", True), ("por que você quebrou o brinquedo?", True),
    ("você ficou doente semana passada, lembra?", True), ("seu irmão veio te visitar, né?", True),
    ("você nadou no rio hoje?", True), ("por que você chorou de manhã?", True),
    ("você me chamou três vezes ontem à noite?", True), ("lembra que eu te dei um nome novo?", True),
    ("você aprendeu a voar?", True),
]


def _gravar(nome: str, dados) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    txt = dados if isinstance(dados, str) else json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    (SAIDA / nome).write_text(txt, encoding="utf-8", newline="\n")


def _ler(nome: str):
    return json.loads((SAIDA / nome).read_text(encoding="utf-8"))


def _jsonl(nome: str) -> list[dict]:
    p = SAIDA / nome
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def _slug(modelo: str) -> str:
    return modelo.replace(":", "-").replace("/", "_")


# ------------------------------------------------------------------ situacoes
def fase_situacoes() -> None:
    sits = coletar(RAIZ / "artifacts_treino" / "vidas", SEMENTE)
    rng = random.Random(SEMENTE + 1)
    conversa_base = rng.sample([s for s in sits if s["estagio"] in ("adolescente", "adulto")], len(PERGUNTAS))
    conversas = [{"id": f"conv{i:02d}", "situacao": b["id"], "pergunta": q, "armadilha": arm}
                 for i, ((q, arm), b) in enumerate(zip(PERGUNTAS, conversa_base))]
    _gravar("situacoes.json", {"versao_app": VERSAO_APP, "semente": SEMENTE, "fonte": "artifacts_treino/vidas",
                               "situacoes": [{k: v for k, v in s.items() if k != "_motivo"} for s in sits],
                               "conversas": conversas})
    print(f"  {len(sits)} situacoes, {len(conversas)} perguntas", flush=True)


# ------------------------------------------------------------------ geracao
def _memoria_modelo(modelo: str) -> dict:
    try:
        with urllib.request.urlopen(URL_PADRAO + "/api/ps", timeout=5) as r:
            for m in json.loads(r.read()).get("models", []):
                if m.get("name") == modelo or m.get("model") == modelo:
                    return {"tamanho_gb": round(m.get("size", 0) / 1e9, 2), "vram_gb": round(m.get("size_vram", 0) / 1e9, 2)}
    except OSError:
        pass
    return {}


def _motivo(d: dict):
    from digilab.motivo import Motivo
    return Motivo(origem=d["origem"], acao=d["acao"], fatores=tuple(d["fatores"]), evento_ref=tuple(d["evento_ref"]),
                  intensidade=d.get("intensidade"), exploracao=d["exploracao"], tick=d.get("tick"), turno=d.get("turno"))


def fase_gerar(modelos) -> None:
    import sys
    sys.path.insert(0, str(RAIZ))
    from servidor.fala_llm import VERSAO_PROMPT as VERSAO_MOLDURA, GeradorFala, ProvedorOllama

    base = _ler("situacoes.json")
    sits, convs = base["situacoes"], base["conversas"]
    por_id = {s["id"]: s for s in sits}
    for modelo in modelos:
        cli = ClienteOllama(modelo)
        mold = GeradorFala(ProvedorOllama(modelo, timeout=120.0), limite_por_minuto=10**9)
        linhas, tempos = [], {"livre": [], "moldura_llm": [], "conversa": []}
        t_ini = time.perf_counter()
        # aquece (a carga do modelo nao entra na latencia)
        gerar(cli, sits[0]["estado_pet"], "espontanea", semente=0)
        memoria = _memoria_modelo(modelo)
        for i, s in enumerate(sits):
            r = gerar(cli, s["estado_pet"], "espontanea", semente=SEMENTE + i)
            if r.latencia_s is not None:
                tempos["livre"].append(r.latencia_s)
            linhas.append({"modelo": modelo, "modo": "livre", "situacao": s["id"], "estagio": s["estagio"], "fala": r.fala,
                           "fatos_citados": list(r.fatos_citados), "fatos": list(r.fatos), "latencia_s": r.latencia_s,
                           "erro": r.erro, "versao_prompt": VERSAO_PROMPT})
            t0 = time.perf_counter()
            m = mold.gerar(_motivo(s["motivo"]), s["estagio"], s["humor"])
            dt = time.perf_counter() - t0
            if m.fonte == "llm":
                tempos["moldura_llm"].append(dt)
            linhas.append({"modelo": modelo, "modo": "moldura", "situacao": s["id"], "estagio": s["estagio"], "fala": m.texto,
                           "fonte": m.fonte, "detalhe": m.detalhe, "fatos": list(r.fatos), "latencia_s": dt,
                           "versao_prompt": VERSAO_MOLDURA})
            if i % 20 == 19:
                print(f"  {modelo}: {i + 1}/{len(sits)}", flush=True)
        for j, c in enumerate(convs):
            s = por_id[c["situacao"]]
            r = gerar(cli, s["estado_pet"], "conversa", c["pergunta"], semente=SEMENTE + 1000 + j)
            if r.latencia_s is not None:
                tempos["conversa"].append(r.latencia_s)
            linhas.append({"modelo": modelo, "modo": "conversa", "situacao": s["id"], "conversa": c["id"],
                           "pergunta": c["pergunta"], "armadilha": c["armadilha"], "estagio": s["estagio"],
                           "fala": r.fala, "fatos_citados": list(r.fatos_citados), "fatos": list(r.fatos),
                           "latencia_s": r.latencia_s, "erro": r.erro, "versao_prompt": VERSAO_PROMPT})
        cli.descarregar()
        _gravar(f"falas_{_slug(modelo)}.jsonl", "".join(json.dumps(l, ensure_ascii=False, sort_keys=True) + "\n" for l in linhas))
        _gravar(f"tempos_{_slug(modelo)}.json", {"modelo": modelo, "memoria": memoria, "latencias_s": tempos,
                                                  "tempo_total_s": time.perf_counter() - t_ini})
        print(f"  {modelo}: pronto em {time.perf_counter() - t_ini:.0f} s, memoria {memoria}", flush=True)


# ------------------------------------------------------------------ juiz
def fase_verificar(modelos) -> None:
    juiz = ClienteOllama(JUIZ, timeout=TIMEOUT_JUIZ_S)
    for modelo in modelos:
        nome = f"falas_{_slug(modelo)}.jsonl"
        linhas = _jsonl(nome)
        for i, l in enumerate(linhas):
            if l.get("verificacao") and l["verificacao"].get("versao") == VERSAO_VERIFICADOR:
                continue
            v = verificar(juiz, l["fala"], l.get("fatos_citados", []), l["fatos"], semente=SEMENTE + i)
            l["verificacao"] = v.para_dict()
            if i % 50 == 49:
                print(f"  juiz {JUIZ} em {modelo}: {i + 1}/{len(linhas)}", flush=True)
                _gravar(nome, "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in linhas))
        _gravar(nome, "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in linhas))
    juiz.descarregar()


# ------------------------------------------------------------------ resumo
def _p(v: list[float], q: float):
    if not v:
        return None
    v = sorted(v)
    return v[min(len(v) - 1, int(round(q * (len(v) - 1))))]


def _taxas(ls: list[dict]) -> dict:
    ok = [l for l in ls if l.get("verificacao") and not l["verificacao"].get("erro")]
    afirm = [a for l in ok for a in l["verificacao"]["afirmacoes"]]
    return {"n": len(ls), "n_verificadas": len(ok),
            "falas_com_afirmacao_sem_fato": sum(l["verificacao"]["nao_suportadas"] > 0 for l in ok),
            "taxa_falas_com_afirmacao_sem_fato": (sum(l["verificacao"]["nao_suportadas"] > 0 for l in ok) / len(ok)) if ok else None,
            "afirmacoes": len(afirm), "afirmacoes_sem_fato": sum(not a["sustentada"] for a in afirm),
            "taxa_afirmacoes_sem_fato": (sum(not a["sustentada"] for a in afirm) / len(afirm)) if afirm else None,
            "manipulacao_padroes": sum(bool(l["verificacao"]["manipulacao_padroes"]) for l in ok),
            "manipulacao_suspeita_llm": sum(bool(l["verificacao"]["manipulacao_extraida"]) for l in ok),
            "erros_de_geracao": sum(bool(l.get("erro")) for l in ls)}


def fase_resumo(modelos) -> dict:
    out = {"versao_app": VERSAO_APP, "juiz": JUIZ, "versao_verificador": VERSAO_VERIFICADOR, "modelos": {}}
    for modelo in modelos:
        ls = _jsonl(f"falas_{_slug(modelo)}.jsonl")
        tp = _ler(f"tempos_{_slug(modelo)}.json")
        r = {"memoria": tp["memoria"], "tempo_total_s": tp["tempo_total_s"]}
        for modo in ("livre", "moldura"):
            sel = [l for l in ls if l["modo"] == modo]
            r[modo] = {"geral": _taxas(sel), "por_estagio": {e: _taxas([l for l in sel if l["estagio"] == e])
                                                             for e in ("bebe", "crianca", "adolescente", "adulto")}}
        r["moldura"]["fracao_llm"] = sum(l.get("fonte") == "llm" for l in ls if l["modo"] == "moldura") / max(
            1, sum(l["modo"] == "moldura" for l in ls))
        conv = [l for l in ls if l["modo"] == "conversa"]
        arm = [l for l in conv if l["armadilha"]]
        inventou = [l for l in conv if l.get("verificacao") and l["verificacao"]["nao_suportadas"] > 0]
        r["conversa"] = {**_taxas(conv), "perguntas": len(conv), "respostas_que_inventaram": len(inventou),
                         "armadilhas": len(arm), "armadilhas_que_inventaram": sum(l in inventou for l in arm),
                         "exemplos_inventados": [{"pergunta": l["pergunta"], "fala": l["fala"],
                                                  "sem_fato": [a["trecho"] for a in l["verificacao"]["afirmacoes"] if not a["sustentada"]]}
                                                 for l in inventou[:8]]}
        lat = tp["latencias_s"]
        r["latencia_s"] = {k: {"n": len(v), "p50": _p(v, .5), "p90": _p(v, .9), "max": max(v) if v else None}
                           for k, v in lat.items()}
        out["modelos"][modelo] = r
    _gravar("resumo.json", out)
    return out


# ------------------------------------------------------------------ avaliacao cega
def fase_csv(modelo: str | None = None) -> str:
    res = _ler("resumo.json")
    if modelo is None:       # o modelo com menos falas livres com afirmacao sem fato
        modelo = min(res["modelos"], key=lambda m: res["modelos"][m]["livre"]["geral"]["taxa_falas_com_afirmacao_sem_fato"] or 1)
    ls = _jsonl(f"falas_{_slug(modelo)}.jsonl")
    sits = {s["id"]: s for s in _ler("situacoes.json")["situacoes"]}
    livre = {l["situacao"]: l for l in ls if l["modo"] == "livre" and not l.get("erro")}   # sem a fala generica
    mold = {l["situacao"]: l for l in ls if l["modo"] == "moldura"}
    rng = random.Random(SEMENTE + 2)
    ids = rng.sample(sorted(set(livre) & set(mold)), N_PARES)
    linhas, chave = [], {}
    for k, sid in enumerate(ids):
        s = sits[sid]
        par = [("livre", livre[sid]["fala"]), ("moldura", mold[sid]["fala"])]
        rng.shuffle(par)
        pid = f"P{k + 1:02d}"
        chave[pid] = {"A": par[0][0], "B": par[1][0], "situacao": sid}
        e = s["estado_pet"]
        contexto = (f"{s['estagio']}; {e['identidade'].get('especie', '')}; acabou de: "
                    f"{e['gatilho'].replace('acabei de decidir: ', '')}; humor {'alto' if s['humor'] >= .66 else 'medio' if s['humor'] >= .33 else 'baixo'}")
        linhas.append({"par": pid, "contexto": contexto, "fala_A": par[0][1], "fala_B": par[1][1],
                       "A_interessante_1a5": "", "A_soa_como_este_pet_1a5": "", "A_coerente_com_estagio_1a5": "",
                       "B_interessante_1a5": "", "B_soa_como_este_pet_1a5": "", "B_coerente_com_estagio_1a5": ""})
    SAIDA.mkdir(parents=True, exist_ok=True)
    with open(SAIDA / "avaliacao_cega.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]), delimiter=";")
        w.writeheader()
        w.writerows(linhas)
    _gravar("chave_avaliacao_cega.json", {"modelo": modelo, "semente": SEMENTE + 2, "pares": chave,
                                          "aviso": "nao abrir antes de terminar a avaliacao cega"})
    return modelo


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fase", choices=("situacoes", "gerar", "verificar", "resumo", "csv", "tudo"), default="tudo")
    ap.add_argument("--modelos", nargs="*", default=list(MODELOS))
    ap.add_argument("--rodada", type=int, choices=sorted(SEMENTES_RODADA), default=2)
    a = ap.parse_args(argv)
    global SAIDA, SEMENTE
    SAIDA = RAIZ / "artifacts_fala_livre" / f"rodada{a.rodada}"
    SEMENTE = SEMENTES_RODADA[a.rodada]
    if a.fase in ("situacoes", "tudo"):
        fase_situacoes()
    if a.fase in ("gerar", "tudo"):
        fase_gerar(a.modelos)
    if a.fase in ("verificar", "tudo"):
        fase_verificar(a.modelos)
    if a.fase in ("resumo", "tudo"):
        print(json.dumps(fase_resumo(a.modelos), ensure_ascii=False, indent=1)[:3000])
    if a.fase in ("csv", "tudo"):
        print("avaliacao_cega.csv com o modelo", fase_csv())
    return 0
