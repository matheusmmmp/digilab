"""H5 (Stop): com mudança no jogo web, roda `npm run tipos`, `npm test` e `npm run e2e` em `web/app` antes de encerrar o turno.

A tarefa é a `docs/TAREFA_V3_UX_TELA_PET.md`, seção 3.3 (etapa A1). O CI do PR não roda o Vitest nem o e2e
(`docs/infra/GUIA_OPERACIONAL.md`, seção 3), e este hook põe os dois no fim do turno de quem mexe na tela.

Roda quando o diff da worktree toca `web/app/src/`, `web/app/e2e*/`, `web/app/test/` ou `web/app/motor/`. O diff é a soma de duas partes:
- o que mudou contra o `merge-base` com a base (`DIGILAB_H5_BASE`, padrão `origin/main`);
- o que ainda não foi commitado, inclusive os arquivos novos.

Os passos rodam em ordem e param no primeiro que falha. Em falha, devolve o turno (código 2) com o nome do passo e as linhas de falha, não
o log inteiro. **Não bloqueia duas vezes pelo mesmo motivo**, como o H2: com o `stop_hook_active` ou com a mesma assinatura de falha da
última vez (guardada na pasta temporária, por sessão), deixa encerrar.

Duas variáveis de ambiente mudam o comportamento:
- `DIGILAB_H5_PASSOS`: uma lista JSON de `[nome, [argv...]]` que troca os passos. Serve para a UX-3 (só os specs da tela Pet) e para os
  testes deste hook.
- `DIGILAB_H5_LIMITE_S`: o limite de cada passo, em segundos. Um passo que passa do limite não bloqueia; fica para antes do PR.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, git, ler_evento, raiz_do_projeto  # noqa: E402

PASTAS = ("web/app/src/", "web/app/e2e", "web/app/test/", "web/app/motor/")
LIMITE_S = int(os.environ.get("DIGILAB_H5_LIMITE_S", "1800"))
LINHA_DE_FALHA = re.compile(r"(FAIL|✘|×|error TS\d+|^\s*\d+\) |failed|Error:)")


def passos() -> list[tuple[str, list[str]]]:
    bruto = os.environ.get("DIGILAB_H5_PASSOS")
    if bruto:
        return [(str(nome), [str(a) for a in argv]) for nome, argv in json.loads(bruto)]
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("H5: npm não está no PATH")
    return [("tipos", [npm, "run", "tipos"]), ("vitest", [npm, "test"]), ("e2e", [npm, "run", "e2e"])]


def mudados(raiz: Path) -> list[str]:
    base = os.environ.get("DIGILAB_H5_BASE", "origin/main")
    ponto = git(raiz, "merge-base", "HEAD", base).strip()
    caminhos = set(git(raiz, "diff", "--name-only", ponto).splitlines())          # commitado desde a base e o não commitado
    caminhos |= set(git(raiz, "ls-files", "--others", "--exclude-standard").splitlines())
    return sorted(c.strip() for c in caminhos if c.strip().startswith(PASTAS))


def estado(evento: dict) -> Path:
    sessao = "".join(ch for ch in str(evento.get("session_id") or "sem-sessao") if ch.isalnum() or ch in "-_")[:80]
    return Path(tempfile.gettempdir()) / f"digilab_h5_{sessao}.json"


def resumo(saida: str) -> list[str]:
    linhas = [linha.rstrip() for linha in saida.splitlines() if linha.strip()]
    falhas = [linha for linha in linhas if LINHA_DE_FALHA.search(linha)]
    return (falhas or linhas)[-20:]


def main() -> None:
    evento = ler_evento()
    if evento.get("stop_hook_active"):
        return
    raiz = raiz_do_projeto(evento)
    caminhos = mudados(raiz)
    if not caminhos:
        return
    pasta = raiz / "web" / "app"
    for nome, argv in passos():
        try:
            r = subprocess.run(argv, cwd=pasta, capture_output=True, timeout=LIMITE_S)
        except subprocess.TimeoutExpired:
            return                             # longo demais para o fim do turno: fica para antes do PR, sem bloquear
        if r.returncode == 0:
            continue
        linhas = resumo(r.stdout.decode("utf-8", "replace") + "\n" + r.stderr.decode("utf-8", "replace"))
        # a assinatura: o passo e as linhas de falha, sem os tempos ("(1.2s)", "in 3.4s", "12ms") que mudam a cada rodada
        limpas = [re.sub(r"\(?\b[0-9.]+\s?(ms|s|m)\b\)?", "", linha) for linha in linhas]
        assinatura = hashlib.sha256((nome + "\n" + "\n".join(limpas)).encode("utf-8")).hexdigest()
        arquivo = estado(evento)
        anterior = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else {}
        if anterior.get("assinatura") == assinatura:
            return                             # o mesmo motivo de antes: não bloqueia de novo
        arquivo.write_text(json.dumps({"assinatura": assinatura}), encoding="utf-8")
        bloquear(f"H5: o passo '{nome}' do web/app falhou (mudados: {', '.join(caminhos[:8])}"
                 f"{'…' if len(caminhos) > 8 else ''}):\n" + "\n".join(linhas))
    estado(evento).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
