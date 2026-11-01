"""Motivo unificado de decisao, para vida e combate (Parte A).

Somente leitura: calcular um motivo nao consome rng, nao muda estado de
politica nem decisao nenhuma. O motivo e registro estruturado produzido pela
propria decisao; a expressao (expressao.py) so pode mostrar menos do que ele.

Vida
  - PoliticaBandit: usa os pesos AMOSTRADOS que decidiram (ultima_decisao).
    contribuicao_i = x_i * (theta~_escolhida_i - media dos theta~_i das outras).
    So vira fator uma contribuicao POSITIVA (a favor da acao escolhida) e
    >= limiar_motivo, e so se o termo de valor MUDOU a escolha: se sem ele o
    argmax de log(prior) + Gumbel ja daria a mesma acao, quem decidiu foi o
    prior/ruido e o motivo fica sem fator (ver docs/REGISTRO_DESVIOS.md).
  - PoliticaInstinto: a regra que disparou (ultima_regra).
  - PoliticaLobos (V2, L1): quem decidiu foi o impulso (regra com um candidato, ou o
    sorteio com os pesos do prior e o mesmo u da a mesma acao) -> os fatores da regra
    do instinto; senao o lobo de decisao decidiu -> contribuicao da entrada j =
    x_j * (delta_escolhida_j - media dos delta_j dos outros candidatos), delta = w - w0,
    e vale a regra do bandit (positiva, >= limiar, no maximo 2). docs/PLANO_ANALISE_V2_L1.md, 4.1.
  Captura: PoliticaComMotivo embrulha a politica e le o registro depois de
  cada agir(); delega tudo o mais sem alterar nada.

Combate
  Adaptador do motivo que o combate V2 ja grava no log (indice da regra,
  "exploracao", "pesado_automatico", "oraculo"). Nao altera combate_v2/.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Sequence

from .config import CONFIG_EXPRESSAO, ConfigExpressao
from .events import AcaoPet, AcaoUsuario, LogDeEventos
from .memoria import FATORES_MEMORIA
from .memoria_espacos import FATORES_ESPACOS
from .policy import Observacao, Politica, PoliticaInstinto, Transicao
from .policies.lobos import ENTRADAS as ENTRADAS_LOBOS, ENTRADAS_MUNDO, FATORES_PLANO, REGRAS_MUNDO, sortear as sortear_lobos

ORIGENS = ("vida", "combate")

# nome do fator por indice de feature do bandit (policies/bandit.features)
FATOR_DA_FEATURE = (
    "habito", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo",
    "hora", "hora", "tempo_sem_cuidado",
)
# V2, N5-ACOPLADO: as regras do mundo (bola, fruta) e a sub-decisao da fruta (o incentivo ou o aprendido decidiu qual)
FATORES_MUNDO = ("bola", "fruta", "incentivo_fruta", "escolha_aprendida_fruta", "memoria_fruta")
# o pet que pensa, etapa 2: o plano decidiu (a sonda "quem decidiu" mudou a escolha); o fator leva o lugar e o tipo como parametros
FATORES_VIDA = tuple(dict.fromkeys(FATOR_DA_FEATURE)) + FATORES_MEMORIA + FATORES_ESPACOS + FATORES_MUNDO + FATORES_PLANO
# nome do fator por entrada da percepcao da PoliticaLobos (policies/lobos.ENTRADAS): os mesmos nomes do bandit
FATOR_DA_ENTRADA_LOBOS = ("habito", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora",
                          "tempo_sem_cuidado")
# as entradas do mundo (lobos.ENTRADAS_MUNDO), no fim da percepcao quando os lobos veem a bola e as frutas
FATOR_DA_ENTRADA_MUNDO = ("bola", "fruta")
_FATOR_POR_ENTRADA = dict(zip(ENTRADAS_LOBOS + ENTRADAS_MUNDO, FATOR_DA_ENTRADA_LOBOS + FATOR_DA_ENTRADA_MUNDO))

# regra do instinto -> fatores (variaveis da condicao que disparou)
_FATORES_INSTINTO = {
    "sono_exaustao": ("energia",),
    "sono_continuar": ("dormindo", "energia"),
    "sono_noite": ("hora", "energia"),
    "fome_moderada": ("fome",),
    "tempo_livre": (),          # sorteio ponderado sem condicao: nao ha causa a citar
}


@dataclass(frozen=True)
class Motivo:
    origem: str
    acao: str
    fatores: tuple[str, ...]
    evento_ref: tuple[int, ...]
    intensidade: float | None
    exploracao: bool
    tick: int | None = None      # vida
    turno: int | None = None     # combate

    def __post_init__(self) -> None:
        if self.origem not in ORIGENS:
            raise ValueError(f"origem invalida: {self.origem!r}")
        if len(self.fatores) > 2:
            raise ValueError(f"no maximo 2 fatores, veio {self.fatores}")
        if (self.tick is None) == (self.turno is None):
            raise ValueError("motivo precisa de tick (vida) OU turno (combate)")
        if self.origem == "vida":
            if self.tick is None or self.intensidade is None or not 0.0 <= self.intensidade <= 1.0:
                raise ValueError(f"motivo de vida precisa de tick e intensidade em [0,1]: {self}")
        else:
            if self.turno is None or self.intensidade is not None:
                raise ValueError(f"motivo de combate precisa de turno e intensidade None: {self}")
        if self.exploracao and self.fatores:
            raise ValueError("exploracao nao tem fator")

    def para_dict(self) -> dict:
        return {
            "origem": self.origem, "tick": self.tick, "turno": self.turno, "acao": self.acao,
            "fatores": list(self.fatores), "evento_ref": list(self.evento_ref),
            "intensidade": self.intensidade, "exploracao": self.exploracao,
        }


# ================================================================ vida


def motivo_bandit(decisao: dict, tick: int, ref_ultimo_cuidado: int | None,
                  cfg: ConfigExpressao = CONFIG_EXPRESSAO,
                  indice_do_ordinal: Callable[[int], int | None] | None = None) -> tuple[Motivo, dict]:
    """(Motivo, diagnostico). Funcao pura do registro da decisao.

    Com memoria (PoliticaBanditMemoria), as features extras viram fatores de
    memoria e o evento_ref aponta para a acao do dono que originou o valor.
    """
    x, escolhida = decisao["x"], decisao["acao"]
    amostras = decisao["amostras"]
    # a politica com memoria declara os proprios fatores (B1 e espacos tem 4 features cada)
    extras = tuple(decisao.get("fatores_memoria", FATORES_MEMORIA)) if len(x) > len(FATOR_DA_FEATURE) else ()
    nomes = FATOR_DA_FEATURE + extras
    if len(nomes) != len(x):
        raise ValueError(f"{len(x)} features, {len(nomes)} nomes de fator")
    outras = [a for a in amostras if a is not escolhida]
    contrib: dict[str, float] = {}
    for i, xi in enumerate(x):
        media = sum(amostras[a][i] for a in outras) / len(outras)
        nome = nomes[i]
        contrib[nome] = contrib.get(nome, 0.0) + xi * (amostras[escolhida][i] - media)

    sem_valor = {a: decisao["log_prior"][a] + decisao["gumbel"][a] for a in amostras}
    argmax_sem_valor = max(sem_valor, key=lambda a: (sem_valor[a], -list(amostras).index(a)))
    valor_decidiu = argmax_sem_valor is not escolhida

    positivos = sorted(((c, n) for n, c in contrib.items() if c >= cfg.limiar_motivo), reverse=True)
    maior_abs = max(contrib.items(), key=lambda kv: abs(kv[1]))
    fatores = tuple(n for _, n in positivos[:2]) if valor_decidiu else ()
    soma_pos = sum(c for c in contrib.values() if c > 0)
    intensidade = (positivos[0][0] / soma_pos) if fatores and soma_pos > 0 else 0.0
    refs_l = []
    for f in fatores:
        if f == "tempo_sem_cuidado" and ref_ultimo_cuidado is not None:
            refs_l.append(ref_ultimo_cuidado)
        elif f in extras and indice_do_ordinal is not None:
            ordinal = decisao.get("refs_memoria", {}).get(f)
            if ordinal is not None:
                refs_l.append(indice_do_ordinal(ordinal))
    refs = tuple(sorted(set(r for r in refs_l if r is not None)))
    diag = {
        "valor_decidiu": valor_decidiu,
        # formula literal da tarefa (maior |contribuicao| >= limiar), sem as checagens de honestidade
        "fator_formula_literal": maior_abs[0] if abs(maior_abs[1]) >= cfg.limiar_motivo else None,
    }
    return Motivo("vida", escolhida.value, fatores, refs, min(1.0, intensidade), False, tick=tick), diag


def motivo_instinto(regra: str, obs: Observacao, acao: AcaoPet, tick: int, ref_ultimo_cuidado: int | None,
                    cfg_instinto=None, termo_mundo: float = 0.0) -> Motivo:
    """`termo_mundo` (so nas regras do mundo): o peso que a bola deu a brincar (w_bola x bola) ou a fruta deu a comer
    (w_fruta x fruta), para a intensidade. Honestidade: a fruta e fator quando o pet comeu, porque sem fruta comer nem e candidato
    no tempo livre (mudou a escolha com certeza); a bola nunca e fator aqui, porque brincar ja era candidato e o instinto nao guarda
    o sorteio para saber se a bola mudou a escolha."""
    fome, higiene, energia, humor, *_ = obs.vetor_estado
    if regra in REGRAS_MUNDO:
        if termo_mundo <= 0.0:
            raise ValueError(f"regra do mundo {regra!r} sem o peso do termo do mundo")
        pesos = {AcaoPet.OCIOSO: 3.0, AcaoPet.EXPLORAR: 2.0 + 2.0 * energia,
                 AcaoPet.BRINCAR: 1.0 + 3.0 * humor, AcaoPet.CHAMAR_ATENCAO: 1.0}
        if regra == "bola_no_cenario":
            pesos[AcaoPet.BRINCAR] = pesos[AcaoPet.BRINCAR] + termo_mundo
            fatores = ()
        else:
            pesos[AcaoPet.COMER] = termo_mundo
            fatores = ("fruta",) if acao is AcaoPet.COMER else ()
        total = 0.0
        for p in pesos.values():
            total += p
        return Motivo("vida", acao.value, fatores, (), pesos[acao] / total, False, tick=tick)
    if regra == "pedido_necessidade" and acao is AcaoPet.COMER:
        # mundo fisico (instinto_mundo): com a fome urgente e para onde ir, o pet come; a causa e a fome (a higiene baixa nao o fez comer)
        fatores = ("fome",)
        intensidade = 1.0
    elif regra == "pedido_necessidade":
        fatores = tuple(n for n, v in (("fome", fome), ("higiene", higiene)) if v < 0.25)
        intensidade = 1.0
    elif regra == "abandono":
        fatores = ("tempo_sem_cuidado", "humor") if acao is AcaoPet.EMBURRAR else ("tempo_sem_cuidado",)
        intensidade = 1.0
    elif regra == "fome_moderada":
        fatores, intensidade = _FATORES_INSTINTO[regra], 0.5
    elif regra == "tempo_livre":
        pesos = {AcaoPet.OCIOSO: 3.0, AcaoPet.EXPLORAR: 2.0 + 2.0 * energia,
                 AcaoPet.BRINCAR: 1.0 + 3.0 * humor, AcaoPet.CHAMAR_ATENCAO: 1.0}
        fatores, intensidade = (), pesos[acao] / sum(pesos.values())
    elif regra in _FATORES_INSTINTO:
        fatores, intensidade = _FATORES_INSTINTO[regra], 1.0
    else:
        raise ValueError(f"regra do instinto desconhecida: {regra!r}")
    refs = (ref_ultimo_cuidado,) if "tempo_sem_cuidado" in fatores and ref_ultimo_cuidado is not None else ()
    return Motivo("vida", acao.value, fatores, refs, intensidade, False, tick=tick)


def _escolha_proporcional(presentes: list[str], pesos: list[float], u: float) -> str | None:
    """a conta de MotorFrutas._escolher / PoliticaLobos.escolher_fruta, passo a passo; None se todos os pesos sao zero"""
    total = 0.0
    for p in pesos:
        total += p
    if total <= 0.0:
        return None
    alvo = u * total
    acc = 0.0
    for f, p in zip(presentes, pesos):
        acc += p
        if alvo < acc:
            return f
    return presentes[-1]


def motivo_fruta(reg_fruta: dict, incentivos: dict, sonda_memoria: dict | None = None) -> tuple[str | None, str]:
    """(fator, lobo) da sub-decisao da fruta. O prior escolhe proporcional ao incentivo (coeficiente S); com o mesmo u, se o prior
    daria a mesma fruta, quem decidiu foi o incentivo (fator `incentivo_fruta`, lobo impulsos); senao o peso aprendido da fruta
    mudou a escolha (fator `escolha_aprendida_fruta`, lobo decisao). Incentivos todos zero: sorteio uniforme, sem fator.

    C4, M6 (lacuna 3 da auditoria): com a memoria do N6 ligada, a sonda contrafactual (`sonda_memoria`, do registro do motivo da politica)
    diz se a memoria mudou a fruta. Se mudou, quem decidiu foi a memoria (fator `memoria_fruta`, lobo memoria): "aprendi a escolher essa"
    seria falso. Sem a sonda (memoria desligada, ou uma fruta so), o motivo e o de sempre."""
    if sonda_memoria is not None and sonda_memoria.get("mudou") is True:
        return "memoria_fruta", "memoria"
    presentes = list(reg_fruta["presentes"])
    if set(incentivos) != set(presentes):
        raise ValueError(f"incentivos {sorted(incentivos)} nao sao os das frutas no cenario {presentes}")
    prior = _escolha_proporcional(presentes, [incentivos[f] for f in presentes], reg_fruta["u"])
    if prior is None:
        return None, "impulsos"
    if prior == reg_fruta["escolhida"]:
        return "incentivo_fruta", "impulsos"
    return "escolha_aprendida_fruta", "decisao"


def _motivo_regra_mundo(registro: dict, acao: AcaoPet, tick: int) -> Motivo:
    """O impulso decidiu numa regra do mundo. O termo do mundo vira fator so se, sem ele e com o mesmo u, a acao seria outra:
    bola_no_cenario sem a bola = o tempo livre (brincar com 1 + 3 x humor); fruta_no_cenario sem a fruta = comer com peso zero."""
    candidatos = list(registro["candidatos"])
    prior = registro["contribuicoes"]["impulsos"]
    contra = dict(prior)
    if registro["regra"] == "bola_no_cenario":
        contra[AcaoPet.BRINCAR.value] = 1.0 + 3.0 * registro["percepcao"]["humor"]
        termo = "bola"
    else:
        contra[AcaoPet.COMER.value] = 0.0
        termo = "fruta"
    sem = candidatos[sortear_lobos([contra[a] for a in candidatos], registro["u"])]
    fatores = (termo,) if sem != registro["acao"] else ()
    total = 0.0
    for a in candidatos:
        total += prior[a]
    return Motivo("vida", acao.value, fatores, (), min(1.0, max(0.0, prior[registro["acao"]] / total)), False, tick=tick)


def fator_do_plano(registro: dict) -> str | None:
    """O pet que pensa, etapa 2: o fator do plano quando a sonda "quem decidiu" mudou a escolha (a da decisao primeiro, depois a do
    alvo) e o cerebro achou o que nomear (`lobos._fator_do_plano`): `plano_arvore(J2,b)`, `plano_comida(b)` ou `plano_evita(a)`."""
    for chave in ("plano", "alvo_plano"):
        p = registro.get(chave)
        if p and p.get("plano_decidiu") and p.get("fator"):
            nome, *params = p["fator"]
            if nome not in FATORES_PLANO:
                raise ValueError(f"fator do plano desconhecido: {nome!r}")
            return f"{nome}({','.join(params)})"
    return None


def _com_plano(registro: dict, m: Motivo, diag: dict) -> tuple[Motivo, dict]:
    """o fator do plano na frente (no maximo 2 fatores); sem ele, o motivo de sempre"""
    fp = fator_do_plano(registro)
    if fp is None:
        return m, diag
    fatores = ((fp,) + m.fatores)[:2]
    refs = m.evento_ref if "tempo_sem_cuidado" in fatores else ()
    return (Motivo("vida", m.acao, fatores, refs, m.intensidade, m.exploracao, tick=m.tick),
            {**diag, "plano": fp, "lobo": "planejamento"})


def motivo_lobos(registro: dict, tick: int, ref_ultimo_cuidado: int | None,
                 cfg: ConfigExpressao = CONFIG_EXPRESSAO, incentivos: dict | None = None,
                 sonda_memoria: dict | None = None) -> tuple[Motivo, dict]:
    m, diag = _motivo_lobos_decisao(registro, tick, ref_ultimo_cuidado, cfg)
    if "fruta" not in registro:
        return _com_plano(registro, m, diag)
    # a sub-decisao da fruta (so com os lobos vendo as frutas): o fator dela entra no lugar do segundo fator da decisao de comer
    if incentivos is None:
        raise ValueError("registro com a sub-decisao da fruta sem os incentivos (o PoliticaComMotivo os recebe do motor)")
    fator, lobo = motivo_fruta(registro["fruta"], incentivos, sonda_memoria)
    fatores = (m.fatores[:1] + (fator,)) if fator else m.fatores
    refs = m.evento_ref if "tempo_sem_cuidado" in fatores else ()
    diag = {**diag, "fruta": {"lobo": lobo, "fator": fator, "escolhida": registro["fruta"]["escolhida"]}}
    return _com_plano(registro, Motivo("vida", m.acao, fatores, refs, m.intensidade, m.exploracao, tick=m.tick), diag)


def _motivo_lobos_decisao(registro: dict, tick: int, ref_ultimo_cuidado: int | None,
                          cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> tuple[Motivo, dict]:
    """(Motivo, diagnostico) da PoliticaLobos. Funcao pura do registro da decisao (`ultimo_motivo`).

    O impulso decidiu quando a regra tem um candidato so, ou quando o sorteio com os pesos do PRIOR e o mesmo
    u devolve a mesma acao: os fatores sao os da regra do instinto (motivo_instinto). Senao, o lobo de decisao
    decidiu: contribuicao da entrada j = termo aprendido da escolhida menos a media dos termos aprendidos dos
    outros candidatos; so vira fator uma contribuicao positiva e >= limiar_motivo (no maximo 2)."""
    if len(ENTRADAS_LOBOS) != len(FATOR_DA_ENTRADA_LOBOS):
        raise ValueError("entradas da PoliticaLobos e nomes de fator com tamanhos diferentes")
    acao = AcaoPet(registro["acao"])
    candidatos = list(registro["candidatos"])
    prior = registro["contribuicoes"]["impulsos"]
    comp = registro.get("competicao")
    if comp is not None:
        # a competicao entre as regras (V3-3/V3-4; docs/TAREFA_V2_V3_COMPETICAO.md, secao 3.4): o prior da disputa e o das propostas com o
        # kappa na regra do instinto, e o impulso que decidiu e o da regra de onde veio a acao escolhida (a mais urgente que a propoe)
        kappa = comp["kappa"]
        prior_kappa = [prior[a] * (kappa if comp["propostas"][a] == registro["regra"] else 1) for a in candidatos]
        impulso_decidiu = candidatos[sortear_lobos(prior_kappa, registro["u"])] == registro["acao"]
        if impulso_decidiu != (not comp["aprendido_decidiu"]):
            raise RuntimeError("motivo da competicao: o impulso refeito nao e o do registro (aprendido_decidiu)")
        if impulso_decidiu:
            p = registro["percepcao"]
            obs = Observacao(vetor_estado=(p["fome"], p["higiene"], p["energia"], p["humor"], p["saude"], p["sujeira"],
                                           p["dormindo"], p["hora"]), ticks_desde_cuidado=0, total_cuidados=0)
            regra_da_acao = comp["propostas"][registro["acao"]]
            m = motivo_instinto(regra_da_acao, obs, acao, tick, ref_ultimo_cuidado)
            return m, {"valor_decidiu": False, "fator_formula_literal": None, "lobo": "impulsos",
                       "competicao": {"regra_da_acao": regra_da_acao, "abertura_decidiu": comp["abertura_decidiu"]}}
    elif len(candidatos) == 1:
        impulso_decidiu = True
    else:
        impulso_decidiu = candidatos[sortear_lobos([prior[a] for a in candidatos], registro["u"])] == registro["acao"]
    if impulso_decidiu and registro.get("sem_impulsos"):
        # controle sem lobos (camada_unica): o prior decidiu e nao ha regra para citar
        intensidade = registro["pesos"][registro["acao"]] / sum(registro["pesos"][a] for a in candidatos)
        m = Motivo("vida", acao.value, (), (), min(1.0, max(0.0, intensidade)), False, tick=tick)
        return m, {"valor_decidiu": False, "fator_formula_literal": None, "lobo": "prior"}
    if impulso_decidiu and registro["regra"] in REGRAS_MUNDO:
        return _motivo_regra_mundo(registro, acao, tick), {"valor_decidiu": False, "fator_formula_literal": None,
                                                           "lobo": "impulsos"}
    if impulso_decidiu:
        p = registro["percepcao"]
        obs = Observacao(vetor_estado=(p["fome"], p["higiene"], p["energia"], p["humor"], p["saude"], p["sujeira"],
                                       p["dormindo"], p["hora"]), ticks_desde_cuidado=0, total_cuidados=0)
        m = motivo_instinto(registro["regra"], obs, acao, tick, ref_ultimo_cuidado)
        return m, {"valor_decidiu": False, "fator_formula_literal": None, "lobo": "impulsos"}
    aprendido = registro["aprendido"]
    if aprendido is None:
        raise RuntimeError("o lobo de decisao decidiu sem registro do termo aprendido")
    corpo = registro.get("aprendido_corpo")
    if corpo is not None and any(v != 0.0 for termos_a in corpo.values() for v in termos_a):
        # CORPO: as entradas novas (tedio, solidao...) aprendidas pesaram na decisao e nao tem fator nem texto na expressao; citar so as
        # entradas de hoje esconderia a causa. O motivo delas e da etapa 6 (os drives novos) ou da tarefa da expressao
        raise NotImplementedError("motivo com as entradas novas do corpo aprendidas: sem fator na expressao (etapa 6)")
    social = registro.get("aprendido_social")
    if social is not None and any(v != 0.0 for termos_a in social.values() for v in termos_a):
        # dois pets, etapa 4: as entradas sociais aprendidas pesaram na decisao e nao tem fator nem texto na expressao (como as do corpo)
        raise NotImplementedError("motivo com as entradas sociais aprendidas: sem fator na expressao")
    outras = [b for b in candidatos if b != registro["acao"]]
    # nomes pela ordem da percepcao do registro: as 10 de sempre e, com os lobos vendo o mundo, `bola` e `fruta` no fim
    nomes = [_FATOR_POR_ENTRADA[k] for k in registro["percepcao"]]
    if len(nomes) != len(aprendido[registro["acao"]]):
        raise ValueError(f"percepcao com {len(nomes)} entradas e termo aprendido com {len(aprendido[registro['acao']])}")
    contrib: dict[str, float] = {}
    for j, nome in enumerate(nomes):
        media = sum(aprendido[b][j] for b in outras) / len(outras)
        contrib[nome] = contrib.get(nome, 0.0) + (aprendido[registro["acao"]][j] - media)
    positivos = sorted(((c, n) for n, c in contrib.items() if c >= cfg.limiar_motivo), reverse=True)
    fatores = tuple(n for _, n in positivos[:2])
    soma_pos = sum(c for c in contrib.values() if c > 0)
    intensidade = (positivos[0][0] / soma_pos) if fatores and soma_pos > 0 else 0.0
    refs = (ref_ultimo_cuidado,) if "tempo_sem_cuidado" in fatores and ref_ultimo_cuidado is not None else ()
    diag = {"valor_decidiu": True, "fator_formula_literal": None, "lobo": "decisao"}
    if comp is not None:
        diag["competicao"] = {"regra_da_acao": comp["propostas"][registro["acao"]], "abertura_decidiu": comp["abertura_decidiu"]}
    return Motivo("vida", acao.value, fatores, refs, min(1.0, intensidade), False, tick=tick), diag


class PoliticaComMotivo:
    """Embrulha uma politica de vida e registra o motivo de cada decisao.

    Delega agir/observar/estado_interno/receber_acao_dono sem alterar nada: as
    mesmas chamadas, na mesma ordem, com a mesma rng. `indices_dono[k]` = indice
    no log do k-esimo evento de acao do dono (para evento_ref); opcional.
    """

    def __init__(self, interna: Politica, indices_dono: Sequence[int] | None = None,
                 cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> None:
        self.interna = interna
        self.nome = interna.nome
        self.cfg = cfg
        self._indices_dono = list(indices_dono) if indices_dono is not None else None
        self._n_dono = 0
        self._tick_ultimo_cuidado = 0
        self.motivos: list[Motivo] = []
        self.diagnosticos: list[dict] = []
        self.humores: list[float] = []   # humor observado em cada decisao (emote do bebe)
        self._ref_na_decisao: int | None = None
        # ganchos do MotorFrutas (LOBOS-MUNDO): repassados so se a politica embrulhada os tem, para o embrulho nao mudar a vida
        if hasattr(interna, "escolher_fruta"):
            self.escolher_fruta = self._escolher_fruta
        if hasattr(interna, "fruta_comida"):
            self.fruta_comida = interna.fruta_comida
        # ganchos do MotorMundo (MUNDO-CEREBROS): o mesmo regime, so se a politica embrulhada os tem (sem eles, o padrao do motor)
        if hasattr(interna, "escolher_alvo"):
            self.escolher_alvo = self._escolher_alvo
        if hasattr(interna, "fruta_na_mao"):           # o mundo do J5: a fruta na mao (os modelos do planejador a leem)
            self.fruta_na_mao = interna.fruta_na_mao
        if hasattr(interna, "consequencia_mundo"):
            self.consequencia_mundo = interna.consequencia_mundo
        # ganchos do MotorCorpo (CORPO, docs/TAREFA_V2_CORPO_DRIVES.md, secao 11): o mesmo regime. A licao do N5-ACOPLADO: um gancho nao
        # repassado muda a vida (com a chave do corpo, o cerebro falha alto na decisao seguinte)
        if hasattr(interna, "consequencia_corpo"):
            self.consequencia_corpo = interna.consequencia_corpo
        if hasattr(interna, "mudanca_no_corpo"):
            self.mudanca_no_corpo = self._mudanca_no_corpo
        if getattr(interna, "sem_explorar", False):
            # o P0z (plano do mundo, secao 3) e controle da premissa, nao um pet: o motivo do tempo livre usa os pesos literais
            raise ValueError("PoliticaComMotivo nao cobre o instinto do mundo em sem_explorar (o P0z nao e um pet do jogo)")

    def _indice_do_ordinal(self, k: int) -> int | None:
        return None if self._indices_dono is None else self._indices_dono[k - 1]

    def _ref_cuidado(self) -> int | None:
        if self._indices_dono is None or self._n_dono == 0:
            return None
        return self._indices_dono[self._n_dono - 1]

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        acao = self.interna.agir(obs, rng)
        if acao is AcaoPet.ALIVIAR:
            # o banheiro (TAREFA_V2_BANHEIRO): o aliviar, a regra urgente e a vontade nao tem fator nem texto na expressao ainda
            raise NotImplementedError("motivo do aliviar: sem fator nem texto na expressao (o banheiro, tarefa da expressao)")
        tick = obs.ticks_desde_cuidado + self._tick_ultimo_cuidado
        self._ref_na_decisao = self._ref_cuidado()
        if isinstance(self.interna, PoliticaInstinto):
            regra = self.interna.ultima_regra
            termo = 0.0
            termo_de = getattr(self.interna, "termo_mundo", None)    # o instinto do mundo fisico: o termo vem da percepcao nova
            if termo_de is not None:
                termo = termo_de(regra, obs)
            elif regra == "bola_no_cenario":
                termo = self.interna.cb.w_bola * obs.bola
            elif regra == "fruta_no_cenario":
                termo = self.interna.cf.w_fruta * obs.fruta
            m = motivo_instinto(regra, obs, acao, tick, self._ref_cuidado(), termo_mundo=termo)
            diag = {"valor_decidiu": None, "fator_formula_literal": None}
        elif hasattr(self.interna, "ultimo_motivo"):
            reg = self.interna.ultimo_motivo
            if reg is None or reg["acao"] != acao.value:
                raise RuntimeError("registro da decisao da PoliticaLobos nao corresponde a acao devolvida")
            m, diag = motivo_lobos(reg, tick, self._ref_cuidado(), self.cfg)
        elif hasattr(self.interna, "ultima_decisao"):
            dec = self.interna.ultima_decisao
            if dec is None or dec["acao"] is not acao:
                raise RuntimeError("registro da decisao do bandit nao corresponde a acao devolvida")
            m, diag = motivo_bandit(dec, tick, self._ref_cuidado(), self.cfg, self._indice_do_ordinal)
        else:
            raise TypeError(f"politica sem registro de decisao: {type(self.interna).__name__}")
        self.motivos.append(m)
        self.diagnosticos.append(diag)
        self.humores.append(obs.vetor_estado[3])
        return acao

    def observar(self, transicao: Transicao) -> None:
        self.interna.observar(transicao)

    def _escolher_fruta(self, presentes: list[str], incentivos: dict, u: float) -> str | None:
        """Repassa a sub-decisao da fruta e refaz o motivo da decisao de comer com ela (os incentivos so chegam por aqui)."""
        escolhida = self.interna.escolher_fruta(presentes, incentivos, u)
        if escolhida is None:
            return None
        reg = getattr(self.interna, "ultimo_motivo", None)
        if reg is None or "fruta" not in reg or not self.motivos or reg["acao"] != AcaoPet.COMER.value:
            raise RuntimeError("sub-decisao da fruta sem a decisao de comer registrada")
        sonda = ((getattr(self.interna, "motivos", None) or [{}])[-1].get("fruta") or {}).get("sonda_memoria")
        m, diag = motivo_lobos(reg, self.motivos[-1].tick, self._ref_na_decisao, self.cfg, incentivos=dict(incentivos),
                               sonda_memoria=sonda)
        self.motivos[-1] = m
        self.diagnosticos[-1] = diag
        return escolhida

    def _escolher_alvo(self, acao: AcaoPet, candidatos: list, percepcao, u: int):
        """Repassa o alvo e, com o planejador (o pet que pensa), refaz o motivo da decisao com a sonda do alvo (ela so existe depois do
        agir). Sem o planejador o registro nao tem `alvo_plano` e o motivo fica o de sempre."""
        alvo = self.interna.escolher_alvo(acao, candidatos, percepcao, u)
        reg = getattr(self.interna, "ultimo_motivo", None)
        if reg is not None and reg.get("alvo_plano") is not None:
            if not self.motivos or reg["acao"] != acao.value:
                raise RuntimeError("alvo do plano sem a decisao registrada")
            m, diag = motivo_lobos(reg, self.motivos[-1].tick, self._ref_na_decisao, self.cfg)
            self.motivos[-1] = m
            self.diagnosticos[-1] = diag
        return alvo

    def _mudanca_no_corpo(self, obs_antes: Observacao, obs_depois: Observacao) -> None:
        """O carinho com `gestos` (secao 8) nao passa por `receber_acao_dono`, mas e uma acao do dono no log: o relogio do cuidado e o
        indice dos eventos do dono andam aqui, e o gancho segue para a politica."""
        self._tick_ultimo_cuidado = self._tick_ultimo_cuidado + obs_antes.ticks_desde_cuidado
        self._n_dono += 1
        self.interna.mudanca_no_corpo(obs_antes, obs_depois)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        self._tick_ultimo_cuidado = tick
        self._n_dono += 1
        f = getattr(self.interna, "receber_acao_dono", None)
        if f is not None:
            f(acao, tick)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()


def indices_eventos_dono(log: LogDeEventos) -> list[int]:
    return [i for i, e in enumerate(log) if e.tipo == "acao_usuario"]


def motivos_de_vida(log: LogDeEventos, fabrica: Callable, semente: int, cfg: ConfigExpressao = CONFIG_EXPRESSAO):
    """Reproduz a vida do log com o embrulho; devolve (motor, PoliticaComMotivo)."""
    from .treino import reproduzir_com_feedback

    indices = indices_eventos_dono(log)
    embrulho: list[PoliticaComMotivo] = []

    def fab(c):
        p = PoliticaComMotivo(fabrica(c), indices, cfg)
        embrulho.append(p)
        return p

    motor = reproduzir_com_feedback(log, fab, semente=semente)
    return motor, embrulho[0]


# ================================================================ combate


def nome_condicao(c) -> str:
    """'nome' ou 'nome(p1,p2)' com distancia/acao pelo rotulo."""
    if not c.params:
        return c.nome
    partes = []
    for p in c.params:
        partes.append(getattr(p, "rotulo", None) or getattr(p, "value", p))
    return f"{c.nome}({','.join(str(x) for x in partes)})"


def nome_base(fator: str) -> str:
    return fator.split("(", 1)[0]


def _refs_condicao(c, turno: int, historico_op: tuple) -> tuple[int, ...]:
    """Turnos do log (1-based, campo 't') que sustentam a condicao na decisao do turno `turno`."""
    n = c.nome
    if n == "sempre":
        return ()
    if n == "oponente_preparando":
        return (turno - 1,)
    if n == "oponente_repete":
        _, k = c.params
        return tuple(range(turno - k, turno))
    if n == "oponente_frequente":
        janela = 5
        ini = max(1, turno - janela)
        return tuple(t for t in range(ini, turno) if historico_op[t - 1] is c.params[0])
    return (turno,)  # condicao de estado (hp, guts, distancia): turno corrente


def regra_do_motivo(estilo, motivo_log):
    """Regra de gambits indicada por um motivo inteiro do log (ou None)."""
    if not isinstance(motivo_log, int):
        return None
    g = estilo.gambits
    return g.regras[motivo_log] if motivo_log < len(g.regras) else g.final


def motivos_de_partida(log: list[dict], lutadores, cfg=None) -> list[tuple[int, int, Motivo, object]]:
    """[(turno, lado, Motivo, estado_antes_da_decisao)] reproduzindo a partida pelo log.

    `lutadores` = (Lutador_a, Lutador_b) do combate V2. Evento desconhecido levanta erro.
    """
    from .combate_v2.regras import Acao, estado_inicial, resolver

    a, b = lutadores
    estado = estado_inicial((a.condicao.hp_max, b.condicao.hp_max),
                            (a.condicao.guts_inicial, b.condicao.guts_inicial),
                            (a.condicao.regen_guts, b.condicao.regen_guts))
    saida = []
    for ev in log:
        tipo = ev.get("tipo")
        if tipo in ("cabecalho", "fim"):
            continue
        if tipo != "turno":
            raise ValueError(f"evento desconhecido no log de combate: {tipo!r}")
        t = ev["t"]
        for lado, (acao, m) in enumerate(((ev["a"], ev["ma"]), (ev["b"], ev["mb"]))):
            estilo = (a, b)[lado].estilo
            hist_op = estado.oponente(lado).historico
            if m == "exploracao":
                mot = Motivo("combate", acao, (), (), None, True, turno=t)
            elif m == "pesado_automatico":
                mot = Motivo("combate", acao, (), (t - 1,), None, False, turno=t)
            elif m == "oraculo":
                mot = Motivo("combate", acao, (), (), None, False, turno=t)
            elif isinstance(m, int):
                regra = regra_do_motivo(estilo, m)
                conds = [c for c in regra.condicoes if c.nome != "sempre"]
                refs = sorted({r for c in conds for r in _refs_condicao(c, t, hist_op)})
                mot = Motivo("combate", acao, tuple(nome_condicao(c) for c in conds), tuple(refs),
                             None, False, turno=t)
            else:
                raise ValueError(f"motivo de combate desconhecido: {m!r}")
            saida.append((t, lado, mot, estado))
        estado, _ = resolver(estado, Acao(ev["a"]), Acao(ev["b"]), cfg)
    return saida


def motivos_de_partida_v21(log: list[dict], lutadores) -> list[tuple[int, int, Motivo, object]]:
    """Como `motivos_de_partida`, para o combate V2.1 (`lutadores` = Lutador de combate_v2/v21)."""
    from .combate_v2.v21.regras import Acao, estado_inicial, resolver

    a, b = lutadores
    estado = estado_inicial(a.perfil, b.perfil)
    saida = []
    for ev in log:
        tipo = ev.get("tipo")
        if tipo in ("cabecalho", "fim"):
            continue
        if tipo != "turno":
            raise ValueError(f"evento desconhecido no log de combate: {tipo!r}")
        t = ev["t"]
        for lado, (acao, m) in enumerate(((ev["a"], ev["ma"]), (ev["b"], ev["mb"]))):
            g = (a, b)[lado].gambits
            hist_op = estado.oponente(lado).historico
            if m == "exploracao":
                mot = Motivo("combate", acao, (), (), None, True, turno=t)
            elif m == "pesado_automatico":
                mot = Motivo("combate", acao, (), (t - 1,), None, False, turno=t)
            elif isinstance(m, int):
                regra = g.regras[m] if m < len(g.regras) else g.final
                conds = [c for c in regra.condicoes if c.nome != "sempre"]
                refs = sorted({r for c in conds for r in _refs_condicao(c, t, hist_op)})
                mot = Motivo("combate", acao, tuple(nome_condicao(c) for c in conds), tuple(refs),
                             None, False, turno=t)
            else:
                raise ValueError(f"motivo de combate desconhecido: {m!r}")
            saida.append((t, lado, mot, estado))
        estado, _ = resolver(estado, Acao(ev["a"]), Acao(ev["b"]))
    return saida
