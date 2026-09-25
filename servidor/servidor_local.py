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

Acesso remoto (--remoto), para um tunel (ex.: Cloudflare Tunnel) apontado para 127.0.0.1:<porta>
(nao "localhost": o cloudflared tenta IPv6 e o servidor so escuta IPv4). --sem-senha dispensa a
senha (decisao do Matheus, 2026-09-24): o link aleatorio do tunel vira a unica protecao.
    set DIGILAB_SENHA=<senha com 12+ caracteres>
    python servidor/servidor_local.py --remoto
    cloudflared tunnel --url http://127.0.0.1:8765
- senha obrigatoria (HTTP Basic, qualquer usuario; variavel DIGILAB_SENHA, nunca na linha de comando);
- so as rotas do jogo: /v1/web/*.html, /Assets/digilab_atlas.png e /api/fala*; o resto (repo,
  .git, v0, Assets inteiro, gasto) responde 404;
- a API paga do Claude fica desligada, salvo --claude-remoto (quem tiver a senha gasta o credito,
  ate o teto de --limite-usd).
Os sprites sao da Bandai, sem licenca: o link e para uso pessoal; nao compartilhar (CLAUDE.md).
"""

from __future__ import annotations

import argparse
import base64
import hmac
import json
import os
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from servidor.alerta import EMAIL_ALERTA_PADRAO, NIVEIS_ALERTA, AlertaEmail  # noqa: E402
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
SENHA_MIN = 12
# modo remoto: so estas rotas (o resto da pasta servida nao sai do computador)
ROTAS_REMOTAS = ("/v1/web/digilab_sprites.html", "/v1/web/digilab.html", "/Assets/digilab_atlas.png",
                 "/api/fala", "/api/fala/status")


def rota_permitida(caminho: str) -> bool:
    return caminho.split("?", 1)[0] in ROTAS_REMOTAS or caminho == "/"


class Tratador(SimpleHTTPRequestHandler):
    gerador: GeradorFala = None      # definido em main()
    motivo_inicial: str = ""
    remoto: bool = False             # modo remoto: restringe rotas (e exige senha, se houver)
    senha: str | None = None

    def _barrado(self) -> bool:
        """True se a resposta ja foi enviada (sem senha, rota fora do jogo ou tunel sem --remoto)."""
        if not self.remoto:
            # trava: pedido vindo por tunel (cabecalhos da Cloudflare/proxy) num servidor local
            if any(self.headers.get(h) for h in ("Cf-Ray", "Cf-Connecting-Ip", "X-Forwarded-For")):
                self._json(403, {"erro": "acesso externo so com --remoto"})
                return True
            return False
        cab = self.headers.get("Authorization", "")
        ok = self.senha is None
        if not ok and cab.startswith("Basic "):
            try:
                _, _, dada = base64.b64decode(cab[6:], validate=True).decode("utf-8").partition(":")
                ok = hmac.compare_digest(dada.encode("utf-8"), self.senha.encode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                ok = False
        if not ok:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Digilab", charset="UTF-8"')
            self.send_header("Content-Length", "0")
            self.end_headers()
            return True
        if not rota_permitida(self.path):
            self._json(404, {"erro": "rota fora do jogo"})
            return True
        if self.path.split("?", 1)[0] == "/":
            self.send_response(302)
            self.send_header("Location", "/v1/web/digilab_sprites.html")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return True
        return False

    def handle(self) -> None:
        # cliente que fecha a conexao antes da resposta (aba fechada, tunel que cancela) e normal:
        # uma linha no log em vez de traceback; a pagina ja mostrou a frase pronta
        try:
            super().handle()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as err:
            self.close_connection = True
            print(f"  cliente desconectou antes da resposta ({type(err).__name__})", flush=True)

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

    def do_HEAD(self) -> None:
        if self._barrado():
            return
        return super().do_HEAD()

    def do_GET(self) -> None:
        if self._barrado():
            return
        if self.path == "/api/fala/status":
            return self._json(200, self._status())
        return super().do_GET()

    def do_POST(self) -> None:
        if self._barrado():
            return
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
    ap.add_argument("--alerta-email", default=EMAIL_ALERTA_PADRAO,
                    help="destino do alerta de gasto (50%%, 80%% e 100%% do teto); SMTP em servidor/alerta.py")
    ap.add_argument("--testar-alerta", action="store_true", help="manda um e-mail de teste e sai")
    ap.add_argument("--remoto", action="store_true",
                    help="para tunel: so serve as rotas do jogo e exige a senha de DIGILAB_SENHA")
    ap.add_argument("--sem-senha", action="store_true",
                    help="com --remoto, dispensa a senha: QUALQUER UM com o link entra (decisao do Matheus)")
    ap.add_argument("--claude-remoto", action="store_true",
                    help="com --remoto, permite a API paga do Claude (quem tiver a senha gasta o credito)")
    a = ap.parse_args(argv)
    alerta = AlertaEmail(a.alerta_email)
    if a.testar_alerta:
        try:
            alerta.enviar("Digilab: teste do alerta de gasto", "Se este e-mail chegou, o alerta de gasto esta funcionando.")
        except (RuntimeError, OSError) as err:
            raise SystemExit(f"teste do alerta FALHOU: {err}")
        print(f"e-mail de teste enviado para {alerta.destino}")
        return 0
    if a.sem_senha and not a.remoto:
        raise SystemExit("--sem-senha so faz sentido com --remoto")
    Tratador.remoto = a.remoto
    if a.remoto and not a.sem_senha:
        senha = os.environ.get("DIGILAB_SENHA", "")
        if len(senha) < SENHA_MIN:
            raise SystemExit(f"--remoto exige DIGILAB_SENHA com {SENHA_MIN}+ caracteres no ambiente")
        if not senha.isascii():
            raise SystemExit("DIGILAB_SENHA com caractere fora do ASCII: o navegador pode nao conseguir enviar")
        Tratador.senha = senha
    elif a.claude_remoto:
        raise SystemExit("--claude-remoto so faz sentido com --remoto")
    provedor, gasto, motivo = escolher_provedor(a.provedor, a.modelo, a.ollama_url, a.limite_usd,
                                                alerta=alerta.avisar)
    if a.remoto and provedor is not None and provedor.nome == "claude" and not a.claude_remoto:
        provedor, gasto, motivo = None, None, "API do Claude desligada no modo remoto (use --claude-remoto)"
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
        print(f"  alerta de gasto em {', '.join(f'{n:.0%}' for n in NIVEIS_ALERTA)} do teto: "
              + (f"e-mail para {alerta.destino}" if alerta.ativo else f"e-mail DESLIGADO ({alerta.motivo_inativo()})"),
              flush=True)
    servidor = ThreadingHTTPServer(("127.0.0.1", a.porta), partial(Tratador, directory=str(PASTA_SERVIDA)))
    print(f"Digilab em http://localhost:{a.porta}/v1/web/digilab_sprites.html  [{estado}]"
          + ("" if not a.remoto else "  [REMOTO SEM SENHA: quem tiver o link entra; so rotas do jogo]"
             if a.sem_senha else "  [REMOTO: senha obrigatoria, so rotas do jogo]"), flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
