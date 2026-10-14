"""A bancada da V2, módulo `grupo`.

Dois pets: a bancada do grupo.

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path

from digilab.config import CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA, ConfigFrutas
from digilab.grupo import Grupo
from digilab.donos import criar_dono
from digilab.events import FRUTAS
from digilab.mundo import ESTILOS_LUGAR, MotorMundo
from digilab.protocol import derivar_semente

from . import RAIZ
from .regras_mundo import _Registro


# ================================================================== dois pets: a bancada do grupo (TAREFA_V2_DOIS_PETS, etapa 5)
# PLANO_ANALISE_V2_DOIS_PETS, secoes 2 a 4: o grupo como celula, com um dono (o atencioso, so com o cuidado, PMF-3) e o orcamento por pet
# (DP-7, a validacao inicial), pelo `simular_grupo` do #257. O cerebro e o A do ponto e da montagem da bancada, com o alvo aprendido (#255).
# A visao, o toque e a disputa entre os pets (etapa 3, do A, #263) e as entradas sociais e o modelo dos outros no cerebro (etapa 4, a
# segunda metade, do B, #266) estao na main: o cerebro do grupo os liga, e as medidas sociais e as do modelo saem dos registros. Com os
# canais da montagem completa, a rota do humor no mundo fisico (#269, `presenca_fruta_mundo`) tambem fica ligada.

ROTULO_RUIM = "dois-pets-ruim"               # o tipo que faz mal na unidade (plano, secao 2)
ROTULO_EMBARALHA = "dois-pets-embaralha"     # o desarranjo do A embaralhado (plano, secao 3)
DECISOES_POR_DIA = TICKS_POR_DIA // CONFIG_PADRAO.intervalo_decisao_ticks
if DECISOES_POR_DIA * CONFIG_PADRAO.intervalo_decisao_ticks != TICKS_POR_DIA:   # pragma: no cover - 1440 / 15
    raise RuntimeError("o dia nao e multiplo do intervalo de decisao")
BRACO_DO_B = "P1"                            # todo B e P1 (plano, secao 3)
JANELA_PRIMARIA_DIAS = 7                     # a R_B nos 7 primeiros dias do B (PDP-2)


def tipo_ruim(semente: int) -> str:
    """O tipo de fruta que faz mal na unidade (plano, secao 2): uniforme entre as tres, pela rng propria derivar_semente("dois-pets-ruim",
    s), um sorteio. Nao toca outra rng."""
    return FRUTAS[random.Random(derivar_semente(ROTULO_RUIM, semente)).randrange(len(FRUTAS))]


def desarranjo_dois_pets(semente: int) -> dict:
    """O desarranjo pi do A embaralhado (plano, secao 3), como o desarranjo_n6: um dos dois ciclos de {a, b, c}, pela rng propria
    derivar_semente("dois-pets-embaralha", s). Nenhuma fruta em si mesma."""
    if len(FRUTAS) != 3:                     # pragma: no cover - o mundo tem tres tipos de fruta
        raise ValueError("desarranjo_dois_pets escrito para tres frutas")
    passo = 1 + random.Random(derivar_semente(ROTULO_EMBARALHA, semente)).randrange(len(FRUTAS) - 1)
    return {f: FRUTAS[(i + passo) % len(FRUTAS)] for i, f in enumerate(FRUTAS)}


def efeito_dois_pets(ruim: str, cf: ConfigFrutas) -> dict:
    """O efeito de cada tipo de fruta (plano, secao 2): o ruim com o `efeito_humor_ruim`, os outros dois neutros (`efeito_humor_neutro`).
    Cada tipo tem arvores no jardim e na mata (LAYOUT_MUNDO_PADRAO)."""
    if ruim not in FRUTAS:
        raise ValueError(f"tipo ruim {ruim!r}: so {FRUTAS}")
    return {f: (cf.efeito_humor_ruim if f == ruim else cf.efeito_humor_neutro) for f in FRUTAS}


class MotorMundoTroca(MotorMundo):
    """O MotorMundo do A embaralhado (plano, secao 3): nos K dias o efeito das frutas e o desarranjado (o tipo pi(ruim) faz mal) e, no dia
    K, o mundo passa ao efeito verdadeiro. So no grupo: a troca vem no fim do avanco que chega ao tick do mundo `tick_troca` (o grupo avanca
    em passos do dono, e o dia e multiplo do passo), entao nenhum tick do mundo >= tick_troca roda com o efeito de antes; um avanco que
    passasse do tick falha alto. Na entrada do B (o mesmo tick) os dois ja tem o efeito verdadeiro, como o Grupo confere. A troca fica no
    registro derivado (`troca`) e o replay a refaz pela mesma fabrica."""

    def __init__(self, *a, tick_troca: int, efeito_depois: dict, **kw) -> None:
        super().__init__(*a, **kw)
        if not self.cmf.ligada or self.mundo is None or kw.get("mundo") is None:
            raise ValueError("o A embaralhado so existe no grupo (o MotorMundo ligado sobre o Mundo do grupo)")
        if type(tick_troca) is not int or tick_troca <= self.entrada_mundo or tick_troca % TICKS_POR_DIA:
            raise ValueError(f"a troca e num inicio de dia do mundo depois da entrada do pet: {tick_troca!r}")
        if set(efeito_depois) != set(FRUTAS):
            raise ValueError(f"efeito_depois precisa de {FRUTAS}: {sorted(efeito_depois)}")
        self.tick_troca = tick_troca
        self.efeito_antes = dict(self.efeito_frutas)
        self.efeito_depois = dict(efeito_depois)
        self.troca: dict | None = None

    def efeito_no_tick(self, tick_mundo: int) -> dict:
        return self.efeito_antes if tick_mundo < self.tick_troca else self.efeito_depois

    def _fechar_avanco(self) -> None:
        super()._fechar_avanco()
        agora = self.entrada_mundo + self._estado.tick
        if self.troca is None and agora >= self.tick_troca:
            if agora != self.tick_troca:
                raise RuntimeError(f"o avanco passou da troca do efeito (tick {self.tick_troca}, agora {agora})")
            self.efeito_frutas = dict(self.efeito_depois)
            self.troca = {"tick": agora, "antes": dict(self.efeito_antes), "depois": dict(self.efeito_depois)}


@dataclass(frozen=True)
class BracoGrupo:
    """Um braco do plano dos dois pets (secao 3): o companheiro do B e quando ele entra. O B (P1) entra no dia K e vive os `dias` da
    bancada; o A entra no tick 0 (informativo, embaralhado) ou junto com o B (ingenuo). O "A-so" e o da calibracao do K (secao 5): o A
    informativo sozinho, sem B, os `dias` da bancada."""

    rotulo: str
    companheiro: str | None          # None (sem A), "informativo", "embaralhado" ou "ingenuo"
    a: str | None                    # o braco do A na bancada: "P1" ou "P0"; None sem A
    a_entra: str | None              # "inicio" (tick 0) ou "dia_k" (com o B); None sem A
    b: bool = True                   # o B entra no dia K


BRACOS_GRUPO = {
    "B-so": BracoGrupo("B-so", None, None, None),
    "B+Ainf": BracoGrupo("B+Ainf", "informativo", "P1", "inicio"),
    "B+Aemb": BracoGrupo("B+Aemb", "embaralhado", "P1", "inicio"),
    "B+Aing": BracoGrupo("B+Aing", "ingenuo", "P0", "dia_k"),
    "A-so": BracoGrupo("A-so", "informativo", "P1", "inicio", b=False),
}


@dataclass(frozen=True)
class EspecGrupo:
    """Um grupo da bancada: o braco, a semente do grupo s (o mundo e o A; o B pela derivacao do segundo pet, `sementes_do_grupo`), o K, o
    dono e o lugar dele (plano, secao 2: o atencioso, no comedouro). Sem genoma: o temperamento neutro, como o mundo fisico sem genoma."""

    braco: str
    semente: int
    k: int
    dono: str = "atencioso"
    lugar: str = "comedouro"
    mundo: str = "fisico"

    @property
    def nome(self) -> str:
        m = "" if self.mundo == "fisico" else f"~{self.mundo}"
        return f"{self.dono}-{self.braco}{m}~{self.lugar}~K{self.k}@{self.semente}"


@dataclass
class VidaGrupo:
    espec: EspecGrupo
    grupo: Grupo
    interacoes: dict                 # por pet: o gasto do dono (o orcamento inteiro, conferido pelo canal)
    retirados: dict                  # por pet: os sinais do dono que o filtro sem_ensino ao vivo nao deixou chegar (PMF-3)

    @property
    def nome(self) -> str:
        return self.espec.nome


class _RegistroGrupo(_Registro):
    """O _Registro do replay de medicao do grupo, mais os pesos do alvo aprendido no fim de cada dia do pet (antes da primeira decisao do
    dia seguinte; o do ultimo dia, `fim`). So le."""

    def __init__(self, interna: PoliticaDoBraco) -> None:
        super().__init__(interna)
        self.pesos_alvo_dia: list = []
        self.modelo_dia: list = []

    def pesos_alvo(self):
        w = getattr(self.interna.cerebro, "_pesos_alvo_mundo", None)
        return {k: dict(t) for k, t in w.items()} if w else None

    def modelo(self):
        """o modelo dos outros (so registrado, #266) como o cerebro o serializa: por outro, a familiaridade, a confianca e a afinidade"""
        m = getattr(self.interna.cerebro, "_modelo", None)
        return None if m is None else m.para_dict()["outros"]

    def agir(self, obs, rng):
        k = len(self.decisoes)
        if k and k % DECISOES_POR_DIA == 0:
            self.pesos_alvo_dia.append(self.pesos_alvo())
            self.modelo_dia.append(self.modelo())
        return super().agir(obs, rng)

    def fim(self) -> None:
        self.pesos_alvo_dia.append(self.pesos_alvo())
        self.modelo_dia.append(self.modelo())


def _validar_espec_grupo(eg: EspecGrupo) -> BracoGrupo:
    if eg.braco not in BRACOS_GRUPO:
        raise KeyError(f"braco do grupo desconhecido {eg.braco!r}: {sorted(BRACOS_GRUPO)}")
    bg = BRACOS_GRUPO[eg.braco]
    if mundo_de(eg.mundo).fisico is None:
        raise ValueError(f"{eg.nome}: o grupo vive no mundo fisico, nao {eg.mundo!r}")
    if eg.lugar not in ESTILOS_LUGAR:
        raise ValueError(f"lugar {eg.lugar!r}: so {ESTILOS_LUGAR}")
    if type(eg.k) is not int or eg.k < 0:
        raise ValueError(f"K tem de ser inteiro >= 0: {eg.k!r}")
    if not bg.b and eg.k != 0:
        raise ValueError(f"{eg.braco}: sem B nao ha dia K (K = 0)")
    if bg.a_entra == "inicio" and bg.b and eg.k < 1:
        raise ValueError(f"{eg.braco}: o A vive K >= 1 dias sozinho antes do B")
    return bg


def _entradas(eg: EspecGrupo) -> list[tuple[str, str, int]]:
    """(id, braco na bancada, tick do mundo da entrada) de cada pet do grupo, na ordem dos ids."""
    bg = BRACOS_GRUPO[eg.braco]
    dia_k = eg.k * TICKS_POR_DIA
    out = []
    if bg.a is not None:
        out.append(("A", bg.a, 0 if bg.a_entra == "inicio" else dia_k))
    if bg.b:
        out.append(("B", BRACO_DO_B, dia_k))
    return out


def _resumo_grupo(g: Grupo) -> tuple:
    """O resumo do Grupo, a troca do A embaralhado e a projecao de cada pet (o log de hoje do pet, igual ao do motor)."""
    for i, m in g.motores.items():
        if g.registro.projecao(i).para_jsonl() != m.log.para_jsonl():
            raise ReplayDivergiu(f"a projecao do registro do grupo para {i} nao e o log do motor")
    return (g.registro.para_jsonl(), g.resumo(), {i: getattr(m, "troca", None) for i, m in g.motores.items()})


CHAVES_CONFIG_GRUPO = {"descricao", "plano", "tipo", "bracos", "sementes", "unidades", "k_dias", "dias", "orcamento_por_dia", "dono",
                       "lugar", "ponto", "lobos", "montagem", "consequencia", "mundo", "teto_pesos"}


def validar_config_grupo(cfg: dict) -> dict:
    """A config da bancada do grupo (`"tipo": "grupo"`). As unidades usam o prefixo `dois_pets`. Fora das sementes dos testes, a run e do
    plano: pede o `plano` e a montagem completa (o cerebro do plano, secao 2, com os canais e a rota do humor do #269)."""
    faltam = {"tipo", "bracos", "k_dias", "dias", "orcamento_por_dia"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG_GRUPO
    if faltam or sobram:
        raise ValueError(f"config do grupo: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["tipo"] != "grupo":
        raise ValueError(f"config do grupo com tipo {cfg['tipo']!r}")
    if ("sementes" in cfg) == ("unidades" in cfg):
        raise ValueError("config do grupo: ou 'sementes' ou 'unidades' (bases x K derivadas), um dos dois")
    bracos = list(cfg["bracos"])
    if not bracos or len(set(bracos)) != len(bracos) or any(b not in BRACOS_GRUPO for b in bracos):
        raise ValueError(f"bracos do grupo {bracos}: so {sorted(BRACOS_GRUPO)}, sem repetir")
    if "ponto" in cfg and cfg["ponto"] not in PONTOS_APRENDIZ:
        raise ValueError(f"ponto do aprendiz {cfg['ponto']!r}: so {sorted(PONTOS_APRENDIZ)}")
    if "montagem" in cfg and cfg["montagem"] not in MONTAGENS:
        raise ValueError(f"montagem {cfg['montagem']!r}: so {MONTAGENS}")
    if "mundo" in cfg:
        replace(CONFIG_MUNDO_LIGADA, **cfg["mundo"])
    validar_teto_pesos(cfg)
    for b in bracos:                             # o K, o dono e o lugar de cada braco
        _validar_espec_grupo(EspecGrupo(b, 101, 0 if not BRACOS_GRUPO[b].b else int(cfg["k_dias"]), cfg.get("dono", "atencioso"),
                                        cfg.get("lugar", "comedouro")))
    criar_dono(cfg.get("dono", "atencioso"))
    if "unidades" in cfg:
        u = cfg["unidades"]
        if set(u) != {"bases", "k", "prefixo"} or u["prefixo"] != "dois_pets":
            raise ValueError(f"unidades do grupo: {{'bases', 'k', 'prefixo': 'dois_pets'}}, nao {u}")
        unidades_derivadas(u["bases"], int(u["k"]), u["prefixo"])
        usadas = set(u["bases"])
    else:
        usadas = set(cfg["sementes"])
    for ini, fim, motivo in FAIXAS_QUEIMADAS:
        queimadas = sorted(x for x in usadas if ini <= x <= fim)
        if queimadas:
            raise SementeSemPlano(f"sementes/bases {queimadas} na faixa queimada {ini}...{fim} ({motivo}): nao usar para nada")
    fora = sorted(usadas - SEMENTES_TESTE)
    if fora:
        plano = cfg.get("plano")
        if not plano or not (RAIZ / plano).is_file():
            raise SementeSemPlano(f"sementes/bases {fora} fora das dos testes: precisa do plano de analise registrado (campo 'plano')")
        if cfg.get("montagem") != "completa":
            raise ValueError("a run do plano dos dois pets usa o cerebro do plano (secao 2): a montagem completa")
    return cfg


def rodar_grupo(cfg: dict, pasta: Path) -> dict:
    """Os grupos de todos os bracos x unidades, gravados (o registro do grupo em JSONL) e rejogados do disco; as medidas por grupo."""
    validar_config_grupo(cfg)
    bancada = bancada_da_config({**cfg, "orcamento": int(cfg["orcamento_por_dia"]) * int(cfg["dias"])})
    if "unidades" in cfg:
        unidades = unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), cfg["unidades"]["prefixo"])
        sementes = [(u["semente"], {"base": u["base"], "k": u["k"]}) for u in unidades]
    else:
        sementes = [(int(s), None) for s in cfg["sementes"]]
    teto = None
    if validar_teto_pesos(cfg) is not None:      # o teto do plano: os pesos declarados sao os do maior cerebro dos pets dos bracos
        bg_ = bancada.bancada_grupo()
        cerebros = {}
        for braco in cfg["bracos"]:
            eg = EspecGrupo(braco, sementes[0][0], int(cfg["k_dias"]) if BRACOS_GRUPO[braco].b else 0, cfg.get("dono", "atencioso"),
                            cfg.get("lugar", "comedouro"))
            for ident, _, _ in _entradas(eg):
                cerebros[f"{braco}/{ident}"] = do_braco(bg_.politica(bancada.espec_do_pet(eg, ident))).cerebro
        teto = conferir_teto_pesos(cfg, cerebros)
    grupos, medidas = {}, {}
    for (s, unidade), braco in product(sementes, cfg["bracos"]):
        k = int(cfg["k_dias"]) if BRACOS_GRUPO[braco].b else 0
        v = bancada.grupo(EspecGrupo(braco, s, k, cfg.get("dono", "atencioso"), cfg.get("lugar", "comedouro")))
        caminho = pasta / "grupos" / f"{v.nome}.jsonl"
        _gravar(caminho, v.grupo.registro.para_jsonl())
        bancada.conferir_replay_grupo(v, caminho.read_text(encoding="utf-8"))
        grupos[v.nome] = v
        medidas[v.nome] = {**bancada.medir_grupo(v), "unidade": unidade}
    _gravar(pasta / "medidas.json", _dump(medidas))
    _gravar(pasta / "meta.json", _dump({**meta(cfg), "grupo_sha256": _sha(RAIZ / "digilab" / "grupo.py"),
                                        **({} if teto is None else {"teto_pesos": teto})}))
    return {"grupos": grupos, "medidas": medidas}


# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote
# não ter importação circular (tools/dividir_bancada.py)
from .faixas import FAIXAS_QUEIMADAS, SEMENTES_TESTE, SementeSemPlano, unidades_derivadas  # noqa: E402
from .mundos import mundo_de  # noqa: E402
from .bracos import MONTAGENS, PoliticaDoBraco, PONTOS_APRENDIZ  # noqa: E402
from .vida import ReplayDivergiu  # noqa: E402
from .medidas import do_braco  # noqa: E402
from .config import bancada_da_config, conferir_teto_pesos, validar_teto_pesos  # noqa: E402
from .rodar import _dump, _gravar, meta, _sha  # noqa: E402
