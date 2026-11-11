"""O gabarito da voz do jogo antes da DC5 (CONVERSA_PET; docs/PLANO_ANALISE_V3_CONVERSA_DC5.md, secoes 9 e 13; CLAUDE.md: o gabarito e
gravado num commit proprio, antes da mudanca).

Grava, para entradas fixas, as mensagens que a voz do jogo monta hoje: a voz-v2 no dec-v2 e a voz-v3 no dec-v3 (`prompt.mensagens_voz` sem
`voz`), na fala espontanea e na conversa (com historico do estagio, [J] e comando), e as mensagens que o servico do jogo
(`servidor.fala_livre.ServicoFalaLivre`) manda ao cliente pelo mesmo caminho da pagina. O teste `tests/test_conversa_dc5a.py` confere que o
codigo de hoje da o mesmo, byte a byte: a voz-v4 so entra quando pedida, e a voz do jogo nao muda.

    python experiments/exportar_gabarito_voz_jogo_dc5.py --saida experiments/configs/v3_conversa_dc5/gabarito_voz_jogo.json

So biblioteca padrao. Nenhuma chamada a modelo: o cliente e falso e so guarda as mensagens.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab_fala_livre import conceitos as dec  # noqa: E402
from digilab_fala_livre import prompt as pr  # noqa: E402
from digilab_fala_livre.ollama import Resposta  # noqa: E402

D2 = {"versao": "dec-v2", "k": 3, "intencao": "fome", "conceitos": [
    {"nome": "fome", "valor": 900, "confianca": 700, "alvo": "racao"}, {"nome": "aversao", "valor": 600, "confianca": 300, "alvo": "bola"},
    {"nome": "lembranca", "valor": 800, "confianca": 800, "alvo": "ep4", "episodio": {"acao": "comer", "classe": "racao", "desfecho": "bom"}},
    {"nome": "sono", "valor": 300, "confianca": 900}]}
D2_VAZIO = {"versao": "dec-v2", "k": 7, "intencao": "curiosidade", "conceitos": [{"nome": "curiosidade", "valor": 100, "confianca": 100}]}


def _d3(pedido: str) -> dict:
    return {**D2, "versao": "dec-v3", "intencao": pedido}


ENTRADAS = {"d2": D2, "d2_vazio": D2_VAZIO, **{f"d3_{p}": _d3(p) for p in ("fome", "higiene", "solidao")}}
HISTORICO = [["oi, tudo bem?", "Oi! Tô aqui.", "adulto"], ["e aí, quer brincar?", "Hmm, acho que sim.", "adulto"],
             ["você é bebê?", "nhã", "bebe"]]
CASOS = [(e, est, sit) for e in ENTRADAS for est in ("crianca", "adulto") for sit in ("espontanea", "conversa")]


class ClienteGuarda:
    """cliente falso: guarda as mensagens e devolve uma fala fixa (voz) ou nenhuma afirmacao (verificador)"""

    def __init__(self, papel: str) -> None:
        self.modelo, self.papel, self.carregado, self.mensagens = "falso", papel, True, []

    def conversar(self, mensagens, esquema, max_tokens, semente) -> Resposta:
        self.mensagens.append(mensagens)
        if self.papel == "verif":
            return Resposta(json.dumps({"afirmacoes": []}), self.modelo, 0.0, 10, 2, True)
        d = {"fala": "Oi!", "fatos_citados": [], **({"comando": None} if "comando" in esquema["properties"] else {})}
        return Resposta(json.dumps(d, ensure_ascii=False), self.modelo, 0.0, 10, 2, True)


def mensagens_do_prompt() -> dict:
    out = {}
    for e, est, sit in CASOS:
        c = dec.validar(ENTRADAS[e])
        jog = "você lutou ontem, né?" if sit == "conversa" else None
        out[f"{e}/{est}/{sit}"] = pr.mensagens_voz(c, est, sit, jog, HISTORICO if sit == "conversa" else None, comando=sit == "conversa")
    return out


def mensagens_do_servico() -> dict:
    from servidor.fala_livre import ServicoFalaLivre

    class Servico(ServicoFalaLivre):
        """o servico do jogo, sem mudar nada, com o verificador falso"""

        def __init__(self, voz, verif) -> None:
            super().__init__(cliente=voz, ambiente={})
            self._verif_gabarito = verif

        @property
        def cliente_verif(self):
            return self._verif_gabarito

    out = {}
    for e, est, sit in CASOS:
        voz, verif = ClienteGuarda("voz"), ClienteGuarda("verif")
        s = Servico(voz, verif)
        pedido = {"situacao": sit, "estado": {"identidade": {"estagio": est}}, "conceitos": ENTRADAS[e], "semente": 7,
                  "historico": HISTORICO if sit == "conversa" else []}
        if sit == "conversa":
            pedido.update(fala_jogador="você lutou ontem, né?", comando=True)
        r = s.fala(pedido)
        out[f"{e}/{est}/{sit}"] = {"mensagens_voz": voz.mensagens, "versao_prompt": r["versao_prompt"]}
    return out


def gabarito() -> dict:
    d = {"prompt": mensagens_do_prompt(), "servico": mensagens_do_servico()}
    texto = json.dumps(d, ensure_ascii=False, sort_keys=True)
    return {"sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(), **d}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="o gabarito da voz do jogo antes da DC5")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args(argv)
    Path(a.saida).write_text(json.dumps(gabarito(), ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
