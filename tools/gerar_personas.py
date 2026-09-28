"""Gera um lote de personas de dono com LLM (educacao-v1, sistema E) e congela em experiments/personas/.

    python tools/gerar_personas.py --provedor ollama --n 20 --lote ollama-qwen-01
    python tools/gerar_personas.py --provedor claude --modelo claude-haiku-4-5 --n 50 --lote haiku-01 --limite-usd 1

Uma chamada por persona (saida pequena, validada uma a uma por digilab.personas.validar_persona; a que nao
valida e refeita com outra semente, ate 3 vezes, e o lote falha alto se ainda assim nao validar). Pede
diversidade dizendo ao modelo quais personas ja existem. O lote vai para o disco uma vez so; o sha256 que o
script imprime e o que o protocolo da run registra (Fase 3). Nomes repetidos: sufixo numerico.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tools"))

from digilab.personas import ESQUEMA_PERSONA, PersonaInvalida, carregar_lote, validar_persona  # noqa: E402
from llm_pesquisa import LLMFalhou, abrir_provedor, chamar_json  # noqa: E402

VERSAO_PROMPT = "personas-v1"
PASTA = RAIZ / "experiments" / "personas"
TENTATIVAS = 3

SISTEMA = (
    "Voce cria pessoas ficticias e variadas que cuidam de um bichinho virtual (estilo Tamagotchi/Digimon). "
    "Cada pessoa tem rotina, horarios e manias proprias: umas atentas, outras ocupadas, rigidas, permissivas, "
    "inconstantes. Responda SO o JSON pedido, em portugues, sem nomes de pessoas reais."
)


def esquema_json() -> dict:
    props = {}
    for k, (tipo, regra, desc) in ESQUEMA_PERSONA.items():
        if tipo is float:
            props[k] = {"type": "number", "minimum": regra[0], "maximum": regra[1], "description": desc}
        elif k == "horarios":
            props[k] = {"type": "array", "minItems": 1, "maxItems": 4, "description": desc,
                        "items": {"type": "array", "minItems": 2, "maxItems": 2,
                                  "items": {"type": "integer", "minimum": 0, "maximum": 24}}}
        elif k == "perfil_treino":
            props[k] = {"type": "string", "enum": list(regra), "description": desc}
        else:
            props[k] = {"type": "string", "description": desc}
    return {"type": "object", "properties": props, "required": list(ESQUEMA_PERSONA), "additionalProperties": False}


def pedido(existentes: list[dict]) -> str:
    ja = "; ".join(f"{p['nome']}: {p['descricao']}" for p in existentes[-12:]) or "nenhuma ainda"
    return ("Crie UMA pessoa nova, bem diferente destas que ja existem: " + ja +
            ". Campos: " + "; ".join(f"{k} = {d}" for k, (_, _, d) in ESQUEMA_PERSONA.items()))


def gerar(provedor, gasto, n: int, semente_base: int) -> tuple[list[dict], str]:
    out: list[dict] = []
    modelo = "?"
    for i in range(n):
        for t in range(TENTATIVAS):
            try:
                d, modelo = chamar_json(provedor, gasto, SISTEMA, pedido(out), esquema_json(), semente_base + 1000 * t + i)
                nomes = {p["nome"] for p in out}
                base, k = d.get("nome", ""), 2
                while d.get("nome") in nomes:
                    d["nome"] = f"{base[:36]}-{k}"
                    k += 1
                validar_persona(d)
                out.append(d)
                print(f"  {i + 1}/{n} {d['nome']}", flush=True)
                break
            except (PersonaInvalida, LLMFalhou) as err:
                print(f"  {i + 1}/{n} tentativa {t + 1} falhou: {err}", flush=True)
        else:
            raise LLMFalhou(f"persona {i + 1} nao validou em {TENTATIVAS} tentativas")
    return out, modelo


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--provedor", choices=("ollama", "claude"), required=True)
    ap.add_argument("--modelo", default=None)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--lote", required=True, help="nome do arquivo (sem .json)")
    ap.add_argument("--semente", type=int, default=20260928)
    ap.add_argument("--limite-usd", type=float, default=1.0)
    a = ap.parse_args(argv)
    destino = PASTA / f"{a.lote}.json"
    if destino.exists():
        raise FileExistsError(f"{destino} ja existe: lote congelado nao e sobrescrito")
    provedor, gasto = abrir_provedor(a.provedor, a.modelo, a.limite_usd)
    personas, modelo = gerar(provedor, gasto, a.n, a.semente)
    meta = {"origem": "LLM", "provedor": a.provedor, "modelo": modelo, "versao_prompt": VERSAO_PROMPT,
            "semente": a.semente, "n": a.n, "data": date.today().isoformat(), "versao_esquema": "persona-v1"}
    PASTA.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps({"meta": meta, "personas": personas}, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    _, sha = carregar_lote(destino)
    print(f"lote {destino} ({len(personas)} personas) sha256 {sha}")
    if gasto is not None:
        print(f"gasto: {gasto.para_dict()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
