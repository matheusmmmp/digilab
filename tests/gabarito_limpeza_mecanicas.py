"""Gabarito da LIMPEZA, parte 2 (docs/TAREFA_V3_LIMPEZA.md, 3.1): as mecanicas do jogo que hoje so tem gabarito Python com o cerebro A,
agora com os cerebros que ficam: o DigiBrain modular do jogo (o REL do conserto, o M3* com a memoria autobiografica) e o instinto do mundo.
Gravado com o codigo da main (58a22928) ANTES da LZ2, num commit proprio. Depois da LZ2, da LZ3 e da LZ4, estas vidas tem de sair iguais,
byte a byte.

As mecanicas, cada uma pela chave dela no motor do mundo com o corpo (o mesmo `com_corpo(MotorMundo)` do orquestrador):
  - `base`: o mundo e o corpo do orquestrador, sem chave nova (o controle);
  - `sacudir_ilha`: a chave da arvore que sacode (ConfigSacudir) na ilha, sem o dono sacudir;
  - `roteiro_sacudir`: o dono que sacode a primeira arvore do layout de 4 em 4 horas, na ilha (o MVP nao tem arvore, e a ilha
    com agua exige o controlador do contrato);
  - `banheiro`: o corpo com a vontade e o conforto (CONFIG_CORPO_BANHEIRO) e o banheiro do mundo ligado;
  - `metabolismo`: o corpo com o metabolismo (CONFIG_CORPO_METABOLISMO);
  - `drives`: o corpo da etapa 6 inteira (CONFIG_CORPO_DRIVES), o dos orgaos;
  - `fruta_ao_lado`: a fruta ao lado da racao (ConfigFrutaAoLado), com o dono no comedouro;
  - `lance`: o lance do dono (ConfigLanceDono), no motor e no cerebro modular.
Os dois pets e o lance tambem ficam guardados pelas entradas do modular (`grupo|REL`, `roteiro|...`) do gabarito do lance do dono, e o
modular com a TV pelos gabaritos do enjoo e do orgao da visao.

Uma combinacao que o motor ou o cerebro recusa hoje fica gravada com o tipo e a mensagem do erro: a recusa tambem tem de continuar igual.

De cada vida: a impressao do gabarito do mundo (o log, o estado, o estado do motor, as acoes, as rngs, o mundo), o sha256 do estado interno
do cerebro (so o modular) e o numero de decisoes.

    python tests/gabarito_limpeza_mecanicas.py     # grava tests/gabaritos/limpeza_mecanicas_de_hoje.json (so com o codigo de antes da LZ2)
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

import gabarito_mundo as gm  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.config import (CONFIG_BANHEIRO_LIGADA, CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES,  # noqa: E402
                            CONFIG_CORPO_METABOLISMO, CONFIG_DIGIBRAIN_INATOS, CONFIG_FRUTA_AO_LADO_LIGADA,
                            CONFIG_LANCE_DONO_LIGADA, TICKS_POR_DIA, CONFIG_MUNDO_ILHA, CONFIG_PADRAO, CONFIG_SACUDIR_LIGADA)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, DonoFrutaAoLado, MotorMundo, simular_vida_mundo  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "limpeza_mecanicas_de_hoje.json"
SEMENTES = (101, 202)                                   # so as dos testes
DIAS = 3
ORCAMENTO = 16 * DIAS
DONOS = ("atencioso", "aleatorio")
CEREBROS = ("REL", "instinto")
# a mecanica -> (o mundo, o corpo (None: o do orquestrador), o lugar da comida, as chaves do motor, as do cerebro modular, a fruta ao lado)
MECANICAS = {
    "base": (orq.CM, None, "perto", {}, {}, False),
    "sacudir_ilha": (CONFIG_MUNDO_ILHA, None, "perto", {"cfg_sacudir": CONFIG_SACUDIR_LIGADA}, {}, False),
    "banheiro": (orq.CM, CONFIG_CORPO_BANHEIRO, "perto", {"cfg_banheiro": CONFIG_BANHEIRO_LIGADA}, {}, False),
    "metabolismo": (orq.CM, CONFIG_CORPO_METABOLISMO, "perto", {}, {}, False),
    "drives": (orq.CM, CONFIG_CORPO_DRIVES, "perto", {}, {}, False),
    "fruta_ao_lado": (orq.CM, None, "comedouro", {"cfg_fruta_ao_lado": CONFIG_FRUTA_AO_LADO_LIGADA}, {}, True),
    "lance": (orq.CM, None, "perto", {"cfg_lance_dono": CONFIG_LANCE_DONO_LIGADA}, {"cfg_lance": CONFIG_LANCE_DONO_LIGADA}, False),
}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=repr)


def politica(cerebro: str, cm, semente: int, kw_cerebro: dict):
    if cerebro == "instinto":
        return PoliticaInstintoMundo(CONFIG_PADRAO)
    cd = orq.config_do_braco(cerebro, None, True)
    return orq.Registro(DigiBrain(CONFIG_PADRAO, cd, cm, semente=semente, **kw_cerebro), CONFIG_DIGIBRAIN_INATOS.escala)


def vida(mecanica: str, cerebro: str, dono: str, semente: int):
    cm, corpo, lugar, kw_motor, kw_cerebro, ao_lado = MECANICAS[mecanica]
    cc = corpo or orq.bancada(DIAS, ORCAMENTO // DIAS).cfg_corpo_de(orq.bv.EspecVida(dono, orq.gl.BRACO_V11, semente))

    def fm(p, cfg, s, **kw):
        return com_corpo(MotorMundo)(p, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=cm, cfg_corpo=cc, **kw_motor, **kw)

    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, cm)
    extra = {"ao_lado": DonoFrutaAoLado(d, semente, CONFIG_FRUTA_AO_LADO_LIGADA, cm)} if ao_lado else {}
    p = politica(cerebro, cm, semente, kw_cerebro)
    return simular_vida_mundo(dono, d, p, semente, DIAS, ORCAMENTO, fm, rotulo_dono=dono, **extra), p


def impressao(mecanica: str, cerebro: str, dono: str, semente: int) -> dict:
    try:
        v, p = vida(mecanica, cerebro, dono, semente)
    except Exception as ex:                    # a recusa de hoje fica gravada, e tem de continuar igual
        return {"erro": type(ex).__name__, "mensagem": str(ex)}
    m = v.motor
    out = {**gm.impressao(m, v.interacoes), "decisoes": len(m.decisoes_mundo)}
    if cerebro != "instinto":
        c = orq.cerebro_de(p)
        out["cerebro"] = _sha(_texto(c.estado_interno()))
    return out


PASSO, RACAO_A_CADA, SACUDIR_A_CADA = 30, 360, 240     # o roteiro do dono que sacode a arvore, em ticks
MUNDOS_SACUDIR = {"ilha": CONFIG_MUNDO_ILHA}   # a ilha com agua exige o controlador do contrato


def roteiro_sacudir(mundo: str, cerebro: str, semente: int):
    """o dono que sacode a arvore (a acao do dono no jogo, `MotorMundo.sacudir_arvore`): a vida anda de PASSO em PASSO ticks; a cada
    RACAO_A_CADA o dono poe a racao no comedouro, e a cada SACUDIR_A_CADA ele sacode a primeira arvore do layout. Devolve (motor, politica)"""
    cm = MUNDOS_SACUDIR[mundo]
    cc = orq.bancada(DIAS, ORCAMENTO // DIAS).cfg_corpo_de(orq.bv.EspecVida("atencioso", orq.gl.BRACO_V11, semente))
    p = politica(cerebro, cm, semente, {})
    motor = com_corpo(MotorMundo)(p, CONFIG_PADRAO, semente, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=cm, cfg_corpo=cc,
                                  cfg_sacudir=CONFIG_SACUDIR_LIGADA)
    arvore = cm.layout.arvores[0][0]
    for _ in range(DIAS * TICKS_POR_DIA // PASSO):
        motor.avancar(PASSO)
        t = motor._estado.tick
        if t % RACAO_A_CADA == 0:
            motor.deixar_comida("racao", *motor.mundo.comedouro)
        if t % SACUDIR_A_CADA == 0:
            motor.sacudir_arvore(arvore)
    return motor, p


def impressao_sacudir(mundo: str, cerebro: str, semente: int) -> dict:
    try:
        m, p = roteiro_sacudir(mundo, cerebro, semente)
    except Exception as ex:                    # a recusa de hoje fica gravada, e tem de continuar igual
        return {"erro": type(ex).__name__, "mensagem": str(ex)}
    out = {**gm.impressao(m), "decisoes": len(m.decisoes_mundo), "sacudidas": len(m.mundo.sacudidas)}
    if cerebro != "instinto":
        out["cerebro"] = _sha(_texto(orq.cerebro_de(p).estado_interno()))
    return out


def gerar() -> dict:
    out = {f"{mec}|{c}|{dono}|{s}": impressao(mec, c, dono, s)
           for mec in MECANICAS for c in CEREBROS for dono in DONOS for s in SEMENTES}
    out.update({f"roteiro_sacudir|{mundo}|{c}|{s}": impressao_sacudir(mundo, c, s)
                for mundo in MUNDOS_SACUDIR for c in CEREBROS for s in SEMENTES})
    return out


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes da LZ2")
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
