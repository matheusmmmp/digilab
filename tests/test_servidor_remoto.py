"""Modo remoto do servidor (senha + rotas do jogo) e alertas de gasto. Sem rede externa."""

from __future__ import annotations

import base64
import threading
import urllib.error
import urllib.request
from functools import partial
from http.server import ThreadingHTTPServer

import pytest

from servidor.alerta import AlertaEmail
from servidor.fala_llm import ControleGasto, GeradorFala
from servidor.servidor_local import PASTA_SERVIDA, PREFIXO, PREFIXO_APP, Tratador, main, rota_permitida

SENHA = "senha-de-teste-123"


@pytest.fixture
def servidor():
    Tratador.gerador = GeradorFala(None)
    Tratador.motivo_inicial = "teste"
    Tratador.senha = SENHA
    Tratador.remoto = True
    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(Tratador, directory=str(PASTA_SERVIDA)))
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    Tratador.senha = None
    Tratador.remoto = False


def _get(url, senha=None):
    req = urllib.request.Request(url)
    if senha is not None:
        req.add_header("Authorization", "Basic " + base64.b64encode(f"eu:{senha}".encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as err:
        return err.code


def test_remoto_exige_senha(servidor):
    assert _get(servidor + PREFIXO + "/web/digilab_sprites.html") == 401
    assert _get(servidor + PREFIXO + "/web/digilab_sprites.html", "errada") == 401
    assert _get(servidor + PREFIXO + "/web/digilab_sprites.html", SENHA) == 200
    assert _get(servidor + "/api/fala/status", SENHA) == 200


def test_remoto_so_serve_as_rotas_do_jogo(servidor):
    for caminho in (PREFIXO + "/CLAUDE.md", PREFIXO + "/.git/config", PREFIXO + "/servidor/servidor_local.py", "/v0/",
                    "/Assets/catalogo_sprites.json", PREFIXO + "/web/../CLAUDE.md"):
        assert _get(servidor + caminho, SENHA) == 404, caminho
    assert rota_permitida("/Assets/digilab_atlas.png")


def test_remoto_serve_so_o_que_fica_dentro_do_build_do_app():
    p = PREFIXO_APP
    for ok in (p, p + "index.html", p + "assets/index-abc123.js", p + "assets/index.css?v=1", p[:-1]):
        assert rota_permitida(ok), ok
    for fora in (p + "../digilab_sprites.html", p + "../../CLAUDE.md", p + "%2e%2e/%2e%2e/CLAUDE.md", p + "assets/..%2f..%2f..%2fCLAUDE.md",
                 p + "..%5c..%5cCLAUDE.md", p + "./index.html", p[:-1] + "x/index.html", p.replace("/dist/", "/app/") + "index.html",
                 p.replace("/dist/", "/app/") + "package.json"):
        assert not rota_permitida(fora), fora


def test_remoto_nao_serve_o_codigo_do_app(servidor):
    for caminho in (PREFIXO + "/web/app/package.json", PREFIXO + "/web/app/src/main.tsx", PREFIXO_APP + "%2e%2e/%2e%2e/CLAUDE.md"):
        assert _get(servidor + caminho, SENHA) == 404, caminho


def test_remoto_sem_senha_forte_nao_sobe(monkeypatch):
    monkeypatch.setenv("DIGILAB_SENHA", "curta")
    with pytest.raises(SystemExit):
        main(["--remoto", "--provedor", "nenhum"])
    monkeypatch.delenv("DIGILAB_SENHA")
    with pytest.raises(SystemExit):
        main(["--claude-remoto", "--provedor", "nenhum"])


def test_alerta_dispara_uma_vez_por_nivel_e_persiste(tmp_path):
    avisos = []
    arq = tmp_path / "gasto.json"
    g = ControleGasto(2.0, arq, alerta=lambda n, d: avisos.append((n, d["gasto_usd"])))
    assert g.reservar(0.9)
    g.acertar(0.9, 0.9)            # 45%: nada
    assert avisos == []
    assert g.reservar(0.2)
    g.acertar(0.2, 0.2)            # 55%: 50%
    assert [n for n, _ in avisos] == [0.5]
    assert g.reservar(0.6)
    g.acertar(0.6, 0.6)            # 85%: 80%
    assert [n for n, _ in avisos] == [0.5, 0.8]
    assert not g.reservar(0.5)     # passaria do teto: recusa e avisa 100%
    assert [n for n, _ in avisos] == [0.5, 0.8, 1.0]
    assert not g.reservar(0.5)     # nao repete
    assert len(avisos) == 3
    avisos.clear()
    g2 = ControleGasto(2.0, arq, alerta=lambda n, d: avisos.append(n))
    assert not g2.reservar(0.5)    # reiniciar nao repete os avisos
    assert avisos == []


def test_alerta_sem_smtp_fica_desligado_e_nao_derruba():
    a = AlertaEmail("x@exemplo.com", ambiente={})
    assert not a.ativo and "DIGILAB_SMTP" in a.motivo_inativo()
    a.avisar(0.5, {"gasto_usd": 1.0, "limite_usd": 2.0, "chamadas": 3})   # so loga
    with pytest.raises(RuntimeError):
        a.enviar("assunto", "texto")


def test_remoto_sem_senha_continua_so_com_as_rotas_do_jogo(servidor):
    Tratador.senha = None
    assert _get(servidor + PREFIXO + "/web/digilab_sprites.html") == 200
    assert _get(servidor + PREFIXO + "/CLAUDE.md") == 404
    with pytest.raises(SystemExit):
        main(["--sem-senha", "--provedor", "nenhum"])


def test_sem_remoto_recusa_pedido_vindo_de_tunel(servidor):
    Tratador.senha = None
    Tratador.remoto = False
    req = urllib.request.Request(servidor + PREFIXO + "/web/digilab_sprites.html", headers={"Cf-Ray": "abc"})
    with pytest.raises(urllib.error.HTTPError) as err:
        urllib.request.urlopen(req, timeout=5)
    assert err.value.code == 403
    assert _get(servidor + PREFIXO + "/web/digilab_sprites.html") == 200     # local continua livre


def test_cliente_que_desconecta_nao_derruba_o_servidor(servidor, capsys):
    import socket
    from urllib.parse import urlparse

    u = urlparse(servidor)
    s = socket.create_connection((u.hostname, u.port))
    s.sendall(b"GET " + PREFIXO.encode() + b"/web/digilab_sprites.html HTTP/1.1\r\nHost: x\r\nAuthorization: Basic "
              + base64.b64encode(f"eu:{SENHA}".encode()) + b"\r\n\r\n")
    s.close()                                                         # fecha sem ler a resposta
    assert _get(servidor + "/api/fala/status", SENHA) == 200          # o servidor segue atendendo
