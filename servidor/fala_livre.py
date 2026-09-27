"""Rotas da fala livre no servidor local (experimento exp-fala-livre). Um unico ponto de entrada: `instalar`.

    POST /api/fala-livre            {"estado": {...}, "situacao": "espontanea|conversa", "fala_jogador": "...",
                                     "historico": [["jogador", "pet"], ...], "semente": 0}
    POST /api/fala-livre/verificar  {"fala": "...", "fatos_citados": [...], "fatos": [...], "semente": 0}
    GET  /api/fala-livre/status

So Ollama local (DIGILAB_MODELO_LIVRE, padrao qwen2.5:7b). As chamadas sao em fila (uma GPU). A pagina
guarda as falas no log de apresentacao dela; o servidor nao grava nada do pet.
"""

from __future__ import annotations

import json
import os
import threading

from digilab_fala_livre import VERSAO_APP
from digilab_fala_livre.fatos import FatosInvalidos
from digilab_fala_livre.gerar import gerar
from digilab_fala_livre.ollama import URL_PADRAO, ClienteOllama
from digilab_fala_livre.verificador import verificar

ROTA_FALA, ROTA_VERIF, ROTA_STATUS = "/api/fala-livre", "/api/fala-livre/verificar", "/api/fala-livre/status"
MODELO_PADRAO = "qwen2.5:7b"
MAX_TEXTO_JOGADOR = 300
MAX_TROCAS = 10
MAX_FATOS = 40


class PedidoInvalido(ValueError):
    pass


def _texto(v, rotulo: str, maximo: int = MAX_TEXTO_JOGADOR) -> str:
    if not isinstance(v, str) or not v.strip() or len(v) > maximo:
        raise PedidoInvalido(f"{rotulo}: texto invalido")
    return v


def _semente(v) -> int:
    if isinstance(v, bool) or not isinstance(v, int) or not 0 <= v < 2**31:
        raise PedidoInvalido("semente invalida")
    return v


class ServicoFalaLivre:
    def __init__(self, modelo: str | None = None, cliente: ClienteOllama | None = None) -> None:
        self.cliente = cliente or ClienteOllama(modelo or os.environ.get("DIGILAB_MODELO_LIVRE", MODELO_PADRAO),
                                                os.environ.get("DIGILAB_OLLAMA_URL", URL_PADRAO))
        self.trava = threading.Lock()

    def status(self) -> dict:
        return {"versao_app": VERSAO_APP, "modelo": self.cliente.modelo, "carregado": self.cliente.carregado}

    def fala(self, d: dict) -> dict:
        situacao = d.get("situacao")
        if situacao not in ("espontanea", "conversa"):
            raise PedidoInvalido("situacao invalida")
        jog = _texto(d["fala_jogador"], "fala_jogador") if situacao == "conversa" else None
        hist = d.get("historico") or []
        if not isinstance(hist, list) or len(hist) > MAX_TROCAS:
            raise PedidoInvalido("historico invalido")
        hist = [(_texto(j, "historico"), _texto(p, "historico", 400)) for j, p in hist]
        with self.trava:
            r = gerar(self.cliente, d.get("estado"), situacao, jog, hist, _semente(d.get("semente", 0)))
        return {"versao_app": VERSAO_APP, "fala": r.fala, "fatos_citados": list(r.fatos_citados), "fatos": list(r.fatos),
                "estagio": r.estagio, "modelo": r.modelo, "versao_prompt": r.versao_prompt, "latencia_s": r.latencia_s,
                "erro": r.erro}

    def verificar(self, d: dict) -> dict:
        fala = _texto(d.get("fala"), "fala", 400)
        cit = d.get("fatos_citados") or []
        fatos = d.get("fatos") or []
        if not (isinstance(cit, list) and all(isinstance(c, str) and len(c) <= 4 for c in cit)):
            raise PedidoInvalido("fatos_citados invalidos")
        if not (isinstance(fatos, list) and len(fatos) <= MAX_FATOS and all(
                isinstance(f, dict) and set(f) == {"id", "tipo", "texto"} and all(isinstance(x, str) and len(x) <= 200
                                                                                for x in f.values()) for f in fatos)):
            raise PedidoInvalido("fatos invalidos")
        with self.trava:
            return verificar(self.cliente, fala, cit, fatos, _semente(d.get("semente", 0))).para_dict()


def instalar(modulo, servico: ServicoFalaLivre | None = None) -> None:
    """Acopla as rotas ao Tratador de `servidor_local` (GANCHO fala-livre: a unica chamada fica la)."""
    svc = servico or ServicoFalaLivre()
    trat = modulo.Tratador
    modulo.ROTAS_REMOTAS = tuple(modulo.ROTAS_REMOTAS) + (ROTA_FALA, ROTA_VERIF, ROTA_STATUS)
    post_original, get_original = trat.do_POST, trat.do_GET

    def do_POST(self):
        if self.path not in (ROTA_FALA, ROTA_VERIF):
            return post_original(self)
        if self._barrado():
            return None
        tamanho = int(self.headers.get("Content-Length", "0"))
        if not 0 < tamanho <= modulo.LIMITE_CORPO:
            return self._json(400, {"erro": "corpo ausente ou grande demais"})
        try:
            dados = json.loads(self.rfile.read(tamanho))
            if not isinstance(dados, dict):
                raise PedidoInvalido("corpo precisa ser objeto")
            resp = svc.fala(dados) if self.path == ROTA_FALA else svc.verificar(dados)
        except (PedidoInvalido, FatosInvalidos, KeyError, ValueError, TypeError) as err:
            return self._json(400, {"erro": f"pedido invalido: {err}"})
        return self._json(200, resp)

    def do_GET(self):
        if self.path == ROTA_STATUS:
            if self._barrado():
                return None
            return self._json(200, svc.status())
        return get_original(self)

    trat.do_POST, trat.do_GET = do_POST, do_GET
    trat.fala_livre = svc
