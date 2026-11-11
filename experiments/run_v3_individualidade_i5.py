"""O orquestrador do I5 da INDIVIDUALIDADE: o habito como medida (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I5.md, APROVADO em 2026-11-09).

Nenhuma vida nova (IH-1): cada vida do I2 (os bracos REL e REL+F, os donos atencioso, relapso e aleatorio, IH-2) sai do log do
`artifacts_v3_individualidade/vidas.tar.gz` e e rejogada. O log refeito tem de ser o do disco (o G1, de novo), e o `decisoes_mundo` tem de
ter 96 decisoes por dia. Os perfis de cada dia (SEQ, LUGAR e HORA) e a distintividade de cada pet saem de `digilab/metrics.py` (IH-7). A
analise (secao 4 do plano): o H_dono e o H_mundo por braco e por perfil, com o IC95 bootstrap sobre as sementes, nos dias 8 a 14; o
descritivo por dono, os dias 1 a 7, o D_braco, a regiao e os dias fora. Descritiva: nao ha gate.

A trava (secoes 0 e 8 do plano): a analise de pesquisa so roda com o cabecalho do plano "APROVADO pelo Matheus", a secao do registro da
analise no plano (secao 9), o `vidas.tar.gz` do I2, as bases e o K do I2, no maximo 4 processos e nada por cima de uma pasta. A fumaca (as
sementes dos testes, 101...505) vive as proprias vidas (a `viver` da C4, sem a bateria), empacota-as como o I2 e segue o mesmo caminho.

    python experiments/run_v3_individualidade_i5.py --config experiments/configs/v3_individualidade/individualidade_i5.json --processos 4
"""
from __future__ import annotations

import argparse
import io
import json
import platform
import random
import sys
import tarfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import run_v3_individualidade as ri  # noqa: E402
from digilab import metrics as M  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I5.md"
MARCA_APROVADO = ri.MARCA_APROVADO
TITULO_REGISTRO = "## 11. O registro da análise"                                      # secao 9 do plano: a secao nova no fim
FASE = "individualidade-i5"
VIDAS_I2 = f"{ri.SAIDA}/vidas.tar.gz"                                                 # IH-1
BASES, K_POR_BASE, PREFIXO, LUGAR = ri.BASES, ri.K_POR_BASE, ri.PREFIXO, ri.LUGAR     # as do I2 (secao 0)
BRACOS = ri.BRACOS                                                                    # secao 2
DONOS = ("atencioso", "relapso", "aleatorio")                                         # IH-2 (D-IND-I2c-2): o incoerente sai
DIAS, ORCAMENTO_POR_DIA = ri.DIAS, ri.ORCAMENTO_POR_DIA                               # os do I2: 14 dias, 16 por dia
DECISOES_POR_DIA = 96                                                                 # secao 0: TICKS_POR_DIA / 15
PRIMEIRO_DIA_JANELA, ULTIMO_DIA_JANELA = 8, 14                                        # IH-5 (a JANELA_8_14)
MAX_PROCESSOS = ri.MAX_PROCESSOS                                                      # V3-D8
BOOTSTRAP = 2000                                                                      # secao 4.3
MEDIDAS = ("D_si", "D_dono", "D_mundo", "H_dono", "H_mundo")
COM_IC = ("H_dono", "H_mundo")                                                        # secao 4.3: o IC95 do H
SAIDA = "artifacts_v3_individualidade_i5"
CHAVES_CONFIG = {"descricao", "fase", "plano", "vidas", "unidades", "dias", "orcamento_por_dia"}


# ================================================================== a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_plano_aprovado(texto: str) -> None:
    """o cabecalho do plano tem a marca "APROVADO pelo Matheus" e a secao do registro da analise existe (uma vez)"""
    linhas = texto.splitlines()
    status = next((x for x in linhas[1:12] if x.startswith("**Status:")), None)
    if status is None or not status.startswith(MARCA_APROVADO):
        raise RuntimeError("o plano do I5 sem o status APROVADO pelo Matheus no cabecalho: nenhuma vida rejogada")
    if sum(1 for x in linhas if x.startswith(TITULO_REGISTRO)) != 1:
        raise RuntimeError(f"o plano do I5 sem a secao {TITULO_REGISTRO!r} (o registro da analise, secao 9): nenhuma vida rejogada")


def modo_da_config(cfg: dict, texto_plano: str | None = None) -> str:
    """'fumaca' (as sementes dos testes, as vidas feitas aqui) ou 'individualidade-i5' (as vidas do I2; a trava); o resto falha alto"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento ou o K")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not PRIMEIRO_DIA_JANELA <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de {PRIMEIRO_DIA_JANELA} a {DIAS} (a janela comeca no dia 8)")
        if cfg["vidas"] is not None:
            raise ValueError("a fumaca vive as proprias vidas: `vidas` e null")
        if len(bases) * u["k"] < 2:
            raise ValueError("a fumaca precisa de ao menos duas sementes (o D_dono)")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou as do I2 {list(BASES)} (IH-1)")
    exigir_plano_aprovado(_plano() if texto_plano is None else texto_plano)
    erros = [f"dias {cfg['dias']}"] if cfg["dias"] != DIAS else []
    erros += [f"K {u['k']}"] if u["k"] != K_POR_BASE else []
    erros += [f"plano {cfg.get('plano')!r}"] if cfg.get("plano") != PLANO else []
    erros += [f"vidas {cfg.get('vidas')!r}"] if cfg.get("vidas") != VIDAS_I2 else []
    if erros:
        raise ValueError(f"a analise segue o plano a letra: {erros}")
    return FASE


# ================================================================== as vidas
def nome_da_vida(braco: str, dono: str, semente: int) -> str:
    """o caminho da vida no `vidas.tar.gz` do I2 (o `_vida` do run_v3_individualidade)"""
    return f"vidas/{braco}/{dono}_{LUGAR}_{semente}.jsonl"


def fabricas_vida(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int) -> tuple:
    """as fabricas (do cerebro, do motor) da `viver` da C4 (run_v2_memoria_autobio.viver), sem o coletor das categorias; o replay de cada
    vida confere, pelo log, que sao as mesmas"""
    fp, _ = orq.fabricas(braco, dono, semente, dias, orcamento_por_dia, conserto=True)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, ma.gl.BRACO_V11, semente))

    def fm(politica, cfg, s):                                           # a mesma da `viver` da C4
        return ma.lr.MotorGravaCorpo(politica, cfg, s, ma.NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    return fp, fm


def ler_vidas(caminho: Path, esperadas: list[tuple[str, str, int]]) -> dict[tuple[str, str, int], str]:
    """o texto do log de cada vida esperada, do tar.gz; falha alto se uma falta ou se aparece uma vida de dono, braco ou semente fora"""
    with tarfile.open(caminho, "r:gz") as tar:
        membros = {m.name: m for m in tar.getmembers() if m.isfile() and m.name.endswith(".jsonl")}
        pedidos = {nome_da_vida(*e): e for e in esperadas}
        faltam = sorted(set(pedidos) - set(membros))
        if faltam:
            raise RuntimeError(f"{len(faltam)} vidas faltam no {caminho.name}: {faltam[:3]}")
        permitidas = set(pedidos) | {nome_da_vida(b, "incoerente", s) for b, _, s in esperadas}   # o incoerente do I2 fica no pacote
        estranhas = sorted(set(membros) - permitidas)
        if estranhas:
            raise RuntimeError(f"vidas fora do plano no {caminho.name}: {estranhas[:3]}")
        return {e: tar.extractfile(membros[n]).read().decode("utf-8") for n, e in pedidos.items()}


def decisoes_por_dia(decisoes: list[dict], dias: int) -> list[int]:
    return [sum(1 for d in decisoes if (dia - 1) * M.TICKS_POR_DIA <= d["tick"] < dia * M.TICKS_POR_DIA) for dia in range(1, dias + 1)]


def rejogar(braco: str, dono: str, unidade: dict, texto: str, dias: int, orcamento_por_dia: int) -> dict:
    """uma vida: o replay do log, o G1 (o log refeito e o do disco), as 96 decisoes por dia, os perfis de cada dia e a regiao"""
    p0 = time.perf_counter()
    semente = unidade["semente"]
    fp, fm = fabricas_vida(braco, dono, semente, dias, orcamento_por_dia)
    motor = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm)
    if motor.log.para_jsonl() != texto:
        raise bv.ReplayDivergiu(f"{braco}|{dono}|{semente}: o log rejogado nao e o do disco")
    decisoes = motor.decisoes_mundo
    n_dia = decisoes_por_dia(decisoes, dias)
    if n_dia != [DECISOES_POR_DIA] * dias or len(decisoes) != DECISOES_POR_DIA * dias:
        raise RuntimeError(f"{braco}|{dono}|{semente}: as decisoes por dia nao sao {DECISOES_POR_DIA}: {n_dia}")
    perfis = {dia: M.perfis_habito_dia(decisoes, dia) for dia in range(1, dias + 1)}
    nomes = [r[0] for r in motor.cmf.layout.regioes]                   # 0 casa, 1 jardim, 2 campo, 3 mata (`mundo.regiao_de`)
    regiao = {}
    for d in decisoes:
        if d["acao"] != "dormir":
            dia, nome = d["tick"] // M.TICKS_POR_DIA + 1, nomes[d["regiao"]]
            regiao.setdefault(dia, {}).setdefault(nome, 0)
            regiao[dia][nome] += 1
    return {"vida": f"{braco}|{dono}|{LUGAR}|{semente}", "braco": braco, "dono": dono, "semente": semente, "base": unidade["base"],
            "k": unidade["k"], "perfis": perfis, "regiao": regiao, "custo": {"vida_parede": time.perf_counter() - p0}}


def tarefa(lote: list[tuple], dias: int, orcamento_por_dia: int) -> list[dict]:
    return [rejogar(b, d, u, texto, dias, orcamento_por_dia) for b, d, u, texto in lote]


def viver_fumaca(cfg: dict, unidades: list[dict], destino: Path) -> None:
    """a fumaca: as vidas da C4 (sem a bateria, que nao muda o log: o G2 do I2) com as sementes dos testes, num tar.gz como o do I2"""
    with tarfile.open(destino, "w:gz") as tar:
        for u in unidades:
            for b in BRACOS:
                for d in DONOS:
                    motor, *_ = ma.viver(b, d, LUGAR, u["semente"], cfg["dias"], cfg["orcamento_por_dia"])
                    dados = motor.log.para_jsonl().encode("utf-8")
                    info = tarfile.TarInfo(nome_da_vida(b, d, u["semente"]))
                    info.size = len(dados)
                    tar.addfile(info, io.BytesIO(dados))


# ================================================================== a analise
def _dias(primeiro: int, ultimo: int) -> list[int]:
    return list(range(primeiro, ultimo + 1))


def _perfil(registro: dict, perfil: str) -> dict:
    return {int(dia): (None if p is None else p[perfil]) for dia, p in registro["perfis"].items()}


def distintividades(registros: list[dict], braco: str, perfil: str, dias: list[int]) -> list[dict]:
    """a distintividade (4.2) e o D_braco (4.4) de cada pet do braco, num perfil e nos dias dados"""
    por = {(r["braco"], r["dono"], r["semente"]): _perfil(r, perfil) for r in registros}
    outro_braco = next(b for b in BRACOS if b != braco)
    saida = []
    for r in sorted((r for r in registros if r["braco"] == braco), key=lambda r: (r["dono"], r["semente"])):
        dono, s = r["dono"], r["semente"]
        do_dono = [p for (b, d, s2), p in sorted(por.items()) if b == braco and d == dono and s2 != s]
        do_mundo = [p for (b, d, s2), p in sorted(por.items()) if b == braco and s2 == s and d != dono]
        proprio = por[(braco, dono, s)]
        x = M.distintividade_habito(proprio, do_dono, do_mundo, dias)
        x["D_braco"] = M.distancia_mesmo_dia(proprio, [por[(outro_braco, dono, s)]], dias)
        saida.append({"dono": dono, "semente": s, **x})
    return saida


def ic_sementes(pets: list[dict], medida: str, boot: int, rotulo: tuple) -> list[float] | None:
    """o IC95 percentil da media da medida sobre os pets, reamostrando as sementes (a semente leva os tres donos juntos)"""
    sementes = sorted({p["semente"] for p in pets})
    por_semente = {s: [p[medida] for p in pets if p["semente"] == s and p[medida] is not None] for s in sementes}
    rng = random.Random(derivar_semente("individualidade-i5-boot", *rotulo))
    medias = []
    for _ in range(boot):
        vs = [v for s in (rng.choice(sementes) for _ in sementes) for v in por_semente[s]]
        if vs:
            medias.append(sum(vs) / len(vs))
    ic = ri._percentis(medias)
    return None if ic is None else list(ic)


def frase(ic: list[float] | None, alem: str) -> str:
    """6.2: as frases que a leitura pode escrever"""
    if ic is not None and ic[0] > 0:
        return f"o pet tem habito proprio alem {alem}"
    return "nao se distingue de zero nesta analise"


def _resumo(pets: list[dict]) -> dict:
    return {m: M.media_habito([p[m] for p in pets]) for m in MEDIDAS + ("D_braco",)}


def analisar(registros: list[dict], dias_vida: int, boot: int = BOOTSTRAP) -> dict:
    janela = _dias(PRIMEIRO_DIA_JANELA, min(ULTIMO_DIA_JANELA, dias_vida))
    cedo = _dias(1, PRIMEIRO_DIA_JANELA - 1)
    out = {"janela": [janela[0], janela[-1]], "dias_cedo": [cedo[0], cedo[-1]], "bootstrap": boot, "por_braco": {}}
    for braco in BRACOS:
        do_braco = [r for r in registros if r["braco"] == braco]
        b = out["por_braco"][braco] = {"por_perfil": {}, "dias_fora": {}, "regiao": {}}
        for perfil in M.PERFIS_HABITO:
            pets = distintividades(registros, braco, perfil, janela)
            x = {"medias": _resumo(pets), "ic95": {m: ic_sementes(pets, m, boot, (braco, perfil, m)) for m in COM_IC}}
            x["frases"] = {"H_dono": frase(x["ic95"]["H_dono"], "do dono"), "H_mundo": frase(x["ic95"]["H_mundo"], "do mundo da semente")}
            x["por_dono"] = {d: _resumo([p for p in pets if p["dono"] == d]) for d in DONOS}
            x["dias_1_7"] = _resumo(distintividades(registros, braco, perfil, cedo))
            b["por_perfil"][perfil] = x
        for nome, dias in (("janela", janela), ("dias_1_7", cedo)):
            b["dias_fora"][nome] = {d: sum(1 for r in do_braco if r["dono"] == d for dia in dias if r["perfis"][str(dia)] is None)
                                    for d in DONOS}
        for d in DONOS:
            conta: dict[str, int] = {}
            for r in do_braco:
                if r["dono"] == d:
                    for dia in janela:
                        for reg, n in r["regiao"].get(str(dia), {}).items():
                            conta[reg] = conta.get(reg, 0) + n
            total = sum(conta.values())
            b["regiao"][d] = {reg: n / total for reg, n in sorted(conta.items())} if total else {}
    return out


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None, boot: int = BOOTSTRAP) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a analise se recusa a gravar por cima")
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
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py")},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    esperadas = [(b, d, u["semente"]) for u in unidades for b in BRACOS for d in DONOS]
    textos = ler_vidas(vidas, esperadas)
    lotes = [[(b, d, u, textos[(b, d, u["semente"])]) for b in BRACOS for d in DONOS] for u in unidades]
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (lote, cfg["dias"], cfg["orcamento_por_dia"])) for lote in lotes], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    if len(registros) != len(esperadas):
        raise RuntimeError(f"{len(registros)} vidas rejogadas, eram {len(esperadas)}")
    registros = sorted(registros, key=lambda r: r["vida"])
    with (pasta / "perfis.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in registros:
            for dia in range(1, cfg["dias"] + 1):
                p = r["perfis"][dia]
                for perfil in M.PERFIS_HABITO:
                    f.write(json.dumps({"braco": r["braco"], "dono": r["dono"], "semente": r["semente"], "base": r["base"], "k": r["k"],
                                        "dia": dia, "perfil": perfil, "contagens": None if p is None else p[perfil],
                                        "regiao": r["regiao"].get(dia, {})}, sort_keys=True) + "\n")
    lidos = _ler_perfis(pasta / "perfis.jsonl", registros)       # a analise sai do artefato gravado
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "vidas": len(lidos), **analisar(lidos, cfg["dias"], boot)}
    bv._gravar(pasta / "analise.json", bv._dump(resultado))
    custos = [r["custo"]["vida_parede"] for r in registros]
    bv._gravar(pasta / "custo.json", bv._dump({"vidas": len(custos), "parede_media_s": sum(custos) / len(custos), "parede_max_s": max(custos),
                                               "total_parede_s": meta["vidas_parede_s"]}))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("perfis.jsonl", "analise.json", "custo.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _ler_perfis(caminho: Path, registros: list[dict]) -> list[dict]:
    """as vidas refeitas do `perfis.jsonl` (as chaves de dia viram texto, como num json lido do disco); confere contra os registros"""
    vidas: dict[tuple, dict] = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        x = json.loads(linha)
        v = vidas.setdefault((x["braco"], x["dono"], x["semente"]), {"braco": x["braco"], "dono": x["dono"], "semente": x["semente"],
                                                                       "perfis": {}, "regiao": {}})
        dia = str(x["dia"])
        if x["contagens"] is None:
            v["perfis"][dia] = None
        else:
            if v["perfis"].get(dia, {}) is None:
                raise RuntimeError(f"perfis.jsonl: o dia {dia} fora num perfil e dentro noutro")
            v["perfis"].setdefault(dia, {})[x["perfil"]] = x["contagens"]
        v["regiao"][dia] = x["regiao"]
    if len(vidas) != len(registros):
        raise RuntimeError(f"perfis.jsonl com {len(vidas)} vidas, eram {len(registros)}")
    for r in registros:
        v = vidas[(r["braco"], r["dono"], r["semente"])]
        if v["perfis"] != {str(d): p for d, p in r["perfis"].items()}:
            raise RuntimeError(f"{r['vida']}: o perfis.jsonl nao e o que a vida deu")
    return list(vidas.values())


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
    print(json.dumps({"modo": res["modo"], "vidas": res["vidas"], "custo_medio_s": r["meta"]["vidas_parede_s"] / res["vidas"],
                      "H": {b: {p: {m: x["medias"][m]["media"] for m in COM_IC} for p, x in v["por_perfil"].items()}
                            for b, v in res["por_braco"].items()}}, indent=1, ensure_ascii=True))


if __name__ == "__main__":
    main()
