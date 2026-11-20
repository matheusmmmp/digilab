"""E1 da linhagem: natureza x criacao (docs/PLANO_ANALISE_LINHAGEM.md, registrado antes da run).

    python experiments/run_natureza_criacao.py --rodada piloto
    python experiments/run_natureza_criacao.py --rodada especie_fixa --processos 16
    python experiments/run_natureza_criacao.py --rodada especies_balanceadas --processos 16

Separa a semente do GENOMA (g: especie e temperamento do ovo de evolucao.ovo(g), temperamento do motor de
temperamento.sortear(g)) da semente do AMBIENTE (r: engine, dono, travessuras, obediencia, lesoes, sparring), sem
mexer no engine.py: o genoma e injetado em simular_vida_educacao. Com g = r a vida e a da V3 (run_educacao._vida),
byte a byte (tests/test_natureza_criacao.py). Nenhuma mecanica nova.

1. Vidas: G genomas x D donos x R ambientes, uma por celula, a vida da V3 (educacao e lesoes ligadas, 14 dias,
   10 sparrings). Log gravado e rejogado DO DISCO.
2. Painel B, condicao neutra: 8 formas x 4 especies, 50 partidas por bot; sementes pela celula (g, r), iguais
   entre os donos. Morto conta 0.
3. Analise: metrics.decomposicao_cruzada (componentes de variancia) e bootstrap pigeonhole sobre genomas e
   ambientes (metrics.bootstrap_cruzado). Gate so na rodada especie_fixa: IC95 de sigma2_G acima de 0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.combate_v2.v21.bots import FORMAS, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import SOMBRIA_DA_LINHA, forma_adulta  # noqa: E402
from digilab.combate_v2.v21.partida import jogar  # noqa: E402
from digilab.config import CONFIG_CATALOGO, CONFIG_LESOES_LIGADA, CONFIG_PADRAO, ConfigArenaPesquisa  # noqa: E402
from digilab.donos_educacao import simular_vida_educacao  # noqa: E402
from digilab.educacao import politica_no_tick_educacao, reproduzir_educacao  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.evolucao import carater, ovo  # noqa: E402
from digilab.metrics import bootstrap_cruzado, componentes_cruzados, decomposicao_cruzada, ic_percentil  # noqa: E402
from digilab.protocol import (ENGINE_SHA256_V0, derivar_semente, hash_parametros_educacao, sha256_engine,  # noqa: E402
                              validar_parametros_educacao)
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino_vida import orcamento_treino  # noqa: E402
from run_educacao import SONDAS, T_ADUL, _fabricas, condicao_da_saude, lutador_painel, rival_por_nome, taxa, ticks_sparring  # noqa: E402
from run_poder import _dump, _gravar, regras_de  # noqa: E402

CFG_PADRAO = RAIZ / "experiments" / "configs" / "linhagem" / "natureza_criacao.json"
SAIDA_PADRAO = RAIZ / "artifacts_linhagem" / "natureza_criacao"
CONTRASTES = (("atencioso", "aleatorio"), ("atencioso", "permissivo"), ("atencioso", "relapso"), ("permissivo", "aleatorio"))


# ------------------------------------------------------------------ genoma
def especie_da_rodada(regra: str, indice: int) -> str | None:
    """'rodizio': especies_ativas[i % 4] (balanceadas); senao o nome da especie fixa."""
    ativas = CONFIG_CATALOGO.especies_ativas
    if regra == "rodizio":
        return ativas[indice % len(ativas)]
    if regra not in ativas:
        raise ValueError(f"especie desconhecida: {regra!r}")
    return regra


def genoma(g: int, especie: str | None = None) -> tuple[str, dict, object]:
    """(especie, temperamento do ovo, temperamento do motor) da semente do genoma; `especie` troca a do ovo."""
    esp, temp_ovo = ovo(g)
    return (especie or esp), temp_ovo, sortear(g)


# ------------------------------------------------------------------ 1. vidas
def vida_com_genoma(b: str, g: int, r: int, esp: str, temp_ovo: dict, tmp, dias: int, saida: str,
                    nome_arq: str) -> tuple[dict | None, dict]:
    """A vida da V3 (run_educacao._vida) com o genoma injetado e o ambiente pela semente r. (spec do painel, dados)."""
    fp, fm_base, _, pet = _fabricas(b, r, esp, tmp, temp_ovo)
    v = simular_vida_educacao(b, r, dias, esp, tmp, cl=CONFIG_LESOES_LIGADA, sparring=ticks_sparring(b),
                              rival_sparring=pet.rival, lutador_do_pet=pet.lutador, rival_por_nome=rival_por_nome)
    m = v.motor
    orc, _ = orcamento_treino(dias)
    if not v.morta and v.interacoes != orc:
        raise RuntimeError(f"{nome_arq}: {v.interacoes} interacoes, esperado {orc}")
    arq = Path(saida) / "vidas" / f"{nome_arq}.jsonl"
    _gravar(arq, m.log.para_jsonl())
    fp2, _, fm2, _ = _fabricas(b, r, esp, tmp, temp_ovo)
    rep = reproduzir_educacao(LogDeEventos.de_jsonl(arq.read_text(encoding="utf-8")), fp2, semente=r, fabrica_motor=fm2)
    if (rep.estado() != m.estado() or rep.resumo_educacao() != m.resumo_educacao() or rep.historico_lutas != m.historico_lutas
            or rep.vinculo.serie != m.vinculo.serie or rep.transicoes != m.transicoes):
        raise RuntimeError(f"replay de {nome_arq} divergiu")
    lutas = m.historico_lutas
    dados = {"dono": b, "genoma": g, "ambiente": r, "especie": esp, "morta": v.morta, "morte": m.morte,
             "sparring": {"lutas": len(lutas), "vitorias": sum(x["resultado"] == "vitoria" for x in lutas),
                          "lesoes": sum(x["lesao"] for x in lutas)},
             "adulto_liberado": m.adulto_liberado, "disciplina_final": m.disciplina,
             "saude_final": m.estado()["saude"], "vinculo_final": m.vinculo.valor, "sombria": bool(m.sombria),
             "treino_total": sum(m.treino.pontos.values())}
    spec = None
    if not v.morta:
        _, linha, ramo = pet._adolescente(m)
        pol = politica_no_tick_educacao(m.log, fp, r, T_ADUL, fm_base)
        car_adul, _ = carater(pol, fp(CONFIG_PADRAO), *SONDAS)
        if m.adulto_liberado:
            adulta = SOMBRIA_DA_LINHA[linha] if m.sombria else forma_adulta(linha, car_adul, len(lutas))
            forma = {"estagio": "adulto", "ramo": ramo, "linha": linha, "adulta": adulta}
        else:
            forma = {"estagio": "adolescente", "ramo": ramo, "linha": linha, "adulta": None}
        spec = {"forma": forma, "temp_ovo": temp_ovo, "carater": car_adul, "condicao": condicao_da_saude(m.estado()["saude"]),
                "pontos": dict(m.treino.pontos), "disciplina": m.disciplina, "especie": esp}
        dados["forma"] = forma
    return spec, dados


def chave(b: str, g: int, r: int) -> str:
    return f"{b}@g{g}r{r}"


def _vida(args):
    b, g, r, esp_regra, dias, saida = args
    t0 = time.perf_counter()
    esp, temp_ovo, tmp = genoma(g, esp_regra)
    spec, dados = vida_com_genoma(b, g, r, esp, temp_ovo, tmp, dias, saida, chave(b, g, r))
    return (b, g, r), spec, dados, time.perf_counter() - t0


# ------------------------------------------------------------------ 2. painel
def catalogo_do_painel(cfg: dict):
    """catalogo do pet no painel: o padrao, salvo `catalogo_painel.peso_carater_stats` = k na config
    (docs/PLANO_ANALISE_CANAL_DONO.md, Etapa B): os modificadores do carater nos stats multiplicados por k (inteiros
    vezes k, exatos). Fica fora da ConfigCatalogo e do catalogo.py, que entram nos hashes gravados das validacoes.
    A vida e os bots do painel usam sempre o padrao."""
    extra = cfg.get("catalogo_painel")
    if not extra:
        return None
    if set(extra) != {"peso_carater_stats"}:
        raise ValueError(f"catalogo_painel so aceita peso_carater_stats: {sorted(extra)}")
    k = float(extra["peso_carater_stats"])
    return replace(CONFIG_CATALOGO, carater={e: {s: m * k for s, m in mods.items()}
                                             for e, mods in CONFIG_CATALOGO.carater.items()})


def _painel_da_celula(args):
    g, r, specs, cfg, m_b, rotulo = args
    regras = regras_de(cfg)
    carena = ConfigArenaPesquisa(condicao_neutra=True)
    cat = catalogo_do_painel(cfg)
    lut = {b: (None if sp is None else lutador_painel(chave(b, g, r), sp, carena, regras.v21, cat)) for b, sp in specs.items()}
    painel, n = {}, 0
    for esp in CONFIG_CATALOGO.especies_ativas:
        for f in FORMAS:
            bot = lutador_adulto(f, esp, regras.v21, nome=f"painel:{f}@{esp}")
            for b, L in lut.items():
                pts = []
                for k in range(m_b):
                    if L is None:
                        pts.append(0.0)                       # morto nao luta
                        continue
                    sp = derivar_semente(f"{rotulo}|B|{g}:{r}", bot.nome, k)
                    pts.append(jogar(L, bot, sp, regras).pontos_a if k < m_b // 2 else 1.0 - jogar(bot, L, sp, regras).pontos_a)
                    n += 1
                painel.setdefault(b, {})[bot.nome] = pts
    return g, r, painel, n


# ------------------------------------------------------------------ 3. analise
def _estatisticas(donos: list[str]):
    idx = {d: j for j, d in enumerate(donos)}

    def est(y) -> dict:
        c = componentes_cruzados(y)
        out = {f"var_{k}": v for k, v in c["componentes"].items()}
        out.update({f"frac_{k}": v for k, v in c["fracao"].items()})
        for x, z in CONTRASTES:
            if x in idx and z in idx:
                vals = [yg[idx[x]][k] - yg[idx[z]][k] for yg in y for k in range(len(yg[0]))]
                out[f"{x}-{z}"] = sum(vals) / len(vals)
        return out
    return est


def analisar(Y: dict, pets: dict, donos: list[str], genomas: list[int], cfg_boot: dict, com_gate: bool) -> dict:
    dec = decomposicao_cruzada(Y)
    gs, ds, rs = dec["rotulos"]["G"], dec["rotulos"]["D"], dec["rotulos"]["R"]
    y = [[[Y[(g, d, r)] for r in rs] for d in ds] for g in gs]
    est = _estatisticas(ds)
    pontual = est(y)
    ics = {}
    for modo in ("GR", "G"):
        boots = bootstrap_cruzado(y, est, cfg_boot["reamostragens"], cfg_boot["semente"], reamostrar=modo)
        ics[modo] = {k: ic_percentil([b[k] for b in boots]) for k in pontual}
    out = {"estimativas": pontual, "ic95_pigeonhole_GR": ics["GR"], "ic95_so_genomas": ics["G"],
           "decomposicao": {k: dec[k] for k in ("componentes", "fracao", "ss", "gl", "qm", "ss_total", "media_geral",
                                                "media_por_dono", "niveis")}}
    if com_gate:
        lo = ics["GR"]["var_G"][0]
        out["gate"] = {"criterio": "limite inferior do IC95 pigeonhole de sigma2_G > 0",
                       "var_G": pontual["var_G"], "ic95": ics["GR"]["var_G"], "resultado": "PASSOU" if lo > 0 else "FALHOU"}
    # especie: soma de quadrados entre especies sobre as medias dos genomas (descritivo)
    esp_de = {}
    for d in pets.values():
        esp_de[d["genoma"]] = d["especie"]
    mg = {g: sum(Y[(g, d, r)] for d in ds for r in rs) / (len(ds) * len(rs)) for g in gs}
    media = sum(mg.values()) / len(mg)
    por_esp: dict = {}
    for g, v in mg.items():
        por_esp.setdefault(esp_de[g], []).append(v)
    ss_g = sum((v - media) ** 2 for v in mg.values())
    ss_e = sum(len(v) * (sum(v) / len(v) - media) ** 2 for v in por_esp.values())
    out["especie"] = {"media_por_especie": {e: sum(v) / len(v) for e, v in sorted(por_esp.items())},
                      "n_genomas_por_especie": {e: len(v) for e, v in sorted(por_esp.items())},
                      "fracao_da_variacao_entre_genomas": (ss_e / ss_g) if ss_g > 0 else 0.0}
    mec = {}
    for b in donos:
        xs = [d for d in pets.values() if d["dono"] == b]
        vivos = [d for d in xs if not d["morta"]]
        formas: dict = {}
        for d in vivos:
            k = d["forma"]["adulta"] or f"adolescente:{d['forma']['linha']}"
            formas[k] = formas.get(k, 0) + 1
        mec[b] = {"n": len(xs), "mortes": len(xs) - len(vivos), "qualificados_adulto": sum(bool(d["adulto_liberado"]) for d in vivos),
                  "sombrias": sum(d["sombria"] for d in vivos), "saude_final_media": sum(d["saude_final"] for d in xs) / len(xs),
                  "disciplina_final_media": sum(d["disciplina_final"] for d in xs) / len(xs), "formas": formas}
    out["mecanismo"] = mec
    return out


# ------------------------------------------------------------------ main
def rodar(nome: str, cfg: dict, saida: Path, processos: int) -> dict:
    rc = cfg["rodadas"][nome]
    genomas, ambientes, donos = list(rc["genomas"]), list(rc["ambientes"]), list(cfg["donos"])
    evitar = set(cfg["sementes_antigas_evitar"])
    if set(genomas) & set(ambientes) or (set(genomas) | set(ambientes)) & evitar:
        raise ValueError("sementes de genoma e de ambiente colidem entre si ou com runs antigas")
    if nome != "piloto" and set(genomas) & set(cfg["rodadas"]["piloto"]["genomas"]):
        raise ValueError("a validacao nao pode reusar sementes do piloto")
    m_b = cfg["M_B_por_bot"]
    if m_b % 2:
        raise ValueError("partidas por bot precisa ser par")
    esp_por_g = {g: especie_da_rodada(rc["especie"], i) for i, g in enumerate(genomas)}
    saida.mkdir(parents=True, exist_ok=True)
    tempos = {}
    with ProcessPoolExecutor(processos) as pool:
        t0 = time.perf_counter()
        vidas = list(pool.map(_vida, [(b, g, r, esp_por_g[g], cfg["dias"], str(saida))
                                      for g in genomas for r in ambientes for b in donos]))
        tempos["vidas_s"] = time.perf_counter() - t0
        specs = {k: sp for k, sp, _, _ in vidas}
        pets = {chave(*k): d for k, _, d, _ in vidas}
        _gravar(saida / "pets.json", _dump(pets))
        print(f"  [{nome}] {len(vidas)} vidas em {tempos['vidas_s']:.0f} s", flush=True)
        t1 = time.perf_counter()
        por_celula, n = {}, 0
        for g, r, painel, k in pool.map(_painel_da_celula, [(g, r, {b: specs[(b, g, r)] for b in donos}, cfg, m_b,
                                                               cfg["rotulo_partidas"]) for g in genomas for r in ambientes]):
            por_celula[f"{g}:{r}"] = painel
            n += k
        tempos["painel_s"] = time.perf_counter() - t1
        _gravar(saida / "partidas_neutra.json", _dump({"por_celula": por_celula}))
        print(f"  [{nome}] painel: {n} partidas em {tempos['painel_s']:.0f} s", flush=True)
    return concluir(nome, cfg, saida, genomas, ambientes, donos, esp_por_g, pets, por_celula, tempos)


def reanalisar(nome: str, cfg: dict, saida: Path, motivo: str) -> dict:
    """Refaz so a analise e o meta a partir do pets.json e do partidas_neutra.json ja gravados (nenhuma vida nem
    partida nova). Usado quando a run caiu depois do painel (motivo gravado no meta)."""
    rc = cfg["rodadas"][nome]
    genomas, ambientes, donos = list(rc["genomas"]), list(rc["ambientes"]), list(cfg["donos"])
    esp_por_g = {g: especie_da_rodada(rc["especie"], i) for i, g in enumerate(genomas)}
    pets = json.loads((saida / "pets.json").read_text(encoding="utf-8"))
    por_celula = json.loads((saida / "partidas_neutra.json").read_text(encoding="utf-8"))["por_celula"]
    esperado = {chave(b, g, r) for g in genomas for r in ambientes for b in donos}
    if set(pets) != esperado or set(por_celula) != {f"{g}:{r}" for g in genomas for r in ambientes}:
        raise ValueError("arquivos gravados nao batem com a rodada do config")
    if any(pets[chave(b, g, r)]["especie"] != esp_por_g[g] for g in genomas for r in ambientes for b in donos):
        raise ValueError("especie gravada diferente da regra da rodada")
    return concluir(nome, cfg, saida, genomas, ambientes, donos, esp_por_g, pets, por_celula, {"reanalise": motivo})


def concluir(nome, cfg, saida, genomas, ambientes, donos, esp_por_g, pets, por_celula, tempos) -> dict:
    Y = {(g, b, r): taxa(por_celula[f"{g}:{r}"][b]) for g in genomas for r in ambientes for b in donos}
    t2 = time.perf_counter()
    res = analisar(Y, pets, donos, genomas, cfg["bootstrap"], com_gate=(nome == "especie_fixa"))
    tempos["analise_s"] = time.perf_counter() - t2
    res["rodada"] = nome
    res["taxa_por_celula"] = {f"{g}|{b}|{r}": v for (g, b, r), v in sorted(Y.items())}
    fontes = ("experiments/run_natureza_criacao.py", "experiments/run_educacao.py", "digilab/metrics.py",
              "digilab/educacao.py", "digilab/donos_educacao.py", "digilab/config.py", "digilab/evolucao.py",
              "digilab/combate_v2/v21/catalogo.py", "digilab/combate_v2/v21/regras.py")
    meta = {"plano": cfg["plano"], "rodada": nome, "config": cfg, "especie_por_genoma": {str(g): e for g, e in esp_por_g.items()},
            "hash_parametros_educacao": hash_parametros_educacao(), "tempos": tempos,
            "fontes_sha256": hashlib.sha256(b"".join((RAIZ / p).read_bytes().replace(b"\r\n", b"\n") for p in fontes)).hexdigest(),
            "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()}}
    _gravar(saida / "meta.json", _dump(meta))
    _gravar(saida / "resultado.json", _dump(res))
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=str(CFG_PADRAO))
    ap.add_argument("--rodada", required=True, choices=("piloto", "especie_fixa", "especies_balanceadas"))
    ap.add_argument("--saida", default=None, help="padrao: artifacts_linhagem/natureza_criacao/<rodada>")
    ap.add_argument("--processos", type=int, default=None)
    ap.add_argument("--reanalisar", default=None, metavar="MOTIVO",
                    help="refaz so a analise a partir dos arquivos gravados (nenhuma vida nova); o motivo vai para o meta")
    a = ap.parse_args(argv)
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")
    validar_parametros_educacao()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    saida = Path(a.saida) if a.saida else SAIDA_PADRAO / a.rodada
    if a.reanalisar:
        res = reanalisar(a.rodada, cfg, saida, a.reanalisar)
    else:
        res = rodar(a.rodada, cfg, saida, a.processos or cfg["processos"])
    e, ic = res["estimativas"], res["ic95_pigeonhole_GR"]
    for k in ("var_G", "var_D", "var_R", "var_GD", "var_GR", "var_DR", "var_e"):
        print(f"  {k}: {e[k]:+.6f} [{ic[k][0]:+.6f}, {ic[k][1]:+.6f}]  fracao {e['frac_' + k[4:]]:.3f}")
    for x, z in CONTRASTES:
        k = f"{x}-{z}"
        print(f"  {k}: {e[k]:+.4f} [{ic[k][0]:+.4f}, {ic[k][1]:+.4f}]")
    if "gate" in res:
        print(f"  GATE: {res['gate']['resultado']} (sigma2_G {res['gate']['var_G']:+.6f}, IC95 {res['gate']['ic95']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
