"""M-ESTADO, o estado dinamico (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 3 e 4.4), na forma I (integradores com vazamento).

A intencao em curso I* = (b, o) so existe nas unidades com um alvo de identidade fixa (PROPOSTO): comer a comida `id`, brincar com a bola,
explorar o lugar lembrado. Nas outras (o cheiro e o vagar, cujo ponto o motor refaz a cada decisao, e as sem alvo) cada decisao e uma
opcao de uma decisao so, sem compromisso nem frustracao.

O estado: I*, o compromisso C em [0, S], a distancia ao alvo na ultima decisao, as decisoes seguidas sem progresso `n_sp` e a
frustracao F em [0, S]. A atualizacao:
  - a cada decisao (`contexto`): F <- F - mul(k_F', F); a persistencia h = mul(w_pers, C), so para I* e so com a subchave;
  - escolheu I* de novo (`escolhida`): C <- C + mul(k_C, S - C); escolheu outra: a I* anterior acaba sem a meta ("trocou") e, se a nova
    e uma intencao, I* <- a nova, com C <- mul(k_C, S);
  - na consequencia: com a meta (comeu a comida, brincou com a bola, chegou ao lugar), C = 0; o alvo fora dos `vistos` depois de andar e
    sem cheiro ("sumiu"), ou `n_sp >= N_desiste` decisoes sem a distancia cair ("desistiu"), a intencao acaba sem a meta;
  - acabou sem a meta: F <- F + mul(k_F, S - F).

O credito (PE-3, por opcao; o M-PLAST, secao 4.8): cada opcao guarda a elegibilidade e_j = z_j da decisao que a comecou, soma o r_n de
cada consequencia dela, e e entregue ao P2 quando acaba (com a meta, sem ela, ou na propria consequencia, nas opcoes de uma decisao).
Sem rng."""
from __future__ import annotations

from ..config import CONFIG_DIGIBRAIN_INATOS, Config, ConfigDigibrain, ConfigDigibrainInatos
from ._comum import chave_json, clamp, ganho_de_tau, mul

TIPOS_INTENCAO = (("comer", "comida"), ("brincar", "bola"), ("explorar", "ponto"))


def e_intencao(chave: tuple) -> bool:
    return (chave[0], chave[1]) in TIPOS_INTENCAO


class EstadoDinamico:
    """o M-ESTADO (docstring do modulo)"""

    def __init__(self, cfg: Config, cfg_digibrain: ConfigDigibrain, inatos: ConfigDigibrainInatos | None = None) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.cd = cfg_digibrain
        self.S = self.p.escala
        delta = cfg.intervalo_decisao_ticks
        self.k_c = ganho_de_tau(self.p.tau_c, delta, self.S)
        self.k_f_sobe = ganho_de_tau(self.p.tau_f_sobe, delta, self.S)
        self.k_f_desce = ganho_de_tau(self.p.tau_f_desce, delta, self.S)
        self.I: dict | None = None          # a intencao em curso
        self.opcao: dict | None = None      # a opcao da decisao em curso (a I* ou uma de uma decisao so)
        self.F = 0
        self.fins = {"meta": 0, "trocou": 0, "sumiu": 0, "desistiu": 0}

    def contexto(self) -> dict:
        self.F = self.F - mul(self.k_f_desce, self.F, self.S)
        h = {}
        if self.I is not None and self.cd.persistencia:
            h[self.I["chave"]] = mul(self.p.w_pers, self.I["C"], self.S)
        return {"F": self.F, "persistencia": h, "I": None if self.I is None else self.I["chave"],
                "C": 0 if self.I is None else self.I["C"], "n_sp": 0 if self.I is None else self.I["n_sp"]}

    def _acabar(self, motivo: str, meta: bool) -> dict:
        I = self.I
        if not meta:
            self.F = self.F + mul(self.k_f_sobe, self.S - self.F, self.S)
        self.fins[motivo] += 1
        self.I = None
        return {**I, "C": 0, "motivo": motivo, "meta": meta}

    def escolhida(self, unidade: dict, z: list, g_apr: int, k: int) -> list[dict]:
        """a unidade escolhida na decisao k (com a distancia ao alvo, ou None): devolve as opcoes que acabaram por ela (a I* trocada)"""
        chave = unidade["chave"]
        fins = []
        if self.I is not None and self.I["chave"] == chave:
            self.I["C"] = self.I["C"] + mul(self.k_c, self.S - self.I["C"], self.S)
            self.I["n"] += 1
            self.I["g_apr"] = g_apr
            self.I["d"] = unidade["d"]
            self.opcao = self.I
            return fins
        if self.I is not None:
            fins.append(self._acabar("trocou", False))
        op = {"chave": chave, "inicio": k, "e": list(z), "r": 0, "n": 1, "g_apr": g_apr, "d": unidade["d"]}
        if e_intencao(chave):
            self.I = {**op, "C": mul(self.k_c, self.S, self.S), "n_sp": 0}
            self.opcao = self.I
        else:
            self.opcao = op
        return fins

    def consequencia(self, r_n: int, ocorrido: dict | None, depois: dict) -> list[dict]:
        """a consequencia da decisao em curso. `depois` = {"visto": o alvo nos `vistos` depois de andar, "d": a distancia a ele (None sem
        ele), "ha_cheiro"}. Devolve as opcoes que acabaram nela."""
        op = self.opcao
        if op is None:
            raise RuntimeError("M-ESTADO: consequencia sem a opcao da decisao")
        self.opcao = None
        op["r"] = clamp(op["r"] + r_n, -self.S, self.S)
        if op is not self.I:
            return [{**op, "motivo": "unica", "meta": None}]
        acao, tipo, ident = op["chave"]
        if ocorrido is not None and ((acao == "comer" and ocorrido["comeu"] is not None and ocorrido["comeu"]["id"] == ident)
                                     or (acao == "brincar" and ocorrido["brincou_com_bola"])
                                     or (acao == "explorar" and ocorrido["chegou"])):
            return [self._acabar("meta", True)]
        if not depois["visto"] and not depois["ha_cheiro"]:
            return [self._acabar("sumiu", False)]
        if depois["d"] is not None and op["d"] is not None and depois["d"] < op["d"]:
            op["n_sp"] = 0
        else:
            op["n_sp"] += 1
        if op["n_sp"] >= self.p.n_desiste:
            return [self._acabar("desistiu", False)]
        return []

    def estado_interno(self) -> dict:
        I = self.I
        return {"I": None if I is None else {"chave": chave_json(I["chave"]), "C": I["C"], "n_sp": I["n_sp"], "inicio": I["inicio"],
                                             "n": I["n"], "r": I["r"], "d": I["d"]},
                "F": self.F, "fins": dict(self.fins)}
