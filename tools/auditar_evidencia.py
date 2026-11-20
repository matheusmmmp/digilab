"""Auditoria da evidência existente (fase A0): só leitura do git, sem vida nova.

Uso:
    python tools/auditar_evidencia.py <commit> <saida.json>

Para cada experimento com resultado registrado (C1, C2, C3, C4, AN4, GVN2,
PET_VIVO, COOP A1), lê do git, no <commit>:
- o meta (ou manifesto) da run: o SHA do código, se a árvore estava limpa, o
  Python, o Node, o comando;
- o plano: o primeiro commit em que o blob do plano tem o sha256 gravado no
  meta (com LF ou CRLF), e se esse commit é ancestral do código da run;
- os artefatos versionados: o sha256 do blob (e do conteúdo descomprimido de
  um .gz), comparado com o gravado no meta;
- os commits que puseram no git o meta e o documento de resultado.

Também lista todos os .gz em artifacts_*/ e os .py que citam o caminho de cada
um, e os meta.json em artifacts_*/ sem SHA do código. Sai igual byte a byte a
cada execução no mesmo commit. Falha alto se um caminho esperado não existir.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys

# Cada experimento: os caminhos no commit auditado. "plano_meta" diz de onde
# vem o sha256 do plano (a chave do meta); None quando o meta não o grava.
EXPERIMENTOS = [
    {
        "nome": "C1", "pergunta": "longe regular: M3* - M2 por episódio no longe_fixo",
        "meta": "artifacts_v2_digibrain_prototipo/longe_regular/run/meta.json",
        "plano": "docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md", "plano_meta": "plano_sha256",
        "resultado_doc": "docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md",
        "artefatos": {
            "resultado.json": "artifacts_v2_digibrain_prototipo/longe_regular/run/resultado.json",
            "medidas.json": "artifacts_v2_digibrain_prototipo/longe_regular/run/medidas.json",
        },
        "vidas": "artifacts_v2_digibrain_prototipo/longe_regular/run/vidas.tar.gz",
    },
    {
        "nome": "C2", "pergunta": "crédito na intenção: M2c - M2",
        "meta": "artifacts_v2_digibrain_prototipo/habito_intencao/run/meta.json",
        "plano": "docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md", "plano_meta": "plano_sha256",
        "resultado_doc": "docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md",
        "artefatos": {
            "resultado.json": "artifacts_v2_digibrain_prototipo/habito_intencao/run/resultado.json",
            "medidas.json": "artifacts_v2_digibrain_prototipo/habito_intencao/run/medidas.json",
        },
        "vidas": "artifacts_v2_digibrain_prototipo/habito_intencao/run/vidas.tar.gz",
    },
    {
        "nome": "C3", "pergunta": "redecidir por evento: M3*R - M3*",
        "meta": "artifacts_v2_digibrain_prototipo/redecidir_evento/run/meta.json",
        "plano": "docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md", "plano_meta": "plano_sha256",
        "resultado_doc": "docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md",
        "artefatos": {
            "resultado.json": "artifacts_v2_digibrain_prototipo/redecidir_evento/run/resultado.json",
            "medidas.json": "artifacts_v2_digibrain_prototipo/redecidir_evento/run/medidas.json",
        },
        "vidas": "artifacts_v2_digibrain_prototipo/redecidir_evento/run/vidas.tar.gz",
    },
    {
        "nome": "C4", "pergunta": "memória autobiográfica: REL - SEM, REL - REC, REL - EMB (Holm)",
        "meta": "artifacts_v2_digibrain_prototipo/memoria_autobio/run/meta.json",
        "plano": "docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md", "plano_meta": "plano_sha256",
        "resultado_doc": "docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md",
        "artefatos": {
            "resultado.json": "artifacts_v2_digibrain_prototipo/memoria_autobio/run/resultado.json",
            "medidas.json": "artifacts_v2_digibrain_prototipo/memoria_autobio/run/medidas.json.gz",
        },
        "vidas": "artifacts_v2_digibrain_prototipo/memoria_autobio/run/vidas.tar.gz",
    },
    {
        "nome": "AN4", "pergunta": "passeio: G-COMEDOURO-AN e MOV",
        "meta": "artifacts_v3_acoes_novas/run/meta.json",
        "plano": "docs/PLANO_ANALISE_V3_ACOES_NOVAS.md", "plano_meta": "plano_sha256",
        "resultado_doc": "docs/RESULTADO_V3_ACOES_NOVAS.md",
        "artefatos": {
            "resultado.json": "artifacts_v3_acoes_novas/run/resultado.json",
            "medidas.json": "artifacts_v3_acoes_novas/run/medidas.json",
        },
        "vidas": "artifacts_v3_acoes_novas/run/vidas.tar.gz",
    },
    {
        "nome": "GV3", "pergunta": "gosto visual (run base da GVN2)",
        "meta": "artifacts_v3_gosto_visual/gosto_visual/meta.json",
        "plano": "docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md", "plano_meta": "plano_sha256",
        "resultado_doc": "docs/RESULTADO_V3_GOSTO_VISUAL.md",
        "artefatos": {
            "analise.json": "artifacts_v3_gosto_visual/gosto_visual/analise.json",
            "medidas.json": "artifacts_v3_gosto_visual/gosto_visual/medidas.json",
        },
        "vidas": "artifacts_v3_gosto_visual/gosto_visual/vidas.tar.gz",
    },
    {
        "nome": "GV3b", "pergunta": "gosto visual com enjoo (run base da GVN2)",
        "meta": "artifacts_v3_gosto_visual/gosto_visual_enjoo2/meta.json",
        "plano": "docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO2.md", "plano_meta": "plano_sha256",
        "resultado_doc": "docs/RESULTADO_V3_GOSTO_VISUAL_ENJOO.md",
        "artefatos": {
            "analise.json": "artifacts_v3_gosto_visual/gosto_visual_enjoo2/analise.json",
            "medidas.json": "artifacts_v3_gosto_visual/gosto_visual_enjoo2/medidas.json",
        },
        "vidas": "artifacts_v3_gosto_visual/gosto_visual_enjoo2/vidas.tar.gz",
    },
    {
        "nome": "GVN2", "pergunta": "leitura descritiva das vidas da GV3 e da GV3b (Spearman Δ_I × dif_fica)",
        "meta": None,
        "plano": "docs/PLANO_ANALISE_V3_GOSTO_VISUAL_GVN2.md", "plano_meta": None,
        "resultado_doc": "docs/futuro/gosto_visual_porque_negativo.md",
        "artefatos": {
            "leitura.json": "artifacts_v3_gosto_visual/gvn2/leitura.json",
            "leitura.py": "artifacts_v3_gosto_visual/gvn2/leitura.py",
        },
        "vidas": None,
    },
    {
        "nome": "PET_VIVO", "pergunta": "auditoria da escolha (0b) e age pelo estado (0c), pós hoc",
        "meta": None,
        "plano": "docs/PLANO_ANALISE_V3_PET_VIVO.md", "plano_meta": None,
        "resultado_doc": "docs/RESULTADO_V3_PET_VIVO.md",
        "artefatos": {
            "auditoria.json": "artifacts_v3_pet_vivo/auditoria/auditoria.json",
            "auditoria_vidas.json.gz": "artifacts_v3_pet_vivo/auditoria/auditoria_vidas.json.gz",
        },
        "vidas": None,
    },
    {
        "nome": "COOP_A1", "pergunta": "cooperação, adendo 1: A1-EMERGE, A1-DOSE, A1-CUSTO",
        "meta": "artifacts_v3_cooperacao_bancada/manifesto_ad1.json",
        "plano": "docs/PLANO_ANALISE_V3_COOPERACAO.md", "plano_meta": None,
        "resultado_doc": "docs/futuro/cooperacao_bancada_resultado.md",
        "artefatos": {
            "resultado_ad1.json": "artifacts_v3_cooperacao_bancada/resultado_ad1.json",
        },
        "vidas": None,
    },
]


def git(*args: str, binario: bool = False):
    saida = subprocess.run(["git", *args], capture_output=True, check=True)
    return saida.stdout if binario else saida.stdout.decode("utf-8")


def blob(commit: str, caminho: str) -> bytes:
    try:
        return git("show", f"{commit}:{caminho}", binario=True)
    except subprocess.CalledProcessError as erro:
        raise SystemExit(f"caminho ausente em {commit}: {caminho}") from erro


def sha(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


def variantes(dados: bytes) -> dict:
    """sha256 do blob com LF e com CRLF (o disco do Windows pode ter CRLF)."""
    lf = dados.replace(b"\r\n", b"\n")
    return {"lf": sha(lf), "crlf": sha(lf.replace(b"\n", b"\r\n"))}


def ancestral(a: str, b: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b]).returncode == 0


def commit_que_adicionou(commit: str, caminho: str):
    linhas = git("log", "--diff-filter=A", "--format=%H %cI", commit, "--", caminho).split()
    if not linhas:
        return None
    return {"commit": linhas[-2], "data": linhas[-1]}


def commit_do_plano(commit: str, plano: str, alvo: str):
    """O commit mais antigo em que o plano tem o sha256 `alvo` (LF ou CRLF)."""
    linhas = git("log", "--format=%H %cI", "--reverse", commit, "--", plano).splitlines()
    for linha in linhas:
        h, data = linha.split()
        try:
            dados = git("show", f"{h}:{plano}", binario=True)
        except subprocess.CalledProcessError:
            continue
        v = variantes(dados)
        if alvo in (v["lf"], v["crlf"]):
            return {"commit": h, "data": data, "codificacao": "lf" if alvo == v["lf"] else "crlf"}
    return None


def auditar_experimento(commit: str, exp: dict) -> dict:
    linha = {"nome": exp["nome"], "pergunta": exp["pergunta"], "plano": exp["plano"],
             "resultado_doc": exp["resultado_doc"]}
    linha["resultado_doc_adicionado"] = commit_que_adicionou(commit, exp["resultado_doc"])
    linha["plano_adicionado"] = commit_que_adicionou(commit, exp["plano"])
    meta = {}
    if exp["meta"]:
        meta = json.loads(blob(commit, exp["meta"]))
        linha["meta"] = exp["meta"]
        linha["meta_adicionado"] = commit_que_adicionou(commit, exp["meta"])
        codigo = meta.get("git_head") or meta.get("codigo")
        linha["codigo"] = codigo
        linha["codigo_completo"] = bool(codigo) and len(codigo) == 40
        linha["git_limpo"] = meta.get("git_limpo")
        linha["python"] = meta.get("python")
        linha["node"] = meta.get("node")
        linha["comando_no_meta"] = any(k in meta for k in ("comando", "command", "argv"))
        linha["inicio"] = meta.get("inicio")
        linha["processos"] = meta.get("processos")
        if codigo and len(codigo) < 40:
            linha["codigo_resolvido"] = git("rev-parse", codigo).strip()
    if exp["plano_meta"]:
        alvo = meta[exp["plano_meta"]]
        achado = commit_do_plano(commit, exp["plano"], alvo)
        linha["plano_sha256_meta"] = alvo
        linha["plano_commit_com_esse_sha"] = achado
        if achado and linha.get("codigo"):
            linha["plano_ancestral_do_codigo"] = ancestral(achado["commit"], linha["codigo"])
    artefatos = {}
    gravados = meta.get("artefatos_sha256", {})
    for nome, caminho in exp["artefatos"].items():
        dados = blob(commit, caminho)
        item = {"caminho": caminho, "bytes": len(dados), "sha256_blob": sha(dados)}
        conteudo = gzip.decompress(dados) if caminho.endswith(".gz") else dados
        if caminho.endswith(".gz"):
            item["sha256_descomprimido"] = sha(conteudo)
        chave = nome[:-3] if nome.endswith(".gz") else nome
        if chave in gravados:
            v = variantes(conteudo) if not caminho.endswith(".gz") else {"lf": sha(conteudo), "crlf": None}
            item["sha256_no_meta"] = gravados[chave]
            item["confere_meta"] = gravados[chave] in (v["lf"], v["crlf"], sha(conteudo))
        item["adicionado"] = commit_que_adicionou(commit, caminho)
        artefatos[nome] = item
    if exp["vidas"]:
        dados = blob(commit, exp["vidas"])
        artefatos["vidas.tar.gz"] = {"caminho": exp["vidas"], "bytes": len(dados), "sha256_blob": sha(dados),
                                     "adicionado": commit_que_adicionou(commit, exp["vidas"])}
    linha["artefatos"] = artefatos
    return linha


def grep_py(commit: str, texto: str) -> list:
    """Os .py do commit que citam `texto` (git grep sai 1 quando não acha)."""
    r = subprocess.run(["git", "grep", "-l", "-F", texto, commit, "--", "*.py"], capture_output=True)
    if r.returncode not in (0, 1):
        raise SystemExit(r.stderr.decode("utf-8"))
    return [c.split(":", 1)[1] for c in r.stdout.decode("utf-8").splitlines() if c]


def inventario_gz(commit: str) -> list:
    arquivos = git("ls-tree", "-r", "--name-only", commit).splitlines()
    gz = sorted(a for a in arquivos if a.startswith("artifacts") and a.endswith(".gz"))
    saida = []
    for caminho in gz:
        dados = blob(commit, caminho)
        citado_por = sorted(set(grep_py(commit, caminho)) | set(grep_py(commit, caminho.split("/", 1)[1])))
        saida.append({"caminho": caminho, "bytes": len(dados), "sha256": sha(dados), "py_que_citam": citado_por})
    return saida


def metas_sem_sha(commit: str) -> list:
    arquivos = git("ls-tree", "-r", "--name-only", commit).splitlines()
    metas = sorted(a for a in arquivos if a.startswith("artifacts")
                   and (a.endswith("/meta.json") or "/manifesto" in a and a.endswith(".json")))
    saida = []
    for caminho in metas:
        try:
            meta = json.loads(blob(commit, caminho))
        except json.JSONDecodeError:
            saida.append({"caminho": caminho, "motivo": "json inválido"})
            continue
        if not isinstance(meta, dict):
            saida.append({"caminho": caminho, "motivo": "não é objeto"})
            continue
        codigo = None
        for k in ("git_head", "commit", "codigo", "git_sha", "sha_codigo"):
            if isinstance(meta.get(k), str):
                codigo = meta[k]
                break
        if not codigo:
            saida.append({"caminho": caminho, "motivo": "sem SHA do código"})
        elif len(codigo) < 40:
            saida.append({"caminho": caminho, "motivo": f"SHA curto ({codigo})"})
    return {"metas_lidos": len(metas), "lacunas": saida}


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    commit = git("rev-parse", sys.argv[1]).strip()
    relatorio = {
        "commit_auditado": commit,
        "experimentos": [auditar_experimento(commit, e) for e in EXPERIMENTOS],
        "gz_em_artifacts": inventario_gz(commit),
        "metas_em_artifacts": metas_sem_sha(commit),
    }
    with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
