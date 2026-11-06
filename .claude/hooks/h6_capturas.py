"""H6 (PreToolUse, Edit|Write|MultiEdit|NotebookEdit e Bash|PowerShell): as referências visuais só mudam com o Matheus.

O desenho é o da seção 3.3 de `docs/TAREFA_V3_UX_TELA_PET.md`, feito uma vez só pela INFRA_AGENTES E1 (D-IA-5 de
`docs/TAREFA_V3_INFRA_AGENTES.md`):
- **nas ferramentas de edição:** código 2 ao escrever em qualquer pasta `*-snapshots/` ou na pasta das referências do portão, fora do git
  (`DIGILAB_CAPTURAS`, relativa a `web/app`, padrão `../../artifacts_v2_front_react/capturas`, o `snapshotPathTemplate` do
  `web/app/playwright.capturas.config.ts`);
- **no shell:** código 2 num comando que apaga, move, copia ou escreve (por redirecionamento) num desses caminhos; a decisão `ask` num
  comando do Playwright com `--update-snapshots` ou `-u` (o `npx playwright test -u`, o `npm run e2e -- -u`, o `npm run capturas --
  --update-snapshots`): é o único caminho para trocar uma referência, e o Matheus confirma na hora.

Como o H3, o hook lê o texto do comando: um script que escreva por dentro não passa por aqui. Ler (`ls`, `cat`, `git diff`) passa.
"""
from __future__ import annotations

import os
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, ler_evento, perguntar, raiz_do_projeto  # noqa: E402

SEPARADORES = re.compile(r"&&|\|\||;|\||\n")
ESCRITA = {"rm", "rmdir", "mv", "cp", "del", "erase", "move", "copy", "xcopy", "robocopy", "touch", "tee", "truncate", "remove-item",
           "move-item", "copy-item", "rename-item", "new-item", "set-content", "add-content", "out-file", "clear-content", "ri", "mi",
           "cpi", "rni", "ni", "sc", "ac", "rd"}
GIT_ESCRITA = {"rm", "mv", "checkout", "restore", "clean"}
SCRIPTS_PLAYWRIGHT = {"e2e", "capturas", "poc:e2e"}
MOTIVO = ("H6: as referências visuais (*-snapshots/ e a pasta de DIGILAB_CAPTURAS) só mudam com a aprovação do Matheus. Rode o teste e "
          "devolva o diff; a troca da referência é pelo --update-snapshots, que pede confirmação.")


def pasta_capturas(raiz: Path) -> str:
    pasta = Path(os.environ.get("DIGILAB_CAPTURAS") or "../../artifacts_v2_front_react/capturas")
    if not pasta.is_absolute():
        pasta = raiz / "web" / "app" / pasta
    return normalizar(str(pasta.resolve()))


def normalizar(texto: str) -> str:
    return texto.replace("\\", "/").lower().rstrip("/")


def protegido(caminho: str, capturas: str) -> bool:
    c = normalizar(caminho)
    if any(parte.endswith("-snapshots") for parte in c.split("/")):
        return True
    return c == capturas or c.startswith(capturas + "/")


def caminho_da_ferramenta(evento: dict) -> str | None:
    entrada = evento.get("tool_input") or {}
    return entrada.get("file_path") or entrada.get("notebook_path") or entrada.get("path")


def tokens_de(pedaco: str) -> list[str]:
    try:
        return shlex.split(pedaco, posix=True)
    except ValueError:
        return pedaco.split()


def e_playwright(tokens: list[str]) -> bool:
    nomes = [Path(t).stem.lower() for t in tokens]
    if "playwright" in nomes:
        return True
    return bool(nomes) and nomes[0] == "npm" and "run" in tokens and any(t in SCRIPTS_PLAYWRIGHT for t in tokens)


def atualiza_referencia(tokens: list[str]) -> bool:
    return e_playwright(tokens) and any(t == "-u" or t == "--update-snapshots" or t.startswith("--update-snapshots=") for t in tokens)


def escreve_em_protegido(pedaco: str, tokens: list[str], capturas: str, raiz: Path) -> bool:
    """Algum argumento é um caminho protegido (como está, ou relativo à raiz ou a `web/app`, de onde o npm roda) e o comando escreve."""
    bases = (raiz, raiz / "web" / "app")
    candidatos = [t for t in tokens if not t.startswith("-")]
    if not any(protegido(t, capturas) or any(protegido(str((b / t).resolve()), capturas) for b in bases if not Path(t).is_absolute())
               for t in candidatos):
        return False
    if ">" in pedaco:
        return True
    nomes = [Path(t).stem.lower() if i == 0 else t.lower() for i, t in enumerate(tokens)]
    if not nomes:
        return False
    if nomes[0] in ESCRITA:
        return True
    if nomes[0] == "git" and len(nomes) > 1 and any(t in GIT_ESCRITA for t in nomes[1:3]):
        return True
    return nomes[0] == "sed" and any(t.startswith("-i") for t in nomes[1:])


def main() -> None:
    evento = ler_evento()
    raiz = raiz_do_projeto(evento)
    capturas = pasta_capturas(raiz)
    if evento.get("tool_name") in ("Bash", "PowerShell"):
        comando = (evento.get("tool_input") or {}).get("command") or ""
        for pedaco in SEPARADORES.split(comando):
            tokens = tokens_de(pedaco.strip())
            if tokens and escreve_em_protegido(pedaco, tokens, capturas, raiz):
                bloquear(MOTIVO)
        for pedaco in SEPARADORES.split(comando):
            if atualiza_referencia(tokens_de(pedaco.strip())):
                perguntar("H6: --update-snapshots troca as referências visuais. Só com a aprovação do Matheus, na hora: confirme se é "
                          "para trocar agora.")
        return
    alvo = caminho_da_ferramenta(evento)
    if not alvo:
        return
    caminho = Path(alvo)
    if not caminho.is_absolute():
        caminho = Path(evento.get("cwd") or raiz) / caminho
    if protegido(str(caminho.resolve()), capturas):
        bloquear(MOTIVO)


if __name__ == "__main__":
    main()
