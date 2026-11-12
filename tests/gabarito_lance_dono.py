"""Gabarito das vidas de hoje que passam pelo Brincar do dono com o mundo, antes do lance do dono (docs/TAREFA_V3_BOLA_BRINCAR.md, BB-8; a
regra da chave desligada). Gravado com o codigo da main (7eae252d) ANTES da `ConfigLanceDono`, num commit proprio. Com a chave desligada (o
padrao), estas vidas tem de sair iguais, byte a byte.

O lance mexe no Brincar do dono (`MotorMundo._aplicar_acao_usuario`), na bola do `Mundo` (que o grupo partilha), no momento da decisao do pet
e numa entrada nova do DigiBrain modular. Por isso as vidas sao as que recebem o Brincar do dono com o mundo ligado:
  - `orq`: o braco do laboratorio e do jogo (REL, o M3* com a memoria autobiografica), os quatro donos (que brincam pelo orcamento), o
    `longe_fixo` e o comedouro, as sementes 101 e 202, 3 dias, pelo orquestrador do prototipo; com o sono que segura desligado e ligado (o
    pet v27 do jogo), e o A11 (o cerebro A, BB-6) com os quatro donos no comedouro, semente 101;
  - `roteiro`: o dono que brinca de tempos em tempos (o Brincar a cada `BRINCAR_A_CADA` ticks e a racao no comedouro a cada
    `RACAO_A_CADA`), com o REL (sono desligado e ligado) e o A11, as sementes 101, 202 e 303, 3 dias;
  - `grupo`: dois pets no mesmo mundo, com o DigiBrain modular (REL) e com os lobos (a primeira vida do exportar_gabarito_grupo), 3 dias.
De cada vida: o sha256 do log, o do estado interno do cerebro, o do resumo do mundo fisico do motor e o numero de decisoes; no grupo, o
sha256 do resumo do grupo.

    python tests/gabarito_lance_dono.py     # grava tests/gabaritos/lance_dono_de_hoje.json (so com o codigo de antes da mudanca)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_grupo as eg  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

from digilab.config import CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, CONFIG_SONO_SEGURA_LIGADA, TICKS_POR_DIA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "lance_dono_de_hoje.json"
DIAS = 3
SEMENTES_ORQ = (101, 202)
LUGARES = ("longe_fixo", "comedouro")
DONOS = orq.DONOS
SEMENTES_ROTEIRO = (101, 202, 303)
PASSO = 30                                     # o passo do roteiro, em ticks
BRINCAR_A_CADA = 120                           # o Brincar do roteiro, a cada 2 h de jogo
RACAO_A_CADA = 360                             # a racao no comedouro, a cada 6 h de jogo
SONOS = {"": None, "+sono": CONFIG_SONO_SEGURA_LIGADA}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=repr)


def impressao(motor) -> dict:
    """o log, o estado interno do cerebro, o resumo do mundo fisico e as decisoes do pet"""
    return {"log": _sha(motor.log.para_jsonl()), "estado": _sha(_texto(motor.politica.estado_interno())),
            "fisico": _sha(_texto(motor.resumo_mundo_fisico())), "decisoes": len(motor.acoes_recentes(10 ** 9))}


def roteiro(fp, fm, semente: int, dias: int = DIAS, ao_brincar=None, racao: bool = True):
    """o dono que brinca de tempos em tempos: a vida anda de `PASSO` em `PASSO` ticks; a cada `RACAO_A_CADA` ticks o dono poe a racao no
    comedouro e a cada `BRINCAR_A_CADA` ticks ele brinca (`ao_brincar(motor)`, se dado, logo antes do Brincar: a medida do teste). Sem
    `racao` (o G-BB-2 do tests/test_lance_dono.py), o dono so brinca e o pet chega a fome urgente. Devolve o motor"""
    motor = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, semente)
    for _ in range(dias * TICKS_POR_DIA // PASSO):
        motor.avancar(PASSO)
        t = motor._estado.tick
        if racao and t % RACAO_A_CADA == 0:
            motor.deixar_comida("racao", *motor.mundo.comedouro)
        if t % BRINCAR_A_CADA == 0:
            if ao_brincar is not None:
                ao_brincar(motor)
            motor.observar(AcaoUsuario.BRINCAR)
    return motor


def fabricas_grupo(braco: str, dono: str, semente: int, dias: int = DIAS, **kw_orq):
    """as fabricas de um pet do grupo com o cerebro do braco e o motor do orquestrador (o corpo do v11), aceitando o mundo e a entrada do
    grupo"""
    fp, _ = orq.fabricas(braco, dono, semente, dias, orq.ORCAMENTO_POR_DIA, conserto=True, **kw_orq)
    cc = orq.bancada(dias, orq.ORCAMENTO_POR_DIA).cfg_corpo_de(orq.bv.EspecVida(dono, orq.gl.BRACO_V11, semente))

    extra = {} if kw_orq.get("lance") is None else {"cfg_lance_dono": kw_orq["lance"]}     # o lance do dono (tests/test_lance_dono.py)

    def fm(politica, cfg, s, **kw):
        return orq.com_corpo(orq.MotorMundo)(politica, cfg, s, orq.NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM,
                                             cfg_corpo=cc, **extra, **kw)
    return fp, fm


def grupo_modular(semente: int, donos: tuple = ("atencioso", "relapso"), dias: int = DIAS, **kw_orq):
    """dois pets REL no comedouro comum, os dois desde o tick 0"""
    sementes = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident, dono in zip(CONFIG_GRUPO_LIGADA.ids, donos):
        fp, fm = fabricas_grupo("REL", dono, sementes[ident], dias, **kw_orq)
        d = DonoComLugar(criar_dono(dono), "comedouro", sementes[ident], dono, orq.CM)
        pets.append(PetDoGrupo(ident, 0, fp, fm, d, dono, "REL"))
    return simular_grupo(orq.CM, semente, pets, dias)


def grupo_lobos():
    """a primeira vida do exportar_gabarito_grupo (dois lobos, o atencioso e o relapso)"""
    semente, layout, corpo, cerebros, donos, entrada_b, lugar = eg.VIDAS[0]
    sementes = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident, cerebro, dono, entrada in (("A", cerebros[0], donos[0], 0), ("B", cerebros[1], donos[1], entrada_b * TICKS_POR_DIA)):
        fp, fm = eg._fabricas(layout, corpo, cerebro)
        d = DonoComLugar(criar_dono(dono), lugar, sementes[ident], dono, eg.LAYOUTS[layout])
        pets.append(PetDoGrupo(ident, entrada, fp, fm, d, dono, cerebro))
    return simular_grupo(eg.LAYOUTS[layout], semente, pets, eg.DIAS)


def gerar() -> dict:
    out = {}
    for rotulo, sono in SONOS.items():
        for semente in SEMENTES_ORQ:
            for dono in DONOS:
                for lugar in LUGARES:
                    motor, _, _ = orq.viver("REL", dono, lugar, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True, sono=sono)
                    out[f"orq|REL{rotulo}|{dono}|{lugar}|{semente}"] = impressao(motor)
    for dono in DONOS:
        motor, _, _ = orq.viver("A11", dono, "comedouro", 101, DIAS, orq.ORCAMENTO_POR_DIA)
        out[f"orq|A11|{dono}|comedouro|101"] = impressao(motor)
    for braco, sono in (("REL", None), ("REL+sono", CONFIG_SONO_SEGURA_LIGADA), ("A11", None)):
        for semente in SEMENTES_ROTEIRO:
            fp, fm = orq.fabricas(braco.split("+")[0], "atencioso", semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True, sono=sono)
            out[f"roteiro|{braco}|{semente}"] = impressao(roteiro(fp, fm, semente))
    out["grupo|REL|101"] = {"resumo": _sha(eg._json(grupo_modular(101).resumo()))}
    out["grupo|lobos|101"] = {"resumo": _sha(eg._json(grupo_lobos().resumo()))}
    return out


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
