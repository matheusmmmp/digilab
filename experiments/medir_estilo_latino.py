"""Mede o efeito do filtro do alfabeto no bloco de estilo (corpus.carregar(so_latino)) na CONVERSA da voz propria.

    python experiments/medir_estilo_latino.py            -> artifacts_voz/estilo_latino/{respostas.jsonl,resumo.json,RELATORIO.md}

30 mensagens escritas a mao x 3 especies cujo corpus descreve o registro japones (Angemon, Gabumon, Garurumon), prompt
livre-v6 na conversa (o do jogo), gemma2:9b, uma semente por mensagem, nos dois modos: COM o filtro (o servidor de hoje)
e SEM (o de antes). Metrica: fracao de respostas que `saida.ler` rejeita por letra fora do alfabeto latino (a fala vira
"…" no jogo). So Ollama local; nenhum numero no relatorio sem este artefato.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab_fala_livre import VERSAO_APP, corpus  # noqa: E402
from digilab_fala_livre.gerar import gerar  # noqa: E402
from digilab_fala_livre.ollama import ClienteOllama  # noqa: E402
from digilab_fala_livre.prompt import VERSAO_PROMPT_V6  # noqa: E402

SAIDA = RAIZ / "artifacts_voz" / "estilo_latino"
SEMENTE = 20261006
MODELO = "gemma2:9b"
MENSAGENS = ("oi, tudo bem?", "como foi seu dia?", "você lembra do que aconteceu ontem?", "me conta uma história",
             "eu tive um dia cansativo no trabalho", "qual é o seu Digimon favorito?", "você tem medo do escuro?",
             "o que você acha do Piedmon?", "eu tô com saudade de você", "por que você fez isso mais cedo?",
             "você gosta de mim?", "boa noite, até amanhã", "tá chovendo aqui hoje", "o que você sonhou?",
             "você quer evoluir?", "quem é seu melhor amigo?", "hoje eu comi pizza", "me explica como funciona a arena",
             "você já lutou na Floresta?", "vai comer", "toma banho", "vamos brincar!", "não come agora, espera",
             "você quer comer?", "você tá com fome?", "está doendo o machucado?", "muito bem! você foi ótimo hoje",
             "isso foi feio, não faz mais isso", "quer brincar mais tarde?", "amanhã a gente brinca")
PETS = (
    {"identidade": {"estagio": "adulto", "especie": "Amizade", "forma": "Angemon"},
     "temperamento": {"curiosidade": 0.5, "teimosia": 0.1, "sensibilidade": 0.3, "rancor": -0.1},
     "estado": {"fome": 0.7, "higiene": 0.5, "energia": 0.6, "humor": 0.7, "saude": 0.9}, "vinculo": 0.6,
     "historia": [{"tipo": "O", "regra": "demora", "chave": "O:demora", "texto": "você atende meus chamados rápido",
                   "dados": {"rapido": True}}]},
    {"identidade": {"estagio": "crianca", "especie": "Amizade", "forma": "Gabumon"},
     "temperamento": {"curiosidade": 0.3, "teimosia": -0.4, "sensibilidade": 0.6, "rancor": 0.0},
     "estado": {"fome": 0.5, "higiene": 0.6, "energia": 0.9, "humor": 0.8, "saude": 1.0}, "vinculo": 0.5, "historia": []},
    {"identidade": {"estagio": "adolescente", "especie": "Amizade", "forma": "Garurumon", "linha": "cacador"},
     "temperamento": {"curiosidade": 0.1, "teimosia": 0.6, "sensibilidade": -0.2, "rancor": 0.3},
     "estado": {"fome": 0.3, "higiene": 0.8, "energia": 0.4, "humor": 0.4, "saude": 0.7}, "vinculo": 0.3,
     "historia": [{"tipo": "P", "regra": "gosto", "chave": "P:gosto:brincar", "texto": "gosto de brincar",
                   "dados": {"acao": "brincar"}}]},
)


def main() -> int:
    assert len(MENSAGENS) == 30
    com, _, sha = corpus.carregar(so_latino=True)
    sem, _, _ = corpus.carregar(so_latino=False)
    for p in PETS:
        assert p["identidade"]["forma"] in com and sem[p["identidade"]["forma"]].descartados.get("NAO LATINO", 0) == 0
        assert com[p["identidade"]["forma"]].descartados.get("NAO LATINO", 0) > 0, p["identidade"]["forma"]
    cli = ClienteOllama(MODELO)
    gerar(cli, PETS[0], "conversa", "oi", semente=0, versao=VERSAO_PROMPT_V6)          # aquece
    linhas, t0 = [], time.perf_counter()
    for i, txt in enumerate(MENSAGENS):
        pet = PETS[i % 3]
        forma = pet["identidade"]["forma"]
        for modo, esps in (("com_filtro", com), ("sem_filtro", sem)):
            r = gerar(cli, pet, "conversa", txt, semente=SEMENTE + i, versao=VERSAO_PROMPT_V6, especie=esps[forma])
            rej = bool(r.erro) and "alfabeto latino" in r.erro
            linhas.append({"i": i, "mensagem": txt, "forma": forma, "modo": modo, "semente": SEMENTE + i, "fala": r.fala,
                           "erro": r.erro, "rejeitada_nao_latino": rej, "latencia_s": r.latencia_s})
        print(f"{i + 1:2d}/30 {forma:<10} {txt[:32]!r:<36} com: {linhas[-2]['fala'][:40]!r} | sem: {linhas[-1]['fala'][:40]!r}", flush=True)
    cli.descarregar()
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "respostas.jsonl").write_text("".join(json.dumps(l, ensure_ascii=False, sort_keys=True) + "\n" for l in linhas),
                                          encoding="utf-8", newline="\n")
    res = {}
    for modo in ("com_filtro", "sem_filtro"):
        sel = [l for l in linhas if l["modo"] == modo]
        res[modo] = {"n": len(sel), "rejeitadas_nao_latino": sum(l["rejeitada_nao_latino"] for l in sel),
                     "taxa_rejeitadas": sum(l["rejeitada_nao_latino"] for l in sel) / len(sel),
                     "outros_erros": sum(bool(l["erro"]) and not l["rejeitada_nao_latino"] for l in sel),
                     "por_forma": {f: sum(l["rejeitada_nao_latino"] for l in sel if l["forma"] == f) for f in ("Angemon", "Gabumon", "Garurumon")}}
    out = {"versao_app": VERSAO_APP, "modelo": MODELO, "semente": SEMENTE, "prompt": VERSAO_PROMPT_V6, "corpus_sha256": sha,
           "descartados_nao_latino_no_corpus": sum(e.descartados.get("NAO LATINO", 0) for e in com.values()),
           "especies_com_descarte": sum(1 for e in com.values() if e.descartados.get("NAO LATINO", 0)), "especies": len(com),
           "resultado": res, "tempo_total_s": time.perf_counter() - t0}
    (SAIDA / "resumo.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    pc = lambda v: f"{100 * v:.1f}%"  # noqa: E731
    rel = ["# Filtro do alfabeto no bloco de estilo — conversa da voz própria", "",
           f"{MODELO}, prompt {VERSAO_PROMPT_V6}, 30 mensagens × 3 espécies (uma semente por mensagem). Números de `resumo.json` e `respostas.jsonl`.", "",
           f"Corpus: {out['especies']} espécies, {out['especies_com_descarte']} com item não latino, {out['descartados_nao_latino_no_corpus']} itens fora do estilo com o filtro.", "",
           "| modo | n | rejeitadas por letra não latina | outros erros |", "|---|---|---|---|"]
    rel += [f"| {m} | {r['n']} | {r['rejeitadas_nao_latino']} ({pc(r['taxa_rejeitadas'])}) | {r['outros_erros']} |" for m, r in res.items()]
    rel += ["", "Por espécie (rejeitadas com / sem filtro): " + ", ".join(
        f"{f} {res['com_filtro']['por_forma'][f]}/{res['sem_filtro']['por_forma'][f]}" for f in ("Angemon", "Gabumon", "Garurumon")), ""]
    (SAIDA / "RELATORIO.md").write_text("\n".join(rel), encoding="utf-8", newline="\n")
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
