"""A bateria de sondas da INDIVIDUALIDADE (docs/TAREFA_V3_INDIVIDUALIDADE.md, etapa I1; docs/futuro/individualidade_pet.md, secao 3).

Uma sonda e uma situacao padronizada aplicada a uma COPIA do pet num tick T da vida. A copia sai do replay do log da vida ate T
(`reproduzir_mundo(..., ate_tick=T)`); a vida real nao e tocada (o G2: o log e o resumo da vida saem os mesmos com e sem a bateria).
Cada replica da sonda e uma copia profunda da copia do dia, com a rng de politica trocada por uma derivada (`derivar_semente`), para
separar o pet do acaso da sonda.

As janelas (D-IND-I1-1: o "dono some" e o "tedio" sao a mesma janela, a nula, lida por dois tracos):
  - `nula`        nada acontece: sem gesto do dono, sem objeto novo. E o controle das outras e a leitura do `chamar_atencao` (o dono
                  some, a faceta `apego_dono`) e do `explorar` (o tedio; o drive do tedio esta ligado no corpo das vidas da C4);
  - `comida_nova` uma fruta `a` perto do pet (o mundo do produto nunca tem fruta: a classe e nova); pelo `deixar_comida` do motor, que
                  e contato do dono, como no jogo (D-IND-I1-2);
  - `longe`       a racao no canto do mapa mais longe do pet, tambem pelo `deixar_comida` (contato);
  - `bola`        a bola parada perto do pet (`deixar_bola`, nao e contato);
  - `susto`       o `tapa` (o corpo dos gestos sobe susto, dor e estresse), SO NA COPIA: a vida real nunca recebe o tapa.

O momento do dia: a primeira decisao acordada da vida real a partir de HORA_SONDA, dentro de JANELA_BUSCA; sem nenhuma, o dia fica sem
sonda (`tick` None). A bateria so grava as decisoes da janela; os tracos e a analise sao do I2, com plano registrado antes.

Todos os numeros abaixo sao PROPOSTOS, SEM FONTE (ferramenta de medida, nao mecanica do pet: nao entram no `config.py`)."""
from __future__ import annotations

import copy
import copyreg
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.ambiente import _PoliticaComBola  # noqa: E402
from digilab.frutas import _PoliticaComFrutas  # noqa: E402
from digilab.modelo_mundo import PoliticaComModelo  # noqa: E402
from digilab.mundo import _PoliticaComMundo, deslocar  # noqa: E402
from digilab.obediencia import _PoliticaObservada  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.rede_de_si import PoliticaComRede  # noqa: E402


def _refazer(cls, estado: dict):
    obj = cls.__new__(cls)
    obj.__dict__.update(estado)
    return obj


# A copia profunda do motor (D-IND-I1-3): os embrulhos de politica delegam todo atributo ao embrulhado pelo `__getattr__`, e o `copy`
# padrao cria a copia sem ele e pergunta pelo `__setstate__`, o que entra em recursao. O redutor copia o `__dict__` (o embrulhado e o motor,
# que a copia profunda leva juntos pelo memo). So muda como o objeto e copiado; o `digilab/` nao muda. A lista sao os embrulhos com
# `__getattr__` do `digilab/` que ficam entre o motor e o cerebro, e o `Registro` do orquestrador do prototipo.
EMBRULHOS = (_PoliticaObservada, _PoliticaComBola, _PoliticaComFrutas, _PoliticaComMundo, PoliticaComModelo, PoliticaComRede, orq.Registro)
for _cls in EMBRULHOS:
    copyreg.pickle(_cls, lambda o: (_refazer, (type(o), o.__dict__)))

TICKS_POR_DIA = 1440
PASSO_DONO = 15                 # o passo do dono das vidas (CONFIG_DONOS.passo_ticks); o momento cai num passo
HORA_SONDA = 600                # PROPOSTO, SEM FONTE: 10 h do dia
JANELA_BUSCA = 480              # PROPOSTO, SEM FONTE: a primeira decisao acordada ate as 18 h
JANELA_TICKS = 240              # PROPOSTO, SEM FONTE: 4 h, 16 decisoes de 15 ticks (o longe precisa de tempo para andar)
REPLICAS = 3                    # PROPOSTO, SEM FONTE
DIST_PERTO = 64                 # PROPOSTO, SEM FONTE: 4 celulas de 16 subunidades (dentro da visao)
MARGEM_CANTO = 16               # PROPOSTO, SEM FONTE: uma celula de folga da parede
FRUTA_NOVA = "a"

JANELAS = ("nula", "comida_nova", "longe", "bola", "susto")
ACAO_CHAVE = {"nula": "chamar_atencao", "comida_nova": "comer", "longe": "comer", "bola": "brincar", "susto": None}


class SondaDesconhecida(ValueError):
    pass


def momentos(motor, dias: int) -> list[tuple[int, int | None]]:
    """(dia, tick) de cada dia: o passo do dono em que cai a primeira decisao acordada da vida real em
    [dia x 1440 + HORA_SONDA, + JANELA_BUSCA]; None se o pet dormiu a janela toda. O dia 0 so tem a sonda se a vida ja passou dela."""
    fim = motor.estado()["tick"]
    saida = []
    for dia in range(dias):
        ini = dia * TICKS_POR_DIA + HORA_SONDA
        tick = next((t for t, a in motor._acoes_pet if ini <= t <= ini + JANELA_BUSCA and a is not AcaoPet.DORMIR), None)
        if tick is not None:
            tick -= tick % PASSO_DONO
            if tick + JANELA_TICKS > fim:
                raise ValueError(f"a janela da sonda do dia {dia} passa do fim da vida")
        saida.append((dia, tick))
    return saida


def copia_em(motor, fabricas_vida: tuple, semente: int, tick: int):
    """o pet no tick, pelo replay do log da vida (nao toca o motor da vida)"""
    fp, fm = fabricas_vida
    m = orq.reproduzir_mundo(motor.log, fp, semente=semente, fabrica_motor=fm, ate_tick=tick)
    if m.estado()["tick"] != tick:
        raise RuntimeError(f"o replay parou no tick {m.estado()['tick']}, nao no {tick}")
    return m


def _limites(m) -> tuple[int, int]:
    cm = m.cmf
    return cm.celulas_x * cm.sub - 1, cm.celulas_y * cm.sub - 1


def _canto_longe(m) -> tuple[int, int]:
    xm, ym = _limites(m)
    px, py = m.pet
    cantos = [(MARGEM_CANTO, MARGEM_CANTO), (xm - MARGEM_CANTO, MARGEM_CANTO), (MARGEM_CANTO, ym - MARGEM_CANTO),
              (xm - MARGEM_CANTO, ym - MARGEM_CANTO)]
    return max(cantos, key=lambda c: ((c[0] - px) ** 2 + (c[1] - py) ** 2, c))


def aplicar(janela: str, m, rng: random.Random) -> int | None:
    """poe a situacao na copia; devolve o id da comida posta (comida_nova e longe) ou None"""
    if janela not in JANELAS:
        raise SondaDesconhecida(janela)
    if janela == "comida_nova":
        x, y = deslocar(*m.pet, rng.randrange(16), DIST_PERTO, m.cmf)
        m.deixar_comida(FRUTA_NOVA, x, y)
        return m.deixadas[-1]["id"]
    if janela == "longe":
        m.deixar_comida("racao", *_canto_longe(m))
        return m.deixadas[-1]["id"]
    if janela == "bola":
        m.deixar_bola(*deslocar(*m.pet, rng.randrange(16), DIST_PERTO, m.cmf))
    elif janela == "susto":
        m.observar(AcaoUsuario.TAPA)
    return None


def ler_janela(janela: str, m, alvo: int | None) -> dict:
    """avanca a copia JANELA_TICKS e le as decisoes da janela, pelo registro do cerebro"""
    c = orq.cerebro_de(m.politica)
    n0, pos0 = len(c.motivos), m.pet
    m.avancar(JANELA_TICKS)
    decisoes = c.motivos[n0:]
    if not decisoes:
        raise RuntimeError(f"{janela}: a janela nao teve decisao")
    acoes = [d["acao"] for d in decisoes]
    chave = ACAO_CHAVE[janela]
    if alvo is not None:
        lat = next((i for i, d in enumerate(decisoes) if list(d["escolha"]) == ["comer", "comida", alvo]), None)
    else:
        lat = next((i for i, a in enumerate(acoes) if a == chave), None) if chave else None
    contagem: dict[str, int] = {}
    for a in acoes:
        contagem[a] = contagem.get(a, 0) + 1
    return {"acoes": acoes, "contagem": dict(sorted(contagem.items())), "latencia": lat, "n": len(decisoes),
            "pos0": list(pos0), "pos1": list(m.pet), "corpo_fim": m.estado()["corpo"]}


def bateria(motor, fabricas_vida: tuple, semente: int, dias: int, replicas: int = REPLICAS) -> dict:
    """a bateria da vida inteira: por dia, por janela, por replica. Nada do motor da vida muda."""
    log_antes = motor.log.para_jsonl()
    saida = []
    for dia, tick in momentos(motor, dias):
        reg = {"dia": dia, "tick": tick, "janelas": {}}
        if tick is not None:
            base = copia_em(motor, fabricas_vida, semente, tick)
            for janela in JANELAS:
                reps = []
                for r in range(replicas):
                    m = copy.deepcopy(base)
                    m._rng_politica = random.Random(derivar_semente("individualidade-politica", semente, dia, janela, r))
                    alvo = aplicar(janela, m, random.Random(derivar_semente("individualidade-posicao", semente, dia, janela, r)))
                    reps.append(ler_janela(janela, m, alvo))
                reg["janelas"][janela] = reps
        saida.append(reg)
    if motor.log.para_jsonl() != log_antes:
        raise RuntimeError("a bateria mudou o log da vida (G2)")
    return {"semente": semente, "dias": dias, "replicas": replicas, "hora": HORA_SONDA, "janela_ticks": JANELA_TICKS, "por_dia": saida}


def vida_com_bateria(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int,
                     replicas: int = REPLICAS):
    """a vida da C4 (`run_v2_memoria_autobio.viver`) e a bateria dela; devolve (motor, registro, fabricas, bateria)"""
    motor, registro, fab, _ = ma.viver(braco, dono, lugar, semente, dias, orcamento_por_dia)
    return motor, registro, fab, bateria(motor, fab, semente, dias, replicas)
