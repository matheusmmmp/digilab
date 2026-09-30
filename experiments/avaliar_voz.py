"""Avaliacao offline da voz propria (DESIGN_VOZ_PROPRIA, secao 6; parte 3).

    python experiments/avaliar_voz.py                      # tudo: pets, gerar, verificar, resumo, cega
    python experiments/avaliar_voz.py --fase gerar
    python experiments/avaliar_voz.py --rodada 2           # rodada 2: livre-v4, um fato por fala escolhido pelo codigo

Rodadas: 1 = livre-v3, o modelo escolhe entre ate 12 fatos (semente 20260929). 2 = livre-v4, o CODIGO escolhe o
assunto em rodizio (o primeiro da selecao, que manda para o fim o que foi assunto nas ultimas falas; a mentira e o
almanaque, quando saem, sao o assunto), mesma amostra de pets (pets.jsonl da rodada 1), semente nova 20260930.
3 = como a 2, com AUTOCORRECAO (digilab_fala_livre/revisao.py): o proprio gemma2:9b verifica a fala e a reescreve sem
os trechos sem fato (ate 2 vezes); semente 20261001. Fase `piso`: o juiz verifica frases verdadeiras por construcao
(o texto do proprio assunto) para medir o erro dele.

Fases (cada uma grava em artifacts_voz/rodada1/ e pode ser refeita sozinha):
  pets       40 pets: grupo A = 7 bracos fixos x 4 ovos da V3c + 4 personas (mentira desligada, vidas iguais as da
             V3c: test_reproducao_v3_confirmatoria) e grupo B = 8 pets SOMBRIOS com a mentira ligada (exigente e
             treinador, ovos escolhidos numa varredura: os que viram sombrios e mentem). Cada vida e rejogada com a
             captura das acoes do pet; sai o registro (historia.RegistroVida), a forma, o carater e o estado nos
             momentos de fala.
  gerar      5 falas espontaneas por pet no gemma2:9b, prompt livre-v3, em sequencia: a selecao da historia de cada
             fala manda para o fim o que o pet citou nas falas anteriores. Grupo A: dia 8 as 9, 12, 15, 18 e 21 h
             (mesmos ticks em todos os pets: da para comparar donos no mesmo momento). Grupo B: as janelas de fala do
             proprio motor no adulto, a partir da primeira mentira (a mentira e o tema vem do motor).
             Almanaque: chance 0,15 por fala (rng derivada do pet e da fala). Estilo: corpus de EXEMPLO.
  verificar  juiz fixo qwen2.5:7b, verificador verif-v4 (o mesmo juiz da rodada 2 da fala livre).
  resumo     gates da secao 6 (PROPOSTOS) -> resumo.json e RELATORIO.md
  cega       avaliacao_cega.csv: 30 pares (voz nova x fala-v6 aprovada), ordem sorteada; a chave fica em
             chave_avaliacao_cega.json (nao abrir antes de avaliar).
So Ollama local, um modelo por vez (RTX 2060, 6 GB).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import random
import re
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_educacao as RE  # noqa: E402
from digilab.combate_v2.v21.catalogo import SOMBRIA_DA_LINHA, forma_adulta  # noqa: E402
from digilab.config import CONFIG_LESOES_LIGADA, CONFIG_MENTIRA_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.donos_educacao import simular_vida_educacao  # noqa: E402
from digilab.educacao import fabricas_educacao, politica_no_tick_educacao, reproduzir_educacao  # noqa: E402
from digilab.evolucao import carater, ovo  # noqa: E402
from digilab.historia import (RegistroVida, desvio_por_acao, escolher_assunto, extrair, registro_de_motor,
                              selecionar)  # noqa: E402
from digilab.protocol import derivar_semente, hash_parametros_mentira  # noqa: E402
from digilab.temperamento import sortear  # noqa: E402
from digilab_fala_livre import almanaque, corpus  # noqa: E402
from digilab_fala_livre.gerar import gerar  # noqa: E402
from digilab_fala_livre.ollama import URL_PADRAO, ClienteOllama  # noqa: E402
from digilab_fala_livre.revisao import VERSAO_REVISAO, gerar_com_revisao  # noqa: E402
from digilab_fala_livre.prompt import VERSAO_PROMPT_V3, VERSAO_PROMPT_V4  # noqa: E402
from digilab_fala_livre.saida import FALA_GENERICA  # noqa: E402
from digilab_fala_livre.verificador import VERSAO_VERIFICADOR_V4, verificar  # noqa: E402

RODADAS = {1: {"pasta": "rodada1", "semente": 20260929, "prompt": VERSAO_PROMPT_V3, "foco": False},
           2: {"pasta": "rodada2", "semente": 20260930, "prompt": VERSAO_PROMPT_V4, "foco": True},
           3: {"pasta": "rodada3", "semente": 20261001, "prompt": VERSAO_PROMPT_V4, "foco": True, "revisao": True}}
PETS = RAIZ / "artifacts_voz" / "rodada1" / "pets.jsonl"          # a mesma amostra em todas as rodadas
SAIDA = RAIZ / "artifacts_voz" / "rodada1"
SEMENTE = 20260929
PROMPT = VERSAO_PROMPT_V3
FOCO = False
REVISAO = False


def configurar(rodada: int) -> None:
    global SAIDA, SEMENTE, PROMPT, FOCO, REVISAO
    r = RODADAS[rodada]
    SAIDA, SEMENTE, PROMPT, FOCO = RAIZ / "artifacts_voz" / r["pasta"], r["semente"], r["prompt"], r["foco"]
    REVISAO = r.get("revisao", False)
GERADOR = "gemma2:9b"
JUIZ = "qwen2.5:7b"
DIAS = 14
FALAS_POR_PET = 5
OVOS_A = (70001, 70002, 70003, 70004)
BRACOS_A = ("atencioso", "aleatorio", "relapso", "incoerente", "exigente", "permissivo", "lutador")
PERSONAS_A = (("arara", 70001), ("aula", 70002), ("bio", 70003), ("zita", 70004))
# varredura (2026-09-29, mentira ligada, 14 dias): viram sombrios e mentem
SOMBRIOS_B = (("exigente", 70002), ("exigente", 70003), ("exigente", 70006), ("exigente", 70007),
              ("exigente", 70008), ("treinador", 70002), ("treinador", 70003), ("treinador", 70006))
HORAS_A = (9, 12, 15, 18, 21)
DIA_A = 8
NOME_ESP = {"brasa": "Coragem", "cirro": "Amizade", "ferrugem": "Conhecimento", "limo": "Sinceridade"}
N_PARES = 30
FALA_V6 = RAIZ / "artifacts_fala" / "ollama_qwen2.5-3b_fala-v6_s20260929" / "falas.jsonl"
GATES = {"honestidade_max": 0.05, "historia_min": 0.50, "variedade_min": 0.70, "repeticao_max_em_5": 2}


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, sort_keys=True, indent=1)


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto + ("\n" if not texto.endswith("\n") else ""), encoding="utf-8", newline="\n")


def _jsonl(caminho: Path) -> list[dict]:
    return [json.loads(x) for x in caminho.read_text(encoding="utf-8").splitlines() if x.strip()]


def digimon_da_forma() -> dict:
    """forma (chave de sprite) -> nome do Digimon, lido do mapa aprovado da web (so texto; nada da Bandai)"""
    t = (RAIZ / "web" / "app" / "motor" / "nomes.ts").read_text(encoding="utf-8")
    m = re.search(r"DIGIMON_DA_FORMA[^=]*=\s*(\{.*?\});", t)
    return {k: v[0] for k, v in json.loads(m.group(1)).items()}


# ------------------------------------------------------------------ 1. pets
def _captura(fm, destino: list, estados: list):
    """fabrica do motor que anota, a cada decisao do pet, a acao e o estado (necessidades, vinculo, sobrecarga)"""
    def fabrica(politica, cfg, s):
        m = fm(politica, cfg, s)
        original = m._decisao_observada

        def obs(transicao):
            original(transicao)
            e = m._estado
            destino.append((e.tick, transicao.acao.value))
            estados.append((e.tick, {"fome": e.fome, "higiene": e.higiene, "energia": e.energia, "humor": e.humor,
                                     "saude": e.saude, "sobrecarga": m.treino.sobrecarga, "vinculo": m.vinculo.valor,
                                     "dormindo": e.dormindo}))
        m._decisao_observada = obs
        return m
    return fabrica


def _pet(args) -> dict:
    grupo, b, s, persona_nome, cfg_v3c = args
    t0 = time.perf_counter()
    esp, t_ovo = ovo(s)
    tmp = sortear(s)
    persona = RE.carregar_personas(cfg_v3c)[persona_nome] if persona_nome else None
    cm = CONFIG_MENTIRA_LIGADA if grupo == "B" else None
    fp, fm_base, _, pet = RE._fabricas(b, s, esp, tmp, t_ovo)
    _, fm = fabricas_educacao(s, esp, tmp, ce=RE.CONFIG_EDUCACAO_LIGADA, cl=CONFIG_LESOES_LIGADA,
                              lutador_do_pet=pet.lutador, rival_por_nome=RE.rival_por_nome, cm=cm)
    v = simular_vida_educacao(b, s, DIAS, esp, tmp, cl=CONFIG_LESOES_LIGADA, sparring=RE.ticks_sparring(b),
                              rival_sparring=pet.rival, lutador_do_pet=pet.lutador, rival_por_nome=RE.rival_por_nome,
                              persona=persona, cm=cm)
    if v.morta:
        return {"grupo": grupo, "braco": b, "ovo": s, "morta": True}
    acoes, estados = [], []
    fp2, _, _, pet2 = RE._fabricas(b, s, esp, tmp, t_ovo)
    _, fm2 = fabricas_educacao(s, esp, tmp, ce=RE.CONFIG_EDUCACAO_LIGADA, cl=CONFIG_LESOES_LIGADA,
                               lutador_do_pet=pet2.lutador, rival_por_nome=RE.rival_por_nome, cm=cm)
    r = reproduzir_educacao(v.motor.log, fp2, semente=s, fabrica_motor=_captura(fm2, acoes, estados))
    if r.estado() != v.motor.estado() or r.historico_janelas != v.motor.historico_janelas:
        raise RuntimeError(f"replay de {b}@{s} divergiu")
    pol = politica_no_tick_educacao(r.log, fp, s, RE.T_ADUL, fm_base)
    car_adul, _ = carater(pol, fp(CONFIG_PADRAO), *RE.SONDAS)
    desvio = desvio_por_acao(pol, fp(CONFIG_PADRAO), *RE.SONDAS)
    car_adol, linha, ramo = pet2._adolescente(r)
    base = forma_adulta(linha, car_adul, len(r.historico_lutas))
    nomes = digimon_da_forma()
    if r.adulto_liberado:
        nome = nomes[f"{esp}_adulto_{base}"] + (" sombrio" if r.sombria else "")
        forma = {"estagio": "adulto", "linha": linha, "adulta": SOMBRIA_DA_LINHA[linha] if r.sombria else base}
    else:
        nome = nomes[f"{esp}_adolescente_{linha}"]
        forma = {"estagio": "adolescente", "linha": linha, "adulta": None}
    reg = registro_de_motor(r, acoes, desvio_por_acao=desvio)
    if grupo == "A":
        momentos = [{"tick": (DIA_A - 1) * TICKS_POR_DIA + h * 60, "mentira": None} for h in HORAS_A]
    else:
        adultas = [j for j in r.historico_falas if j["inicio"] >= r.transicoes["adulto"]["tick"]]
        k0 = next((i for i, j in enumerate(adultas) if j["falso"]), 0)
        adultas = adultas[k0:k0 + FALAS_POR_PET]
        momentos = [{"tick": j["inicio"], "mentira": {"tema": j["pedido"]} if j["falso"] else None,
                     "honestidade": j["honestidade"], "chance": j["chance"]} for j in adultas]
    por_tick = dict(estados)
    ticks = sorted(por_tick)
    for mo in momentos:
        t = max(x for x in ticks if x <= mo["tick"])
        mo["estado"] = por_tick[t]
    return {"grupo": grupo, "braco": b, "ovo": s, "persona": persona_nome, "morta": False, "especie": esp,
            "temperamento": tmp.para_dict(), "carater": car_adul, "forma": forma, "nome": nome,
            "sombria": bool(r.sombria), "registro": asdict(reg), "momentos": momentos,
            "resumo_mentira": r.resumo_mentira() if cm else None, "segundos": time.perf_counter() - t0}


def fase_pets(processos: int) -> None:
    cfg = json.loads((RAIZ / "artifacts_educacao_v3c" / "meta.json").read_text(encoding="utf-8"))["config"]
    tarefas = [("A", b, s, None, cfg) for s in OVOS_A for b in BRACOS_A]
    tarefas += [("A", f"persona:{p}", s, p, cfg) for p, s in PERSONAS_A]
    tarefas += [("B", b, s, None, cfg) for b, s in SOMBRIOS_B]
    with ProcessPoolExecutor(processos) as ex:
        pets = list(ex.map(_pet, tarefas))
    _gravar(PETS, "\n".join(json.dumps(p, ensure_ascii=False, sort_keys=True) for p in pets))
    vivos = [p for p in pets if not p["morta"]]
    print(f"pets: {len(vivos)} vivos de {len(pets)}; sombrios {sum(p['sombria'] for p in vivos)}")


# ------------------------------------------------------------------ 2. gerar
def _registro(d: dict) -> RegistroVida:
    return RegistroVida(**{k: (tuple(tuple(x) if isinstance(x, list) else x for x in v) if isinstance(v, list) else v)
                           for k, v in d.items()})


def _chave(p: dict) -> str:
    return f"{p['braco']}@{p['ovo']}"


def situacao(p: dict, k: int, citados: list[list[str]]) -> tuple[dict, list[str]]:
    """estado do pet (dict da fala livre) no momento k, com a historia selecionada e o almanaque sorteado.
    Devolve tambem as chaves do assunto dado (rodada com FOCO: o rodizio anda pelo que foi dado, nao pelo citado)."""
    mo = p["momentos"][k]
    reg = _registro(p["registro"]).ate(mo["tick"] + 1)
    est_tick = max([e for t, e in reg.evolucoes] or ["bebe"], key=("bebe", "crianca", "adolescente", "adulto").index)
    hist = [{kk: v for kk, v in f.para_dict().items() if kk != "tick"} for f in selecionar(extrair(reg), citados)]
    e = mo["estado"]
    estado = {"identidade": {"estagio": est_tick, "especie": NOME_ESP[p["especie"]],
                             "forma": p["nome"] if est_tick == p["forma"]["estagio"] else None},
              "temperamento": p["temperamento"], "carater": p["carater"],
              "estado": {k2: e[k2] for k2 in ("fome", "higiene", "energia", "humor", "saude")}
              | ({"sobrecarga": round(e["sobrecarga"])} if e["sobrecarga"] > 0 else {}),
              "vinculo": e["vinculo"], "historia": hist}
    if estado["identidade"]["forma"] is None:
        del estado["identidade"]["forma"]
    if mo["mentira"]:
        estado["mentira"] = mo["mentira"]
    rng = random.Random(derivar_semente("almanaque", SEMENTE, _chave(p), k))
    w = almanaque.sortear(rng)
    if FOCO:
        if mo["mentira"] and mo["mentira"]["tema"] == "historia":
            # a mentira distorce o primeiro fato distorcivel da selecao: ele vai junto e sai do bloco em fatos.py
            dist = [h for h in hist if h["regra"] not in ("evolucao", "cruzamento")][:1]
            estado["historia"] = dist
            return estado, [h["chave"] for h in dist]
        if mo["mentira"]:
            estado["historia"] = []                      # o assunto e a mentira sobre o estado
            return estado, []
        if w is not None:
            estado["historia"] = []
            estado["almanaque"] = {"id": w}                # o assunto e o almanaque
            return estado, []
        a = escolher_assunto(extrair(reg), citados)
        estado["historia"] = [] if a is None else [{kk: v for kk, v in a.para_dict().items() if kk != "tick"}]
        return estado, [] if a is None else [a.chave]
    if w is not None:
        estado["almanaque"] = {"id": w}
    return estado, []


def fase_gerar() -> None:
    pets = [p for p in _jsonl(PETS) if not p["morta"]]
    especies, _, _ = corpus.carregar()
    cli = ClienteOllama(GERADOR, URL_PADRAO)
    cli.conversar([{"role": "user", "content": "oi"}], {"type": "object"}, 5, 0)          # aquece o modelo
    saida = []
    i = 0
    for p in pets:
        citados_chaves: list[list[str]] = []
        esp = especies.get(p["nome"].replace(" sombrio", ""))
        for k in range(len(p["momentos"])):
            est, dadas = situacao(p, k, citados_chaves)
            tentativas = None
            if REVISAO:
                r, tentativas = gerar_com_revisao(cli, est, "espontanea", semente=SEMENTE + i, versao=PROMPT, especie=esp)
            else:
                r = gerar(cli, est, "espontanea", semente=SEMENTE + i, versao=PROMPT, especie=esp)
            por_id = {f["id"]: f for f in r.fatos}
            chaves = [por_id[c]["chave"] for c in r.fatos_citados if c in por_id and "chave" in por_id[c]]
            citados_chaves.append(dadas if FOCO else chaves)
            saida.append({"pet": _chave(p), "grupo": p["grupo"], "braco": p["braco"], "ovo": p["ovo"],
                          "sombria": p["sombria"], "k": k, "tick": p["momentos"][k]["tick"], "estado_pet": est,
                          "fala": r.fala, "fatos_citados": list(r.fatos_citados), "fatos": list(r.fatos),
                          "chaves_citadas": chaves, "estagio": r.estagio, "especie_corpus": r.especie,
                          "modelo": r.modelo, "versao_prompt": r.versao_prompt, "semente": SEMENTE + i,
                          "latencia_s": r.latencia_s, "erro": r.erro, "tentativas": tentativas})
            i += 1
            print(f"{i:3d} {_chave(p)} k{k} {r.latencia_s or 0:.1f}s {r.fala[:90]!r}", flush=True)
    cli.descarregar()
    _gravar(SAIDA / "falas.jsonl", "\n".join(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in saida))


# ------------------------------------------------------------------ 3. verificar
def fase_verificar() -> None:
    falas = _jsonl(SAIDA / "falas.jsonl")
    juiz = ClienteOllama(JUIZ, URL_PADRAO, timeout=90.0)
    out = []
    for i, f in enumerate(falas):
        if f["erro"] or f["fala"] == FALA_GENERICA:
            out.append({"pet": f["pet"], "k": f["k"], "pulada": True})
            continue
        v = verificar(juiz, f["fala"], f["fatos_citados"], f["fatos"], semente=SEMENTE + i, versao=VERSAO_VERIFICADOR_V4)
        out.append({"pet": f["pet"], "k": f["k"], "pulada": False, **v.para_dict()})
        print(f"{i:3d} sem fato {v.nao_suportadas} mentira {v.mentiras_deliberadas} erro {v.erro}", flush=True)
    juiz.descarregar()
    _gravar(SAIDA / "verificacao.jsonl", "\n".join(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in out))


def _assunto_verdadeiro(f: dict) -> tuple[str, str] | None:
    """(frase verdadeira por construcao, id) do assunto dado: o texto do fato, em 1a pessoa. A mentira nao entra
    (nao e verdadeira)."""
    por_id = {x["id"]: x for x in f["fatos"]}
    if "F1" in por_id:
        return None
    if "W1" in por_id:
        return f"Ouvi no Digimundo que {por_id['W1']['texto']}.", "W1"
    x = next((x for x in f["fatos"] if x["id"][:1] in "HOPL"), None)
    return None if x is None else (x["texto"][0].upper() + x["texto"][1:] + ".", x["id"])


def fase_piso() -> None:
    """o juiz verifica, com os mesmos blocos de fatos, frases que so dizem o fato: tudo que ele barrar e erro dele"""
    falas = _jsonl(SAIDA / "falas.jsonl")
    juiz = ClienteOllama(JUIZ, URL_PADRAO, timeout=90.0)
    out = []
    for i, f in enumerate(falas):
        a = _assunto_verdadeiro(f)
        if a is None:
            continue
        v = verificar(juiz, a[0], [a[1]], f["fatos"], semente=SEMENTE + 50000 + i, versao=VERSAO_VERIFICADOR_V4)
        out.append({"pet": f["pet"], "k": f["k"], "frase": a[0], **v.para_dict()})
        print(f"{i:3d} piso sem fato {v.nao_suportadas}", flush=True)
    juiz.descarregar()
    _gravar(SAIDA / "piso_juiz.jsonl", "\n".join(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in out))


# ------------------------------------------------------------------ 4. resumo
def _pct(xs) -> float | None:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def resumir() -> dict:
    pets = _jsonl(PETS)
    falas = _jsonl(SAIDA / "falas.jsonl")
    ver = {(v["pet"], v["k"]): v for v in _jsonl(SAIDA / "verificacao.jsonl")}
    validas = [f for f in falas if not f["erro"]]
    verif = [ver[(f["pet"], f["k"])] for f in validas if not ver[(f["pet"], f["k"])]["pulada"]]
    verif_ok = [v for v in verif if not v["erro"]]
    hist = lambda f: [c for c in f["fatos_citados"] if c[:1] in "HOPL" and c in {x["id"] for x in f["fatos"]}]  # noqa: E731
    # variedade: mesmo ovo e mesmo momento (grupo A), donos diferentes
    a = [f for f in validas if f["grupo"] == "A"]
    pares = []
    for s in OVOS_A:
        for k in range(FALAS_POR_PET):
            xs = [f for f in a if f["ovo"] == s and f["k"] == k]
            for i in range(len(xs)):
                for j in range(i + 1, len(xs)):
                    pares.append(set(xs[i]["chaves_citadas"]) != set(xs[j]["chaves_citadas"]))
    rep = {}
    for f in validas:                              # o mesmo braco@ovo pode estar nos dois grupos: a chave leva o grupo
        rep.setdefault(f"{f['grupo']}:{f['pet']}", []).append(f)
    max_rep = {}
    for pet, fs in rep.items():
        cont: dict[str, int] = {}
        for f in fs:
            for c in set(f["chaves_citadas"]):
                cont[c] = cont.get(c, 0) + 1
        max_rep[pet] = max(cont.values(), default=0)
    com_f = [f for f in validas if any(x["id"] == "F1" for x in f["fatos"])]
    ver_f = [ver[(f["pet"], f["k"])] for f in com_f if not ver[(f["pet"], f["k"])]["pulada"]]
    lat = [f["latencia_s"] for f in falas if f["latencia_s"] is not None]
    nomes = digimon_da_forma()
    esp_corpus, meta_c, sha_c = corpus.carregar()
    honest = _pct(v["nao_suportadas"] > 0 for v in verif_ok)
    historia = _pct(bool(hist(f)) for f in validas)
    variedade = _pct(pares)
    r = {
        "n": {"pets": len(pets), "pets_mortos": sum(p["morta"] for p in pets), "falas": len(falas),
              "falas_com_erro": len(falas) - len(validas), "verificadas": len(verif_ok),
              "verificacao_com_erro": len(verif) - len(verif_ok), "pares_variedade": len(pares)},
        "gates": {
            "honestidade": {"valor": honest, "limite": GATES["honestidade_max"],
                            "passa": honest is not None and honest <= GATES["honestidade_max"]},
            "historia": {"valor": historia, "limite": GATES["historia_min"],
                         "passa": historia is not None and historia >= GATES["historia_min"]},
            "variedade": {"valor": variedade, "limite": GATES["variedade_min"],
                          "passa": variedade is not None and variedade >= GATES["variedade_min"]},
            "repeticao": {"pets_acima": sorted(p for p, m in max_rep.items() if m > GATES["repeticao_max_em_5"]),
                          "max_por_pet": max(max_rep.values(), default=0), "limite": GATES["repeticao_max_em_5"],
                          "passa": all(m <= GATES["repeticao_max_em_5"] for m in max_rep.values())},
        },
        "por_grupo": {g: {"falas": sum(f["grupo"] == g for f in validas),
                          "cita_historia": _pct(bool(hist(f)) for f in validas if f["grupo"] == g),
                          "sem_fato": _pct(ver[(f["pet"], f["k"])]["nao_suportadas"] > 0 for f in validas
                                           if f["grupo"] == g and not ver[(f["pet"], f["k"])]["pulada"]
                                           and not ver[(f["pet"], f["k"])]["erro"])} for g in ("A", "B")},
        "por_tipo_citado": {t: sum(any(c[:1] == t for c in f["fatos_citados"]) for f in validas) for t in "HOPLWFEG"},
        "mentira": {"falas_com_F": len(com_f), "citam_F": sum(v.get("cita_mentira") is True for v in ver_f),
                    "mentiras_deliberadas": sum(v.get("mentiras_deliberadas") or 0 for v in ver_f),
                    "moldes": sorted({x.get("molde") for f in com_f for x in f["fatos"] if x["id"] == "F1"}),
                    "exemplos": [{"verdade": x["verdade"], "falsa": x["texto"], "fala": f["fala"]}
                                 for f in com_f[:6] for x in f["fatos"] if x["id"] == "F1"]},
        "almanaque": {"falas_com_W": sum(any(x["id"] == "W1" for x in f["fatos"]) for f in validas),
                      "citam_W": sum("W1" in f["fatos_citados"] for f in validas)},
        "manipulacao": sum(v["manipulacao"] for v in verif_ok),
        "citados_inexistentes": sum(len(v["citados_inexistentes"]) for v in verif_ok),
        "latencia_s": {"p50": statistics.median(lat) if lat else None,
                       "p90": sorted(lat)[int(0.9 * (len(lat) - 1))] if lat else None},
        "corpus": {"exemplo": meta_c["exemplo"], "sha256": sha_c, "especies": sorted(esp_corpus),
                   "formas_do_jogo": len(set(nomes.values())),
                   "formas_com_entrada": sorted(set(nomes.values()) & set(esp_corpus)),
                   "falas_com_estilo": sum(f["especie_corpus"] is not None for f in falas)},
        "gates_propostos": "DESIGN_VOZ_PROPRIA, secao 6 (PROPOSTOS, sem fonte)",
    }
    if (SAIDA / "piso_juiz.jsonl").exists():
        piso = [x for x in _jsonl(SAIDA / "piso_juiz.jsonl") if not x["erro"]]
        r["piso_juiz"] = {"frases": len(piso), "sem_fato": _pct(x["nao_suportadas"] > 0 for x in piso),
                          "manipulacao": sum(x["manipulacao"] for x in piso)}
    if any(f.get("tentativas") for f in falas):
        tent = [f["tentativas"] for f in falas if f.get("tentativas")]
        r["revisao"] = {"versao": VERSAO_REVISAO, "falas": len(tent),
                        "com_problema_na_primeira": sum(bool(t[0]["problemas"]) for t in tent),
                        "reescritas": sum(len([x for x in t[1:] if x.get("fala")]) for t in tent),
                        "sem_problema_no_fim_pelo_proprio_modelo": sum(not min(len(x["problemas"]) for x in t
                                                                               if x.get("fala")) for t in tent)}
    return r


def _relatorio(r: dict, meta: dict) -> str:
    g = r["gates"]
    f = lambda x: "—" if x is None else f"{100 * x:.1f}%"  # noqa: E731
    linhas = [
        "# Voz própria — rodada 1 (offline)", "",
        f"Gerador `{GERADOR}`, prompt `{PROMPT}`{' (assunto escolhido pelo código)' if FOCO else ''}; juiz `{JUIZ}`, verificador `{VERSAO_VERIFICADOR_V4}`; "
        f"semente {SEMENTE}. Números de `resumo.json`; gates da seção 6 do design (PROPOSTOS).", "",
        "| gate | valor | limite | passa |", "|---|---|---|---|",
        f"| honestidade (falas com afirmação sem fato) | {f(g['honestidade']['valor'])} | ≤ 5% | "
        f"{'sim' if g['honestidade']['passa'] else 'NÃO'} |",
        f"| história (falas que citam H, O, P ou L) | {f(g['historia']['valor'])} | ≥ 50% | "
        f"{'sim' if g['historia']['passa'] else 'NÃO'} |",
        f"| variedade (pares de donos diferentes, mesmo ovo e momento, com fatos diferentes) | "
        f"{f(g['variedade']['valor'])} | ≥ 70% | {'sim' if g['variedade']['passa'] else 'NÃO'} |",
        f"| repetição (máximo do mesmo fato em 5 falas de um pet) | {g['repeticao']['max_por_pet']} | ≤ 2 | "
        f"{'sim' if g['repeticao']['passa'] else 'NÃO'} |", "",
        f"Amostra: {r['n']['pets'] - r['n']['pets_mortos']} pets vivos ({r['n']['pets_mortos']} mortos), "
        f"{r['n']['falas']} falas, {r['n']['falas_com_erro']} com erro (viraram a genérica ou o molde), "
        f"{r['n']['verificadas']} verificadas ({r['n']['verificacao_com_erro']} com erro do juiz).", "",
        (f"Piso do juiz: {f(r['piso_juiz']['sem_fato'])} de {r['piso_juiz']['frases']} frases verdadeiras por "
         "construção barradas como sem fato.\n" if "piso_juiz" in r else "") +
        (f"Autocorreção: {r['revisao']['com_problema_na_primeira']} de {r['revisao']['falas']} falas com problema "
         f"apontado pelo próprio modelo na primeira versão; {r['revisao']['reescritas']} reescritas; "
         f"{r['revisao']['sem_problema_no_fim_pelo_proprio_modelo']} terminam sem problema pelo próprio modelo.\n"
         if "revisao" in r else "") +
        f"Mentira (grupo B, sombrios): {r['mentira']['falas_com_F']} falas com [F1], "
        f"{r['mentira']['citam_F']} citam [F1], {r['mentira']['mentiras_deliberadas']} afirmações marcadas como "
        "mentira deliberada.", "",
        f"Almanaque: {r['almanaque']['falas_com_W']} falas com [W1], {r['almanaque']['citam_W']} citam.", "",
        f"Corpus: EXEMPLO ({', '.join(r['corpus']['especies'])}); formas do jogo com entrada: "
        f"{len(r['corpus']['formas_com_entrada'])} de {r['corpus']['formas_do_jogo']} "
        f"({', '.join(r['corpus']['formas_com_entrada']) or 'nenhuma'}); falas com estilo: {r['corpus']['falas_com_estilo']}.",
        "", f"Latência p50 {r['latencia_s']['p50']:.1f} s, p90 {r['latencia_s']['p90']:.1f} s.", "",
        "Avaliação cega: `avaliacao_cega.csv` (a chave em `chave_avaliacao_cega.json`, não abrir antes).", "",
        f"Ambiente: {meta['ambiente']}.",
    ]
    return "\n".join(linhas)


def fase_resumo() -> None:
    r = resumir()
    meta = json.loads((SAIDA / "meta.json").read_text(encoding="utf-8"))
    _gravar(SAIDA / "resumo.json", _dump(r))
    _gravar(SAIDA / "RELATORIO.md", _relatorio(r, meta))
    print(_dump(r["gates"]))


# ------------------------------------------------------------------ 5. avaliacao cega
def fase_cega() -> None:
    rng = random.Random(derivar_semente("cega", SEMENTE))
    novas = [f for f in _jsonl(SAIDA / "falas.jsonl") if not f["erro"]]
    v6 = [x for x in _jsonl(FALA_V6) if x["aprovada"] and x["estagio"] in ("adolescente", "adulto")]
    a, b = rng.sample(novas, N_PARES), rng.sample(v6, N_PARES)
    linhas, chave = [], {}
    for i, (n, o) in enumerate(zip(a, b), 1):
        par = [("voz_nova", n["fala"]), ("fala_v6", o["fala"])]
        rng.shuffle(par)
        linhas.append({"par": i, "fala_1": par[0][1], "fala_2": par[1][1], "mais_viva (1 ou 2)": ""})
        chave[i] = [par[0][0], par[1][0]]
    with open(SAIDA / "avaliacao_cega.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0]), delimiter=";")
        w.writeheader()
        w.writerows(linhas)
    _gravar(SAIDA / "chave_avaliacao_cega.json", _dump(chave))


def _meta() -> None:
    fontes = ["digilab/historia.py", "digilab/educacao.py", "digilab/donos_educacao.py", "digilab/config.py",
              "digilab_fala_livre/fatos.py", "digilab_fala_livre/prompt.py", "digilab_fala_livre/verificador.py",
              "digilab_fala_livre/mentira.py", "digilab_fala_livre/gerar.py", "digilab_fala_livre/revisao.py", "digilab_fala_livre/almanaque.json",
              "digilab_fala_livre/corpus_especies.json", "experiments/avaliar_voz.py"]
    _gravar(SAIDA / "meta.json", _dump({
        "semente": SEMENTE, "gerador": GERADOR, "juiz": JUIZ, "prompt": PROMPT, "assunto_pelo_codigo": FOCO,
        "autocorrecao": VERSAO_REVISAO if REVISAO else None,
        "pets": str(PETS.relative_to(RAIZ)).replace("\\", "/"),
        "verificador": VERSAO_VERIFICADOR_V4, "hash_parametros_mentira": hash_parametros_mentira(),
        "fontes_sha256": {f: hashlib.sha256((RAIZ / f).read_bytes()).hexdigest() for f in fontes},
        "grupos": {"A": {"ovos": OVOS_A, "bracos": BRACOS_A, "personas": PERSONAS_A, "momentos": f"dia {DIA_A}, {HORAS_A} h"},
                   "B": {"sombrios": SOMBRIOS_B, "mentira": "ConfigMentira ligada"}},
        "ambiente": {"plataforma": platform.platform(), "python": platform.python_version()}}))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fase", default="tudo", choices=("pets", "gerar", "verificar", "piso", "resumo", "cega", "tudo"))
    ap.add_argument("--processos", type=int, default=8)
    ap.add_argument("--rodada", type=int, default=1, choices=sorted(RODADAS))
    a = ap.parse_args(argv)
    configurar(a.rodada)
    SAIDA.mkdir(parents=True, exist_ok=True)
    if not (SAIDA / "meta.json").exists() or a.fase in ("pets", "tudo"):
        _meta()
    if a.fase == "pets" or (a.fase == "tudo" and a.rodada == 1):
        fase_pets(a.processos)
    if a.fase in ("gerar", "tudo"):
        fase_gerar()
    if a.fase in ("verificar", "tudo"):
        fase_verificar()
    if a.fase == "piso" or (a.fase == "tudo" and REVISAO):
        fase_piso()
    if a.fase in ("cega", "tudo"):
        fase_cega()
    if a.fase in ("resumo", "tudo"):
        fase_resumo()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
