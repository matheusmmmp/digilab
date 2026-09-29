"""Gera um lote de personas de dono com LLM (educacao-v1, sistema E) e congela em experiments/personas/.

    python tools/gerar_personas.py --provedor ollama --n 20 --lote ollama-qwen-01
    python tools/gerar_personas.py --provedor claude --modelo claude-haiku-4-5 --n 50 --lote haiku-01 --limite-usd 1

Uma chamada por persona (saida pequena, validada uma a uma por digilab.personas.validar_persona; a que nao
valida e refeita com outra semente e o motivo da recusa no pedido, ate 5 vezes, e o lote falha alto se ainda assim nao validar).

Diversidade (personas-v2): mostrar as personas ja feitas fazia o modelo copiar (o lote v1 do gemma2 saiu todo
"zen"). Agora a variedade vem do desenho: cada persona recebe uma ROTINA de uma lista e FAIXAS para os quatro
numeros, tiradas de uma grade balanceada (3 niveis por numero, fatorial 3^4 embaralhado pela semente) e o
perfil de treino alternado. A LLM escreve a pessoa e escolhe os numeros dentro das faixas (conferido). As faixas
de cada persona ficam no `meta` do lote. O lote vai para o disco uma vez so; o sha256 impresso e o que o
protocolo da run registra. Nomes repetidos: sufixo numerico.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tools"))

from digilab.personas import ESQUEMA_PERSONA, PersonaInvalida, carregar_lote, validar_persona  # noqa: E402
from llm_pesquisa import LLMFalhou, abrir_provedor, chamar_json  # noqa: E402

VERSAO_PROMPT = "personas-v2"
# rotinas ficticias (pessoas comuns, nenhuma real): o "quem e" de cada persona
ROTINAS = (
    "estudante que assiste aula de dia e joga a noite", "enfermeira de plantao 12 por 36", "motorista de aplicativo com turnos longos",
    "aposentado com muito tempo livre", "pai de um bebe recem-nascido, dorme pouco", "programadora que trabalha de casa",
    "garcom do turno da noite", "professor com aulas de manha e a tarde", "atleta amadora que treina cedo",
    "vendedor que viaja a semana toda", "adolescente na escola, com celular so a noite", "cientista de laboratorio com horarios irregulares",
    "cozinheira de restaurante, fim de semana cheio", "freelancer que trabalha de madrugada", "agricultor que acorda as 4 h",
    "caminhoneira que passa dias na estrada",
)
NIVEIS = {"prob_atender_janela": ((0.1, 0.4), (0.4, 0.7), (0.7, 1.0)), "prob_ceder_petisco": ((0.0, 0.3), (0.3, 0.7), (0.7, 1.0)),
          "prob_feedback_coerente": ((0.1, 0.4), (0.4, 0.7), (0.7, 1.0)), "limiar_cuidado": ((0.1, 0.35), (0.35, 0.6), (0.6, 0.9))}


def plano(n: int, semente: int) -> list[dict]:
    """rotina, faixas e perfil de cada persona: fatorial 3^4 embaralhado (balanceado), rotinas em rodizio"""
    rng = random.Random(semente)
    combos = list(itertools.product(range(3), repeat=len(NIVEIS)))
    rng.shuffle(combos)
    rotinas = list(ROTINAS)
    rng.shuffle(rotinas)
    return [{"rotina": rotinas[i % len(rotinas)], "perfil_treino": ("atencioso", "exigente")[i % 2],
             "faixas": {k: NIVEIS[k][c[j]] for j, k in enumerate(NIVEIS)}} for i, c in enumerate(combos[i % len(combos)] for i in range(n))]


def conferir_plano(d: dict, p: dict) -> None:
    for k, (a, b) in p["faixas"].items():
        if not a <= d[k] <= b:
            raise PersonaInvalida(f"{k} = {d[k]} fora da faixa pedida [{a}, {b}]")
    if d["perfil_treino"] != p["perfil_treino"]:
        raise PersonaInvalida(f"perfil_treino = {d['perfil_treino']}, pedido {p['perfil_treino']}")
PASTA = RAIZ / "experiments" / "personas"
TENTATIVAS = 5

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
            props[k] = {"type": "string", "description": desc, "maxLength": 40 if k == "nome" else regra}
    return {"type": "object", "properties": props, "required": list(ESQUEMA_PERSONA), "additionalProperties": False}


def _campo(k: str, tipo, regra, desc: str) -> str:
    if tipo is float:
        return f"{k} = {desc} (numero decimal entre {regra[0]} e {regra[1]}, ex.: 0.35; NAO use porcentagem)"
    return f"{k} = {desc}"


def pedido(existentes: list[dict], p: dict, erro: str | None = None) -> str:
    nomes = ", ".join(x["nome"] for x in existentes) or "nenhum"
    faixas = "; ".join(f"{k} entre {a} e {b}" for k, (a, b) in p["faixas"].items())
    txt = (f"Crie UMA pessoa: {p['rotina']}. Os horarios em que ela olha o pet devem combinar com essa rotina. "
           f"Use EXATAMENTE estas faixas: {faixas}; perfil_treino = {p['perfil_treino']}. "
           f"Invente um nome curto novo (ja usados: {nomes}). Campos: " + "; ".join(_campo(k, *v) for k, v in ESQUEMA_PERSONA.items()))
    if erro:
        txt += f". ATENCAO: a tentativa anterior foi rejeitada ({erro}); corrija isso."
    return txt


def gerar(provedor, gasto, n: int, semente_base: int) -> tuple[list[dict], str, list[dict]]:
    out: list[dict] = []
    modelo = "?"
    planos = plano(n, semente_base)
    for i in range(n):
        erro = None
        for t in range(TENTATIVAS):
            try:
                d, modelo = chamar_json(provedor, gasto, SISTEMA, pedido(out, planos[i], erro), esquema_json(),
                                        semente_base + 1000 * t + i)
                nomes = {p["nome"] for p in out}
                base, k = d.get("nome", ""), 2
                while d.get("nome") in nomes:
                    d["nome"] = f"{base[:36]}-{k}"
                    k += 1
                validar_persona(d)
                conferir_plano(d, planos[i])
                out.append(d)
                print(f"  {i + 1}/{n} {d['nome']}", flush=True)
                break
            except (PersonaInvalida, LLMFalhou, TimeoutError, OSError) as err:     # rede/tempo: nova tentativa
                erro = str(err)
                print(f"  {i + 1}/{n} tentativa {t + 1} falhou: {err}", flush=True)
        else:
            raise LLMFalhou(f"persona {i + 1} nao validou em {TENTATIVAS} tentativas")
    return out, modelo, planos


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
    personas, modelo, planos = gerar(provedor, gasto, a.n, a.semente)
    meta = {"origem": "LLM", "provedor": a.provedor, "modelo": modelo, "versao_prompt": VERSAO_PROMPT,
            "semente": a.semente, "n": a.n, "data": date.today().isoformat(), "versao_esquema": "persona-v1",
            "planos": [{**p, "faixas": {k: list(v) for k, v in p["faixas"].items()}} for p in planos]}
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
