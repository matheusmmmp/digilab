"""Gabarito das vidas de GRUPO de hoje (dois pets, degrau 1: visao, toque, disputa), para o G2 da etapa 8 dos dois pets (o cheiro proprio,
o rastro e o som; docs/TAREFA_V2_DOIS_PETS.md, etapa 8; docs/futuro/dois_pets.md, secoes 5.3, 5.4 e 5.6): gravado com o codigo da main
ANTES dos sentidos do degrau 1b. Com a chave dos sentidos desligada, estes grupos tem de sair iguais, byte a byte.

Duas fontes de grupo:
- **o `simular_grupo` direto**: os dois pets com o instinto do mundo ou com os lobos aprendendo, sem e com o corpo inteiro da etapa 6, o B
  entrando no dia 0 ou no dia 1, os dois layouts, os donos atencioso e aleatorio (o aleatorio faz o pet chamar e emburrar), 2 sementes;
- **a bancada do grupo** (`experiments/bancada_v2.py`): os braços B-so, B+Ainf, B+Aemb, B+Aing e A-so com K = 1, 2 dias, o cerebro do
  grupo (o alvo aprendido, as entradas sociais, o modelo dos outros e a presenca da fruta), nas montagens simples e completa, 2 sementes.

O que se confere: o sha256 do registro do grupo e do resumo do grupo (o mundo, as vezes sorteadas, a rng da ordem, os contatos, as
disputas e cada pet: estado, estado(), acoes, rngs, registro do mundo fisico, estado interno da politica, log e o resumo social).

    python tests/gabarito_sentidos.py      # grava tests/gabaritos/sentidos_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_dois_pets as gdp  # noqa: E402

from digilab.config import CONFIG_GRUPO_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "sentidos_vidas_de_hoje.json"
DIAS = 3
SEMENTES = (101, 202)                                   # so as dos testes
CEREBROS = ("instinto", "lobos")
CORPOS = ("sem", "drives")
ENTRADAS_B = (0, 1)
LAYOUTS = ("padrao", "afastado")
DONOS = ("atencioso", "aleatorio")
BRACOS_GRUPO = ("B-so", "B+Ainf", "B+Aemb", "B+Aing", "A-so")
MONTAGENS = ("simples", "completa")


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=repr)


def impressao(g) -> dict:
    return {"registro": _sha(g.registro.para_jsonl()), "resumo": _sha(_texto(g.resumo()))}


def fabricas(cerebro: str, corpo: str, layout: str):
    """as fabricas do grupo (as de tests/test_grupo.py): os lobos num corpo ligado recebem a chave do corpo"""
    fp, _ = gdp.fabricas_diretas(layout, corpo, cerebro)
    cm, cc = gdp.LAYOUTS[layout], gdp.CORPOS[corpo]
    if cerebro == "lobos" and cc is not None:
        fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=cm, cfg_corpo=cc)  # noqa: E731
    if cc is None:
        fm = lambda p, cfg, s, **kw: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, **kw)  # noqa: E731
    else:
        fm = lambda p, cfg, s, **kw: gdp.MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm,  # noqa: E731
                                                          cfg_corpo=cc, **kw)
    return fp, fm


def grupo_direto(cerebro: str, corpo: str, entrada_b: int, layout: str, dono: str, s: int):
    sementes = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident, entrada in (("A", 0), ("B", entrada_b)):
        fp, fm = fabricas(cerebro, corpo, layout)
        d = DonoComLugar(criar_dono(dono), "perto", sementes[ident], dono, gdp.LAYOUTS[layout])
        pets.append(PetDoGrupo(ident, entrada, fp, fm, d, dono, cerebro))
    return simular_grupo(gdp.LAYOUTS[layout], s, pets, DIAS)


def bancada_do_grupo(montagem: str) -> bv.Bancada:
    cfg = {"tipo": "grupo", "bracos": list(BRACOS_GRUPO), "sementes": list(SEMENTES), "k_dias": 1, "dias": 2, "orcamento_por_dia": 16,
           "ponto": "T3", "consequencia": {"ganho": 4}, "orcamento": 32}
    if montagem == "completa":
        cfg = {**cfg, "montagem": "completa", "lobos": {"w0_info": 256, "memoria_ganho": 512, "w0_pedido": 256},
               "consequencia": {"ganho": 4, "canais_ligados": True}}
    return bv.bancada_da_config(cfg)


def casos_diretos():
    for cerebro in CEREBROS:
        for corpo in CORPOS:
            for entrada_b in ENTRADAS_B:
                for layout in LAYOUTS:
                    for dono in DONOS:
                        for s in SEMENTES:
                            yield f"direto|{cerebro}|{corpo}|B{entrada_b}|{layout}|{dono}|{s}", (cerebro, corpo, entrada_b, layout, dono, s)


def casos_bancada():
    for montagem in MONTAGENS:
        for braco in BRACOS_GRUPO:
            for s in SEMENTES:
                yield f"bancada|{montagem}|{braco}|{s}", (montagem, braco, s)


def gerar() -> dict:
    out = {}
    for chave, caso in casos_diretos():
        out[chave] = impressao(grupo_direto(*caso))
    bancadas = {m: bancada_do_grupo(m) for m in MONTAGENS}
    for chave, (montagem, braco, s) in casos_bancada():
        k = 1 if bv.BRACOS_GRUPO[braco].b else 0
        out[chave] = impressao(bancadas[montagem].grupo(bv.EspecGrupo(braco, s, k)).grupo)
    return out


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} grupos")
