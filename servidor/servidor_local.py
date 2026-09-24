"""Servidor local do jogo web com fala por LLM (Parte C).

    python servidor/servidor_local.py                              # provedor auto, porta 8765
    python servidor/servidor_local.py --provedor ollama --modelo qwen2.5:3b
    python servidor/servidor_local.py --provedor claude --modelo claude-haiku-4-5 --limite-usd 2

Serve a pasta D:\\Trab\\digilab (a pai do repo) como o `python -m http.server`
fazia, entao os enderecos nao mudam:
    http://localhost:8765/v1/web/digilab_sprites.html
e acrescenta:
    GET  /api/fala/status   {"ativo", "provedor", "modelo", "motivo", "gasto", "estatisticas"}
    POST /api/fala          {"motivo": {...}, "estagio": "...", "humor": 0.5}
                            -> {"texto", "fonte": "llm"|"template", "detalhe", "gasto"}

Provedores (--provedor):
    auto    Ollama local se estiver rodando com o modelo; senao Claude se houver chave; senao so template
    ollama  modelo local (sem custo); padrao qwen2.5:3b
    claude  API do Claude (chave em ANTHROPIC_API_KEY); teto de gasto TOTAL --limite-usd (padrao 2),
            acumulado em servidor/gasto_fala.json
    nenhum  so template
So escuta em 127.0.0.1.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from servidor.fala_llm import (  # noqa: E402
    LIMITE_USD_PADRAO,
    URL_OLLAMA_PADRAO,
    GeradorFala,
    ProvedorOllama,
    escolher_provedor,
    motivo_de_dict,
)

PASTA_SERVIDA = RAIZ.parent
LIMITE_CORPO = 16 * 1024


class Tratador(SimpleHTTPRequestHandler):
    gerador: GeradorFala = None      # definido em main()
    motivo_inicial: str = ""

    def _json(self, codigo: int, dados: dict) -> None:
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def end_headers(self) -> None:
        # a pagina muda com frequencia durante o desenvolvimento: nada de cache velho
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def _status(self) -> dict:
        g, p = self.gerador, self.gerador.provedor
        if p is None:
            ativo, motivo = False, self.motivo_inicial
        else:
            ativo, motivo = p.disponivel()     # consultado ao vivo: o Ollama pode ser ligado depois
        return {"ativo": ativo, "provedor": None if p is None else p.nome, "modelo": g.modelo,
                "sem_custo": p is not None and not p.tem_custo, "motivo": motivo,
                "gasto": g.gasto.para_dict() if g.gasto else None, "estatisticas": g.estatisticas}

    def do_GET(self) -> None:
        if self.path == "/api/fala/status":
            return self._json(200, self._status())
        return super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/fala":
            return self._json(404, {"erro": "rota desconhecida"})
        tamanho = int(self.headers.get("Content-Length", "0"))
        if not 0 < tamanho <= LIMITE_CORPO:
            return self._json(400, {"erro": "corpo ausente ou grande demais"})
        try:
            dados = json.loads(self.rfile.read(tamanho))
            motivo = motivo_de_dict(dados["motivo"])
            estagio = dados["estagio"]
            humor = dados.get("humor")
            resultado = self.gerador.gerar(motivo, estagio, None if humor is None else float(humor))
        except (KeyError, ValueError, TypeError) as err:
            return self._json(400, {"erro": f"pedido invalido: {err}"})
        g = self.gerador
        return self._json(200, {**resultado.para_dict(), "gasto": g.gasto.para_dict() if g.gasto else None})

    def log_message(self, formato, *args) -> None:
        if "/api/" in self.path:
            super().log_message(formato, *args)


def _aquecer(p: ProvedorOllama) -> None:
    try:
        p.aquecer()
        print(f"  modelo {p.modelo} carregado", flush=True)
    except Exception as err:   # nao e fatal: a primeira fala so demora mais (ou cai no template)
        print(f"  aquecimento do Ollama falhou ({type(err).__name__}); as falas tentam de novo", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Servidor local do Digilab com fala por LLM")
    ap.add_argument("--porta", type=int, default=8765)
    ap.add_argument("--provedor", choices=("auto", "ollama", "claude", "nenhum"), default="auto")
    ap.add_argument("--modelo", default=None, help="padrao: qwen2.5:3b (ollama) ou claude-haiku-4-5 (claude)")
    ap.add_argument("--ollama-url", default=URL_OLLAMA_PADRAO)
    ap.add_argument("--limite-usd", type=float, default=LIMITE_USD_PADRAO,
                    help="teto TOTAL de gasto com a API do Claude (acumulado em servidor/gasto_fala.json)")
    a = ap.parse_args(argv)
    provedor, gasto, motivo = escolher_provedor(a.provedor, a.modelo, a.ollama_url, a.limite_usd)
    Tratador.gerador = GeradorFala(provedor, gasto=gasto)
    Tratador.motivo_inicial = motivo
    if provedor is None:
        estado = f"sem LLM: so template ({motivo})"
    elif provedor.nome == "ollama":
        estado = f"LLM local: Ollama {provedor.modelo}" + (f" — ainda indisponível: {motivo}" if motivo else "")
        if not motivo:
            threading.Thread(target=_aquecer, args=(provedor,), daemon=True).start()
    else:
        estado = f"LLM: Claude {provedor.modelo}; gasto US$ {gasto.gasto:.4f} de US$ {gasto.limite:.2f}"
    servidor = ThreadingHTTPServer(("127.0.0.1", a.porta), partial(Tratador, directory=str(PASTA_SERVIDA)))
    print(f"Digilab em http://localhost:{a.porta}/v1/web/digilab_sprites.html  [{estado}]", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
