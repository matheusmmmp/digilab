"""Confere se uma tarefa tem autorização de implementação válida do Matheus numa Issue.

O protocolo (docs/infra/GUIA_OPERACIONAL.md, "AUTORIZAR IMPLEMENTAÇÃO") pede um comentário na Issue:

    AUTORIZO IMPLEMENTAÇÃO: docs/TAREFA_V2_<FRENTE>.md
    blob SHA: <sha do arquivo aprovado>
    Escopo: seção 3 dessa tarefa

O problema que esta ferramenta resolve: com escrita no conector, o ChatGPT Work comenta **como matheusmmmp** (docs/infra/TESTE_CHATGPT_WORK.md,
passo 6). Na tela, o comentário dele e o do Matheus parecem iguais. A API distingue: o do Work vem com `performed_via_github_app`
("ChatGPT Codex Connector"). Um comentário só vale como autorização quando:
1. o autor é o dono (`--dono`, padrão matheusmmmp) e é do tipo User;
2. `performed_via_github_app` é nulo (não foi escrito por um app do GitHub, como o conector do ChatGPT);
3. o comentário não foi editado depois de criado (a API não diz quem editou);
4. cita o caminho da tarefa e o blob SHA, e esse SHA é o do arquivo hoje em `--ref` (padrão origin/main). Se a tarefa mudou, a autorização
   não vale mais.

Limite conhecido: o `gh` do Claude Code usa o token do próprio Matheus (um app OAuth, não um GitHub App), então um comentário escrito pelo
Claude Code por `gh` passa pela regra 2. Por isso o AGENTS.md proíbe qualquer agente de escrever "AUTORIZO" (decisão IM-8 para um hook).

Uso:
  python tools/conferir_autorizacao.py --issue 336 --tarefa docs/TAREFA_V2_<FRENTE>.md [--ref origin/main] [--dono matheusmmmp]

Sai com 0 se há pelo menos uma autorização válida para o conteúdo atual da tarefa; com 1, e a tabela do porquê, se não.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

GATILHO = re.compile(r"^\s*AUTORIZO IMPLEMENTA[ÇC][ÃA]O\s*:\s*`?([^\s`]+)`?\s*$", re.M | re.I)
BLOB = re.compile(r"^\s*blob SHA\s*:\s*`?([0-9a-f]{7,40})`?\s*$", re.M | re.I)


@dataclass
class Veredito:
    comentario: str  # id ou url
    valido: bool
    motivos: list[str]


def avaliar(comentario: dict, tarefa: str, sha_atual: str, dono: str) -> Veredito | None:
    """None se o comentário não é uma autorização; senão, o veredito com todos os motivos de recusa."""
    corpo = (comentario.get("body") or "").replace("\r\n", "\n")
    m = GATILHO.search(corpo)
    if m is None:
        return None
    motivos = []
    usuario = comentario.get("user") or {}
    if usuario.get("login") != dono:
        motivos.append(f"autor {usuario.get('login')!r}, não {dono!r}")
    if usuario.get("type") != "User":
        motivos.append(f"autor do tipo {usuario.get('type')!r}, não User")
    app = comentario.get("performed_via_github_app")
    if app is not None:
        motivos.append(f"escrito por um app do GitHub ({app.get('name', '?')}), não pelo Matheus")
    if comentario.get("created_at") != comentario.get("updated_at"):
        motivos.append("editado depois de criado (a API não diz por quem)")
    if m.group(1) != tarefa:
        motivos.append(f"autoriza {m.group(1)!r}, não {tarefa!r}")
    b = BLOB.search(corpo)
    if b is None:
        motivos.append("sem linha 'blob SHA:'")
    elif not sha_atual.startswith(b.group(1).lower()):
        motivos.append(f"blob SHA {b.group(1)} não é o da tarefa hoje ({sha_atual[:12]}): o conteúdo mudou ou o SHA está errado")
    return Veredito(str(comentario.get("html_url") or comentario.get("id")), not motivos, motivos)


def conferir(comentarios: list[dict], tarefa: str, sha_atual: str, dono: str) -> list[Veredito]:
    return [v for c in comentarios if (v := avaliar(c, tarefa, sha_atual, dono)) is not None]


def sha_do_blob(raiz: Path, ref: str, tarefa: str) -> str:
    r = subprocess.run(["git", "-C", str(raiz), "rev-parse", f"{ref}:{tarefa}"], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"a tarefa {tarefa} não existe em {ref}: {r.stderr.strip()}")
    return r.stdout.strip()


def comentarios_da_issue(repo: str, issue: int) -> list[dict]:
    r = subprocess.run(["gh", "api", "--paginate", f"repos/{repo}/issues/{issue}/comments"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(f"gh api falhou: {r.stderr.strip()}")
    # --paginate concatena as páginas como listas JSON seguidas
    saida: list[dict] = []
    for pedaco in re.split(r"(?<=\])\s*(?=\[)", r.stdout.strip()):
        if pedaco:
            saida.extend(json.loads(pedaco))
    return saida


def principal(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--issue", type=int, required=True)
    p.add_argument("--tarefa", required=True, help="caminho da tarefa, ex.: docs/TAREFA_V2_X.md")
    p.add_argument("--ref", default="origin/main")
    p.add_argument("--dono", default="matheusmmmp")
    p.add_argument("--repo", default="matheusmmmp/digilab")
    p.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
    a = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    sha = sha_do_blob(a.raiz.resolve(), a.ref, a.tarefa)
    vereditos = conferir(comentarios_da_issue(a.repo, a.issue), a.tarefa, sha, a.dono)
    print(f"Tarefa {a.tarefa} em {a.ref}: blob {sha}")
    if not vereditos:
        print(f"Nenhum comentário de autorização na Issue #{a.issue}.")
        return 1
    print("| comentário | vale? | motivo |\n|---|---|---|")
    for v in vereditos:
        print(f"| {v.comentario} | {'sim' if v.valido else 'NÃO'} | {'; '.join(v.motivos) or 'ok'} |")
    return 0 if any(v.valido for v in vereditos) else 1


if __name__ == "__main__":
    sys.exit(principal())
