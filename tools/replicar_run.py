"""Replica uma run de pesquisa a partir do snapshot do código e compara os artefatos byte a byte (EVIDENCIA A3, docs/PREREGISTRO.md).

Dado o nome de uma run e o SHA do código dela:
1. lê o `meta.json` versionado da run (no git, na ref `--artefatos`, a HEAD por padrão) e falha alto se o `git_head` gravado não for o SHA
   dado, ou se a árvore da run não estava limpa;
2. cria uma worktree destacada nesse SHA (fora do repositório, na pasta `--trabalho`), sem tocar na árvore de trabalho atual;
3. roda o comando do `meta.json` (ou, quando o meta não o gravou, o comando do plano, que fica na tabela RUNS abaixo, com a fonte), com o
   mesmo Python desta execução e com `--saida` numa pasta nova da worktree (o orquestrador se recusa a gravar por cima da pasta versionada);
4. compara o sha256 de cada artefato da réplica com o do blob versionado. Um `.gz` versionado (o `medidas.json.gz` da C4) é descomprimido
   antes: o orquestrador grava o `.json`, e o `.gz` foi feito depois, para caber no GitHub;
5. grava um relatório JSON com o comando, as versões, a parede e cada comparação, e sai com 0 se tudo saiu igual, 1 se algo divergiu.

Uso:
  python tools/replicar_run.py --listar
  python tools/replicar_run.py c4 a287ba20fafdc1fbbf9be7100f89d9c90f466948 --relatorio replica_c4.json
  python tools/replicar_run.py c4 a287ba20... --so-comparar <pasta da replica>    # refaz só a comparação de uma réplica já rodada

A worktree sai apagada no fim, a menos que `--manter`. Nenhum artefato versionado é escrito. A ferramenta não conserta nada: uma
divergência é reportada como está, com os dois sha256.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# As runs conhecidas. `pasta` é a pasta versionada dos artefatos; `artefatos` liga o nome que a réplica grava ao caminho versionado (um
# `.gz` é descomprimido antes da comparação); `comando` só entra quando o meta não gravou o dele, com a fonte do comando.
RUNS: dict[str, dict] = {
    "c4": {
        "descricao": "C4, a memoria autobiografica (adendo 9 do PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO)",
        "pasta": "artifacts_v2_digibrain_prototipo/memoria_autobio/run",
        "artefatos": {"resultado.json": "resultado.json", "medidas.json": "medidas.json.gz"},
        "comando": "python experiments/run_v2_memoria_autobio.py --config experiments/configs/v2_memoria_autobio/memoria_autobio.json "
                   "--processos 4",
        "fonte_do_comando": "o plano, adendo 9, A9.13 (o meta da C4 nao grava o comando; docs/AUDITORIA_EVIDENCIA.md, secao 1.4)",
        "nao_comparados": {"vidas.tar.gz": "feito fora do orquestrador, depois da run (o commit 1df2e328); a replica grava as vidas soltas"},
    },
    "a1_validacao": {
        "descricao": "EVIDENCIA A1, a baseline trivial: a validacao (docs/PLANO_ANALISE_V3_BASELINE_TRIVIAL.md)",
        "pasta": "artifacts_v3_baseline_trivial/validacao",
        "artefatos": {"resultado.json": "resultado.json", "medidas.json": "medidas.json", "vidas.tar.gz": "vidas.tar.gz"},
    },
    "a2": {
        "descricao": "EVIDENCIA A2, a ablacao do aprendizado no jogo (docs/PLANO_ANALISE_V3_ABLACAO_APRENDIZADO.md)",
        "pasta": "artifacts_v3_ablacao_aprendizado/run",
        "artefatos": {"resultado.json": "resultado.json", "medidas.json": "medidas.json"},
    },
}


def sha256(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


def git(raiz: Path, *args: str, binario: bool = False):
    r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} falhou: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout if binario else r.stdout.decode("utf-8").strip()


def blob(raiz: Path, ref: str, caminho: str) -> bytes:
    return git(raiz, "show", f"{ref}:{caminho}", binario=True)


def conteudo(caminho: str, dados: bytes) -> bytes:
    """O conteúdo comparável: um `.gz` descomprimido (o cabeçalho do gzip leva a data e o nome; o conteúdo não)."""
    return gzip.decompress(dados) if caminho.endswith(".gz") else dados


def spec_da_run(nome: str) -> dict:
    if nome not in RUNS:
        raise KeyError(f"run desconhecida: {nome}; as conhecidas: {', '.join(sorted(RUNS))}")
    return RUNS[nome]


def ler_meta(raiz: Path, spec: dict, ref: str, sha: str) -> dict:
    meta = json.loads(blob(raiz, ref, f"{spec['pasta']}/meta.json").decode("utf-8"))
    cheio = git(raiz, "rev-parse", f"{sha}^{{commit}}")
    if meta.get("git_head") != cheio:
        raise RuntimeError(f"o SHA {sha} ({cheio}) nao e o git_head do meta ({meta.get('git_head')})")
    if meta.get("git_limpo") is not True:
        raise RuntimeError(f"a run de {spec['pasta']} nao foi gravada com a arvore limpa (git_limpo = {meta.get('git_limpo')})")
    return meta


def montar_comando(spec: dict, meta: dict, saida: Path) -> tuple[list[str], str]:
    """O comando da réplica: o do meta (ou o da tabela, com a fonte), o Python desta execução no lugar de `python` e o `--saida` novo."""
    if meta.get("comando"):
        texto, fonte = meta["comando"], "meta.json"
    elif spec.get("comando"):
        texto, fonte = spec["comando"], spec["fonte_do_comando"]
    else:
        raise RuntimeError("o meta nao grava o comando e a tabela RUNS nao tem um")
    partes = shlex.split(texto)
    if not partes or partes[0] != "python":
        raise RuntimeError(f"o comando nao comeca por python: {texto}")
    if "--saida" in partes:
        raise RuntimeError(f"o comando ja tem --saida; a replica nao sabe onde ele grava: {texto}")
    return [sys.executable, *partes[1:], "--saida", str(saida)], fonte


def comparar(raiz: Path, spec: dict, ref: str, meta: dict, saida: Path) -> list[dict]:
    out = []
    gravados = meta.get("artefatos_sha256", {})
    for nome, versionado in spec["artefatos"].items():
        original = blob(raiz, ref, f"{spec['pasta']}/{versionado}")
        alvo = conteudo(versionado, original)
        novo = saida / nome
        if not novo.exists():
            raise FileNotFoundError(f"a replica nao gravou {novo}")
        replica = novo.read_bytes()
        out.append({"artefato": nome, "versionado": f"{spec['pasta']}/{versionado}", "sha256_versionado": sha256(original),
                    "sha256_conteudo_versionado": sha256(alvo), "sha256_no_meta": gravados.get(nome),
                    "sha256_replica": sha256(replica), "bytes_versionado": len(alvo), "bytes_replica": len(replica),
                    "igual": sha256(replica) == sha256(alvo)})
    return out


def versao(prog: list[str]) -> str | None:
    if shutil.which(prog[0]) is None:
        return None
    r = subprocess.run(prog, capture_output=True, text=True)
    return (r.stdout or r.stderr).strip()


def replicar(nome: str, sha: str, raiz: Path = RAIZ, ref: str = "HEAD", trabalho: Path | None = None, manter: bool = False,
             so_comparar: Path | None = None) -> dict:
    spec = spec_da_run(nome)
    meta = ler_meta(raiz, spec, ref, sha)
    cheio = meta["git_head"]
    relatorio = {"run": nome, "descricao": spec["descricao"], "sha": cheio, "artefatos_ref": git(raiz, "rev-parse", ref),
                 "pasta": spec["pasta"], "python_original": meta.get("python"), "node_original": meta.get("node"),
                 "python": platform.python_version(), "node": versao(["node", "--version"]), "git": versao(["git", "--version"]),
                 "so": platform.platform(), "nao_comparados": spec.get("nao_comparados", {})}
    if so_comparar is not None:
        relatorio |= {"modo": "so_comparar", "saida": str(so_comparar)}
        relatorio["comparacoes"] = comparar(raiz, spec, ref, meta, so_comparar)
    else:
        trabalho = trabalho or raiz.parent / f"v3-replica-{nome}-{cheio[:8]}"
        if trabalho.exists():
            raise FileExistsError(f"{trabalho} ja existe: a replica nao reusa uma pasta")
        git(raiz, "worktree", "add", "--detach", str(trabalho), cheio)
        try:
            saida = trabalho / "_replica" / spec["pasta"]
            comando, fonte = montar_comando(spec, meta, saida)
            relatorio |= {"modo": "replica", "trabalho": str(trabalho), "saida": str(saida), "comando": comando, "fonte_do_comando": fonte,
                          "inicio": time.strftime("%Y-%m-%dT%H:%M:%S")}
            t0 = time.perf_counter()
            log = trabalho / "_replica" / "replica.log"
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("w", encoding="utf-8") as f:
                r = subprocess.run(comando, cwd=trabalho, stdout=f, stderr=subprocess.STDOUT,
                                   env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            relatorio |= {"parede_s": time.perf_counter() - t0, "fim": time.strftime("%Y-%m-%dT%H:%M:%S"), "saida_codigo": r.returncode,
                          "log_fim": log.read_text(encoding="utf-8", errors="replace")[-3000:]}
            if r.returncode != 0:
                raise RuntimeError(f"o comando saiu com {r.returncode}; o fim do log:\n{relatorio['log_fim']}")
            relatorio["comparacoes"] = comparar(raiz, spec, ref, meta, saida)
        finally:
            if not manter:
                git(raiz, "worktree", "remove", "--force", str(trabalho))
    relatorio["byte_a_byte"] = all(c["igual"] for c in relatorio["comparacoes"])
    return relatorio


def principal(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("run", nargs="?")
    p.add_argument("sha", nargs="?")
    p.add_argument("--listar", action="store_true")
    p.add_argument("--artefatos", default="HEAD", help="a ref de onde ler o meta e os artefatos versionados")
    p.add_argument("--trabalho", type=Path, help="a pasta da worktree (padrao: ../v3-replica-<run>-<sha8>)")
    p.add_argument("--manter", action="store_true", help="nao apaga a worktree no fim")
    p.add_argument("--so-comparar", type=Path, help="so compara uma pasta de replica ja rodada")
    p.add_argument("--relatorio", type=Path, help="grava o relatorio JSON aqui")
    p.add_argument("--raiz", type=Path, default=RAIZ)
    a = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    if a.listar:
        for nome, s in sorted(RUNS.items()):
            print(f"{nome}: {s['descricao']} ({s['pasta']})")
        return 0
    if not a.run or not a.sha:
        p.error("diga a run e o SHA (ou --listar)")
    r = replicar(a.run, a.sha, a.raiz.resolve(), a.artefatos, a.trabalho, a.manter, a.so_comparar)
    texto = json.dumps(r, indent=1, ensure_ascii=False)
    if a.relatorio:
        a.relatorio.parent.mkdir(parents=True, exist_ok=True)
        a.relatorio.write_text(texto + "\n", encoding="utf-8")
    print(json.dumps({"run": r["run"], "sha": r["sha"], "byte_a_byte": r["byte_a_byte"],
                      "comparacoes": [{k: c[k] for k in ("artefato", "igual", "sha256_conteudo_versionado", "sha256_replica")}
                                      for c in r["comparacoes"]]}, indent=1, ensure_ascii=False))
    return 0 if r["byte_a_byte"] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
