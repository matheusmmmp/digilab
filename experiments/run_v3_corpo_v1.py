"""CORPO V1-a, o teto baixo no pet do jogo (docs/PLANO_ANALISE_V3_CORPO_V1.md, APROVADO pelo Matheus em 2026-11-21, D-V1A-1 a D-V1A-9).

Pergunta (secao 1): no pet v38, o DTB ainda faz o pet passar mais tempo bem, sem perder saude nem forrageio?

Os bracos (secao 2): o CTRL38 (o pet v38 de hoje) e o DTB38 (o mesmo pet com a ponte da D e o teto em C/2). No `medidas.json` os
bracos se chamam CTRL e DTB, como na C4: o pet e que muda. O pet v38 e o da PET_VIVO (`experiments/pv2.py`, `fabricas(..., v38=True)`:
os inatos do E1, o sono que segura, o lance do dono, o equilibrio do cuidado e o estagio de bebe), montado aqui no motor da sonda da C3
para a analise da C4 ter as mesmas medidas. So o bloco I: as 12 celulas x 200 unidades (D-V1A-3); os pares ficam fora (D-V1A-4).
Este orquestrador e proprio para o `run_v3_corpo_c4.py` e o `pv2.py` ficarem intactos; as pecas vem de la.

A analise (secao 6): a regra da C4 sem o S2. A primaria e o "Tempo bem" (dias 1 a 14), DTB - CTRL, nas 12 celulas e nas 11 distintas;
as guardas sao a saude (12 celulas e as 6 do relapso e do aleatorio), a taxa por episodio no `longe_fixo` e o "Tempo bem" por lugar; a
saude por celula nao reprova, mas vira ressalva. As premissas da secao 5.2 deixam a medida "inconclusiva por premissa". O descritivo
ganha a fome (medida na propria run), a fracao das vidas com o "Tempo bem" acima de 0,99 e os numeros da C4 ao lado.

As conferencias de cada vida (secao 8): o replay, o T-CENARIO-1, as do mecanismo, as da memoria e as do corpo do braco. A conferencia do
reflexo da C3 (`conferir_conserto`) nao serve ao pet v38 (exige os inatos da bancada e o sono que segura desligado): aqui o cerebro e
conferido pelas chaves do pet v38, nos dois bracos.

A trava (secao 0): sem o "APROVADO pelo Matheus" no cabecalho do plano, sem a faixa em FAIXAS_RESERVADAS, com a pasta de saida ja
existente ou fora das bases do plano, o orquestrador recusa; a run passa antes pelo `tools/pre_run.py` e confere o disco. A fumaca usa as
sementes dos testes.

Uso: python experiments/run_v3_corpo_v1.py --config experiments/configs/v3_corpo_v1/run.json --processos 4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import pre_run  # noqa: E402
import pv2  # noqa: E402
import run_v3_corpo_c4 as C4  # noqa: E402
import run_v3_corpo_c4_fome as FO  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import CONFIG_LANCE_DONO_LIGADA, CONFIG_PADRAO, CONFIG_SONO_SEGURA_LIGADA, inatos_e1  # noqa: E402
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402

C3, TB = C4.C3, C4.TB
C2, orq, ma, lr, V, CA = C3.C2, C3.orq, C3.ma, C3.lr, C3.V, C3.CA
PLANO = "docs/PLANO_ANALISE_V3_CORPO_V1.md"
ORQUESTRADOR = "experiments/run_v3_corpo_v1.py"
FASE = "corpo_v1a"
PREFIXO = C3.PREFIXO
FAIXA = (109001, 109200)                                      # secao 4, D-V1A-8
BASES = tuple(range(109001, 109201))                          # 200 sementes independentes
K_POR_BASE = 1
DIAS, ORCAMENTO_POR_DIA = C3.DIAS, C3.ORCAMENTO_POR_DIA
SAIDA = "artifacts_v3_corpo/v1a"                              # secao 7
MAX_PROCESSOS = C3.MAX_PROCESSOS
CONTROLE, TRATADO, BRACOS = C4.CONTROLE, C4.TRATADO, C4.BRACOS
CELULAS, CELULAS_DISTINTAS, CELULAS_SEM_COMIDA = C4.CELULAS, C4.CELULAS_DISTINTAS, C4.CELULAS_SEM_COMIDA
PRIMARIO, LUGARES = C4.PRIMARIO, C4.LUGARES
MARGEM, ALFA = C4.MARGEM, C4.ALFA                             # 0,032 (SEM FONTE) e 0,025 unilateral: os da C4, sem mudar (D-V1A-5)
EPISODIO, SAUDE, PRIVACAO, EXAUSTAO, TEMPO_BEM, CHUTES = C4.EPISODIO, C4.SAUDE, C4.PRIVACAO, C4.EXAUSTAO, C4.TEMPO_BEM, C4.CHUTES
CHAVES_CONFIG = {"descricao", "fase", "plano", "dias", "orcamento_por_dia", "unidades"}
PISO_DISCO_GB = C4.PISO_DISCO_GB                              # secao 4, SEM FONTE
# os pisos das premissas (secao 5.2, D-V1A-6): os da C4, sem o da janela dos pares; todos SEM FONTE
PISOS = {k: v for k, v in C4.PISOS.items() if k != "pares_com_a_janela_min"}
CORTE_PERTO_DO_TETO = 0.99                                    # so descritivo (secao 5.2): o "Tempo bem" perto de 1; SEM FONTE
INATOS_V38 = inatos_e1()
S = orq.CONFIG_DIGIBRAIN_INATOS.escala
PROXIMO = ("confirma libera a V1-b; confirma com ressalva volta ao Matheus com a celula; "
           "nao confirma ou indeterminado fica registrado, a V1 para e o pet do jogo fica como esta")


# ================================================================== as vidas
def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int) -> tuple:
    """(a fabrica do cerebro, a do motor) do pet v38 da PET_VIVO (`pv2.fabricas(..., v38=True)`), no motor da sonda da C3, com as chaves
    do corpo do braco. No CTRL a vida e, byte a byte, a do `pv2.viver("HOJE", ..., v38=True)` (teste)."""
    m = C3.montar(braco)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, C3.VC.gl.BRACO_V11, semente))
    cd = orq.config_do_braco("REL", None, True)

    def fp(cfg=None):
        registro = orq.Registro(DigiBrain(cfg or CONFIG_PADRAO, cd, orq.CM, semente=semente, inatos=INATOS_V38,
                                          cfg_sono=CONFIG_SONO_SEGURA_LIGADA, cfg_lance=CONFIG_LANCE_DONO_LIGADA,
                                          cfg_equilibrio=pv2.EQUILIBRIO_V38, cfg_conserto=m["conserto"]), S)
        pv2.bebe_pelas_decisoes(orq.cerebro_de(registro))     # na fabrica, para o replay ter o mesmo bebe (como no pv2)
        return registro

    def fm(politica, cfg, s):
        return C3.SA.MotorSonda(politica, cfg, s, C3.NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc,
                                cfg_lance_dono=CONFIG_LANCE_DONO_LIGADA, **C3._kw_corpo(m))

    return fp, fm


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int):
    """uma vida do pet v38 com as chaves do braco; como o `C3.viver`, le as categorias da memoria e a energia baixa de cada decisao,
    sem mudar a vida"""
    fp, fm = fabricas(braco, dono, semente, dias, orcamento_por_dia)
    registro = fp(CONFIG_PADRAO)
    c, categorias = orq.cerebro_de(registro), ma.Categorias()
    agir, reflexo = c.agir, c.m.arb.reflexo
    baixas: list[bool] = []

    def agir_e_ler(obs, rng):
        acao = agir(obs, rng)
        for e in c.m.mem.recente:
            categorias.setdefault(e["id"], list(e["categoria"]))
        return acao

    def reflexo_e_ler(sens, urgencias=None):
        baixas.append(sens["leitura"]["energia"] < c.inatos.lambda_sono)
        return reflexo(sens, urgencias)

    c.agir, c.m.arb.reflexo = agir_e_ler, reflexo_e_ler
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    c.agir, c.m.arb.reflexo = agir, reflexo
    return motor, registro, (fp, fm), categorias, baixas


def conferir_vida(braco: str, motor, registro, baixas: list[bool]) -> None:
    """secao 8: o corpo tem as chaves do braco e o cerebro e o do pet v38, nos dois bracos (falha alta). Troca a `conferir_conserto` da
    C3, que exige os inatos da bancada e o sono que segura desligado."""
    c = orq.cerebro_de(registro)
    arb = c.m.arb
    C3.conferir_braco(braco, motor.corpo, arb)
    if braco != CONTROLE and (motor.contabil.acum["falta_combustivel"] or motor.contabil.ticks_falta):
        raise RuntimeError(f"{braco}: o cansaco subiu pela falta de combustivel com a D ligada")
    erros = [n for n, ok in (("os inatos do E1", c.inatos == INATOS_V38), ("o sono que segura ligado", arb.sono == CONFIG_SONO_SEGURA_LIGADA),
                             ("o lance no cerebro", c.cl == CONFIG_LANCE_DONO_LIGADA), ("o lance no motor", motor.cld == CONFIG_LANCE_DONO_LIGADA),
                             ("o equilibrio do cuidado", c.ceq == pv2.EQUILIBRIO_V38)) if not ok]
    if erros:
        raise RuntimeError(f"{braco}: o pet da vida nao e o v38 ({', '.join(erros)})")
    if len(baixas) != len(c.motivos):
        raise RuntimeError(f"{braco}: {len(baixas)} leituras do reflexo para {len(c.motivos)} decisoes")
    if arb.suaves != 0:
        raise RuntimeError(f"{braco}: o reflexo suave somou peso sem a chave")


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    """uma vida: a da C4 (`C4._vida`, as mesmas medidas) com o pet v38, a conferencia dele e a fome medida na propria run"""
    if braco not in BRACOS:
        raise ValueError(f"braco {braco!r}: so {BRACOS}")
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab, categorias, baixas = viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    texto = motor.log.para_jsonl()
    arquivo.write_text(texto, encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo("REL", registro, None)
    ma.conferir_memoria("REL", orq.cerebro_de(registro))
    fins = ma.conferir_fins("REL", registro)
    conferir_vida(braco, motor, registro, baixas)
    med = orq.medidas(motor, registro, "REL", cfg["dias"], True)
    dec = motor.decisoes_mundo
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins,
            "memoria": ma.medidas_memoria(registro, cfg["dias"], categorias),
            "valuation": V.descritivo_valuation(registro, med), "acoplamento": CA.medidas_acoplamento(motor, registro, baixas),
            **C3.medidas_c3(motor, registro, cfg["dias"]),
            **TB.medidas_da_vida(registro.estados, passo, cfg["dias"]),
            **FO.fome_da_vida(registro.estados, passo, cfg["dias"]),
            "chutes": sum(1 for d in dec if d["brincou_com_bola"]), "brincar": sum(1 for d in dec if d["acao"] == "brincar"),
            "descartado": motor.corpo.descartado_total, "log_sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== a analise (secao 6, escrita antes)
def guardas(registros: list[dict], base=CELULAS) -> dict:
    """as guardas vinculantes: as da C4 sem o S2 (D-V1A-4 e D-V1A-5). `base`: as 12 celulas, ou as 11 distintas na sensibilidade"""
    nome = "as 12 celulas" if base == CELULAS else f"as {len(base)} celulas"
    return {"saude_12_celulas": C3._guarda(registros, SAUDE, base, nome, TRATADO, "< 0"),
            "saude_sem_comida": C3._guarda(registros, SAUDE, tuple(c for c in base if c in CELULAS_SEM_COMIDA),
                                           "as celulas do relapso e do aleatorio", TRATADO, "< 0"),
            C4.G_TAXA: C3._guarda(registros, EPISODIO, C3._celulas(PRIMARIO, base), PRIMARIO, TRATADO, "< 0"),
            **{f"tempo_bem_{lugar}": C3._guarda(registros, TEMPO_BEM, C3._celulas(lugar, base), lugar, TRATADO, "< 0") for lugar in LUGARES}}


def premissas(registros: list[dict]) -> dict:
    """secao 5.2: as premissas da C4 sem a da janela dos pares, contra os mesmos pisos (D-V1A-6)"""
    return {n: p for n, p in C4.premissas(registros, []).items() if n != "janela_do_reencontro"}


def leitura(prim: dict, g: dict, celulas: dict, prem: dict) -> dict:
    """a tabela da secao 6: a da C4 (`C4.leitura`), com o que cada leitura faz na V1 (secao 9)"""
    return {**C4.leitura(prim, g, celulas, prem), "proximo": PROXIMO}


FOME_MEDIA = lambda r: r["fome_media"]                        # noqa: E731
FOME_ACIMA = lambda r: r["fome_acima_do_teto"]                # noqa: E731
PERTO_DO_TETO = lambda r: float(r["tempo_bem"] > CORTE_PERTO_DO_TETO)   # noqa: E731
DESCRITIVOS = {**C4.DESCRITIVOS, "fome_media": FOME_MEDIA, "fome_acima_do_teto": FOME_ACIMA, "tempo_bem_perto_do_teto": PERTO_DO_TETO}
POR_DONO = {**C4.POR_DONO, "tempo_bem_8_14": C4.TEMPO_BEM_8_14, "fome_media": FOME_MEDIA, "fome_acima_do_teto": FOME_ACIMA,
            "tempo_bem_perto_do_teto": PERTO_DO_TETO}


def comparacao_com_a_c4() -> dict | None:
    """os numeros da C4 (o pet da bancada), para irem ao lado dos do pet v38. Sementes e pets diferentes: o par nao e um contraste. None
    sem o artefato"""
    r = RAIZ / "artifacts_v3_corpo" / "c4" / "resultado.json"
    if not r.exists():
        return None
    c4 = json.loads(r.read_text(encoding="utf-8"))
    so = lambda x: {k: x[k] for k in ("media", "ic95")}       # noqa: E731
    return {"fontes_sha256": {"c4/resultado.json": bv._sha(r)},
            "primaria": {n: {**so(v), "niveis": v["niveis"]} for n, v in c4["primaria"].items()},
            "guardas": {n: so(v) for n, v in c4["guardas"].items() if n != C4.G_S2},
            "saude_por_celula": {n: so(v) for n, v in c4["saude_por_celula"].items()},
            "as_oito_guardas_da_c3": {n: so(v) for n, v in c4["descritivo"]["as_oito_guardas_da_c3"].items()}}


def descritivo(registros: list[dict]) -> dict:
    """secao 6, sem teste: por lugar, por dono, as guardas da C3, os chutes, as 11 celulas, o incoerente e a C4 ao lado"""
    grupos = (("12_celulas", CELULAS), ("11_celulas", CELULAS_DISTINTAS), *((lugar, C3._celulas(lugar)) for lugar in LUGARES))
    idx = {(r["braco"], r["dono"], r["lugar"], r["semente"]): r["log_sha256"] for r in registros}
    sementes = sorted({r["semente"] for r in registros})
    return {"por_lugar": {onde: {n: C4._descr(registros, f, cs) for n, f in DESCRITIVOS.items()} for onde, cs in grupos},
            "por_dono": {f"{d}|{lugar}": {n: C4._descr(registros, f, ((d, lugar),)) for n, f in POR_DONO.items()} for d, lugar in CELULAS},
            "as_oito_guardas_da_c3": {n: {k: v for k, v in x.items() if k not in ("passa", "reprova_com")}
                                      for n, x in C3.guardas_b(registros, TRATADO).items()},
            "chutes": {lugar: {**C4._descr(registros, CHUTES, C3._celulas(lugar)),
                               "fracao_vidas_com_chute": {b: C4._media([float(r["chutes"] > 0) for r in registros
                                                                        if r["braco"] == b and r["lugar"] == lugar]) for b in BRACOS}}
                       for lugar in LUGARES},
            "guardas_11_celulas": {n: {k: x[k] for k in ("media", "ic95", "classe", "passa")}
                                   for n, x in guardas(registros, CELULAS_DISTINTAS).items()},
            "incoerente_igual_ao_atencioso": {f"{b}|{lugar}": {"vidas": len(sementes), "iguais": sum(
                1 for s in sementes if idx[(b, "atencioso", lugar, s)] == idx[(b, "incoerente", lugar, s)])} for b in BRACOS for lugar in LUGARES},
            "comparacao_com_a_c4": comparacao_com_a_c4()}


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    prim, g, cel, prem = C4.primaria(registros, boot), guardas(registros), C4.saude_por_celula(registros), premissas(registros)
    return {"primaria": prim, "guardas": g, "saude_por_celula": cel, "premissas": prem, "veredito": leitura(prim, g, cel, prem),
            "descritivo": descritivo(registros),
            "nao_demonstra": ["nada sobre o jogo web (a chave fica desligada nele)",
                              "nada sobre o pet v38 com a TV, a ilha grande e a memoria de 128 celulas: o pet e o v38 do Python (D-V1A-2)",
                              "nada sobre outro teto alem de C/2", "nada sobre os pares e o social: o bloco II ficou fora (D-V1A-4)"]}


# ================================================================== a trava e a run
def modo_da_config(cfg: dict) -> str:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA:
        raise ValueError("config fora do plano: o prefixo ou o orcamento (secao 3)")
    if type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError(f"config: o K {u.get('k')!r}")
    bases = tuple(u["bases"])
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano("bases fora do plano: so as dos testes (fumaca) ou as da secao 4")
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA} nao esta em FAIXAS_RESERVADAS (secao 4)")
    CA.exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    erros = [m for m, ok in ((f"dias {cfg['dias']} (o plano: {DIAS})", cfg["dias"] == DIAS),
                             (f"plano {cfg.get('plano')!r}", cfg.get("plano") == PLANO),
                             (f"K {u['k']} (o plano: {K_POR_BASE})", u["k"] == K_POR_BASE)) if not ok]
    if erros:
        raise ValueError(f"a run segue o plano a letra: {erros}")
    return FASE


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; secao 4)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None,
            "python": platform.python_version(), "node": V._versao_node(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "orquestrador_c4_sha256": rc._sha_arquivo(Path(C4.__file__)),
            "orquestrador_c3_sha256": rc._sha_arquivo(Path(C3.__file__)), "pv2_sha256": rc._sha_arquivo(Path(pv2.__file__)),
            "tempo_bem_sha256": rc._sha_arquivo(Path(TB.__file__)), "fome_sha256": rc._sha_arquivo(Path(FO.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS],
            "bracos": {b: {k: vars(v) for k, v in C3.montar(b).items()} for b in BRACOS},
            "pet": {"inatos": "inatos_e1()", "sono_segura": vars(CONFIG_SONO_SEGURA_LIGADA), "lance_dono": vars(CONFIG_LANCE_DONO_LIGADA),
                    "equilibrio": vars(pv2.EQUILIBRIO_V38), "bebe": "pv2.bebe_pelas_decisoes"},
            "faixa": list(FAIXA), "pisos": PISOS, "margem": MARGEM, "alfa": ALFA, "corte_perto_do_teto": CORTE_PERTO_DO_TETO,
            "limiar_fome": FO.LIMIAR_FOME, "disco_livre_gb": shutil.disk_usage(pasta).free / 2**30,
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "corpo.py", "motor_corpo.py", "engine.py", "metrics.py",
                                                                         "mundo.py")}
            | {f"digibrain/{q.name}": rc._sha_arquivo(q) for q in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    if len(registros) != len(unidades) * len(BRACOS) * len(CELULAS):
        raise RuntimeError(f"{len(registros)} vidas, eram {len(unidades) * len(BRACOS) * len(CELULAS)}")
    registros.sort(key=lambda r: r["vida"])
    custos = {r["vida"]: r.pop("custo") for r in registros}            # o relogio fora do medidas.json, como na C4
    bv._gravar(pasta / "medidas.json", bv._dump(registros))
    bv._gravar(pasta / "custos.json", bv._dump(custos))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos), **analisar(lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    V.tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    meta["pasta_crua_apagada"] = {"vidas": C4.conferir_e_apagar(pasta / "vidas", pasta / "vidas.tar.gz")}
    nomes = ["medidas.json", "custos.json", "resultado.json", "vidas.tar.gz"]
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in nomes}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _resumo(r: dict) -> str:
    """o resumo no console, ASCII puro"""
    return json.dumps({"modo": r["modo"], "vidas": r["vidas"], "veredito": r["veredito"],
                       "primaria": {k: {c: v[c] for c in ("media", "ic95", "p_unilateral")} for k, v in r["primaria"].items()}},
                      indent=1, ensure_ascii=True, default=str)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    if modo_da_config(cfg) == "fumaca":
        if a.saida is None:
            raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    else:
        pre_run.exigir(ORQUESTRADOR, a.config, a.processos)             # o plano da origin/main e a V3-D8, antes de tudo
        livre = shutil.disk_usage(RAIZ).free / 2**30
        if livre < PISO_DISCO_GB:
            raise SystemExit(f"so {livre:.1f} GB livres no disco: o piso e {PISO_DISCO_GB} GB (secao 4)")
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]))


if __name__ == "__main__":
    main()
