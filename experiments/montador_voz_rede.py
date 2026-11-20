"""O espelho Python do montador do pedido da voz pela rede (CONVERSA_PET, DC4a; docs/PLANO_ANALISE_V3_CONVERSA_DC4.md, secoes 3 e 10).

O que a pagina manda ao servidor com a chave "Fala pela rede (teste)" ligada e o que `web/app/src/falaRede.ts` monta, linha a linha:

- `conceitos_da_voz(dec_v2, conteudo)` = `conceitosDaVoz(m)`: o `dec-v2` da ultima decisao do modular (`Motor.conceitosDec("dec-v2")`, aqui o
  `decodificar_v2` do Python) e, quando a ultima decisao foi uma unidade de fala (`Motor.conteudoDaFala()`, aqui o conteudo da escolha), o
  formato `dec-v3` com a intencao do conteudo; nas outras decisoes o `dec-v2` como esta. Em todo conceito o `alvo` so vai se for de catalogo
  da voz (uma classe de objeto ou `ep<N>`; a `fome` pode trazer `comida` ou `cheiro`, que a pagina tira, D-CP-DC2b-5) e o `episodio` vai como
  veio;
- `estado_da_voz(estagio, forma)` = `estadoDaVoz(m)`: `{identidade: {estagio, forma}}`, a forma cortada em 60 caracteres. Na DC4 o pet de
  teste do Python nao tem forma (D-CP-DC4a, no registro): `forma=None` tira a chave.

A paridade com a pagina: `experiments/exportar_gabarito_fala_rede.py` grava as entradas e as saidas deste montador em vidas curtas do LAB+F
(sementes dos testes), e `web/app/test/fala_rede_montador.test.ts` passa as mesmas entradas pelo `conceitosDaVoz` do TS e compara.
So biblioteca padrao; nada daqui muda o pet (so le o `dec-v2` e o conteudo).
"""
from __future__ import annotations

import re

VERSAO_DEC_FALA = "dec-v3"                                   # = falaRede.ts VERSAO_DEC_FALA (= conceitos.py VERSAO_DEC_V3)
CLASSES_ALVO = ("racao", "a", "b", "c", "podre", "bola")     # = falaRede.ts CLASSES_ALVO (= conceitos.py CLASSES_OBJETO)
ALVO_EPISODIO = re.compile(r"^ep[0-9]{1,6}$")                # = falaRede.ts ALVO_EPISODIO
CONTEUDOS_FALA = ("fome", "higiene", "solidao")              # = digilab/config.py CONTEUDOS_FALA (conferido no teste)
MAX_FORMA = 60                                               # = falaRede.ts estadoDaVoz: nomeForma(...).slice(0, 60)


def alvo_de_catalogo(alvo) -> str | None:
    """= `alvoDeCatalogo`: o alvo so fica se for uma classe de objeto ou `ep<N>`; senao None (a chave sai do conceito)"""
    if isinstance(alvo, str) and (alvo in CLASSES_ALVO or ALVO_EPISODIO.match(alvo) is not None):
        return alvo
    return None


def conceitos_da_voz(dec_v2: dict | None, conteudo: str | None) -> dict | None:
    """= `conceitosDaVoz(m)`: None sem decisao do modular (a chave nao muda nada). `conteudo`: o da unidade de fala da ultima decisao, ou None
    quando ela nao foi uma fala. Um conteudo fora dos tres falha alto, como o `conteudoDaFala` do TS."""
    if dec_v2 is None:
        return None
    if conteudo is not None and conteudo not in CONTEUDOS_FALA:
        raise ValueError(f"a fala com o conteudo {conteudo!r}: so {CONTEUDOS_FALA}")
    conceitos = []
    for x in dec_v2["conceitos"]:
        alvo = alvo_de_catalogo(x.get("alvo"))
        c = {"nome": x["nome"], "valor": x["valor"], "confianca": x["confianca"]}
        if alvo is not None:
            c["alvo"] = alvo
        if x.get("episodio") is not None:
            c["episodio"] = x["episodio"]
        conceitos.append(c)
    return {"versao": dec_v2["versao"] if conteudo is None else VERSAO_DEC_FALA, "k": dec_v2["k"],
            "intencao": dec_v2["intencao"] if conteudo is None else conteudo, "conceitos": conceitos}


def estado_da_voz(estagio: str, forma: str | None = None) -> dict:
    """= `estadoDaVoz(m)`: o unico estado do pedido da voz. Sem forma (o pet do Python), so o estagio."""
    ident = {"estagio": estagio}
    if forma is not None:
        ident["forma"] = forma[:MAX_FORMA]
    return {"identidade": ident}
