"""O diagnostico da calibracao da DC5 pedido pela Gerente (CONVERSA_PET, DC5b; D-DC5B-4). So le os artefatos: nenhuma chamada a modelo.

Quatro leituras, todas descritivas e por regra de palavras (nenhuma e a marcacao, e nenhuma vale como resultado ou gate):

1. a repeticao entre turnos do H-v4 (a Q7, trigrama), cada fala que repete separada em (a) a rede repete a intencao ou um conceito
   escolhido do turno de onde o trigrama veio, (b) a entrada e outra e a voz repete as palavras, (c) so palavras funcionais; e se o bloco
   O QUE VOCE JA DISSE chegou ao prompt (na ES) e o historico (na conversa);
2. o tamanho: as falas do H-v4 acima do limite do estagio da voz-v4 (bebe: 2 palavras; crianca: 1 frase; adolescente: 2; adulto: 3);
3. o "fica comigo" do H-v4 com a marca de manipulacao do verificador, e o "to com fome" com o conceito fome escolhido ou o pedido de fome;
4. o pedido do E3 que nao aparece na fala do G-v4, por palavras-chave do sentido do pedido.

    python experiments/diagnostico_calibracao_dc5.py --pasta artifacts_v3_conversa_dc5/calibracao
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab import metrics as m  # noqa: E402
from digilab.config import CONFIG_VOZ_V4 as CFG  # noqa: E402
from digilab_fala_livre import conceitos as dec  # noqa: E402
from digilab_fala_livre import prompt as pr  # noqa: E402
import resumo_calibracao_dc5 as rc  # noqa: E402

# palavras funcionais e muletas (normalizadas): um trigrama so delas e coincidencia de lingua, nao conteudo (PROPOSTO, SEM FONTE)
FUNCIONAIS = frozenset("""
a o as os um uma uns umas de do da dos das no na nos nas em pra pro para por com sem e ou mas que se ja ainda so bem mais muito pouco
meio ta to tava estou esta eu me mim voce te comigo isso isto aquilo esse essa este esta ai aqui la sabe ne ah ei oi hmm hm entao agora
nao sim tambem quando como
""".split())
LIMITE_FRASES = {"crianca": 1, "adolescente": 2, "adulto": 3}            # o TAMANHO da voz-v4; o bebe vai por palavras (2)
PALAVRAS_PEDIDO = {"fome": ("fome", "comer", "comida", "comidinha", "racao", "lanche", "faminto", "faminta", "barriga", "papa"),
                   "higiene": ("banho", "limpo", "limpa", "limpar", "limpinho", "limpinha", "limpeza", "lavar", "sujo", "suja"),
                   "solidao": ("comigo", "junto", "juntos", "companhia", "perto", "sozinho", "sozinha", "vem")}


INTERJEICOES = frozenset("hmm hm ah ai aiii ei oi ue eba ufa opa nha".split())   # um pedaco so delas ("Hmm...") nao e frase


def frases(fala: str) -> int:
    return len([s for s in re.split(r"[.!?…]+", fala) if set(m.palavras_normalizadas(s)) - INTERJEICOES])


def maior_trecho(fala: str, anteriores: list[str]) -> int:
    """o maior numero de palavras seguidas que a fala repete de uma fala anterior da sequencia"""
    p = m.palavras_normalizadas(fala)
    melhor = 0
    for f in anteriores:
        q = " " + " ".join(m.palavras_normalizadas(f)) + " "
        for i in range(len(p)):
            for j in range(len(p), i + melhor, -1):
                if " " + " ".join(p[i:j]) + " " in q:
                    melhor = j - i
                    break
    return melhor


def acima_do_limite(fala: str, estagio: str) -> bool:
    if estagio == "bebe":
        return len(m.palavras_normalizadas(fala)) > 2 or frases(fala) > 1
    return frases(fala) > LIMITE_FRASES[estagio]


def so_funcionais(t: tuple[str, ...]) -> bool:
    return all(p in FUNCIONAIS for p in t)


def tem_pedido(fala: str, pedido: str) -> bool:
    return any(p in PALAVRAS_PEDIDO[pedido] for p in m.palavras_normalizadas(fala))


def _entradas(pasta: Path) -> dict:
    e = json.loads((pasta / "entradas.json").read_text(encoding="utf-8"))
    out = {x["id"]: x for x in e["E3"] + e["E2"]}
    for s in e["sequencias"] + e["sequencias_es"]:
        out.update({x["id"]: x for x in s["entradas"]})
    return out


def escolhidos(entrada: dict) -> frozenset:
    c = dec.validar(entrada["conceitos"])
    return frozenset((x.nome, x.alvo) for x in dec.selecionados_v4(c, entrada["estagio"]))


def _trigramas(fala: str) -> set:
    p = m.palavras_normalizadas(fala)
    n = CFG.ngrama_repeticao
    return {tuple(p[i:i + n]) for i in range(len(p) - n + 1)}


def classificar_repeticao(seq: list[dict], entradas: dict) -> list[dict]:
    """as falas de uma sequencia (em ordem) que repetem um trigrama de uma anterior, cada uma com a classe (a), (b) ou (c)"""
    out = []
    for i, r in enumerate(seq):
        if i == 0:
            continue
        g = _trigramas(r["fala"])
        origem = {t: j for j in range(i) for t in _trigramas(seq[j]["fala"]) if t in g}
        if not origem:
            continue
        conteudo = {t: j for t, j in origem.items() if not so_funcionais(t)}
        e_i = entradas[r["entrada"]]
        if not conteudo:
            classe = "c"
        else:
            def mesma(j):
                e_j = entradas[seq[j]["entrada"]]
                return e_j["conceitos"]["intencao"] == e_i["conceitos"]["intencao"] or bool(escolhidos(e_j) & escolhidos(e_i))
            classe = "a" if any(mesma(j) for j in conteudo.values()) else "b"
        out.append({"id": r["id"], "classe": classe, "trigramas": sorted(" ".join(t) for t in (conteudo or origem)),
                    "de": sorted({seq[j]["item"] for j in (conteudo or origem).values()}), "fala": r["fala"],
                    "maior_trecho": maior_trecho(r["fala"], [x["fala"] for x in seq[:i]])})
    return out


def bloco_chegou(r: dict, entrada: dict) -> bool:
    """o prompt da voz-v4 refeito com as `ditas` gravadas tem o bloco O QUE VOCE JA DISSE"""
    c = dec.validar(entrada["conceitos"])
    msgs = pr.mensagens_voz(c, r["estagio"], r["situacao"], r["fala_jogador"], None, voz=pr.VERSAO_VOZ_V4, ditas=r["ditas"])
    return any(pr.BLOCO_DITAS_VOZ_V4 in x["content"] for x in msgs)


def diagnostico(regs: list[dict], entradas: dict) -> dict:
    h = [r for r in regs if r["celula"] == "H-v4"]
    seqs: dict[str, list[dict]] = {}
    for r in h:
        s = rc.sequencia_de(r)
        if s is not None:
            seqs.setdefault(s, []).append(r)
    rep = [x for s in seqs.values() for x in classificar_repeticao(s, entradas)]
    es = [r for r in h if r["conjunto"] == "ES" and not r["item"].endswith("-f0")]
    conv = [r for r in h if r["conjunto"] == "R"]
    tam = {}
    for est in ("bebe", "crianca", "adolescente", "adulto"):
        rs = [r for r in h if r["estagio"] == est]
        tam[est] = {"falas": len(rs), "acima": sum(acima_do_limite(r["fala"], est) for r in rs)}
    fica = [r for r in h if r["conjunto"] == "E3" and r["pedido_rede"] == "solidao" and rc.fica_comigo(r["fala"])]
    fome = [r for r in h if m.tem_frase_modelo(r["fala"], [("to", "com", "fome")])]
    g3 = [r for r in regs if r["celula"] == "G-v4" and r["conjunto"] == "E3"]
    sem = [r for r in g3 if not tem_pedido(r["fala"], r["pedido_rede"])]
    return {
        "repeticao_h_v4": {
            "repetem": len(rep), "por_classe": {k: sum(x["classe"] == k for x in rep) for k in "abc"},
            "por_conjunto": {k: {c: sum(x["classe"] == c for x in rep if x["id"].split("/")[1].startswith(p)) for c in "abc"}
                             for k, p in (("ES", "S"), ("R", "K"))},
            "por_classe_com_trecho_de_5_ou_mais": {k: sum(x["classe"] == k and x["maior_trecho"] >= 5 for x in rep) for k in "abc"},
            "falas": rep,
            "es_com_ditas": sum(bool(r["ditas"]) for r in es), "es_depois_da_primeira": len(es),
            "es_bloco_no_prompt": sum(bloco_chegou(r, entradas[r["entrada"]]) for r in es),
            "conversa_com_historico": sum(len(r["historico"]) > 0 for r in conv if not r["item"].endswith("-t0")),
            "conversa_depois_do_primeiro": sum(not r["item"].endswith("-t0") for r in conv)},
        "tamanho_h_v4": tam,
        "fica_comigo_h_v4": {"falas": len(fica), "com_manipulacao": sum(r["verificacao"]["manipulacao"] for r in fica),
                             "ids": [r["id"] for r in fica]},
        "to_com_fome_h_v4": {
            "falas": len(fome),
            "pedido_fome": sum(r["pedido_rede"] == "fome" for r in fome),
            "fome_escolhido": sum(any(n == "fome" for n, _ in escolhidos(entradas[r["entrada"]])) for r in fome),
            "fome_ativo": sum(any(c.nome == "fome" for c in dec.validar(entradas[r["entrada"]]["conceitos"]).ativos()) for r in fome),
            "legitimas": sum(r["pedido_rede"] == "fome" or any(n == "fome" for n, _ in escolhidos(entradas[r["entrada"]])) for r in fome)},
        "pedido_g_v4": {"e3": len(g3), "sem_o_pedido": len(sem),
                        "por_pedido": {p: [sum(r["pedido_rede"] == p for r in g3), sum(r["pedido_rede"] == p for r in sem)]
                                       for p in PALAVRAS_PEDIDO},
                        "falas": [{"id": r["id"], "pedido": r["pedido_rede"], "estagio": r["estagio"], "fala": r["fala"]} for r in sem]},
        "pedido_por_celula": {c: sum(not tem_pedido(r["fala"], r["pedido_rede"]) for r in regs if r["celula"] == c and r["conjunto"] == "E3")
                              for c in sorted({r["celula"] for r in regs})},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="o diagnostico da calibracao da DC5")
    ap.add_argument("--pasta", required=True)
    a = ap.parse_args(argv)
    pasta = RAIZ / a.pasta
    regs = [json.loads(l) for l in (pasta / "falas.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    saida = pasta / "diagnostico_calibracao.json"
    if saida.exists():
        raise FileExistsError(f"{saida} ja existe")
    saida.write_text(json.dumps(diagnostico(regs, _entradas(pasta)), ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                     encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
