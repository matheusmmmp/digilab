"""M-ADAPT, o adaptador cerebro-corpo-motor (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.1 e 7): o DigiBrain modular sob o `Protocol`
`Politica` (digilab/policy.py), com os ganchos que o motor procura no cerebro (`escolher_alvo`, `consequencia_mundo`,
`consequencia_corpo`, `receber_acao_dono`). Nenhuma conta propria: encaminha a Observacao aos modulos, a rng de politica so ao M-ARB, e a
consequencia ao M-AFETO, ao M-PLAST, ao M-ESTADO e ao M-MEM.

**A decisao** (`agir`): M-SENS -> M-AFETO -> M-ESTADO (o contexto) -> M-MEM (a recuperacao, com a subchave) -> M-IMPULSO (as unidades,
com o incentivo e o habito do M-PLAST) -> M-ARB (a escolha, o u e as sondas) -> M-ESTADO (a intencao escolhida; a opcao trocada vai ao
P2). A unidade escolhida e o par (comportamento, alvo): o `agir` devolve a acao, e o `escolher_alvo` o alvo dela. O reflexo do sono e uma
conta so (`Arbitragem.reflexo`), feita depois do M-AFETO e passada ao M-ESTADO e ao M-ARB. Com a subchave `intencao_suspensa` (a parte (b)
da L-2, docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md, secao 2.3), o M-ESTADO cuida da intencao suspensa antes do contexto
(`cuidar_suspensa`); as que acabam ali vao ao P2 e ao registro com as do `escolhida`, e o motivo ganha a `suspensa`. Com a subchave
`redecidir_evento` (a C3, docs/ESPEC_REDECIDIR_EVENTO_DIGIBRAIN_MODULAR.md, secao 2.3), o M-ESTADO confere os eventos antes do contexto
(`eventos`, com o gesto do dono desde a decisao anterior), o M-ARB segura o candidato sem sorteio quando nao ha evento, e o motivo ganha
`segurada` e `evento`.

**O alvo** (`escolher_alvo`): o candidato do motor do tipo (e do id) da unidade escolhida; o `u` do motor e ignorado. **A excecao unica**
(a PE-14 revista): em EXPLORAR, o lugar lembrado do M-MEM e entregue como `Alvo.ponto(x, y)`, fora da lista do motor, que o valida por
conta propria (`MotorMundo._validar_alvo`: so em EXPLORAR, coordenadas inteiras dentro do mapa). Brincar sem bola a vista nao tem alvo
(devolve None, e o padrao do motor sem bola e nenhum).

**A consequencia:** a ordem dos ganchos no motor com o mundo e o corpo e `agir`, `escolher_alvo`, `observar`, `consequencia_mundo` (so
nas acoes com alvo) e `consequencia_corpo`. A decisao guarda tudo numa pendencia e so a fecha no comeco da decisao seguinte.

**As falhas altas** (secao 4.1, o padrao do A em lobos.py:2318-2330):
  - a Observacao chega sem `corpo` ou sem `mundo`;
  - uma decisao fica sem o gancho de consequencia (o corpo e o `observar`; o do mundo nas acoes com alvo), ou o motor nao pediu o alvo
    numa acao com alvo;
  - o alvo da unidade nao esta entre os candidatos (salvo o `ponto`, so em EXPLORAR), ou o gancho chega para outra acao;
  - uma subchave desligada e o termo do modulo diferente de 0 numa decisao (ou o estado dele fora de 0).

**Os gestos do dono** (`receber_acao_dono`): o motor os entrega (o MotorComFeedback e o tapa do corpo); o M-ADAPT so os registra na
decisao seguinte. Nenhum modulo os recebe como sinal: o corpo os sente pelos receptores e o dono pesa pela consequencia no mundo, nunca
como recompensa direta (a D-B do PLANO_V2_PESQUISA, secao 3; escolha PROPOSTA da etapa 1a).

**O registro** (secao 7): cada decisao guarda o seu motivo em `motivos` (derivado, nunca no log): as unidades com os termos, os pesos, o
u, a escolha, o afeto, o estado, a memoria, as sondas e, no fechamento, a consequencia."""
from __future__ import annotations

import random
from dataclasses import dataclass

from ..config import (CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, VERSAO_PET_DIGIBRAIN, Config,
                      ConfigDigibrain, ConfigDigibrainInatos, ConfigMundo)
from ..events import AcaoPet, AcaoUsuario
from ..modelo_mundo import raiz_inteira
from ..mundo import ACOES_COM_ALVO, Alvo
from ..policies.lobos import leitura_receptor
from ..policy import Observacao, Transicao
from ._comum import chave_json
from .afeto import Afeto
from .arb import Arbitragem
from .estado import EstadoDinamico
from .impulso import Impulso
from .mem import Memoria
from .plast import Plasticidade
from .sens import COMIDAS_BOAS, Sens, classe_do_tipo


class DigibrainDesligado(RuntimeError):
    """o DigiBrain modular montado com a ConfigDigibrain desligada"""


@dataclass(frozen=True)
class Intencao:
    """a escolha do M-ARB vista pelo motor: a acao e, nas acoes com alvo, o tipo do candidato do motor, o id dele (a comida, a bola) e,
    no lugar lembrado, o ponto"""

    acao: AcaoPet
    tipo_alvo: str | None = None
    id_alvo: int | None = None
    ponto: tuple | None = None


@dataclass
class Modulos:
    """os modulos da DM-3, um por arquivo"""

    sens: Sens
    afeto: Afeto
    estado: EstadoDinamico
    impulso: Impulso
    mem: Memoria
    arb: Arbitragem
    plast: Plasticidade

    def itens(self) -> tuple:
        return (("sens", self.sens), ("afeto", self.afeto), ("estado", self.estado), ("impulso", self.impulso), ("mem", self.mem),
                ("arb", self.arb), ("plast", self.plast))


def montar_modulos(cfg: Config, cd: ConfigDigibrain, cm: ConfigMundo, inatos: ConfigDigibrainInatos,
                   serie_e_doadora: tuple | None) -> Modulos:
    return Modulos(sens=Sens(cfg, cm, inatos), afeto=Afeto(cfg, cd, inatos, serie_e_doadora), estado=EstadoDinamico(cfg, cd, inatos),
                   impulso=Impulso(inatos, cd), mem=Memoria(cm, inatos), arb=Arbitragem(inatos), plast=Plasticidade(cd, inatos))


def intencao_da_unidade(unidade: dict) -> Intencao:
    acao, tipo, ident = unidade["chave"]
    a = AcaoPet(acao)
    if tipo == "ponto":
        return Intencao(a, "ponto", None, tuple(ident))
    return Intencao(a, tipo, ident if tipo in ("comida", "bola") else None)


class DigiBrain:
    """o cerebro modular (a v13, DM-5), so com a ConfigDigibrain ligada"""

    nome = "digibrain"
    versao_pet = VERSAO_PET_DIGIBRAIN

    def __init__(self, cfg: Config | None = None, cfg_digibrain: ConfigDigibrain | None = None, cfg_mundo: ConfigMundo | None = None,
                 inatos: ConfigDigibrainInatos | None = None, serie_e_doadora: tuple | None = None) -> None:
        self.cd = cfg_digibrain or CONFIG_DIGIBRAIN
        if not self.cd.ligada:
            raise DigibrainDesligado("o DigiBrain modular so existe com a ConfigDigibrain ligada")
        self.cfg = cfg or CONFIG_PADRAO
        self.cm = cfg_mundo or CONFIG_MUNDO_LIGADA      # so a geometria (o raio da visao, a celula): a mesma no layout do MVP
        self.inatos = inatos or CONFIG_DIGIBRAIN_INATOS
        self.S = self.inatos.escala
        self.m = montar_modulos(self.cfg, self.cd, self.cm, self.inatos, serie_e_doadora)
        self.k = 0
        self.motivos: list[dict] = []
        self._pendencia: dict | None = None
        self._gestos: list = []
        self.gestos = {}

    @property
    def ultimo_motivo(self) -> dict | None:
        return self.motivos[-1] if self.motivos else None

    # ------------------------------------------------------------ a decisao
    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        if obs.corpo is None or obs.mundo is None:
            raise ValueError("o DigiBrain modular decide com o corpo e o mundo na Observacao (obs.corpo e obs.mundo)")
        if self._pendencia is not None:
            self._fechar(self._pendencia)
            self._pendencia = None
        m, cd = self.m, self.cd
        k = self.k
        sens = m.sens.codificar(obs)
        receptores = m.sens.receptores
        m.plast.montar(receptores)
        afeto = m.afeto.ler(sens)
        reflexo = m.arb.reflexo(sens)                              # uma conta so, ao M-ESTADO e ao M-ARB (a L-2, secao 2.3)
        retomadas = m.estado.retomadas
        fins_susp = m.estado.cuidar_suspensa(sens, afeto, reflexo) if cd.intencao_suspensa else []
        evento, segurar = m.estado.eventos(sens, afeto, reflexo, bool(self._gestos)) if cd.redecidir_evento else ([], None)
        ctx = m.estado.contexto()
        memoria = m.mem.recuperar(sens, afeto) if cd.m_mem else None
        unidades, z = m.impulso.unidades(sens, afeto, ctx, m.plast, memoria, m.afeto.drives(receptores))
        esc = m.arb.escolher(unidades, afeto, sens, rng, reflexo, segurar)  # a rng de politica vai so ao M-ARB
        self._conferir_desligadas(unidades)
        unidade = esc["unidade"]
        fins = fins_susp + m.estado.escolhida(unidade, z, afeto["g_apr"], k, reflexo)
        if cd.redecidir_evento:                       # a C3: o candidato fora da lista (ou com peso 0) e o E-FIM (RE-2)
            evento = evento + (["E-FIM"] if esc["fora"] else [])
            m.estado.registrar_redecisao(unidade["chave"], esc["segurada"], reflexo, evento)
        creditos = _creditar(m.plast, fins, cd)
        if cd.credito_corrida:                        # a C2: a corrida que a troca de comportamento fechou, ao P2 uma vez so
            fechadas = m.estado.corridas_fechadas
            corridas = [{"b": c["b"], "inicio": c["inicio"], "n": c["n"], "r": c["r"]} for c in fechadas]
            creditos += [x for x in (m.plast.creditar(c) for c in fechadas) if x is not None]
        intencao = intencao_da_unidade(unidade)
        urg = afeto["urgencias"]
        self.motivos.append({
            "k": k, "acao": intencao.acao.value, "escolha": chave_json(unidade["chave"]), "tipo_escolha": unidade["tipo"],
            "reflexo": esc["reflexo"],
            "nada_a_fazer": esc["nada_a_fazer"], "u": esc["u"],
            "unidades": [{"chave": chave_json(x["chave"]), "termos": x["termos"], "a": x["a"], "w": w}
                         for x, w in zip(unidades, esc["pesos"])],
            "afeto": {"urgencias": urg, "V": afeto["V"], "E": afeto["E"], "e_usada": afeto["e_usada"], "g_apr": afeto["g_apr"],
                      "g_exp": afeto["g_exp"]},
            "estado": {"I": chave_json(ctx["I"]), "C": ctx["C"], "n_sp": ctx["n_sp"], "F": ctx["F"]},
            "memoria": None if memoria is None else {"pista": memoria["pista"], "recuperado": memoria["recuperado"],
                                                     "lugar": memoria["lugar"], "valor": memoria["valor"]},
            "sondas": esc["sondas"],
            "falta_fome": sens["falta"].get("fome"),
            "contexto": {"drive": max(sorted(urg), key=lambda r: urg[r]) if urg else None,
                         "comida_vista": sens["conjuncoes"]["comida_vista"] > 0, "noite": sens["contexto"]["noite"] > 0},
            "fins": _registrados(fins), "creditos": creditos, "gestos": self._gestos,
            "consequencia": None})
        entregue = [_fim(f) for f in fins if not f.get("registro", True)]
        if entregue:                                  # a busca guardada (DX-4), entregue sem a opcao composta: so com a subchave
            self.motivos[-1]["busca_entregue"] = entregue
        if cd.credito_corrida:                        # a C2: desligada, nenhum campo novo
            self.motivos[-1]["corridas"] = corridas
        if cd.intencao_suspensa:                      # a L-2: a suspensa ao fim da decisao e a retomada (desligada, nenhum campo novo)
            self.motivos[-1]["suspensa"] = m.estado.suspensa_resumo()
            self.motivos[-1]["retomou"] = m.estado.retomadas > retomadas
        if cd.redecidir_evento:                       # a C3: desligada, nenhum campo novo
            self.motivos[-1]["segurada"] = esc["segurada"]
            self.motivos[-1]["evento"] = evento
        self._gestos = []
        self._pendencia = {"k": k, "intencao": intencao, "unidade": unidade, "sens": sens, "g_apr": afeto["g_apr"], "pediu": False,
                           "alvo": None, "corpo": None, "transicao": None, "mundo": None}
        self.k += 1
        return intencao.acao

    def escolher_alvo(self, acao: AcaoPet, candidatos: list, percepcao, u: int):
        p = self._pendente(acao, "escolher_alvo")
        if p["pediu"]:
            raise RuntimeError(f"escolher_alvo duas vezes na mesma decisao ({acao.value})")
        p["pediu"] = True
        it = p["intencao"]
        if it.tipo_alvo is None:
            if acao is AcaoPet.BRINCAR and not any(c.tipo == "bola" for c in candidatos):
                return None                                         # brincar sem bola a vista: sem alvo
            raise ValueError(f"a intencao de {acao.value} chegou sem objeto, e o motor pede um alvo")
        if it.tipo_alvo == "ponto":
            if acao is not AcaoPet.EXPLORAR:                        # pragma: no cover - so o explorar tem a unidade do lugar
                raise ValueError(f"o lugar lembrado (Alvo.ponto) so em EXPLORAR, nao em {acao.value}")
            alvo = Alvo.ponto(*it.ponto)
            self.motivos[-1]["alvo"] = {**alvo.para_dict(), "do_mem": True}
            p["alvo"] = alvo
            return alvo
        alvo = next((c for c in candidatos if c.tipo == it.tipo_alvo and (it.id_alvo is None or c.id == it.id_alvo)), None)
        if alvo is None:
            raise ValueError(f"o alvo da intencao ({it.tipo_alvo}, {it.id_alvo}) nao esta entre os candidatos do motor: "
                             f"{[(c.tipo, c.id) for c in candidatos]}")
        self.motivos[-1]["alvo"] = {**alvo.para_dict(), "do_mem": False}
        p["alvo"] = alvo
        return alvo

    # ------------------------------------------------------------ a consequencia (guardada; vai aos modulos na decisao seguinte)
    def consequencia_corpo(self, acao: AcaoPet, ocorrido: dict, obs_depois: Observacao) -> None:
        p = self._pendente(acao, "consequencia_corpo")
        if p["corpo"] is not None:
            raise RuntimeError("consequencia_corpo duas vezes na mesma decisao")
        p["corpo"] = (ocorrido, obs_depois)

    def observar(self, transicao: Transicao) -> None:
        p = self._pendente(transicao.acao, "observar")
        if p["transicao"] is not None:
            raise RuntimeError("observar duas vezes na mesma decisao")
        p["transicao"] = transicao

    def consequencia_mundo(self, acao: AcaoPet, ocorrido: dict, obs_depois: Observacao) -> None:
        p = self._pendente(acao, "consequencia_mundo")
        if p["mundo"] is not None:
            raise RuntimeError("consequencia_mundo duas vezes na mesma decisao")
        p["mundo"] = (ocorrido, obs_depois)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """o gesto do dono, so registrado (a docstring do modulo)"""
        self._gestos.append([acao.value, tick])
        self.gestos[acao.value] = self.gestos.get(acao.value, 0) + 1

    def estado_interno(self) -> dict:
        return {"nome": self.nome, "versao_pet": self.versao_pet, "k": self.k, "pendente": self._pendencia is not None,
                "gestos": dict(sorted(self.gestos.items())), "modulos": {nome: mod.estado_interno() for nome, mod in self.m.itens()
                                                                          if hasattr(mod, "estado_interno")},
                "motivos": self.motivos}

    # ------------------------------------------------------------ a pendencia
    def _pendente(self, acao: AcaoPet, gancho: str) -> dict:
        p = self._pendencia
        if p is None:
            raise RuntimeError(f"{gancho} sem decisao pendente")
        if p["intencao"].acao is not acao:
            raise RuntimeError(f"{gancho} de {acao.value} na decisao de {p['intencao'].acao.value}")
        return p

    def _conferir_desligadas(self, unidades: list[dict]) -> None:
        """com uma subchave desligada, o termo do modulo e 0 em toda unidade e o estado dele fica em 0 (falha alto)"""
        cd, m = self.cd, self.m
        for termo, ligada in (("incentivo", cd.p1), ("habito", cd.p2), ("memoria", cd.m_mem), ("persistencia", cd.persistencia)):
            if not ligada and any(x["termos"][termo] != 0 for x in unidades):
                raise RuntimeError(f"a subchave do termo {termo!r} esta desligada e o termo nao e 0")
        if not cd.p1 and not m.plast.desfecho_zero():
            raise RuntimeError("sem o P1, o desfecho e o andar ficam em 0")
        if not cd.p2 and not m.plast.habito_zero():
            raise RuntimeError("sem o P2, o habito fica em 0")
        if not cd.m_mem and m.mem.episodios:
            raise RuntimeError("sem o M-MEM, a memoria fica vazia")

    def _fechar(self, p: dict) -> None:
        """a consequencia da decisao anterior aos modulos"""
        it, m, S = p["intencao"], self.m, self.S
        acao = it.acao
        if p["corpo"] is None or p["transicao"] is None:
            raise RuntimeError(f"a decisao de {acao.value} ficou sem o gancho de consequencia (o corpo e o observar)")
        com_alvo = acao in ACOES_COM_ALVO
        if com_alvo and not p["pediu"]:
            raise RuntimeError(f"a decisao de {acao.value} tinha alvo, e o motor nao pediu o alvo")
        if com_alvo and p["mundo"] is None:
            raise RuntimeError(f"a decisao de {acao.value} ficou sem o consequencia_mundo")
        pc0 = p["sens"]["pc"]
        pc1 = p["corpo"][1].corpo
        pm1 = p["transicao"].observacao_seguinte.mundo
        if pc1 is None or pm1 is None:
            raise RuntimeError("a consequencia sem o corpo ou sem o mundo de depois")
        ocorrido = p["mundo"][0] if p["mundo"] is not None else None
        recs = m.sens.receptores
        cons = m.afeto.consequencia(pc0, pc1, recs)
        l0 = [leitura_receptor(pc0, r, S) for r in recs]
        l1 = [leitura_receptor(pc1, r, S) for r in recs]
        pos0, pos1 = p["sens"]["pos"], (pm1.x, pm1.y)
        comeu = None if ocorrido is None else ocorrido["comeu"]
        classe_comida = None if comeu is None else ("podre" if comeu["situacao"] == "podre" else comeu["tipo"])
        p1 = None
        if acao is AcaoPet.COMER:
            p1 = m.plast.consequencia_p1("comer", classe_comida if comeu is not None and comeu["como"] == "comer" else None, l0, l1,
                                         pos0, pos1, p["g_apr"])
        elif acao is AcaoPet.BRINCAR:
            p1 = m.plast.consequencia_p1("brincar", "bola" if ocorrido["brincou_com_bola"] else None, l0, l1, pos0, pos1, p["g_apr"])
        chave = p["unidade"]["chave"]
        visto, d = True, None
        if chave[1] in ("comida", "bola"):
            alvo = next((v for v in pm1.vistos if v[0] == chave[2]), None)
            visto, d = alvo is not None, None if alvo is None else alvo[4]
        elif chave[1] == "ponto":
            px, py = chave[2]
            d = raiz_inteira((px - pos1[0]) * (px - pos1[0]) + (py - pos1[1]) * (py - pos1[1]))
        fins = m.estado.consequencia(cons["r_n"], ocorrido, {
            "visto": visto, "d": d, "ha_cheiro": pm1.direcao_cheiro != 0,
            "comida_boa_vista": any(classe_do_tipo(v[1]) in COMIDAS_BOAS for v in pm1.vistos)})
        creditos = _creditar(m.plast, fins, self.cd)
        episodio = None
        if self.cd.m_mem:
            base = {"decisao": p["k"], "regiao": pm1.regiao, "delta": dict(zip(recs, [b - a for a, b in zip(l0, l1)])), "r": cons["r"],
                    "r_n": cons["r_n"], "hora": p["sens"]["minuto"], "fome_antes": p["sens"]["falta"].get("fome")}
            if comeu is not None:
                episodio = m.mem.codificar({**base, "ponto": pos1, "classe": classe_comida, "origem": "consumo"})
            elif chave[1] == "ponto" and ocorrido["chegou"]:
                episodio = m.mem.codificar({**base, "ponto": chave[2], "classe": "nao_havia", "origem": "visita", "r": 0,
                                                 "r_n": 0})
        motivo = self.motivos[p["k"]]
        motivo["consequencia"] = {"r": cons["r"], "r_n": cons["r_n"], "canais": cons["canais"],
                                  "comeu": None if comeu is None else {"id": comeu["id"], "tipo": comeu["tipo"],
                                                                       "situacao": comeu["situacao"], "como": comeu["como"]},
                                  "chegou": None if ocorrido is None else ocorrido["chegou"], "p1": p1, "creditos": creditos,
                                  "episodio": episodio}
        motivo["fins"] = motivo["fins"] + _registrados(fins)


def _creditar(plast: Plasticidade, fins: list[dict], cd: ConfigDigibrain | None = None) -> list[dict]:
    """as opcoes que acabaram ao P2, salvo a busca guardada no "achou" (DX-4: o credito dela segue pela opcao composta). Com a
    `credito_corrida` (C2) nenhuma opcao vai ao P2: o credito e o da corrida do comportamento, entregue pelo `agir`"""
    if cd is not None and cd.credito_corrida:
        return []
    return [c for c in (plast.creditar(f) for f in fins if f.get("credito", True)) if c is not None]


def _registrados(fins: list[dict]) -> list[dict]:
    """os fins para o registro: sem as opcoes de uma decisao e sem a busca entregue depois do "achou" (ja registrada nele)"""
    return [_fim(f) for f in fins if f["motivo"] != "unica" and f.get("registro", True)]


def _fim(f: dict) -> dict:
    """o resumo de uma opcao que acabou, para o registro (a opcao composta da DX-4 marcada)"""
    out = {"chave": chave_json(f["chave"]), "inicio": f["inicio"], "n": f["n"], "motivo": f["motivo"], "meta": f["meta"], "r": f["r"]}
    if f.get("composta"):
        out["composta"] = True
    if "n_susp" in f:                                 # a L-2: a intencao que ja foi suspensa (so com a subchave), para as S-1 e S-2
        out["n_susp"] = f["n_susp"]
    return out
