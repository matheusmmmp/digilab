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
  - acabou sem a meta: F <- F + mul(k_F, S - F) (menos no "achou" da busca, abaixo).

O credito (PE-3, por opcao; o M-PLAST, secao 4.8): cada opcao guarda a elegibilidade e_j = z_j da decisao que a comecou, soma o r_n de
cada consequencia dela, e e entregue ao P2 quando acaba (com a meta, sem ela, ou na propria consequencia, nas opcoes de uma decisao).

**A DX-4** (o adendo 3 do plano, A3.4; a subchave `intencao_cheiro`): a unidade `comer/cheiro` tambem abre intencao, a busca, com a meta
"comer uma comida". A busca acaba, sem ler a distancia nem a direcao do cheiro (o G-SEM-DIRECAO), no primeiro destes:
  - "meta": o pet come uma comida numa decisao da busca (C = 0, o F nao sobe);
  - "achou": uma comida boa (racao, a, b, c) esta nos `vistos` depois de andar (o F nao sobe: decisao do Matheus de 2026-10-26; continua
    um fim sem a meta, com o motivo e a contagem em `fins`);
  - "sumiu": sem cheiro e sem comida boa a vista;
  - "desistiu": `n_desiste_cheiro` decisoes da busca sem "meta" nem "achou";
  - "trocou": como as outras intencoes.
A opcao composta: no "achou", a opcao da busca nao e entregue; fica guardada por uma decisao. Se a decisao seguinte escolhe uma unidade
`comer/comida`, a intencao dela herda a busca (a mesma elegibilidade e, o mesmo inicio, o r ja somado) e e entregue uma vez so, quando
acaba; se escolhe outra unidade, a busca e entregue nessa decisao, com o r so das decisoes dela. Desligada, nada disso existe (a unidade
`comer/cheiro` e uma opcao de uma decisao, como hoje).

**A parte (b) da L-2** (docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md, secoes 2 e 3; a subchave `intencao_suspensa`): quando o reflexo do sono
interrompe uma intencao de comer (a busca `comer/cheiro` ou a ida `comer/comida`), ela fica suspensa, e nao trocada: o F nao sobe e nada
vai ao P2. A `suspensa` guarda o dicionario da I* (o C, o `n_sp`, a distancia, o inicio, a elegibilidade, o r e o `n`) e o `n_susp`, as
decisoes de reflexo somadas na vida dela (nao zera ao voltar). Ha no maximo uma intencao em curso ou uma suspensa; a suspensa nao da
persistencia. No comeco de cada decisao (`cuidar_suspensa`, antes do contexto):
  - com o reflexo: `n_susp += 1` e os fins "saciou" (a urgencia da fome abaixo de `lambda_retomar`), "sumiu" (a busca sem cheiro e sem
    comida boa a vista; a ida com a comida-alvo fora dos `vistos`) e "expirou" (`n_susp` acima de `n_suspensa_max`);
  - sem o reflexo: o "saciou", o "sumiu", o "achou" (a busca, uma comida boa a vista: o "achou" da DX-4, com a opcao composta) e o
    "superada" (a ida, outra comida boa mais perto que a comida-alvo); sem fim, a retomada: a I* volta a ser a suspensa, com o C, o `n_sp`
    e a distancia de antes, e disputa o sorteio com a persistencia (a retomada nao forca a escolha).
O F so sobe no "sumiu" (LS-5). Desligada, nada disso existe, e o reflexo troca a intencao como hoje.
Sem rng."""
from __future__ import annotations

from ..config import CONFIG_DIGIBRAIN_INATOS, Config, ConfigDigibrain, ConfigDigibrainInatos
from ._comum import chave_json, clamp, ganho_de_tau, mul
from .sens import COMIDAS_BOAS

TIPOS_INTENCAO = (("comer", "comida"), ("brincar", "bola"), ("explorar", "ponto"))
BUSCA = ("comer", "cheiro")                      # a intencao da DX-4, so com a subchave `intencao_cheiro`
IDA = ("comer", "comida")
SUSPENDEM = (BUSCA, IDA)                         # a L-2 (LS-2): os tipos que o reflexo do sono suspende, com `intencao_suspensa`
FINS_SUSPENSA = ("saciou", "expirou", "superada")  # os fins novos da L-2 ("sumiu" e "achou" ja existem)


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
        self.suspensa: dict | None = None   # a intencao suspensa pelo reflexo do sono (a L-2), so com `intencao_suspensa`
        self.suspensas = 0
        self.retomadas = 0
        if self.cd.intencao_suspensa:
            for motivo in FINS_SUSPENSA:
                self.fins[motivo] = 0

    def contexto(self) -> dict:
        self.F = self.F - mul(self.k_f_desce, self.F, self.S)
        h = {}
        if self.I is not None and self.cd.persistencia:
            h[self.I["chave"]] = mul(self.p.w_pers, self.I["C"], self.S)
        return {"F": self.F, "persistencia": h, "I": None if self.I is None else self.I["chave"],
                "C": 0 if self.I is None else self.I["C"], "n_sp": 0 if self.I is None else self.I["n_sp"]}

    def _acabar(self, motivo: str, meta: bool, frustra: bool = True) -> dict:
        I = self.I
        if not meta and frustra:
            self.F = self.F + mul(self.k_f_sobe, self.S - self.F, self.S)
        self.fins[motivo] += 1
        self.I = None
        return {**I, "C": 0, "motivo": motivo, "meta": meta}

    # ------------------------------------------------------------ a L-2: a intencao suspensa no reflexo do sono
    def _acabar_suspensa(self, motivo: str, frustra: bool) -> dict:
        S = self.suspensa
        if not frustra and motivo not in ("achou",) + FINS_SUSPENSA:
            raise RuntimeError(f"M-ESTADO: o fim {motivo!r} da suspensa sem frustracao")
        if frustra:
            self.F = self.F + mul(self.k_f_sobe, self.S - self.F, self.S)
        self.fins[motivo] += 1
        self.suspensa = None
        return {**S, "C": 0, "motivo": motivo, "meta": False}

    def cuidar_suspensa(self, sens: dict, afeto: dict, reflexo: bool) -> list[dict]:
        """o cuidado da intencao suspensa no comeco da decisao (docstring do modulo; a espec da L-2, secao 2.3, passo 2): devolve as
        opcoes que acabaram aqui (ao P2 e ao registro, com as do `escolhida`). So com `intencao_suspensa`; sem rng."""
        if not self.cd.intencao_suspensa:
            raise RuntimeError("M-ESTADO: cuidar_suspensa sem a subchave intencao_suspensa")
        S = self.suspensa
        if S is None:
            return []
        if self.I is not None:
            raise RuntimeError("M-ESTADO: uma intencao em curso e uma suspensa ao mesmo tempo")
        tipo = (S["chave"][0], S["chave"][1])
        objetos = sens["objetos"]
        boas = [o for o in objetos if o["classe"] in COMIDAS_BOAS]
        alvo = next((o for o in objetos if o["id"] == S["chave"][2]), None) if tipo == IDA else None
        if reflexo:
            S["n_susp"] += 1
        if afeto["urgencias"].get("fome", 0) < self.p.lambda_retomar:
            return [self._acabar_suspensa("saciou", False)]
        if (tipo == BUSCA and not sens["ha_cheiro"] and not boas) or (tipo == IDA and alvo is None):
            return [self._acabar_suspensa("sumiu", True)]
        if reflexo:
            if S["n_susp"] > self.p.n_suspensa_max:
                return [self._acabar_suspensa("expirou", False)]
            return []
        if tipo == BUSCA and boas:
            fim = self._acabar_suspensa("achou", False)               # o "achou" da DX-4: o credito segue pela opcao composta
            self.guardada = fim
            return [{**fim, "credito": False}]
        if tipo == IDA and any(o["id"] != alvo["id"] and o["d"] < alvo["d"] for o in boas):
            return [self._acabar_suspensa("superada", False)]
        self.I, self.suspensa = S, None                               # a retomada: o C, o n_sp, a distancia e o inicio de antes
        self.retomadas += 1
        return []

    def escolhida(self, unidade: dict, z: list, g_apr: int, k: int, reflexo: bool = False) -> list[dict]:
        """a unidade escolhida na decisao k (com a distancia ao alvo, ou None): devolve as opcoes que acabaram por ela (a I* trocada). Com
        `intencao_suspensa` e o reflexo do sono, a I* de um tipo que suspende passa a `suspensa`, e nao acaba (a L-2)."""
        chave = unidade["chave"]
        fins = []
        if self.suspensa is not None and not reflexo:
            raise RuntimeError("M-ESTADO: a suspensa sem o reflexo chegou ao escolhida (o cuidar_suspensa nao rodou)")
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
            if self.cd.intencao_suspensa and reflexo and (self.I["chave"][0], self.I["chave"][1]) in SUSPENDEM:
                self.suspensa = {**self.I, "n_susp": self.I.get("n_susp", 0) + 1}   # suspensa: o F nao sobe, nada vai ao P2
                self.I = None
                self.suspensas += 1
            else:
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
            fim = self._acabar("achou", False, frustra=False)       # o "achou" nao sobe o F (decisao de 2026-10-26)
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
        if self.cd.intencao_suspensa:                   # so com a L-2 (desligada, o estado e o de hoje, byte a byte)
            s = self.suspensa
            out["suspensa"] = None if s is None else {"chave": chave_json(s["chave"]), "C": s["C"], "n_sp": s["n_sp"],
                                                      "inicio": s["inicio"], "n": s["n"], "r": s["r"], "d": s["d"], "n_susp": s["n_susp"]}
            out["suspensas"], out["retomadas"] = self.suspensas, self.retomadas
            if I is not None and "n_susp" in I:
                out["I"]["n_susp"] = I["n_susp"]
        return out

    def suspensa_resumo(self) -> dict | None:
        """a suspensa no registro da decisao (a L-2): a chave e o `n_susp`"""
        s = self.suspensa
        return None if s is None else {"chave": chave_json(s["chave"]), "n_susp": s["n_susp"]}
