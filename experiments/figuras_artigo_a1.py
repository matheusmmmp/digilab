"""Figuras e tabelas do artigo A1 (testes causais pre-registrados no cerebro modular), etapa A1-4.

Le SO os artefatos que ja estao no git (nenhuma vida nova) e gera:
- a tabela 1 (a serie T0 a T6), em CSV e em Markdown;
- a tabela 2 (o protocolo por teste), em CSV e em Markdown;
- a figura 2 (a floresta dos efeitos com IC95), a figura 3 (a C4) e a figura 4 (a decomposicao da D-C1-3);
- o `figuras_artigo_a1_proveniencia.json`: cada numero ligado ao arquivo do artefato, ao campo dentro dele e ao sha256 do arquivo.

Regras:
- nenhum numero digitado a mao: todo valor vem de um artefato (`Prov.pegar`) ou e derivado de valores que vieram (`Prov.derivar`);
- as metricas ficam em `digilab/metrics.py`; aqui so se leem resultados prontos;
- o matplotlib so e usado aqui, em `experiments/` (o pacote `digilab/` segue so com a biblioteca padrao);
- os textos das figuras e das tabelas vao em ingles (D-ART-4); nenhum sprite nem asset do jogo entra;
- a conferencia com os `docs/RESULTADO_*.md`: cada numero da tabela 1 e formatado como o relato o escreve e procurado no texto dos
  documentos; o que nao aparece sai em `conferencia_com_os_resultados` como "nao_bateu", sem ser corrigido.

Uso:
  python experiments/figuras_artigo_a1.py [--saida artifacts_artigo_a1] [--vault <pasta>] [--sem-figuras]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
V2 = "artifacts_v2_digibrain_prototipo"
AN = "artifacts_v3_acoes_novas"
VAULT_PADRAO = Path(r"C:\Users\mathe\Documents\DigiLab Research\60 Artigos\A1 — testes causais\figuras")
SAIDA_PADRAO = "artifacts_artigo_a1"
PROVENIENCIA = "figuras_artigo_a1_proveniencia.json"

# Os documentos onde os numeros do plano aparecem escritos (a conferencia automatica, so leitura).
DOCS_RESULTADO = (
    "docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md",
    "docs/RESULTADO_V3_ACOES_NOVAS.md",
)


# ----------------------------------------------------------------------------------------------------------------------
# leitura dos artefatos e proveniencia
# ----------------------------------------------------------------------------------------------------------------------
def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def ler_json(caminho: Path):
    if caminho.suffix == ".gz":
        with gzip.open(caminho, "rt", encoding="utf-8") as f:
            return json.load(f)
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def seguir(obj, campo: str):
    """Segue um ponteiro estilo JSON ('/a/b/0') dentro do objeto lido."""
    for parte in [p for p in campo.split("/") if p != ""]:
        obj = obj[int(parte)] if isinstance(obj, list) else obj[parte]
    return obj


class Prov:
    """Le valores dos artefatos e guarda de onde cada um veio."""

    def __init__(self, raiz: Path):
        self.raiz = raiz
        self._json: dict[str, object] = {}
        self._sha: dict[str, str] = {}
        self.entradas: dict[str, dict] = {}

    def _abrir(self, rel: str):
        if rel not in self._json:
            caminho = self.raiz / rel
            self._json[rel] = ler_json(caminho)
            self._sha[rel] = sha256_arquivo(caminho)
        return self._json[rel]

    def sha(self, rel: str) -> str:
        self._abrir(rel)
        return self._sha[rel]

    def pegar(self, ident: str, rel: str, campo: str):
        valor = seguir(self._abrir(rel), campo)
        assert ident not in self.entradas, ident
        self.entradas[ident] = {"id": ident, "valor": valor, "arquivo": rel, "campo": campo, "sha256": self._sha[rel]}
        return valor

    def derivar(self, ident: str, valor, de: list[str], formula: str):
        assert ident not in self.entradas, ident
        self.entradas[ident] = {"id": ident, "valor": valor, "derivado_de": de, "formula": formula}
        return valor


def classe_curta(texto: str | None) -> str:
    """'> 0', '< 0', '≈ 0' ou 'indeterminado' (alguns artefatos trazem o '≈' com a codificacao quebrada)."""
    if texto is None:
        return "n/a"
    if "indeterminado" in texto:
        return "indeterminate"
    if "<" in texto:
        return "negative"
    if ">" in texto:
        return "positive"
    return "null (about 0)"


def pt(x: float, casas: int, sinal: bool = False) -> str:
    """Formata como o relato: virgula decimal; com sinal explicito se pedido."""
    s = f"{abs(x):.{casas}f}".replace(".", ",")
    if x < 0 and float(f"{abs(x):.{casas}f}") != 0:
        return "-" + s
    return ("+" + s) if sinal else s


# ----------------------------------------------------------------------------------------------------------------------
# tabela 1: a serie T0 a T6
# ----------------------------------------------------------------------------------------------------------------------
def tabela1(p: Prov) -> list[dict]:
    linhas: list[dict] = []

    def linha(**k):
        linhas.append(k)

    # T0: o protótipo inteiro, G-MVP (avaliacao unica)
    a = f"{V2}/avaliacao/resultado.json"
    m = p.pegar("T0.efeito", a, "/G-MVP/media")
    lo = p.pegar("T0.ic_inf", a, "/G-MVP/ic95/ic_inferior")
    hi = p.pegar("T0.ic_sup", a, "/G-MVP/ic95/ic_superior")
    lim = p.pegar("T0.limiar", a, "/G-MVP/limiar")
    passa = p.pegar("T0.passa", a, "/G-MVP/passa")
    linha(id="T0", intervention="Whole prototype: chain food -> body (G-MVP)", contrast="fraction of M3 lives with closure rate >= 0.5, vs limit",
          measure="fraction of lives", effect=m, ci_low=lo, ci_high=hi, reference=lim, casas=3, scale="level",
          reading=("passes" if passa else "fails") + f" (lower limit >= {lim})", cls="positive" if passa else "negative", ids="T0")

    # T1: a intencao suspensa no cochilo (L-2): C-L2-1
    a = f"{V2}/l2/avaliacao/resultado.json"
    dif = p.pegar("T1.efeito", a, "/criterios/C-L2-1/diferenca")
    lo = p.pegar("T1.ic_inf", a, "/criterios/C-L2-1/ic95/ic_inferior")
    hi = p.pegar("T1.ic_sup", a, "/criterios/C-L2-1/ic95/ic_superior")
    ma = p.pegar("T1.media_a", a, "/criterios/C-L2-1/media_a")
    mb = p.pegar("T1.media_b", a, "/criterios/C-L2-1/media_b")
    passa = p.pegar("T1.passa", a, "/criterios/C-L2-1/passa")
    exigido = p.pegar("T1.queda_exigida", a, "/criterios/limiares/C-L2-1")
    queda = p.derivar("T1.queda_relativa", dif / ma, ["T1.efeito", "T1.media_a"], "diferenca / media_a (M3*+S - M3*, sobre o M3*)")
    exig_abs = p.derivar("T1.diferenca_exigida", -exigido * ma, ["T1.queda_exigida", "T1.media_a"], "-(queda exigida) * media_a: a diferenca que a regra pede")
    linha(id="T1", intervention="Intention suspended during a nap (L-2)", contrast="M3*+S minus M3*, far world (C-L2-1)",
          measure="searches switched or expired per life", effect=dif, ci_low=lo, ci_high=hi, reference=exig_abs, casas=2, scale="count",
          reading=f"criterion {'met' if passa else 'not met'}: change of {queda*100:.0f}% vs {-exigido*100:.0f}% required", cls="negative" if not passa else "positive",
          ids="T1", extra={"queda_relativa": queda})

    # T2 a T6: as runs confirmatorias, com o IC95 pelo t sobre as unidades
    def run(ident, interv, contr, rel, caminho, medida, casas):
        efeito = p.pegar(f"{ident}.efeito", rel, f"{caminho}/media")
        lo = p.pegar(f"{ident}.ic_inf", rel, f"{caminho}/ic95/ic_inferior")
        hi = p.pegar(f"{ident}.ic_sup", rel, f"{caminho}/ic95/ic_superior")
        cl = p.pegar(f"{ident}.classe", rel, f"{caminho}/classe/classe")
        return efeito, lo, hi, classe_curta(cl)

    rel = f"{V2}/longe_regular/run/resultado.json"
    e, lo, hi, cl = run("T2", "", "", rel, "/primario", "", 4)
    passa2 = p.pegar("T2.passa", rel, "/primario/passa")
    linha(id="T2", intervention="Fixed places with memory (C1)", contrast="M3* minus M2, fixed far world (primary)",
          measure="closure rate per episode", effect=e, ci_low=lo, ci_high=hi, reference=None, casas=4, scale="rate", reading=f"{cl}; {'passes' if passa2 else 'does not pass'}", cls=cl, ids="T2")
    e2, lo2, hi2, cl2 = run("T2s", "", "", rel, "/sorteado", "", 4)
    linha(id="T2s", intervention="(same, randomized far world)", contrast="M3* minus M2, randomized far world",
          measure="closure rate per episode", effect=e2, ci_low=lo2, ci_high=hi2, reference=None, casas=4, scale="rate", reading=cl2, cls=cl2, ids="T2s")

    rel = f"{V2}/habito_intencao/run/resultado.json"
    e, lo, hi, cl = run("T3", "", "", rel, "/primario", "", 4)
    linha(id="T3", intervention="Credit in the behaviour run (C2)", contrast="M2c minus M2 (primary P-A)",
          measure="'won, stays' index of the day", effect=e, ci_low=lo, ci_high=hi, reference=None, casas=4, scale="rate", reading=cl, cls=cl, ids="T3")

    rel = f"{V2}/redecidir_evento/run/resultado.json"
    e, lo, hi, cl = run("T4", "", "", rel, "/primario", "", 4)
    linha(id="T4", intervention="Re-decide only on events (C3)", contrast="M3*R minus M3*, fixed far world (primary P-R)",
          measure="closure rate per episode", effect=e, ci_low=lo, ci_high=hi, reference=None, casas=4, scale="rate", reading=cl, cls=cl, ids="T4")

    rel = f"{V2}/memoria_autobio/run/resultado.json"
    for suf, nome, chave in (("sem", "SEM", "REL - SEM"), ("rec", "REC", "REL - REC"), ("emb", "EMB", "REL - EMB")):
        e, lo, hi, cl = run(f"T5{suf}", "", "", rel, f"/primario/{chave}", "", 4)
        padj = p.pegar(f"T5{suf}.holm_p_ajustado", rel, f"/primario/{chave}/holm/p_ajustado")
        rej = p.pegar(f"T5{suf}.holm_rejeita", rel, f"/primario/{chave}/holm/rejeita")
        linha(id=f"T5{suf}", intervention="Autobiographical memory (C4)" if suf == "sem" else "(same)",
              contrast=f"REL minus {nome}, fixed far world", measure="closure rate per episode", effect=e, ci_low=lo, ci_high=hi,
              reference=None, casas=4, scale="rate", reading=f"{cl}; Holm {'rejects' if rej else 'does not reject'}", cls=cl, ids=f"T5{suf}",
              extra={"holm_p_ajustado": padj})
    e, lo, hi, cl = run("T5s", "", "", rel, "/secundarias/SEM-SORTEADO", "", 4)
    linha(id="T5s", intervention="(same, randomized far world)", contrast="REL minus SEM, randomized far world",
          measure="closure rate per episode", effect=e, ci_low=lo, ci_high=hi, reference=None, casas=4, scale="rate", reading=cl, cls=cl, ids="T5s")

    rel = f"{AN}/run/resultado.json"
    e, lo, hi, cl = run("T6", "", "", rel, "/guarda", "", 4)
    falha = p.pegar("T6.falha", rel, "/guarda/falha")
    linha(id="T6", intervention="Walk, a new action (AN4)", contrast="LAB+P minus LAB, feeding-place guard",
          measure="closure rate per episode", effect=e, ci_low=lo, ci_high=hi, reference=None, casas=4, scale="rate",
          reading=f"{cl}; guard {'fails' if falha else 'holds'}", cls=cl, ids="T6")
    return linhas


def conferir_com_os_resultados(p: Prov, linhas: list[dict], raiz: Path) -> dict:
    """Procura cada numero da tabela 1, formatado como o relato o escreve, no texto dos RESULTADO_*."""
    textos = {}
    for rel in DOCS_RESULTADO:
        t = (raiz / rel).read_text(encoding="utf-8")
        textos[rel] = (t.replace("\u2212", "-").replace("\\*", "").replace("*", ""), sha256_arquivo(raiz / rel))
    saida: dict[str, dict] = {}
    for l in linhas:
        casas = l["casas"]
        sinal = l["scale"] != "level"
        partes = {
            "efeito": pt(l["effect"], casas, sinal),
            "ic_inf": pt(l["ci_low"], casas, sinal),
            "ic_sup": pt(l["ci_high"], casas, sinal),
        }
        resp = {"formatado": partes, "intervalo_junto_em": None, "numeros_soltos_em": None}
        junto = f"{partes['efeito']} [{partes['ic_inf']}; {partes['ic_sup']}]"
        for rel, (t, sha) in textos.items():
            if junto in t:
                resp["intervalo_junto_em"] = {"arquivo": rel, "sha256": sha}
                break
        if resp["intervalo_junto_em"] is None:
            for rel, (t, sha) in textos.items():
                if all(v in t for v in partes.values()):
                    resp["numeros_soltos_em"] = {"arquivo": rel, "sha256": sha}
                    break
        resp["resultado"] = "bateu" if (resp["intervalo_junto_em"] or resp["numeros_soltos_em"]) else "nao_bateu"
        saida[l["id"]] = resp
    return saida


def gravar_tabela1(linhas: list[dict], conf: dict, saida: Path) -> None:
    campos = ["test", "intervention", "contrast", "measure", "effect", "ci95_low", "ci95_high", "reference", "reading", "provenance_ids"]
    with open(saida / "tabela1_serie_T0_T6.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(campos)
        for l in linhas:
            c = l["casas"]
            w.writerow([l["id"], l["intervention"], l["contrast"], l["measure"], f"{l['effect']:.{c}f}", f"{l['ci_low']:.{c}f}",
                        f"{l['ci_high']:.{c}f}", "" if l["reference"] is None else f"{l['reference']:.{c}f}", l["reading"], l["ids"]])
    md = ["| test | intervention | contrast | measure | effect [95% CI] | reading |", "|---|---|---|---|---|---|"]
    for l in linhas:
        c = l["casas"]
        sg = "+" if l["scale"] != "level" else ""
        ef = f"{l['effect']:{sg}.{c}f} [{l['ci_low']:{sg}.{c}f}; {l['ci_high']:{sg}.{c}f}]".replace("-", "\u2212")
        md.append(f"| {l['id'].replace('T2s','T2 (rand.)').replace('T5s','T5 (rand.)').replace('T5sem','T5 vs SEM').replace('T5rec','T5 vs REC').replace('T5emb','T5 vs EMB')}"
                  f" | {l['intervention']} | {l['contrast']} | {l['measure']} | {ef} | {l['reading']} |")
    md += ["", "Effects are differences in the stated measure; 95% CI by the t on the units (A4.4.6). T0 is a level (fraction of lives), not a",
           "difference: its reference is the pre-registered lower limit. T1 is a count of searches per life. Every number comes from the",
           "artifact listed in `figuras_artigo_a1_proveniencia.json` (file, field, sha256)."]
    (saida / "tabela1_serie_T0_T6.md").write_text("\n".join(md) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------------------------------------------------
# tabela 2: o protocolo por teste
# ----------------------------------------------------------------------------------------------------------------------
# So caminhos e nomes; os valores (bases, K, datas, sha) saem dos artefatos.
PROTOCOLO = (
    {"id": "T0", "meta": f"{V2}/avaliacao/meta.json", "resultado": f"{V2}/avaliacao/resultado.json",
     "calibracao_dirs": [f"{V2}/calibracao", f"{V2}/conserto/calibracao"], "calibracao_arquivos": []},
    {"id": "T1", "meta": f"{V2}/l2/avaliacao/meta.json", "resultado": f"{V2}/l2/avaliacao/resultado.json",
     "calibracao_dirs": [f"{V2}/l2/piloto"], "calibracao_arquivos": [f"{V2}/l2/poder.json", f"{V2}/l2/k_fixado.json"]},
    {"id": "T2", "meta": f"{V2}/longe_regular/run/meta.json", "resultado": f"{V2}/longe_regular/run/resultado.json",
     "calibracao_dirs": [], "calibracao_arquivos": [f"{V2}/longe_regular/adendo6_poder.json"]},
    {"id": "T3", "meta": f"{V2}/habito_intencao/run/meta.json", "resultado": f"{V2}/habito_intencao/run/resultado.json",
     "calibracao_dirs": [], "calibracao_arquivos": [f"{V2}/habito_intencao/adendo7_poder.json"]},
    {"id": "T4", "meta": f"{V2}/redecidir_evento/run/meta.json", "resultado": f"{V2}/redecidir_evento/run/resultado.json",
     "calibracao_dirs": [], "calibracao_arquivos": [f"{V2}/redecidir_evento/adendo8_poder.json"]},
    {"id": "T5", "meta": f"{V2}/memoria_autobio/run/meta.json", "resultado": f"{V2}/memoria_autobio/run/resultado.json",
     "calibracao_dirs": [], "calibracao_arquivos": [f"{V2}/memoria_autobio/adendo9_poder.json"]},
    {"id": "T6", "meta": f"{AN}/run/meta.json", "resultado": f"{AN}/run/resultado.json",
     "calibracao_dirs": [], "calibracao_arquivos": [f"{AN}/plano_an3_poder.json"]},
)


def commit_do_arquivo(raiz: Path, rel: str) -> str | None:
    """A data do primeiro commit que criou o arquivo (None se o git nao responde)."""
    try:
        r = subprocess.run(["git", "log", "--diff-filter=A", "--format=%cI", "--", rel], cwd=raiz, capture_output=True, text=True, timeout=120)
        datas = [d for d in r.stdout.split() if d]
        return datas[-1] if datas else None
    except Exception:
        return None


def antes_de(commit_iso: str | None, inicio_iso: str) -> bool | None:
    if commit_iso is None:
        return None
    c = datetime.fromisoformat(commit_iso)
    i = datetime.fromisoformat(inicio_iso)
    if i.tzinfo is None:
        i = i.astimezone()  # o meta grava a hora local da maquina que rodou
    return c < i


def tabela2(p: Prov, raiz: Path, usar_git: bool = True) -> list[dict]:
    linhas = []
    for t in PROTOCOLO:
        i = t["id"]
        meta = t["meta"]
        cfg = p.pegar(f"{i}.config_arquivo", meta, "/config_arquivo")
        bases = p.pegar(f"{i}.bases", meta, "/config/unidades/bases")
        k = p.pegar(f"{i}.k", meta, "/config/unidades/k")
        inicio = p.pegar(f"{i}.inicio", meta, "/inicio")
        fim = p.pegar(f"{i}.fim", meta, "/fim")
        head = p.pegar(f"{i}.git_head", meta, "/git_head")
        limpo = p.pegar(f"{i}.git_limpo", meta, "/git_limpo")
        procs = p.pegar(f"{i}.processos", meta, "/processos")
        plano = p.pegar(f"{i}.plano", meta, "/plano") if "plano" in ler_json(raiz / meta) else "docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md"
        plano_sha = p.pegar(f"{i}.plano_sha256", meta, "/plano_sha256")
        cfg_sha = p.pegar(f"{i}.config_sha256", meta, "/config_sha256")
        descr = seguir(p._abrir(meta), "/config/descricao")
        aprov = re.search(r"APROVADO pelo Matheus em (\d{4}-\d{2}-\d{2})", descr)
        cal = []
        for d in t["calibracao_dirs"]:
            for filho in sorted(x for x in (raiz / d).rglob("resultado.json")):
                cal.append(filho.relative_to(raiz).as_posix())
        cal += t["calibracao_arquivos"]
        cal_sha = {rel: p.sha(rel) for rel in cal}
        commit = commit_do_arquivo(raiz, cfg) if usar_git else None
        if t["id"] == "T0":
            vidas = None
        else:
            vidas = p.pegar(f"{i}.vidas", t["resultado"], "/vidas") if "vidas" in p._abrir(t["resultado"]) else None
        linhas.append({
            "id": i, "plano": plano, "plano_sha256": plano_sha, "config": cfg, "config_sha256": cfg_sha,
            "aprovacao_no_meta": aprov.group(1) if aprov else "not recorded in the run meta",
            "config_commit": commit, "config_antes_da_run": antes_de(commit, inicio),
            "bases": bases, "k_por_base": k, "vidas": vidas, "inicio": inicio, "fim": fim, "git_head": head, "git_limpo": limpo,
            "processos": procs, "calibracao": cal_sha,
        })
    return linhas


def gravar_tabela2(linhas: list[dict], saida: Path) -> None:
    campos = ["test", "plan_document", "plan_sha256", "config", "approval_in_run_meta", "config_first_commit", "config_committed_before_run",
              "seed_bases", "k_per_base", "lives", "run_start", "run_end", "git_head", "git_clean", "processes", "calibration_artifacts"]
    with open(saida / "tabela2_protocolo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(campos)
        for l in linhas:
            w.writerow([l["id"], l["plano"], l["plano_sha256"], l["config"], l["aprovacao_no_meta"], l["config_commit"] or "",
                        "" if l["config_antes_da_run"] is None else str(l["config_antes_da_run"]).lower(),
                        " ".join(str(b) for b in l["bases"]), l["k_por_base"], "" if l["vidas"] is None else l["vidas"], l["inicio"], l["fim"],
                        l["git_head"], str(l["git_limpo"]).lower(), l["processos"], ";".join(l["calibracao"])])
    md = ["| test | plan before the run | seed band (bases, K per base) | calibration / pilot artifacts | validation (single run) |", "|---|---|---|---|---|"]
    for l in linhas:
        antes = {True: "yes", False: "NO", None: "n/a"}[l["config_antes_da_run"]]
        cal = f"{len(l['calibracao'])} file(s)" if l["calibracao"] else "none on disk"
        md.append(f"| {l['id']} | `{Path(l['plano']).name}` (sha256 `{l['plano_sha256'][:8]}`); config `{Path(l['config']).name}` committed before the run: {antes};"
                  f" approval date in run meta: {l['aprovacao_no_meta']} | {', '.join(str(b) for b in l['bases'])}; K = {l['k_por_base']} | {cal} |"
                  f" {l['inicio'][:16]} to {l['fim'][:16]}; commit `{l['git_head'][:8]}`, clean tree: {'yes' if l['git_limpo'] else 'no'}; {l['processos']} processes |")
    md += ["", "Calibration / pilot = the `resultado.json` of calibration and pilot rounds, and the power / K files, found on disk for each test",
           "(T0: the three calibration rounds and the three repair rounds; T1: the pilot, the power file and the fixed K; T2 to T6: the power",
           "file of the addendum). Source of every field: the run `meta.json` (see the provenance file)."]
    (saida / "tabela2_protocolo.md").write_text("\n".join(md) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------------------------------------------------
# figuras (matplotlib so aqui)
# ----------------------------------------------------------------------------------------------------------------------
COR = {"positive": "#0072B2", "negative": "#D55E00", "null (about 0)": "#6E6E6E", "indeterminate": "#6E6E6E", "n/a": "#6E6E6E"}
MARC = {"positive": "o", "negative": "o", "null (about 0)": "s", "indeterminate": "D", "n/a": "s"}


def _estilo():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42, "figure.dpi": 100})
    return plt


def _salvar(fig, saida: Path, nome: str) -> list[str]:
    fig.savefig(saida / f"{nome}.png", dpi=300, bbox_inches="tight")
    fig.savefig(saida / f"{nome}.pdf", bbox_inches="tight")
    return [f"{nome}.png", f"{nome}.pdf"]


def figura2(linhas: list[dict], saida: Path) -> list[str]:
    plt = _estilo()
    por_id = {l["id"]: l for l in linhas}
    taxa = ["T2", "T2s", "T3", "T4", "T5sem", "T5s", "T6"]
    rot = {"T2": "T2 fixed places (M3* \u2212 M2)", "T2s": "T2 randomized places (M3* \u2212 M2)", "T3": "T3 credit in the run (M2c \u2212 M2)",
           "T4": "T4 re-decide on events (M3*R \u2212 M3*)", "T5sem": "T5 memory, fixed (REL \u2212 SEM)", "T5s": "T5 memory, randomized (REL \u2212 SEM)",
           "T6": "T6 walk, feeding guard (LAB+P \u2212 LAB)"}
    fig = plt.figure(figsize=(10.5, 4.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[3.2, 1.3, 1.3], wspace=0.75)
    ax = fig.add_subplot(gs[0])
    for y, i in enumerate(reversed(taxa)):
        l = por_id[i]
        ax.plot([l["ci_low"], l["ci_high"]], [y, y], color=COR[l["cls"]], lw=2)
        ax.plot(l["effect"], y, MARC[l["cls"]], color=COR[l["cls"]], ms=6)
    ax.axvline(0, color="black", lw=1)
    ax.set_yticks(range(len(taxa)))
    ax.set_yticklabels([rot[i] for i in reversed(taxa)])
    ax.set_xlabel("difference in closure rate per episode (95% CI)")
    ax.set_title("A  rate per episode", loc="left", fontsize=10)
    ax.tick_params(axis="y", length=0)

    ax = fig.add_subplot(gs[1])
    l = por_id["T1"]
    ax.plot([l["ci_low"], l["ci_high"]], [0, 0], color=COR[l["cls"]], lw=2)
    ax.plot(l["effect"], 0, "o", color=COR[l["cls"]], ms=6)
    ax.axvline(0, color="black", lw=1)
    ax.axvline(l["reference"], color="black", lw=1, ls="--")
    ax.text(l["reference"], 0.55, "required\ndrop", ha="center", va="bottom", fontsize=7)
    ax.set_yticks([0]); ax.set_yticklabels(["T1 suspended\nintention (S)"]); ax.tick_params(axis="y", length=0)
    ax.set_ylim(-1, 1)
    ax.set_xlabel("searches switched or\nexpired per life")
    ax.set_title("B  count per life", loc="left", fontsize=10)

    ax = fig.add_subplot(gs[2])
    l = por_id["T0"]
    ax.plot([l["ci_low"], l["ci_high"]], [0, 0], color=COR[l["cls"]], lw=2)
    ax.plot(l["effect"], 0, "o", color=COR[l["cls"]], ms=6)
    ax.axvline(l["reference"], color="black", lw=1, ls="--")
    ax.text(l["reference"], 0.55, "pre-registered\nlower limit", ha="center", va="bottom", fontsize=7)
    ax.set_xlim(0.4, 0.9); ax.set_ylim(-1, 1)
    ax.set_yticks([0]); ax.set_yticklabels(["T0 whole\nprototype"]); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("fraction of lives with\nclosure rate \u2265 0.5")
    ax.set_title("C  level vs limit", loc="left", fontsize=10)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", color=COR["positive"], lw=2, label="positive"), Line2D([], [], marker="o", color=COR["negative"], lw=2, label="negative / fails"),
         Line2D([], [], marker="s", color=COR["null (about 0)"], lw=2, label="null"), Line2D([], [], marker="D", color=COR["indeterminate"], lw=2, label="indeterminate")]
    fig.legend(handles=h, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.16))
    fig.suptitle("Figure 2. Effects of each pre-registered intervention with 95% CI (zero marked)", x=0.01, ha="left", fontsize=10)
    return _salvar(fig, saida, "figura2_floresta")


def figura3(linhas: list[dict], saida: Path) -> list[str]:
    plt = _estilo()
    por_id = {l["id"]: l for l in linhas}
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.1), gridspec_kw={"width_ratios": [1.5, 1], "wspace": 0.35})
    ax = axs[0]
    itens = [("T5sem", "REL \u2212 SEM (no memory)"), ("T5rec", "REL \u2212 REC (most recent episode)"), ("T5emb", "REL \u2212 EMB (shuffled episodes)")]
    for y, (i, r) in enumerate(reversed(itens)):
        l = por_id[i]
        ax.plot([l["ci_low"], l["ci_high"]], [y, y], color=COR["positive"], lw=2)
        ax.plot(l["effect"], y, "o", color=COR["positive"], ms=6)
    ax.axvline(0, color="black", lw=1)
    ax.set_yticks(range(3)); ax.set_yticklabels([r for _, r in reversed(itens)]); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("difference in closure rate per episode (95% CI)")
    ax.set_title("A  three contrasts, fixed far world (Holm)", loc="left", fontsize=10)
    ax = axs[1]
    for y, (i, r) in enumerate(reversed([("T5sem", "regular (fixed)"), ("T5s", "randomized")])):
        l = por_id[i]
        ax.plot([l["ci_low"], l["ci_high"]], [y, y], color=COR[l["cls"]], lw=2)
        ax.plot(l["effect"], y, "o", color=COR[l["cls"]], ms=6)
    ax.axvline(0, color="black", lw=1)
    ax.set_yticks(range(2)); ax.set_yticklabels(["randomized", "regular (fixed)"]); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("REL \u2212 SEM, rate per episode (95% CI)")
    ax.set_title("B  regular vs randomized world", loc="left", fontsize=10)
    fig.suptitle("Figure 3. C4, autobiographical memory: helps in the regular world, costs in the randomized one", x=0.01, y=1.08, ha="left", fontsize=10)
    return _salvar(fig, saida, "figura3_c4")


def decomposicao(p: Prov) -> dict:
    """H3 e H5 da D-C1-3, nos dois cerebros (o M3* da C1 e o REL da C4)."""
    c1 = f"{V2}/longe_regular/dc13/descritivo.json"
    c4 = f"{V2}/memoria_autobio/dc13/descritivo_rel.json"
    saida = {}
    for rotulo, rel, pref in (("C1", c1, "dc13c1"), ("C4", c4, "dc13c4")):
        for h in ("H3", "H5"):
            base = f"/leitura/partes/{h}"
            try:
                m = p.pegar(f"{pref}.{h}.media", rel, f"{base}/media")
                lo = p.pegar(f"{pref}.{h}.ic_inf", rel, f"{base}/ic95/ic_inferior")
                hi = p.pegar(f"{pref}.{h}.ic_sup", rel, f"{base}/ic95/ic_superior")
                cl = p.pegar(f"{pref}.{h}.classe", rel, f"{base}/classe")
                saida[(rotulo, h)] = (m, lo, hi, classe_curta(cl))
            except (KeyError, TypeError):
                saida[(rotulo, h)] = None
    return saida


def figura4(dec: dict, saida: Path) -> list[str]:
    plt = _estilo()
    fig, ax = plt.subplots(figsize=(7, 3.2))
    nomes = {"C1": "C1 brain (M3* − M2)", "C4": "C4 brain (REL − SEM)"}
    hs = {"H3": "H3 cost drop", "H5": "H5 recall decided"}
    linhas_y = [("H3", "C1", 3), ("H3", "C4", 2), ("H5", "C1", 1), ("H5", "C4", 0)]
    for h, rot, y in linhas_y:
        v = dec[(rot, h)]
        if v is None:
            ax.text(0.002, y, "not in the artifact (null)", ha="left", va="center", fontsize=8, style="italic", color="#6E6E6E")
            continue
        m, lo, hi, cl = v
        ax.plot([lo, hi], [y, y], color=COR[cl], lw=2)
        ax.plot(m, y, "o", color=COR[cl], ms=6)
    ax.axvline(0, color="black", lw=1)
    ax.set_yticks([y for _, _, y in linhas_y])
    ax.set_yticklabels([f"{hs[h]}: {nomes[r]}" for h, r, _ in linhas_y], fontsize=8)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("contribution to the closure-rate gain per episode (95% CI)")
    fig.suptitle("Figure 4. D-C1-3 decomposition of the gain, H3 and H5 in the two brains (post hoc, descriptive)", x=0.01, ha="left", fontsize=10)
    return _salvar(fig, saida, "figura4_dc13")


# ----------------------------------------------------------------------------------------------------------------------
def gerar(saida: Path, raiz: Path = RAIZ, figuras: bool = True, usar_git: bool = True) -> dict:
    saida.mkdir(parents=True, exist_ok=True)
    p = Prov(raiz)
    linhas = tabela1(p)
    conf = conferir_com_os_resultados(p, linhas, raiz)
    gravar_tabela1(linhas, conf, saida)
    t2 = tabela2(p, raiz, usar_git=usar_git)
    gravar_tabela2(t2, saida)
    dec = decomposicao(p)
    arquivos = ["tabela1_serie_T0_T6.csv", "tabela1_serie_T0_T6.md", "tabela2_protocolo.csv", "tabela2_protocolo.md"]
    if figuras:
        arquivos += figura2(linhas, saida) + figura3(linhas, saida) + figura4(dec, saida)
    lacunas = [f"{r}/{h}: o artefato nao traz a parcela (null)" for (r, h), v in dec.items() if v is None]
    lacunas += [f"{i}: nao bateu com os RESULTADO_*" for i, c in conf.items() if c["resultado"] == "nao_bateu"]
    doc = {
        "descricao": "Proveniencia das figuras e tabelas do artigo A1 (etapa A1-4): cada numero liga ao arquivo do artefato, ao campo e ao sha256.",
        "script": "experiments/figuras_artigo_a1.py",
        "tabela1_ids": [{"teste": l["id"], "casas": l["casas"], "ids": [f"{l['ids']}.efeito", f"{l['ids']}.ic_inf", f"{l['ids']}.ic_sup"]} for l in linhas],
        "entradas": list(p.entradas.values()),
        "conferencia_com_os_resultados": conf,
        "lacunas": lacunas,
        "arquivos_gerados": arquivos,
    }
    (saida / PROVENIENCIA).write_text(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    return doc


def copiar_para_o_vault(saida: Path, vault: Path, arquivos: list[str]) -> list[str]:
    """Copia so as figuras, os CSV e a proveniencia (as tabelas .md ficam so no repositorio: o vault nao ganha notas)."""
    copiados = []
    if not vault.is_dir():
        return copiados
    for nome in arquivos + [PROVENIENCIA]:
        if nome.endswith(".md"):
            continue
        shutil.copy2(saida / nome, vault / nome)
        copiados.append(nome)
    return copiados


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", default=SAIDA_PADRAO)
    ap.add_argument("--vault", default=str(VAULT_PADRAO))
    ap.add_argument("--sem-figuras", action="store_true")
    a = ap.parse_args(argv)
    saida = (RAIZ / a.saida) if not Path(a.saida).is_absolute() else Path(a.saida)
    doc = gerar(saida, figuras=not a.sem_figuras)
    print(f"{len(doc['entradas'])} entradas de proveniencia; arquivos: {', '.join(doc['arquivos_gerados'])}")
    for l in doc["lacunas"]:
        print("LACUNA:", l)
    if not a.sem_figuras:
        print("vault:", copiar_para_o_vault(saida, Path(a.vault), doc["arquivos_gerados"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
