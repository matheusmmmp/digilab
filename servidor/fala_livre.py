"""Rotas da fala livre no servidor local (experimento exp-fala-livre). Um unico ponto de entrada: `instalar`.

    POST /api/fala-livre            {"estado": {...}, "situacao": "espontanea|conversa", "fala_jogador": "...",
                                     "historico": [["jogador", "pet"], ...], "semente": 0}
    POST /api/fala-livre/verificar  {"fala": "...", "fatos_citados": [...], "fatos": [...], "semente": 0}
    GET  /api/fala-livre/status

So Ollama local (DIGILAB_MODELO_LIVRE, padrao gemma2:9b). As chamadas sao em fila (uma GPU). A pagina
guarda as falas no log de apresentacao dela; o servidor nao grava nada do pet.

Voz propria (DESIGN_VOZ_PROPRIA, parte 4; pedido com "voz": true, pets v5): prompt livre-v6 (o pet pode inventar,
opinar e cobrar), autocorrecao pelo proprio modelo (so volta manipulacao; a fala que nao pode ser verificada e cortada),
verificador verif-v5 (cada invencao fica marcada), estilo da especie pelo corpus (identidade.forma) e o almanaque do
Digimundo (com "internet": true, na espontanea, chance almanaque.CHANCE_ESPONTANEA sorteada da semente) e a arvore
da especie (fato A1, arvore.py). A resposta
traz a verificacao da versao escolhida. Sem "voz", tudo como antes (livre-v2, verif-v3).
"""

from __future__ import annotations

import json
import os
import random
import threading

from digilab_fala_livre import VERSAO_APP
from digilab_fala_livre.fatos import FatosInvalidos
from digilab_fala_livre import almanaque, corpus
from digilab_fala_livre.arvore import ARVORE
from digilab_fala_livre.gerar import gerar
from digilab_fala_livre.ollama import URL_PADRAO, ClienteOllama
from digilab_fala_livre.prompt import VERSAO_PROMPT_V6
from digilab_fala_livre.revisao import gerar_com_revisao
from digilab_fala_livre.verificador import VERSAO_VERIFICADOR_V5, verificar

ROTA_FALA, ROTA_VERIF, ROTA_STATUS = "/api/fala-livre", "/api/fala-livre/verificar", "/api/fala-livre/status"
MODELO_PADRAO = "gemma2:9b"          # escolhido na rodada 2 (artifacts_fala_livre/rodada2/RELATORIO.md)
MAX_TEXTO_JOGADOR = 300
MAX_TROCAS = 10
MAX_FATOS = 40
# chaves de registro que a fala da voz propria devolve em cada fato (Fato.meta) e a pagina manda de volta
META_FATO = {"regra": str, "chave": str, "dados": dict, "mentira": bool, "verdade": str, "molde": str,
             "almanaque": str}


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
        self.especies, meta, self.corpus_sha = corpus.carregar()
        self.corpus_exemplo = bool(meta["exemplo"])
        self.almanaque_sha = almanaque.carregar()[1]

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
        semente = _semente(d.get("semente", 0))
        if d.get("voz") is True:
            return self._fala_voz(d, situacao, jog, hist, semente)
        with self.trava:
            r = gerar(self.cliente, d.get("estado"), situacao, jog, hist, semente)
        return {"versao_app": VERSAO_APP, "fala": r.fala, "fatos_citados": list(r.fatos_citados), "fatos": list(r.fatos),
                "estagio": r.estagio, "modelo": r.modelo, "versao_prompt": r.versao_prompt, "latencia_s": r.latencia_s,
                "erro": r.erro}

    def _fala_voz(self, d: dict, situacao: str, jog, hist, semente: int) -> dict:
        estado = d.get("estado")
        if not isinstance(estado, dict):
            raise PedidoInvalido("estado invalido")
        internet = d.get("internet", False)
        rival = d.get("rival")
        if not isinstance(internet, bool) or (rival is not None and not isinstance(rival, str)):
            raise PedidoInvalido("internet ou rival invalidos")
        if "almanaque" in estado or "arvore" in estado:
            raise PedidoInvalido("o almanaque e a arvore sao do servidor")
        estado = dict(estado)
        if (estado.get("identidade") or {}).get("especie") in ARVORE:
            estado["arvore"] = True                      # o pet sabe a arvore da especie dele (fato A1)
        if internet and situacao == "espontanea" and "mentira" not in estado:
            w = almanaque.sortear(random.Random(semente))
            if w is not None:
                estado["almanaque"] = {"id": w}
                estado["historia"] = []                  # o assunto passa a ser o que ele ouviu no Digimundo
        forma = (estado.get("identidade") or {}).get("forma")
        especie = self.especies.get(forma.removesuffix(" sombrio")) if isinstance(forma, str) else None
        with self.trava:
            r, tent = gerar_com_revisao(self.cliente, estado, situacao, semente, jog, hist, versao=VERSAO_PROMPT_V6,
                                        especie=especie, rival=rival, versao_verificador=VERSAO_VERIFICADOR_V5,
                                        so_respeito=True)
        escolhida = next((x for x in reversed(tent) if x.get("fala") == r.fala), None)
        return {"versao_app": VERSAO_APP, "fala": r.fala, "fatos_citados": list(r.fatos_citados), "fatos": list(r.fatos),
                "estagio": r.estagio, "modelo": r.modelo, "versao_prompt": r.versao_prompt, "latencia_s": r.latencia_s,
                "erro": r.erro, "verificacao": escolhida["verificacao"] if escolhida else None,
                "invencoes": escolhida["invencoes"] if escolhida else [], "revisoes": max(0, len(tent) - 1),
                "especie_corpus": r.especie, "corpus_sha256": self.corpus_sha, "corpus_exemplo": self.corpus_exemplo,
                "almanaque_sha256": self.almanaque_sha}

    def verificar(self, d: dict) -> dict:
        fala = _texto(d.get("fala"), "fala", 400)
        cit = d.get("fatos_citados") or []
        fatos = d.get("fatos") or []
        if not (isinstance(cit, list) and all(isinstance(c, str) and len(c) <= 4 for c in cit)):
            raise PedidoInvalido("fatos_citados invalidos")
        if not (isinstance(fatos, list) and len(fatos) <= MAX_FATOS and all(_fato_ok(f) for f in fatos)):
            raise PedidoInvalido("fatos invalidos")
        versao = VERSAO_VERIFICADOR_V5 if d.get("voz") is True else None
        with self.trava:
            if versao is None:
                return verificar(self.cliente, fala, cit, fatos, _semente(d.get("semente", 0))).para_dict()
            return verificar(self.cliente, fala, cit, fatos, _semente(d.get("semente", 0)), versao=versao).para_dict()


def _fato_ok(f) -> bool:
    """{id, tipo, texto} em texto curto, mais as chaves de registro da voz propria (META_FATO), cada uma no tipo dela"""
    if not isinstance(f, dict) or not {"id", "tipo", "texto"} <= set(f) or set(f) - {"id", "tipo", "texto"} - set(META_FATO):
        return False
    if not all(isinstance(f[k], str) and len(f[k]) <= 200 for k in ("id", "tipo", "texto")):
        return False
    for k, tipo in META_FATO.items():
        if k in f and not isinstance(f[k], tipo):
            return False
        if tipo is str and k in f and len(f[k]) > 200:
            return False
    return "dados" not in f or len(json.dumps(f["dados"])) <= 400


def instalar(modulo, servico: ServicoFalaLivre | None = None) -> None:
    """Acopla as rotas ao Tratador de `servidor_local` (GANCHO fala-livre: a unica chamada fica la)."""
    svc = servico or ServicoFalaLivre()
    trat = modulo.Tratador
    modulo.ROTAS_REMOTAS = tuple(modulo.ROTAS_REMOTAS) + (ROTA_FALA, ROTA_VERIF, ROTA_STATUS,
                                                         f"{modulo.PREFIXO}/web/modulos/fala_livre.js")
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
