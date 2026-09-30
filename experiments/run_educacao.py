"""Run exploratoria da educacao-v1 (docs/PLANO_ANALISE_V3.md, registrado antes da run).

    python experiments/run_educacao.py --processos 8
    python experiments/run_educacao.py --fumaca --painel 2 --saida <pasta>        # ovos 69001-69002

1. Vidas: cada ovo em cada um dos 7 bracos (simular_vida_educacao: educacao e lesoes ligadas, 14 dias, duracao
   teste, orcamento igual), com sparring de verdade no adolescente (10 lutas; o braco lutador faz 20) contra o
   adolescente da mesma linha e especie, carater neutro, sem treino. Log gravado e rejogado DO DISCO.
2. Pet final: morto -> nao luta (0 em todas as partidas). Qualificado (>= 10 lutas, taxa >= 0,8) -> forma adulta
   (ou a sombria); senao continua adolescente. Epsilon do lutador pela disciplina final.
3. Painel B (8 formas adultas x 4 especies, 50 partidas por bot, sementes do ovo/bot/k), condicao neutra
   (principal) e real (descritiva).
4. Analise: bootstrap sobre ovos (10000, semente 20260928), leitura da secao 5 do plano original; gate de
   equilibrio dos estilos (cuidar = atencioso, treinar = exigente, lutar = lutador); mecanismo por braco.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.campanha import REGRAS_CAMPANHA  # noqa: E402
from digilab.combate_v2.v21.bots import (ADOLESCENTES, FORMAS, SOMBRIOS, gambits_adulto, lutador_adolescente,  # noqa: E402
                                         lutador_adulto)
from digilab.combate_v2.v21.catalogo import (SOMBRIA_DA_LINHA, Forma, forma_adulta, linha_do_adolescente,  # noqa: E402
                                             perfil, ramo_da_crianca)
from digilab.combate_v2.v21.partida import Lutador, jogar  # noqa: E402
from digilab.config import (CONFIG_CATALOGO, CONFIG_EDUCACAO_LIGADA, CONFIG_EQUILIBRIO, CONFIG_EVOLUCAO_PESQUISA,  # noqa: E402
                            CONFIG_LESOES_LIGADA, CONFIG_PADRAO, CONFIG_SOMBRIO, CONFIG_SPARRING, ConfigArenaPesquisa)
from digilab.donos_educacao import simular_vida_educacao  # noqa: E402
from digilab.educacao import epsilon_disciplina, fabricas_educacao, politica_no_tick_educacao, reproduzir_educacao  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.evolucao import carater, condicao_na_arena, fracao_cuidado_bebe, ovo  # noqa: E402
from digilab.protocol import (ENGINE_SHA256_V0, PROTOCOLO_ARENA_V1, derivar_semente, hash_parametros_educacao,  # noqa: E402
                              sha256_engine, validar_parametros_educacao)
from digilab.personas import carregar_lote  # noqa: E402
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino_vida import orcamento_treino  # noqa: E402
from run_confirmatoria import bootstrap, leitura  # noqa: E402
from run_poder import _dump, _gravar, regras_de  # noqa: E402

CFG_PADRAO = RAIZ / "experiments" / "configs" / "educacao_pesquisa.json"
SEMENTE_BOOT = 20260928
SONDAS = (PROTOCOLO_ARENA_V1.v("estados_sonda"), PROTOCOLO_ARENA_V1.v("amostras_por_estado"),
          PROTOCOLO_ARENA_V1.v("semente_sonda"))
T_ADOL = CONFIG_EVOLUCAO_PESQUISA.dur_bebe_min + CONFIG_EVOLUCAO_PESQUISA.dur_crianca_min
T_ADUL = T_ADOL + CONFIG_EVOLUCAO_PESQUISA.dur_adolescente_min
ESTILOS_V3 = {"cuidar": "atencioso", "treinar": "exigente", "lutar": "lutador"}   # o config pode trocar ("estilos")


def condicao_da_saude(saude: float) -> float:
    cat = CONFIG_CATALOGO
    return cat.condicao_mult_min + (cat.condicao_mult_max - cat.condicao_mult_min) * max(0.0, min(1.0, saude))


def ticks_sparring(braco: str) -> tuple:
    cs = CONFIG_SPARRING
    n = cs.lutas_braco_lutador if braco == "lutador" else cs.lutas
    return tuple(T_ADOL + cs.primeira_apos_inicio_min + k * cs.intervalo_min for k in range(n))


def rival_por_nome(nome: str) -> Lutador:
    """'sparring:<linha>@<especie>': adolescente da linha, carater neutro, sem treino, regras da campanha"""
    tipo, _, resto = nome.partition(":")
    if tipo != "sparring":
        raise ValueError(f"rival desconhecido na vida de pesquisa: {nome!r}")
    linha, especie = resto.split("@")
    return lutador_adolescente(linha, especie, {}, REGRAS_CAMPANHA.v21)


class PetDaVida:
    """Lutador do pet na vida (sparring) e o carater do adolescente, medido uma vez (no inicio do estagio)."""

    def __init__(self, braco: str, s: int, especie: str, temp_ovo: dict, fp, fm_base) -> None:
        self.braco, self.s, self.especie, self.temp_ovo = braco, s, especie, temp_ovo
        self.fp, self.fm_base = fp, fm_base
        self.adol: tuple | None = None

    def _adolescente(self, m) -> tuple:
        if self.adol is None:
            log = m.log_ate_agora
            pol = politica_no_tick_educacao(log, self.fp, self.s, T_ADOL, self.fm_base)
            car, _ = carater(pol, self.fp(CONFIG_PADRAO), *SONDAS)
            frac, _, _ = fracao_cuidado_bebe(log)
            self.adol = (car, linha_do_adolescente(car), ramo_da_crianca(frac))
        return self.adol

    def rival(self, m) -> str:
        return f"sparring:{self._adolescente(m)[1]}@{self.especie}"

    def lutador(self, m) -> Lutador:
        car, linha, ramo = self._adolescente(m)
        p = perfil(Forma(self.especie, "adolescente", ramo, linha), self.temp_ovo, car,
                   condicao_da_saude(m.estado()["saude"]), REGRAS_CAMPANHA.v21, treino=dict(m.treino.pontos),
                   normalizar_treino=False)
        return Lutador(f"pet:{self.braco}@{self.s}", p, ADOLESCENTES[linha], epsilon_disciplina(m.disciplina))


def _fabricas(b, s, esp, tmp, temp_ovo):
    fp, fm_base = fabricas_educacao(s, esp, tmp, ce=CONFIG_EDUCACAO_LIGADA, cl=CONFIG_LESOES_LIGADA)
    pet = PetDaVida(b, s, esp, temp_ovo, fp, fm_base)
    _, fm = fabricas_educacao(s, esp, tmp, ce=CONFIG_EDUCACAO_LIGADA, cl=CONFIG_LESOES_LIGADA,
                              lutador_do_pet=pet.lutador, rival_por_nome=rival_por_nome)
    return fp, fm_base, fm, pet


# ------------------------------------------------------------------ 1. vidas
def carregar_personas(cfg: dict) -> dict:
    """lote de personas do config (V3c): confere o sha256 registrado antes da run"""
    if not cfg.get("lote_personas"):
        return {}
    ps, sha = carregar_lote(RAIZ / cfg["lote_personas"])
    if sha != cfg["lote_personas_sha256"]:
        raise ValueError(f"lote de personas mudou: sha256 {sha} != {cfg['lote_personas_sha256']}")
    return {p.nome: p for p in ps}


def _vida(args):
    b, s, dias, saida, cfg = args
    t0 = time.perf_counter()
    esp, temp_ovo = ovo(s)
    tmp = sortear(s)
    persona = carregar_personas(cfg)[b.split(":", 1)[1]] if b.startswith("persona:") else None
    fp, fm_base, _, pet = _fabricas(b, s, esp, tmp, temp_ovo)
    v = simular_vida_educacao(b, s, dias, esp, tmp, cl=CONFIG_LESOES_LIGADA, sparring=ticks_sparring(b),
                              rival_sparring=pet.rival, lutador_do_pet=pet.lutador, rival_por_nome=rival_por_nome,
                              persona=persona)
    m = v.motor
    orc, _ = orcamento_treino(dias)
    if not v.morta and v.interacoes != orc:
        raise RuntimeError(f"{b}@{s}: {v.interacoes} interacoes, esperado {orc}")
    arq = Path(saida) / "vidas" / f"{b}@{s}.jsonl"
    _gravar(arq, m.log.para_jsonl())
    fp2, _, fm2, _ = _fabricas(b, s, esp, tmp, temp_ovo)          # replay com cache novo (recalcula o carater)
    r = reproduzir_educacao(LogDeEventos.de_jsonl(arq.read_text(encoding="utf-8")), fp2, semente=s, fabrica_motor=fm2)
    if (r.estado() != m.estado() or r.resumo_educacao() != m.resumo_educacao() or r.historico_lutas != m.historico_lutas
            or r.vinculo.serie != m.vinculo.serie or r.transicoes != m.transicoes):
        raise RuntimeError(f"replay de {b}@{s} divergiu")
    lutas = m.historico_lutas
    dados = {"braco": b, "ovo": s, "especie": esp, "morta": v.morta, "morte": m.morte,
             "sparring": {"lutas": len(lutas), "vitorias": sum(x["resultado"] == "vitoria" for x in lutas),
                          "lesoes": sum(x["lesao"] for x in lutas)},
             "lutas_que_treinaram": sum(1 for x in lutas if x.get("treinou")),
             "qualificacao": m.transicoes.get("adulto", {}).get("vitorias"), "adulto_liberado": m.adulto_liberado,
             "disciplina_final": m.disciplina, "educacao": m.resumo_educacao()["contagem"],
             "saude_final": m.estado()["saude"], "vinculo_final": m.vinculo.valor, "sombria": bool(m.sombria),
             "treino_total": sum(m.treino.pontos.values()), "respostas_dono": dict(v.dono.respostas)}
    spec = None
    if not v.morta:
        car_adol, linha, ramo = pet._adolescente(m)
        pol = politica_no_tick_educacao(m.log, fp, s, T_ADUL, fm_base)
        car_adul, _ = carater(pol, fp(CONFIG_PADRAO), *SONDAS)
        if m.adulto_liberado:
            adulta = SOMBRIA_DA_LINHA[linha] if m.sombria else forma_adulta(linha, car_adul, len(lutas))
            forma = {"estagio": "adulto", "ramo": ramo, "linha": linha, "adulta": adulta}
        else:
            forma = {"estagio": "adolescente", "ramo": ramo, "linha": linha, "adulta": None}
        spec = {"forma": forma, "temp_ovo": temp_ovo, "carater": car_adul, "condicao": condicao_da_saude(m.estado()["saude"]),
                "pontos": dict(m.treino.pontos), "disciplina": m.disciplina, "especie": esp}
        dados["forma"] = forma
    return (b, s), spec, dados, time.perf_counter() - t0


# ------------------------------------------------------------------ 2. painel
def lutador_painel(nome: str, spec: dict, carena: ConfigArenaPesquisa, cfg_v21) -> Lutador:
    f = spec["forma"]
    forma = Forma(spec["especie"], f["estagio"], f["ramo"], f["linha"], f["adulta"])
    p = perfil(forma, spec["temp_ovo"], spec["carater"], condicao_na_arena(spec["condicao"], carena), cfg_v21,
               treino=spec["pontos"], normalizar_treino=True)
    eps = epsilon_disciplina(spec["disciplina"])
    if f["adulta"] is None:
        g = ADOLESCENTES[f["linha"]]
    elif f["adulta"] in SOMBRIOS:
        g, eps = SOMBRIOS[f["adulta"]], max(eps, CONFIG_SOMBRIO.epsilon_minimo)
    else:
        g = gambits_adulto(f["adulta"], cfg_v21)     # = ADULTOS com as chaves da V21D desligadas (docs/PLANO_ANALISE_V21D.md)
    return Lutador(nome, p, g, eps)


def _painel_do_ovo(args):
    s, specs, cfg, neutra, m_b, rotulo = args
    t0 = time.perf_counter()
    r = regras_de(cfg)
    carena = ConfigArenaPesquisa(condicao_neutra=neutra)
    lut = {b: (None if sp is None else lutador_painel(f"{b}@{s}", sp, carena, r.v21)) for b, sp in specs.items()}
    painel, n = {}, 0
    for esp in CONFIG_CATALOGO.especies_ativas:
        for f in FORMAS:
            bot = lutador_adulto(f, esp, r.v21, nome=f"painel:{f}@{esp}")
            for b, L in lut.items():
                pts = []
                for k in range(m_b):
                    if L is None:
                        pts.append(0.0)                       # morto nao luta
                        continue
                    sp = derivar_semente(f"{rotulo}|B|{s}", bot.nome, k)
                    pts.append(jogar(L, bot, sp, r).pontos_a if k < m_b // 2 else 1.0 - jogar(bot, L, sp, r).pontos_a)
                    n += 1
                painel.setdefault(b, {})[bot.nome] = pts
    return s, painel, n, time.perf_counter() - t0


# ------------------------------------------------------------------ 3. analise
def taxa(painel_braco: dict) -> float:
    pts = [x for v in painel_braco.values() for x in v]
    return sum(pts) / len(pts)


def analisar(res: dict, pets: dict, bracos: list[str], estilos: dict | None = None, personas: dict | None = None) -> dict:
    estilos = estilos or ESTILOS_V3
    out = {}
    for var, por_ovo in res.items():
        ovos = sorted(por_ovo, key=int)
        t = {b: [taxa(por_ovo[o][b]) for o in ovos] for b in bracos}
        dif = lambda x, y, k: bootstrap([a - c for a, c in zip(t[x], t[y])], 0.0, SEMENTE_BOOT + k)  # noqa: E731
        comp = {}
        for k, (x, y) in enumerate((("atencioso", "aleatorio"), ("atencioso", "permissivo"), ("relapso", "aleatorio"),
                                    ("incoerente", "aleatorio"), ("exigente", "atencioso"), ("lutador", "atencioso"),
                                    ("permissivo", "aleatorio"), ("treinador", "atencioso"), ("treinador", "exigente"))):
            if x not in t or y not in t:
                continue
            c = dif(x, y, k)
            c["leitura"] = leitura(c)
            comp[f"{x}-{y}"] = c
        medias = {b: sum(v) / len(v) for b, v in t.items()}
        # dominancia: IC95 da diferenca inteiro acima de 0 contra cada um dos outros
        domina = {}
        fixos = [b for b in bracos if not b.startswith("persona:")]
        for i, x in enumerate(fixos):
            domina[x] = all(dif(x, y, 100 + 10 * i + j)["ic95"][0] > 0 for j, y in enumerate(fixos) if y != x)
        ce = CONFIG_EQUILIBRIO
        est = {e: medias[b] for e, b in estilos.items()}
        margens = {e: min(est[e] - est[o] for o in est if o != e) for e in est}
        gate = {"medias_estilos": est,
                "faixa_ok": {e: ce.taxa_min <= v <= ce.taxa_max for e, v in est.items()},
                "margem_sobre_os_outros": margens,
                "margem_ok": all(m <= ce.margem_max for m in margens.values()),
                "braco_dominante": [b for b, d in domina.items() if d]}
        gate["aprovado"] = all(gate["faixa_ok"].values()) and gate["margem_ok"] and not gate["braco_dominante"]
        out[var] = {"taxa_media_por_braco": medias, "comparacoes": comp, "gate_equilibrio": gate}
    mec = {}
    for b in [b for b in bracos if not b.startswith("persona:")]:
        ds = [d for d in pets.values() if d["braco"] == b]
        vivos = [d for d in ds if not d["morta"]]
        sp = [d["sparring"] for d in ds if d["sparring"]["lutas"]]
        formas: dict = {}
        for d in vivos:
            chave = d["forma"]["adulta"] or f"adolescente:{d['forma']['linha']}"
            formas[chave] = formas.get(chave, 0) + 1
        mec[b] = {"n": len(ds), "mortes": len(ds) - len(vivos),
                  "lutas_que_treinaram_media": sum(d.get("lutas_que_treinaram", 0) for d in ds) / len(ds),
                  "causas_morte": sorted({d["morte"]["causa"] for d in ds if d["morte"]}),
                  "qualificados_adulto": sum(bool(d["adulto_liberado"]) for d in vivos),
                  "taxa_sparring_media": (sum(x["vitorias"] / x["lutas"] for x in sp) / len(sp)) if sp else None,
                  "lesoes_media": sum(d["sparring"]["lesoes"] for d in ds) / len(ds),
                  "disciplina_final_media": sum(d["disciplina_final"] for d in ds) / len(ds),
                  "saude_final_media": sum(d["saude_final"] for d in ds) / len(ds),
                  "treino_total_medio": sum(d["treino_total"] for d in ds) / len(ds), "formas": formas}
    out["mecanismo"] = mec
    if personas:
        out["personas"] = analisar_personas(res["neutra"], personas, bracos)
    return out


TRACOS = ("prob_atender_janela", "prob_ceder_petisco", "prob_feedback_coerente", "limiar_cuidado")


def _mqo(X: list[list[float]], y: list[float]) -> list[float]:
    """minimos quadrados pelas equacoes normais (eliminacao de Gauss); X ja com a coluna de 1"""
    k = len(X[0])
    A = [[sum(r[i] * r[j] for r in X) for j in range(k)] + [sum(r[i] * v for r, v in zip(X, y))] for i in range(k)]
    for c in range(k):
        p = max(range(c, k), key=lambda i: abs(A[i][c]))
        A[c], A[p] = A[p], A[c]
        if abs(A[c][c]) < 1e-12:
            raise ValueError("regressao singular")
        for i in range(k):
            if i != c:
                f = A[i][c] / A[c][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[c])]
    return [A[i][k] / A[i][i] for i in range(k)]


def analisar_personas(por_ovo: dict, personas: dict, bracos: list[str]) -> dict:
    """exploratorio (adendo V3c): taxa contra o painel (neutra) por persona e o efeito de cada traco do dono.
    Regressao da taxa media de cada persona nos 4 tracos + perfil exigente; IC por bootstrap sobre ovos."""
    import random as _r
    ovos = sorted(por_ovo, key=int)
    nomes = [b for b in bracos if b.startswith("persona:")]
    X = [[1.0] + [getattr(personas[n.split(":", 1)[1]], t) for t in TRACOS]
         + [1.0 if personas[n.split(":", 1)[1]].perfil_treino == "exigente" else 0.0] for n in nomes]
    def coef(amostra):
        y = [sum(taxa(por_ovo[o][n]) for o in amostra) / len(amostra) for n in nomes]
        return _mqo(X, y), y
    base, y = coef(ovos)
    rng, boots = _r.Random(SEMENTE_BOOT), []
    for _ in range(2000):
        boots.append(coef([ovos[rng.randrange(len(ovos))] for _ in ovos])[0])
    rot = ["intercepto", *TRACOS, "perfil_exigente"]
    efeitos = {}
    for j, r in enumerate(rot):
        v = sorted(b[j] for b in boots)
        efeitos[r] = {"estimativa": base[j], "ic95": [v[int(.025 * len(v))], v[int(.975 * len(v)) - 1]]}
    return {"taxa_media": {n: t for n, t in zip(nomes, y)}, "efeitos_tracos": efeitos,
            "nota": "efeito = mudanca na taxa contra o painel por 1,0 do traco (0 a 1), com os outros fixos"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=str(CFG_PADRAO))
    ap.add_argument("--saida", default=None, help="padrao: o 'saida' do config (ou artifacts_educacao)")
    ap.add_argument("--painel", type=int, default=None, help="partidas por bot (padrao: o do config)")
    ap.add_argument("--processos", type=int, default=None)
    ap.add_argument("--fumaca", action="store_true")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")
    validar_parametros_educacao()
    saida = Path(a.saida or RAIZ / cfg.get("saida", "artifacts_educacao"))
    if a.fumaca:
        ovos = cfg["sementes_fumaca"]
        if saida.resolve().name.startswith("artifacts_educacao"):
            raise ValueError("fumaca fora de artifacts_educacao/")
    else:
        ovos = cfg["sementes"]
        if set(ovos) & set(cfg["sementes_antigas"]) or set(ovos) & set(cfg["sementes_fumaca"]):
            raise ValueError("ovos colidem com runs antigas ou com a fumaca")
    m_b = a.painel or cfg["M_B_por_bot"]
    if m_b % 2:
        raise ValueError("partidas por bot precisa ser par")
    bracos = list(cfg["bracos"]) + [f"persona:{n}" for n in carregar_personas(cfg)]
    saida.mkdir(parents=True, exist_ok=True)
    tempos = {}
    with ProcessPoolExecutor(a.processos or cfg["processos"]) as pool:
        t0 = time.perf_counter()
        vidas = list(pool.map(_vida, [(b, s, cfg["dias"], str(saida), cfg) for s in ovos for b in bracos]))
        tempos["vidas_s"] = time.perf_counter() - t0
        specs = {k: sp for k, sp, _, _ in vidas}
        pets = {f"{b}@{s}": d for (b, s), _, d, _ in vidas}
        _gravar(saida / "pets.json", _dump(pets))
        print(f"  {len(vidas)} vidas em {tempos['vidas_s']:.0f} s", flush=True)
        res = {}
        for nome, neutra in sorted(cfg["variantes_condicao"].items()):
            t1 = time.perf_counter()
            por_ovo, n = {}, 0
            for s, painel, k, _ in pool.map(_painel_do_ovo, [(s, {b: specs[(b, s)] for b in bracos}, cfg, neutra, m_b,
                                                              cfg["rotulo_partidas"]) for s in ovos]):
                por_ovo[str(s)] = painel
                n += k
            tempos[f"painel_{nome}_s"] = time.perf_counter() - t1
            res[nome] = por_ovo
            _gravar(saida / f"partidas_{nome}.json", _dump({"variante": nome, "por_ovo": por_ovo}))
            print(f"  painel {nome}: {n} partidas em {tempos[f'painel_{nome}_s']:.0f} s", flush=True)
    analise = analisar(res, pets, bracos, cfg.get("estilos"), carregar_personas(cfg))
    fontes = ("experiments/run_educacao.py", "digilab/educacao.py", "digilab/donos_educacao.py", "digilab/config.py",
              "digilab/evolucao.py", "digilab/combate_v2/v21/catalogo.py", "digilab/combate_v2/v21/regras.py")
    meta = {"plano": "docs/PLANO_ANALISE_V3.md", "config": cfg, "ovos": ovos, "M_B_por_bot": m_b, "fumaca": a.fumaca,
            "hash_parametros_educacao": hash_parametros_educacao(), "tempos": tempos,
            "fontes_sha256": hashlib.sha256(b"".join((RAIZ / p).read_bytes().replace(b"\r\n", b"\n") for p in fontes)).hexdigest(),
            "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()}}
    _gravar(saida / "meta.json", _dump(meta))
    _gravar(saida / "resultado.json", _dump(analise))
    n = analise["neutra"]
    for k, c in n["comparacoes"].items():
        print(f"  {k}: {c['estimativa']:+.4f} [{c['ic95'][0]:+.4f}, {c['ic95'][1]:+.4f}] p={c['p_bootstrap']:.4f} {c['leitura']}")
    print("  gate equilibrio (neutra):", "APROVADO" if n["gate_equilibrio"]["aprovado"] else "REPROVADO",
          {e: round(v, 3) for e, v in n["gate_equilibrio"]["medias_estilos"].items()})
    for b, d in analise["mecanismo"].items():
        print(f"  {b}: mortes {d['mortes']}/{d['n']}, adulto {d['qualificados_adulto']}, sparring "
              f"{d['taxa_sparring_media'] if d['taxa_sparring_media'] is None else round(d['taxa_sparring_media'], 3)}, "
              f"disciplina {d['disciplina_final_media']:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
