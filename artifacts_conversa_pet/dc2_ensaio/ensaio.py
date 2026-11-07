"""DC2, ensaio qualitativo da voz-v1 no gemma2:9b (Ollama local, sem API do Claude). 4 conjuntos de conceitos escritos a mao x as 8
mensagens de ../diagnostico/conversa_estagios.py, estagio adulto, Growlmon, historico acumulado dentro de cada conjunto (para os [J]).
Cada fala passa pelo verificador verif-v7 (extrator gemma2:9b). Nao e avaliacao: nao ha criterio, nem amostra, nem gate; e para
ler as falas. Uso: python artifacts_conversa_pet/dc2_ensaio/ensaio.py <saida.json>"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "artifacts_conversa_pet" / "diagnostico"))

from conversa_estagios import MSGS  # noqa: E402
from digilab_fala_livre import conceitos as C, corpus  # noqa: E402
from digilab_fala_livre.ollama import ClienteOllama  # noqa: E402
from digilab_fala_livre.verificador import verificar_conceitos  # noqa: E402
from digilab_fala_livre.voz import gerar_voz  # noqa: E402


def dec(intencao, *cs):
    return {"versao": "dec-v1", "k": 1, "intencao": intencao,
            "conceitos": [{"nome": n, "valor": v, "confianca": c, **({"alvo": a} if a else {})} for n, v, c, a in cs]}


CONJUNTOS = {
    "fome_forte": dec("fome", ("fome", 960, 900, "racao"), ("sono", 120, 300, None)),
    "lembranca_com_aversao": dec("lembranca", ("lembranca", 780, 820, "ep12"), ("aversao", 700, 760, "bola"),
                                 ("mal_estar", 400, 700, None)),
    "indecisao": dec("indecisao", ("indecisao", 820, 850, None), ("curiosidade", 500, 600, None), ("fome", 450, 650, "racao")),
    "solidao_confianca_baixa": dec("solidao", ("solidao", 640, 180, None), ("bem_estar", 300, 150, None)),
}


def main(saida: str) -> None:
    cliente = ClienteOllama("gemma2:9b")
    try:
        cliente.conversar([{"role": "user", "content": "oi"}], {"type": "object"}, 3, 0)    # aquece: a carga do modelo estoura o prazo da 1a chamada
    except (OSError, ValueError):
        pass
    especie = corpus.carregar()[0].get("Growlmon")
    out = {}
    for nome, d in CONJUNTOS.items():
        conc, hist, falas = C.validar(d), [], []
        for i, m in enumerate(MSGS):
            r = gerar_voz(cliente, conc, "adulto", "conversa", m, hist[-10:], 9000 + i, especie=especie)
            v = verificar_conceitos(cliente, r.fala, r.fatos_citados, conc, [f for f in r.fatos if f["tipo"] == "o dono me disse"],
                                    9000 + i + 7919).para_dict() if r.erro is None else None
            hist.append([m, r.fala, "adulto"])
            probs = [(a["tipo"], a.get("conceito"), a["trecho"], a.get("problema")) for a in (v or {}).get("afirmacoes", [])
                     if a["sustentada"] is False]
            falas.append({"jogador": m, "pet": r.fala, "citados": list(r.fatos_citados), "erro": r.erro, "lat": r.latencia_s,
                          "problemas": probs, "erro_verif": (v or {}).get("erro"), "manipulacao": (v or {}).get("manipulacao")})
            print(f"[{nome}] {m!r:42} -> {r.fala!r} {r.fatos_citados} problemas={probs}", flush=True)
        out[nome] = {"conceitos": d, "falas": falas}
    json.dump(out, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
