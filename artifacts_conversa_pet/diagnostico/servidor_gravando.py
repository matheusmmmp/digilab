"""Servidor local do worktree com um gravador: cada chamada ao Ollama (mensagens, esquema, saida, latencia) vai para um
JSONL no scratchpad. So para o diagnostico da conversa; nao muda nada do repositorio."""
import json
import os
import sys
import time

RAIZ = r"D:\Trab\digilab\v3-conversa-diagnostico"
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chamadas_ollama.jsonl")
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)

from digilab_fala_livre import ollama  # noqa: E402

_original = ollama.ClienteOllama.conversar


def conversar(self, mensagens, esquema, max_tokens, semente):
    r = _original(self, mensagens, esquema, max_tokens, semente)
    with open(SAIDA, "a", encoding="utf-8") as f:
        f.write(json.dumps({"t": time.time(), "modelo": self.modelo, "mensagens": mensagens, "esquema": esquema,
                            "max_tokens": max_tokens, "semente": semente, "saida": r.texto,
                            "latencia_s": r.latencia_s, "completa": r.completa,
                            "tokens_entrada": r.tokens_entrada, "tokens_saida": r.tokens_saida}, ensure_ascii=False) + "\n")
    return r


ollama.ClienteOllama.conversar = conversar

from servidor import servidor_local  # noqa: E402

sys.exit(servidor_local.main(sys.argv[1:]))
