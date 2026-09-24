"""Servidor local do jogo web com fala por LLM (Parte C).

    python servidor/servidor_local.py            # porta 8765
    python servidor/servidor_local.py --porta 8765 --modelo claude-haiku-4-5 --limite-usd 2

Serve a pasta D:\\Trab\\digilab (a pai do repo) como o `python -m http.server`
fazia, entao os enderecos nao mudam:
    http://localhost:8765/v1/web/digilab_sprites.html
e acrescenta:
    GET  /api/fala/status   {"ativo": bool, "modelo": ..., "estatisticas": ...}
    POST /api/fala          {"motivo": {...}, "estagio": "...", "humor": 0.5}
                            -> {"texto": ..., "fonte": "llm"|"template", "detalhe": ...}

A chave da API fica so aqui (ANTHROPIC_API_KEY ou ANTHROPIC_AUTH_TOKEN no ambiente).
Teto de gasto TOTAL (padrao US$ 2, --limite-usd): acumulado em servidor/gasto_fala.json,
nao zera ao reiniciar; atingido o teto, so template.
Sem credencial, /api/fala devolve o template: a pagina funciona igual.
So escuta em 127.0.0.1.
"""

from __future__ import annotations

import argparse
import json
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from servidor.fala_llm import (  # noqa: E402
    LIMITE_USD_PADRAO,
    MODELO_PADRAO,
    ControleGasto,
    GeradorFala,
    criar_cliente,
    motivo_de_dict,
)

PASTA_SERVIDA = RAIZ.parent
LIMITE_CORPO = 16 * 1024


class Tratador(SimpleHTTPRequestHandler):
    gerador: GeradorFala = None  # definido em main()

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

    def do_GET(self) -> None:
        if self.path == "/api/fala/status":
            g = self.gerador
            return self._json(200, {"ativo": g.cliente is not None, "modelo": g.modelo, "estatisticas": g.estatisticas,
                                    "gasto": g.gasto.para_dict() if g.gasto else None})
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
        return self._json(200, {**resultado.para_dict(), "gasto": self.gerador.gasto.para_dict() if self.gerador.gasto else None})

    def log_message(self, formato, *args) -> None:
        if "/api/" in self.path:
            super().log_message(formato, *args)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Servidor local do Digilab com fala por LLM")
    ap.add_argument("--porta", type=int, default=8765)
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--limite-usd", type=float, default=LIMITE_USD_PADRAO,
                    help="teto TOTAL de gasto com a API (acumulado em servidor/gasto_fala.json)")
    a = ap.parse_args(argv)
    cliente = criar_cliente()
    gasto = ControleGasto(a.limite_usd) if cliente is not None else None
    Tratador.gerador = GeradorFala(cliente, modelo=a.modelo, gasto=gasto)
    estado = (f"LLM ativa ({a.modelo}); gasto US$ {gasto.gasto:.4f} de US$ {gasto.limite:.2f}" if cliente
              else "sem credencial: so template")
    servidor = ThreadingHTTPServer(("127.0.0.1", a.porta), partial(Tratador, directory=str(PASTA_SERVIDA)))
    print(f"Digilab em http://localhost:{a.porta}/v1/web/digilab_sprites.html  [{estado}]", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
