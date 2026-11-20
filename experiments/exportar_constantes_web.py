"""Exporta os parametros de digilab/config.py que o jogo web espelha (TAREFA_FRONT_TS, Etapa 1).

Grava um JSON {ClasseConfig: {campo: valor}} com os valores padrao de cada dataclass de config.
O teste de constantes do web (web/app/test/constantes.test.mjs) compara este JSON com as
constantes do motor web, campo a campo, pela tabela web/app/test/mapa_constantes.json.

So le config.py: nada no pacote digilab/ muda.

uso: python experiments/exportar_constantes_web.py [saida.json]
"""
from __future__ import annotations

import dataclasses
import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab import config  # noqa: E402

SAIDA = RAIZ / "web" / "app" / "test" / "gabaritos" / "constantes_python.json"


def _valor(v):
    """valor em JSON; float nao finito e tipo desconhecido falham alto"""
    if dataclasses.is_dataclass(v):
        return {f.name: _valor(getattr(v, f.name)) for f in dataclasses.fields(v)}
    if isinstance(v, bool) or v is None or isinstance(v, (int, str)):
        return v
    if isinstance(v, float):
        if not math.isfinite(v):
            raise ValueError(f"float nao finito: {v}")
        return v
    if isinstance(v, (list, tuple)):
        return [_valor(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _valor(x) for k, x in v.items()}
    raise TypeError(f"tipo nao exportavel: {type(v).__name__}")


def exportar() -> dict:
    out = {}
    for nome in sorted(dir(config)):
        obj = getattr(config, nome)
        if isinstance(obj, type) and dataclasses.is_dataclass(obj) and nome.startswith("Config"):
            try:
                inst = obj()
            except TypeError as e:          # dataclass sem padrao para algum campo: nao e config espelhada
                raise TypeError(f"{nome} sem valores padrao: {e}") from e
            out[nome] = _valor(inst)
    return out


def main() -> int:
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else SAIDA
    saida.parent.mkdir(parents=True, exist_ok=True)
    dados = exportar()
    saida.write_text(json.dumps(dados, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{saida}: {len(dados)} classes de config")
    return 0


if __name__ == "__main__":
    sys.exit(main())
