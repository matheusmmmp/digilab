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

**A DX-4** (o adendo 3 do plano, A3.4; a subchave `intencao_cheiro`): a unidade `comer/cheiro` tambem abre intencao, a busca, com a meta
"comer uma comida". A busca acaba, sem ler a distancia nem a direcao do cheiro (o G-SEM-DIRECAO), no primeiro destes:
  - "meta": o pet come uma comida numa decisao da busca (C = 0, o F nao sobe);
  - "achou": uma comida boa (racao, a, b, c) esta nos `vistos` depois de andar;
  - "sumiu": sem cheiro e sem comida boa a vista;
  - "desistiu": `n_desiste_cheiro` decisoes da busca sem "meta" nem "achou";
  - "trocou": como as outras intencoes.
A opcao composta: no "achou", a opcao da busca nao e entregue; fica guardada por uma decisao. Se a decisao seguinte escolhe uma unidade
`comer/comida`, a intencao dela herda a busca (a mesma elegibilidade e, o mesmo inicio, o r ja somado) e e entregue uma vez so, quando
acaba; se escolhe outra unidade, a busca e entregue nessa decisao, com o r so das decisoes dela. Desligada, nada disso existe (a unidade
`comer/cheiro` e uma opcao de uma decisao, como hoje).
Sem rng."""
from __future__ import annotations

from ..config import CONFIG_DIGIBRAIN_INATOS, Config, ConfigDigibrain, ConfigDigibrainInatos
from ._comum import chave_json, clamp, ganho_de_tau, mul

TIPOS_INTENCAO = (("comer", "comida"), ("brincar", "bola"), ("explorar", "ponto"))
BUSCA = ("comer", "cheiro")                      # a intencao da DX-4, so com a subchave `intencao_cheiro`


def e_intencao(chave: tuple, intencao_cheiro: bool = False) -> bool:
    return (chave[0], chave[1]) in TIPOS_INTENCAO or (intencao_cheiro and (chave[0], chave[1]) == BUSCA)


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
        self.guardada: dict | None = None   # a busca que acabou em "achou", por uma decisao (DX-4)
        if self.cd.intencao_cheiro:
            self.fins["achou"] = 0

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
        if self.guardada is not None:
            busca, self.guardada = self.guardada, None
            if (chave[0], chave[1]) == ("comer", "comida"):
                return self._herdar_busca(busca, unidade, g_apr)
            fins.append({**busca, "registro": False})                  # registrada no "achou"; entregue agora, so com a busca
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
        if e_intencao(chave, self.cd.intencao_cheiro):
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
        if (acao, tipo) == BUSCA:
            return self._consequencia_busca(op, ocorrido, depois)
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

    # ------------------------------------------------------------ a DX-4: a busca pelo cheiro e a opcao composta
    def _consequencia_busca(self, op: dict, ocorrido: dict | None, depois: dict) -> list[dict]:
        """o fim da busca (docstring do modulo), so pelo que o cerebro ja le: o consumo, as comidas boas nos `vistos` e se ha cheiro"""
        if ocorrido is not None and ocorrido["comeu"] is not None:
            return [self._acabar("meta", True)]
        if depois["comida_boa_vista"]:
            fim = self._acabar("achou", False)
            self.guardada = fim
            return [{**fim, "credito": False}]                         # guardada: o credito segue pela opcao composta
        if not depois["ha_cheiro"]:
            return [self._acabar("sumiu", False)]
        op["n_sp"] += 1
        if op["n"] >= self.p.n_desiste_cheiro:
            return [self._acabar("desistiu", False)]
        return []

    def _herdar_busca(self, busca: dict, unidade: dict, g_apr: int) -> list[dict]:
        """a opcao composta: a intencao `comer/comida` com a elegibilidade, o inicio e o r da busca guardada (I e None: a busca acabou)"""
        op = {"chave": unidade["chave"], "inicio": busca["inicio"], "e": list(busca["e"]), "r": busca["r"], "n": busca["n"] + 1,
              "g_apr": g_apr, "d": unidade["d"], "composta": True}
        self.I = {**op, "C": mul(self.k_c, self.S, self.S), "n_sp": 0}
        self.opcao = self.I
        return []

    def estado_interno(self) -> dict:
        I = self.I
        out = {"I": None if I is None else {"chave": chave_json(I["chave"]), "C": I["C"], "n_sp": I["n_sp"], "inicio": I["inicio"],
                                            "n": I["n"], "r": I["r"], "d": I["d"]},
               "F": self.F, "fins": dict(self.fins)}
        if self.cd.intencao_cheiro:                     # so com a DX-4 (desligada, o estado e o de hoje, byte a byte)
            g = self.guardada
            out["guardada"] = None if g is None else {"chave": chave_json(g["chave"]), "inicio": g["inicio"], "n": g["n"], "r": g["r"]}
            if I is not None and I.get("composta"):
                out["I"]["composta"] = True
        return out
