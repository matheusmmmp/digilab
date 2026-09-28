"""Log de APRESENTACAO (docs/PLANO_VERSAO_FALA_LIVRE.md, secao 3): falas e conversas do pet.

Arquivo separado por pet (`<save>.fala.jsonl`). O log principal do pet nao ganha eventos novos e o replay do
pet nao sabe que este arquivo existe. O replay das falas le o TEXTO gravado; nunca chama a LLM de novo.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

VERSAO_LOG = 1
CAMPOS = ("versao", "t", "situacao", "fala_jogador", "fala", "fatos_citados", "fatos", "estagio", "modelo",
          "versao_prompt", "semente", "latencia_s", "erro", "verificacao")


class LogInvalido(ValueError):
    """Registro do log de apresentacao fora do formato: falha alto."""


def registro(t: int, situacao: str, resultado, semente: int, fala_jogador: str | None = None,
             verificacao: dict | None = None) -> dict:
    """resultado: gerar.Resultado. t: tick do pet no momento da fala (so para ordenar; o pet nao le isto)."""
    return {"versao": VERSAO_LOG, "t": int(t), "situacao": situacao, "fala_jogador": fala_jogador,
            "fala": resultado.fala, "fatos_citados": list(resultado.fatos_citados), "fatos": list(resultado.fatos),
            "estagio": resultado.estagio, "modelo": resultado.modelo, "versao_prompt": resultado.versao_prompt,
            "semente": semente, "latencia_s": resultado.latencia_s, "erro": resultado.erro,
            "verificacao": verificacao}


@dataclass
class LogApresentacao:
    caminho: Path

    def anexar(self, reg: dict) -> None:
        if set(reg) != set(CAMPOS) or reg["versao"] != VERSAO_LOG:
            raise LogInvalido(f"registro com campos {sorted(reg)}")
        with open(self.caminho, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(reg, ensure_ascii=False, sort_keys=True) + "\n")

    def ler(self) -> list[dict]:
        if not self.caminho.exists():
            return []
        regs = []
        for i, linha in enumerate(self.caminho.read_text(encoding="utf-8").splitlines(), 1):
            try:
                reg = json.loads(linha)
            except json.JSONDecodeError as err:
                raise LogInvalido(f"linha {i}: {err.msg}") from err
            if set(reg) != set(CAMPOS) or reg.get("versao") != VERSAO_LOG:
                raise LogInvalido(f"linha {i}: campos {sorted(reg)}")
            regs.append(reg)
        return regs


def replay_falas(log: LogApresentacao) -> list[tuple[int, str | None, str]]:
    """(tick, fala do jogador, fala do pet) na ordem gravada, sem chamar a LLM."""
    return [(r["t"], r["fala_jogador"], r["fala"]) for r in log.ler()]
