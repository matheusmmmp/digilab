"""Rotas da fala livre no servidor local (experimento exp-fala-livre). Um unico ponto de entrada: `instalar`.

    POST /api/fala-livre            {"estado": {...}, "situacao": "espontanea|conversa", "fala_jogador": "...",
                                     "historico": [["jogador", "pet"], ...], "semente": 0}
    POST /api/fala-livre/verificar  {"fala": "...", "fatos_citados": [...], "fatos": [...], "semente": 0}
    GET  /api/fala-livre/status

Provedor (CONVERSA_PET M5, decisao D5): `DIGILAB_PROVEDOR_LIVRE` = `ollama` (padrao, local, gemma2:9b) ou `claude` (API; teto
de gasto proprio, `--limite-usd-livre`, arquivo `servidor/gasto_fala_livre.json`); `DIGILAB_MODELO_LIVRE` escolhe o modelo. O
verificador tem cliente proprio (`DIGILAB_PROVEDOR_VERIF`, `DIGILAB_MODELO_VERIF`; padrao ollama gemma2:9b: o plano fixa o mesmo
verificador em todos os bracos). Com --remoto o provedor Claude fica desligado salvo --claude-remoto. As chamadas sao em fila
(uma GPU). A pagina guarda as falas no log de apresentacao dela; o servidor nao grava nada do pet.

Voz propria (DESIGN_VOZ_PROPRIA, parte 4; pedido com "voz": true, pets v5): prompt livre-v6 (o pet pode inventar,
opinar e cobrar), autocorrecao pelo proprio modelo (so volta manipulacao; a fala que nao pode ser verificada e cortada),
verificador verif-v5 (cada invencao fica marcada), estilo da especie pelo corpus (identidade.forma) e o almanaque do
Digimundo (com "internet": true, na espontanea, chance almanaque.CHANCE_ESPONTANEA sorteada da semente) e a arvore
da especie (fato A1, arvore.py). A resposta
traz a verificacao da versao escolhida. Sem "voz", tudo como antes (livre-v2, verif-v3).

Comando pelo chat (TAREFA_COMANDO_CHAT, 2026-09-30): na CONVERSA com "voz": true o prompt e o livre-v8 (era a v7 ate a
rodada 3 do comando; a v7 continua no pacote e a rodada 1 reproduz) e a resposta
traz "comando": uma acao do catalogo fechado (as 9 acoes do dono) que o pet entendeu como pedido claro, ou null. O
servidor so propoe (saida.ler falha alto fora do catalogo); o app valida de novo e grava o evento `d` de sempre. Na fala
espontanea e sem "voz" o campo vem null.

Comando sem a voz propria (CONVERSA_PET, M1, decisao D1 do Matheus em 2026-11-06): o pedido da conversa com "comando": true
(e sem "voz") usa o prompt livre-v9 (as regras de verdade do livre-v2 + o estilo da especie pelo corpus + o COMANDO da v8):
o pet nao inventa, fala no tom da especie e devolve "comando" validado pelo catalogo. Sem o campo, tudo como antes (livre-v2).
"comando" so vale na CONVERSA, sozinho (nao junto com "voz") e precisa ser booleano: a entrada da pagina nao e confiavel.

Conversa nova (CONVERSA_PET, M2, decisao D2 do Matheus, 2026-11-06): o campo "prompt": "conversa-v1" (enum fechado em PROMPTS_CONVERSA;
qualquer outro valor, inclusive null, e 400) liga o prompt conversa-v1 (M3) na CONVERSA, sem "voz": estilo da especie pelo corpus,
"comando" opcional como no livre-v9 e historico de fronteira, [jogador, pet, estagio] (o estagio vem do catalogo ESTAGIOS; as trocas
de outro estagio o prompt descarta). O texto do jogador passa pela mesma validacao de hoje (tipo e tamanho) e so entra no prompt pelas
`mensagens` do conversa-v1. Sem o campo, tudo como antes (livre-v2 ou livre-v9): a chave da pagina nasce desligada.
"""

from __future__ import annotations

import json
import os
import random
import threading

from digilab_fala_livre import VERSAO_APP
from digilab_fala_livre.fatos import ESTAGIOS, FatosInvalidos
from digilab_fala_livre import almanaque, corpus
from digilab_fala_livre.arvore import ARVORE
from digilab_fala_livre.gerar import gerar
from digilab_fala_livre.ollama import URL_PADRAO, ClienteOllama
from digilab_fala_livre.prompt import (VERSAO_CONVERSA_V1, VERSAO_PROMPT, VERSAO_PROMPT_V6, VERSAO_PROMPT_V8,
                                           VERSAO_PROMPT_V9)
from digilab_fala_livre.revisao import gerar_com_revisao
from digilab_fala_livre.verificador import VERSAO_VERIFICADOR_V5, verificar
from servidor.fala_llm import ControleGasto
from servidor.fala_livre_claude import (ARQUIVO_GASTO_LIVRE, LIMITE_USD_LIVRE_PADRAO, ClienteClaude)

ROTA_FALA, ROTA_VERIF, ROTA_STATUS = "/api/fala-livre", "/api/fala-livre/verificar", "/api/fala-livre/status"
MODELO_PADRAO = "gemma2:9b"          # escolhido na rodada 2 (artifacts_fala_livre/rodada2/RELATORIO.md)
PROVEDORES = ("ollama", "claude")
PROVEDOR_PADRAO = "ollama"
PROMPTS_CONVERSA = (VERSAO_CONVERSA_V1,)       # M2: enum fechado do campo "prompt"
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
    def __init__(self, modelo: str | None = None, cliente: ClienteOllama | None = None, ambiente: dict | None = None,
                 gasto: ControleGasto | None = None, sdk=None, claude_permitido=None) -> None:
        """`cliente` injeta o cliente de geracao (teste). `ambiente` (padrao os.environ) traz DIGILAB_PROVEDOR_LIVRE,
        DIGILAB_MODELO_LIVRE, DIGILAB_PROVEDOR_VERIF e DIGILAB_MODELO_VERIF; `claude_permitido()` False desliga o Claude."""
        amb = os.environ if ambiente is None else ambiente
        url = amb.get("DIGILAB_OLLAMA_URL", URL_PADRAO)
        self.gasto = gasto
        self._sdk, self._permitido = sdk, claude_permitido
        self.provedor = amb.get("DIGILAB_PROVEDOR_LIVRE", PROVEDOR_PADRAO)
        self.provedor_verif = amb.get("DIGILAB_PROVEDOR_VERIF", PROVEDOR_PADRAO)
        modelo_gerador = modelo or amb.get("DIGILAB_MODELO_LIVRE", MODELO_PADRAO)
        modelo_verif = amb.get("DIGILAB_MODELO_VERIF", MODELO_PADRAO)
        self.cliente = cliente or self._construir(self.provedor, modelo_gerador, url)
        # verificador proprio so quando difere do gerador; senao `cliente_verif` e o proprio `self.cliente` (o de hoje).
        # Um cliente injetado (teste) so ganha verificador proprio se o ambiente pedir um
        if cliente is not None:
            proprio = "DIGILAB_PROVEDOR_VERIF" in amb or "DIGILAB_MODELO_VERIF" in amb
        else:
            proprio = not (self.provedor == "ollama" and self.provedor_verif == "ollama" and modelo_verif == modelo_gerador)
        self._verif_proprio = self._construir(self.provedor_verif, modelo_verif, url) if proprio else None
        if self._verif_proprio is not None:
            self.cliente.cliente_verif = self._verif_proprio    # o revisor (gerar_com_revisao) le daqui
        self.trava = threading.Lock()
        self.especies, meta, self.corpus_sha = corpus.carregar()
        self.corpus_exemplo = bool(meta["exemplo"])
        self.almanaque_sha = almanaque.carregar()[1]

    @property
    def cliente_verif(self):
        return self._verif_proprio if self._verif_proprio is not None else self.cliente

    def _construir(self, provedor: str, modelo: str, url: str):
        if provedor not in PROVEDORES:
            raise ValueError(f"provedor desconhecido: {provedor!r} (use {' ou '.join(PROVEDORES)})")
        if provedor == "ollama":
            return ClienteOllama(modelo, url)
        if self.gasto is None:                           # um controle so para o gerador e o verificador Claude
            self.gasto = ControleGasto(LIMITE_USD_LIVRE_PADRAO, ARQUIVO_GASTO_LIVRE)
        return ClienteClaude(modelo, self.gasto, sdk=self._sdk, permitido=self._permitido)

    def definir_teto(self, limite_usd: float, alerta=None) -> None:
        """--limite-usd-livre e o alerta de e-mail, conhecidos so depois que as rotas foram instaladas."""
        if limite_usd < 0:
            raise ValueError("limite de gasto negativo")
        if self.gasto is not None:
            self.gasto.limite = limite_usd
            self.gasto.alerta = alerta

    def status(self) -> dict:
        ativo = self.provedor != "claude" or self._permitido is None or bool(self._permitido())
        return {"versao_app": VERSAO_APP, "provedor": self.provedor, "modelo": self.cliente.modelo,
                "provedor_verificador": self.provedor_verif, "modelo_verificador": self.cliente_verif.modelo,
                "carregado": self.cliente.carregado, "ativo": ativo,
                "gasto": self.gasto.para_dict() if self.gasto is not None else None}

    def fala(self, d: dict) -> dict:
        situacao = d.get("situacao")
        if situacao not in ("espontanea", "conversa"):
            raise PedidoInvalido("situacao invalida")
        jog = _texto(d["fala_jogador"], "fala_jogador") if situacao == "conversa" else None
        hist = d.get("historico") or []
        if not isinstance(hist, list) or len(hist) > MAX_TROCAS:
            raise PedidoInvalido("historico invalido")
        prompt = d.get("prompt", None) if "prompt" in d else False
        if prompt is not False and prompt not in PROMPTS_CONVERSA:
            raise PedidoInvalido("prompt invalido")
        if prompt is not False and (situacao != "conversa" or d.get("voz") is True):
            raise PedidoInvalido("prompt so vale na conversa e sem voz")
        hist = self._historico(hist, com_estagio=prompt is not False)
        semente = _semente(d.get("semente", 0))
        comando = d.get("comando", False)
        if not isinstance(comando, bool):
            raise PedidoInvalido("comando precisa ser booleano")
        if comando and (situacao != "conversa" or d.get("voz") is True):
            raise PedidoInvalido("comando so vale na conversa e sem voz")
        if d.get("voz") is True:
            return self._fala_voz(d, situacao, jog, hist, semente)
        especie, versao = None, VERSAO_PROMPT
        if comando or prompt is not False:                                 # livre-v9: estilo da especie pelo corpus + comando, sem a voz propria
            ident = d["estado"].get("identidade") if isinstance(d.get("estado"), dict) else None
            forma = ident.get("forma") if isinstance(ident, dict) else None
            especie = self.especies.get(forma.removesuffix(" sombrio")) if isinstance(forma, str) else None
            versao = VERSAO_CONVERSA_V1 if prompt is not False else VERSAO_PROMPT_V9
        with self.trava:
            r = gerar(self.cliente, d.get("estado"), situacao, jog, hist, semente, versao=versao, especie=especie,
                      comando=comando)
        return {"versao_app": VERSAO_APP, "fala": r.fala, "fatos_citados": list(r.fatos_citados), "fatos": list(r.fatos),
                "estagio": r.estagio, "modelo": r.modelo, "versao_prompt": r.versao_prompt, "latencia_s": r.latencia_s,
                "erro": r.erro, "comando": r.comando if comando else None,
                **({"especie_corpus": r.especie, "corpus_sha256": self.corpus_sha} if comando or prompt is not False else {})}

    @staticmethod
    def _historico(hist: list, com_estagio: bool) -> list:
        """Valida o historico. Sem o campo "prompt": pares [jogador, pet], como sempre. Com ele: trios [jogador, pet, estagio],
        o estagio do catalogo; o texto do jogador tem a validacao de sempre."""
        out = []
        for troca in hist:
            if not isinstance(troca, list) or len(troca) != (3 if com_estagio else 2):
                raise PedidoInvalido("historico invalido")
            if com_estagio and troca[2] not in ESTAGIOS:
                raise PedidoInvalido("historico: estagio fora do catalogo")
            out.append((_texto(troca[0], "historico"), _texto(troca[1], "historico", 400)) + ((troca[2],) if com_estagio else ()))
        return out

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
        comando = situacao == "conversa"             # livre-v8: o comando so existe na conversa
        with self.trava:
            r, tent = gerar_com_revisao(self.cliente, estado, situacao, semente, jog, hist,
                                        versao=VERSAO_PROMPT_V8 if comando else VERSAO_PROMPT_V6,
                                        especie=especie, rival=rival, versao_verificador=VERSAO_VERIFICADOR_V5,
                                        so_respeito=True, comando=comando)
        escolhida = next((x for x in reversed(tent) if x.get("fala") == r.fala), None)
        return {"versao_app": VERSAO_APP, "fala": r.fala, "fatos_citados": list(r.fatos_citados), "fatos": list(r.fatos),
                "estagio": r.estagio, "modelo": r.modelo, "versao_prompt": r.versao_prompt, "latencia_s": r.latencia_s,
                "erro": r.erro, "comando": r.comando if comando else None,
                "verificacao": escolhida["verificacao"] if escolhida else None,
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
                return verificar(self.cliente_verif, fala, cit, fatos, _semente(d.get("semente", 0))).para_dict()
            return verificar(self.cliente_verif, fala, cit, fatos, _semente(d.get("semente", 0)), versao=versao).para_dict()


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
    def claude_permitido() -> bool:
        t = modulo.Tratador                  # --limite-usd-livre e --remoto so sao lidos depois da instalacao: valem na chamada
        svc.definir_teto(t.limite_usd_livre, t.alerta_livre)
        return not t.remoto or t.claude_remoto

    svc = servico or ServicoFalaLivre(claude_permitido=claude_permitido)
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
