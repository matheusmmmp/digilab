"""H2 (Stop): antes de encerrar o turno, com mudança em `digilab/`, `experiments/` ou `tests/`, roda um conjunto rápido de testes.

O conjunto (a suíte inteira leva ~36 min e fica no PR; o sha do engine é do H1b):
- os arquivos de teste mudados (`tests/test_*.py`);
- para cada módulo mudado `digilab/<x>.py`, `digilab/<pacote>/<x>.py` ou `experiments/<x>.py`, o `tests/test_<x>.py`, se existe;
- para cada gabarito mudado (`tests/gabaritos/<nome>`), os testes que citam o nome dele;
- os testes da frente: `tests/test_<frente>*.py`, com a frente tirada do branch `v3-<frente>` ou `v2-<frente>` (hífen vira sublinhado;
  vale o prefixo mais longo do nome que acha algum arquivo, de modo que `v3-ponte-luta-pe0` acha `test_ponte_luta*.py`);
- **os testes de replay** (`REPLAY`, uma lista fixa), só quando mudou `digilab/` ou `experiments/bancada/`, o código que pode mudar uma
  vida (D-IA-1 de `docs/TAREFA_V3_INFRA_AGENTES.md`; medidos em 2026-11-06: 108 testes em ~7 min).

Se algum falha, devolve o turno ao Claude (código 2) com o resumo do pytest. **Não bloqueia duas vezes pelo mesmo motivo:** com o
`stop_hook_active` (o Claude já continuou por um bloqueio) ou com a mesma assinatura de falha da última vez (guardada fora do repositório,
na pasta temporária, por sessão), deixa encerrar. **O limite de tempo** (`DIGILAB_H2_LIMITE_S`, 600 s) estourado bloqueia uma vez por
sessão, com o pedido de rodar a suíte da frente antes do PR (antes de 2026-11-06 ele deixava passar em silêncio).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, git, ler_evento, raiz_do_projeto  # noqa: E402

PASTAS = ("digilab/", "experiments/", "tests/")
PASTAS_REPLAY = ("digilab/", "experiments/bancada/")
REPLAY = ("test_engine.py", "test_gabarito_*.py", "test_gabaritos_*.py", "test_p4_gabaritos.py", "test_passeio_gabarito.py")
LIMITE_S = int(os.environ.get("DIGILAB_H2_LIMITE_S", "600"))


def mudados(raiz: Path) -> list[str]:
    """Os caminhos mudados no `git status --porcelain` (o destino, num renome), só nas pastas que importam."""
    saida = []
    for linha in git(raiz, "status", "--porcelain", "--untracked-files=all").splitlines():
        caminho = linha[3:].split(" -> ")[-1].strip().strip('"')
        if caminho.startswith(PASTAS):
            saida.append(caminho)
    return sorted(set(saida))


def conjunto_rapido(raiz: Path, caminhos: list[str]) -> list[str]:
    testes = set()
    for c in caminhos:
        p = Path(c)
        if p.parts[0] == "tests" and p.name.startswith("test_") and p.suffix == ".py":
            testes.add(c)
        elif p.suffix == ".py" and p.parts[0] in ("digilab", "experiments"):
            candidato = Path("tests") / f"test_{p.stem}.py"
            if (raiz / candidato).exists():
                testes.add(candidato.as_posix())
        elif len(p.parts) >= 2 and p.parts[:2] == ("tests", "gabaritos"):
            for t in sorted((raiz / "tests").glob("test_*.py")):
                if p.name in t.read_text(encoding="utf-8", errors="replace"):
                    testes.add(t.relative_to(raiz).as_posix())
    return sorted(t for t in testes if (raiz / t).exists())


def testes_de_replay(raiz: Path, caminhos: list[str]) -> list[str]:
    if not any(c.startswith(PASTAS_REPLAY) for c in caminhos):
        return []
    return sorted({t.relative_to(raiz).as_posix() for padrao in REPLAY for t in (raiz / "tests").glob(padrao)})


def testes_da_frente(raiz: Path) -> list[str]:
    ramo = git(raiz, "rev-parse", "--abbrev-ref", "HEAD").strip()
    m = re.fullmatch(r"v[23]-([a-z0-9][a-z0-9-]*)", ramo)
    if m is None:
        return []
    partes = m.group(1).split("-")
    for n in range(len(partes), 0, -1):
        achados = sorted(t.relative_to(raiz).as_posix() for t in (raiz / "tests").glob(f"test_{'_'.join(partes[:n])}*.py"))
        if achados:
            return achados
    return []


def estado(evento: dict) -> Path:
    sessao = "".join(ch for ch in str(evento.get("session_id") or "sem-sessao") if ch.isalnum() or ch in "-_")[:80]
    return Path(tempfile.gettempdir()) / f"digilab_h2_{sessao}.json"


def main() -> None:
    evento = ler_evento()
    if evento.get("stop_hook_active"):
        return
    raiz = raiz_do_projeto(evento)
    caminhos = mudados(raiz)
    if not caminhos:
        return
    testes = sorted(set(conjunto_rapido(raiz, caminhos)) | set(testes_de_replay(raiz, caminhos)) | set(testes_da_frente(raiz)))
    if not testes:
        return
    arquivo = estado(evento)
    anterior = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else {}
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *testes], cwd=raiz,
                           capture_output=True, timeout=LIMITE_S)
    except subprocess.TimeoutExpired:
        if anterior.get("estouro"):
            return                             # já avisou nesta sessão: deixa encerrar
        arquivo.write_text(json.dumps({**anterior, "estouro": True}), encoding="utf-8")
        bloquear(f"H2: os testes do fim do turno passaram de {LIMITE_S} s ({len(testes)} arquivos) e não terminaram. Rode a suíte da "
                 "frente antes do PR (python -m pytest " + " ".join(testes) + " -q).")
    if r.returncode == 0:
        arquivo.unlink(missing_ok=True)
        return
    resumo = r.stdout.decode("utf-8", "replace").strip().splitlines()[-15:]
    # a assinatura do motivo: os testes rodados e as linhas de falha do pytest, sem o tempo ("1 failed in 0.11s" muda a cada rodada)
    falhas = [re.sub(r" in [0-9.]+s", "", linha) for linha in resumo if linha.startswith(("FAILED", "ERROR")) or " failed" in linha]
    assinatura = hashlib.sha256(("\n".join(testes) + "\n" + "\n".join(falhas)).encode("utf-8")).hexdigest()
    if anterior.get("assinatura") == assinatura:
        return                                 # o mesmo motivo de antes: não bloqueia de novo
    arquivo.write_text(json.dumps({**anterior, "assinatura": assinatura}), encoding="utf-8")
    bloquear("H2: os testes do fim do turno falharam (" + ", ".join(testes) + "):\n" + "\n".join(resumo))


if __name__ == "__main__":
    main()
