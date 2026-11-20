"""Gabarito das vidas de hoje que o DigiBrain modular vai tocar (docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, etapa 0;
docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 11): gravado com o codigo da main (79ce52e) ANTES da `ConfigDigibrain` e do candidato
`lembranca` no explorar (PE-14, autorizado para a v13 em 2026-10-25, com o G2 antes). Com a chave desligada, estas vidas tem de sair
iguais, byte a byte, e os candidatos de cada sub-decisao do mundo tambem (o G2 do `lembranca`).

O que os gabaritos de hoje nao guardam e este guarda: a lista de candidatos que o `MotorMundo.candidatos` devolve em cada sub-decisao
(comer, explorar, brincar, aliviar), com o `u` e o tick. O `lembranca` entra no fim da lista do explorar; com a chave desligada, a lista
tem de ser a de hoje, mesmo nas vidas em que o alvo escolhido nao mudaria.

As vidas reusam os casos de quatro gabaritos de antes (como o tests/gabarito_paladar_mundo.py), que cobrem as fontes de candidato do
explorar de hoje (o cheiro, o vagar, a casa, o continuar, as arvores lembradas e os sociais):
- `tests/gabarito_p4.py`, o J1: o cerebro A pela bancada (P0, P0z, P1, P3), nos mundos `fisico` e `fisico_afastado` (36 vidas);
- `tests/gabarito_dois_pets.py`, as vidas diretas: o instinto do mundo e os lobos, sem o corpo, com a quimica e com os drives (a
  curiosidade e a novidade), nos dois layouts, com a bola perto (48 vidas);
- `tests/gabarito_pet_que_pensa_plano.py`: o mundo do J5 ligado (os candidatos `arvore:<id>`), o instinto, o P0 e o P1 do plano (36);
- `tests/gabarito_sentidos.py`, os grupos diretos: dois pets no mesmo mundo (os candidatos `seguir` e `onde_comeu`) (64 grupos).
E vidas novas, porque nenhum gabarito de hoje liga o Olfato da comida (os candidatos do olfato no lugar do `cheiro`) nem os orgaos
inteiros num grupo (os candidatos do cheiro do outro):
- `olfato_vida`: um pet, o corpo da etapa 6 com o Olfato da comida (duas narinas), o instinto e os lobos, perto e longe (8 vidas);
- `olfato_grupo`: dois pets, o mesmo corpo com o Olfato da comida e o social e a Audicao, os sentidos ligados (4 grupos).
O pet v12 no mundo do produto (o cenario do MVP, #403) ja tem os candidatos de cada decisao no web/app/test/gabaritos/
mvp_produto_python.json (tests/test_gabarito_mvp_produto_web.py), e o A no layout padrao, no mvp_mundo_python.json: nao se repetem aqui.

De cada vida: o sha256 da impressao da fonte (a mesma do gabarito dela; o teste confere que gravar nao muda a vida) e o do traco dos
candidatos, com as contagens por acao e por tipo de candidato do explorar.

    python tests/gabarito_digibrain.py      # grava tests/gabaritos/digibrain_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_corpo_mundo as gcm  # noqa: E402
import gabarito_dois_pets as gdp  # noqa: E402
import gabarito_orgao_sem_direcao as gsd  # noqa: E402
import gabarito_p4 as gp4  # noqa: E402
import gabarito_pet_que_pensa_plano as gpp  # noqa: E402
import gabarito_sentidos as gs  # noqa: E402

from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_GRUPO_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_OLFATO, CONFIG_PADRAO,  # noqa: E402
                            CONFIG_SENTIDOS_LIGADA)
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, simular_vida_mundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "digibrain_vidas_de_hoje.json"
# (a fonte, o arquivo do gabarito dela, a parte do arquivo com as vidas)
FONTES = {
    "p4_j1": (gp4.ARQUIVO, "j1"),
    "dois_pets_direta": (gdp.ARQUIVO, None),
    "pqp_plano": (gpp.ARQUIVO, None),
    "sentidos_direto": (gs.ARQUIVO, None),
}
# as vidas novas do olfato (so as sementes dos testes)
SEMENTES = (101, 202)
DIAS = 3
CM = gdp.LAYOUTS["padrao"]
OLFATO_COMIDA = replace(CONFIG_OLFATO, ligada=True, narinas=2, comida=True)
OLFATO_TUDO = replace(OLFATO_COMIDA, outro_pet=True)


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


@contextmanager
def gravando_candidatos():
    """troca o `MotorMundo.candidatos` por um que grava cada chamada (o pet, o tick, a acao, o u e a lista) e devolve a mesma lista; nao
    muda nada da vida. O unico lugar do motor que monta candidatos e este metodo (nenhuma subclasse o sobrescreve)."""
    traco: list = []
    original = MotorMundo.candidatos

    def gravado(self, acao, u):
        cands = original(self, acao, u)
        traco.append([getattr(self, "ident", None), self._estado.tick, acao.value, u, [c.para_dict() for c in cands]])
        return cands

    MotorMundo.candidatos = gravado
    try:
        yield traco
    finally:
        MotorMundo.candidatos = original


def _fabricas_olfato(cerebro: str, co, **extra):
    if cerebro == "instinto":
        fp = lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
    else:
        fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=CM,  # noqa: E731
                                            cfg_corpo=CONFIG_CORPO_DRIVES)
    fm = lambda p, cfg, s, **kw: gsd.MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM,  # noqa: E731
                                                     cfg_corpo=CONFIG_CORPO_DRIVES, cfg_olfato=co, **extra, **kw)
    return fp, fm


def vida_olfato(cerebro: str, lugar: str, s: int) -> dict:
    """um pet com o Olfato da comida: o dono atencioso com lugar e a bola perto (o dono das vidas diretas dos dois pets)"""
    fp, fm = _fabricas_olfato(cerebro, OLFATO_COMIDA)
    dono = gdp.DonoComBolaPerto(DonoComLugar(criar_dono("atencioso"), lugar, s, "atencioso", CM))
    v = simular_vida_mundo("atencioso", dono, fp(CONFIG_PADRAO), s, DIAS, 16 * DIAS, fm, rotulo_dono="atencioso")
    return {**gdp.impressao(v.motor, v.interacoes), "corpo": _sha(_texto(v.motor.corpo.para_dict()))}


def grupo_olfato(cerebro: str, s: int) -> dict:
    """dois pets com os orgaos inteiros (o grupo do tests/gabarito_orgao_sem_direcao.py com o Olfato da comida), o B no dia 0"""
    sementes = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident in ("A", "B"):
        fp, fm = _fabricas_olfato(cerebro, OLFATO_TUDO, cfg_ouvido=gsd.OUVIDO)
        pets.append(PetDoGrupo(ident, 0, fp, fm, DonoComLugar(criar_dono("atencioso"), "perto", sementes[ident], "atencioso", CM),
                               "atencioso", cerebro))
    return gsd.impressao(simular_grupo(CM, s, pets, gsd.DIAS, cfg_sentidos=CONFIG_SENTIDOS_LIGADA))


def casos():
    for chave, caso in gp4.casos_j1():
        yield "p4_j1", chave, caso
    for chave, caso in gdp.casos_diretos():
        yield "dois_pets_direta", chave, caso
    for chave, caso in gpp.casos():
        yield "pqp_plano", chave, caso
    for chave, caso in gs.casos_diretos():
        yield "sentidos_direto", chave, caso
    for cerebro in ("instinto", "lobos"):
        for lugar in ("perto", "longe"):
            for s in SEMENTES:
                yield "olfato_vida", f"{cerebro}|{lugar}|{s}", (cerebro, lugar, s)
    for cerebro in ("instinto", "lobos"):
        for s in SEMENTES:
            yield "olfato_grupo", f"{cerebro}|{s}", (cerebro, s)


def impressao_da_fonte(fonte: str, chave: str, caso) -> dict:
    if fonte == "p4_j1":
        return gcm.vida_de_hoje(*caso)
    if fonte == "dois_pets_direta":
        return gdp.vida_de_hoje(chave, caso)
    if fonte == "pqp_plano":
        return gpp.impressao_de(caso)
    if fonte == "sentidos_direto":
        return gs.impressao(gs.grupo_direto(*caso))
    if fonte == "olfato_vida":
        return vida_olfato(*caso)
    if fonte == "olfato_grupo":
        return grupo_olfato(*caso)
    raise ValueError(f"fonte desconhecida: {fonte!r}")


def vida(fonte: str, chave: str, caso) -> dict:
    with gravando_candidatos() as traco:
        imp = impressao_da_fonte(fonte, chave, caso)
    if not traco:
        raise RuntimeError(f"{fonte}|{chave}: nenhuma sub-decisao com candidatos")
    tipos = Counter(c["tipo"].split(":")[0] for _, _, acao, _, cands in traco if acao == "explorar" for c in cands)
    return {"impressao": _sha(_texto(imp)), "candidatos": _sha(_texto(traco)),
            "n": dict(sorted(Counter(acao for _, _, acao, _, _ in traco).items())), "tipos_explorar": dict(sorted(tipos.items()))}


def gerar() -> dict:
    return {f"{fonte}|{chave}": vida(fonte, chave, caso) for fonte, chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    tipos = Counter()
    for v in g.values():
        tipos.update(v["tipos_explorar"])
    print(f"{ARQUIVO}: {len(g)} vidas; os tipos do explorar: {dict(sorted(tipos.items()))}")
