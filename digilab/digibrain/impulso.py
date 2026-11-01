"""M-IMPULSO, os impulsos e os circuitos de comportamento (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 2.1 a 2.3 e 4.5).

**O contexto z** (CARACTERISTICAS_DIGIBRAIN, ~20): o vies (S), as urgencias dos onze receptores (0 nos ausentes), o contexto e as
conjuncoes do M-SENS, duas conjuncoes com a urgencia (`fome_sem_comida = mul(u_fome, sem_comida)`, `cuidado_humor = mul(sem_cuidado,
u_humor)`), a frustracao F do M-ESTADO e a valencia V e a excitacao E do M-AFETO. Entra em todos os comportamentos.

**As unidades (b, o)**, as sete acoes de ACOES_PET_HOJE (sem acao nova), na ordem do enum e, dentro de cada uma, na dos `vistos`:
  - comer: uma por comida vista (a podre tambem, pelo W0 da classe); o cheiro, se ha cheiro;
  - brincar: uma por bola vista; sem bola a vista, brincar sem alvo;
  - explorar: vagar; o cheiro, se ha; o lugar lembrado, se o M-MEM recuperou um;
  - sem alvo: ocioso, dormir, chamar, emburrar.
**A ativacao** (secao 2.3), cada produto um `mul`, a soma guardada termo a termo:
  a[b,o] = phi( inato  = sum_j W0[b,j] z_j + W0_tipo[b, tipo de o]
              + prox   = W0_prox[b] prox_o
              + nov    = W0_nov[b] nov_o
              + incentivo = mul(G_classe, prox_o), so comer e brincar com objeto (P1)
              + habito = sum_j H[b,j] z_j (P2)
              + memoria = M, so explorar o lugar lembrado (M-MEM)
              + persistencia = h, so a intencao em curso (M-ESTADO) )
**A DX-3** (o adendo 3 do plano, A3.4; a subchave `cheiro_inato`): o inato da unidade `comer/cheiro` soma o `w0_tipo_cheiro` (o cheiro de
comida vale como comida, sem a proximidade). Desligada, o termo e o de hoje (o W0_tipo do comer nao tem o tipo `cheiro`). O cerebro
continua lendo so se ha cheiro (o G-SEM-DIRECAO).
Sem estado e sem rng."""
from __future__ import annotations

from ..config import (CARACTERISTICAS_DIGIBRAIN, COMPORTAMENTOS_DIGIBRAIN, CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, RECEPTORES_DIGIBRAIN,
                      ConfigDigibrain, ConfigDigibrainInatos)
from ..modelo_mundo import raiz_inteira
from ._comum import chave_unidade, mul, phi

TERMOS = ("inato", "prox", "nov", "incentivo", "habito", "memoria", "persistencia")


class Impulso:
    """o M-IMPULSO (docstring do modulo)"""

    def __init__(self, inatos: ConfigDigibrainInatos | None = None, cfg_digibrain: ConfigDigibrain | None = None) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.cd = cfg_digibrain or CONFIG_DIGIBRAIN
        self.S = self.p.escala
        idx = {c: j for j, c in enumerate(CARACTERISTICAS_DIGIBRAIN)}
        self.w0 = {}
        for b, linha in self.p.w0:
            w = [0] * len(CARACTERISTICAS_DIGIBRAIN)
            for c, v in linha:
                w[idx[c]] = v
            self.w0[b] = w
        self.w0_prox = dict(self.p.w0_prox)
        self.w0_nov = dict(self.p.w0_nov)
        self.w0_tipo = {b: dict(t) for b, t in self.p.w0_tipo}
        if "cheiro" in self.w0_tipo.get("comer", {}):
            raise ValueError("o tipo `cheiro` do comer fica no w0_tipo_cheiro, atras da subchave `cheiro_inato` (DX-3)")
        if self.cd.cheiro_inato:
            self.w0_tipo["comer"] = {**self.w0_tipo.get("comer", {}), "cheiro": self.p.w0_tipo_cheiro}

    def contexto_z(self, sens: dict, afeto: dict, contexto: dict) -> list[int]:
        S = self.S
        u = afeto["urgencias"]
        cs, cj = sens["contexto"], sens["conjuncoes"]
        z = [S] + [u.get(r, 0) for r in RECEPTORES_DIGIBRAIN]
        z += [cs["noite"], cs["dormindo"], cs["sem_cuidado"], cj["comida_vista"], cj["sem_comida"], cj["bola_vista"],
              mul(u.get("fome", 0), cj["sem_comida"], S), mul(cs["sem_cuidado"], u.get("humor", 0), S),
              contexto["F"], afeto["V"], afeto["E"]]
        if len(z) != len(CARACTERISTICAS_DIGIBRAIN):          # pragma: no cover - conferido pela config
            raise RuntimeError("M-IMPULSO: z fora de CARACTERISTICAS_DIGIBRAIN")
        return z

    @staticmethod
    def alvos(sens: dict, memoria: dict | None) -> list[dict]:
        """as unidades possiveis da decisao, na ordem fixa: {chave, acao, tipo (o tipo do alvo para o W0_tipo), objeto, d}"""
        out = []
        x, y = sens["pos"]
        for b in COMPORTAMENTOS_DIGIBRAIN:
            if b == "comer":
                for o in sens["objetos"]:
                    if o["classe"] != "bola":
                        out.append({"chave": chave_unidade(b, "comida", o["id"]), "acao": b, "tipo": o["classe"], "objeto": o, "d": o["d"]})
                if sens["ha_cheiro"]:
                    out.append({"chave": chave_unidade(b, "cheiro"), "acao": b, "tipo": "cheiro", "objeto": None, "d": None})
            elif b == "brincar":
                bolas = [o for o in sens["objetos"] if o["classe"] == "bola"]
                for o in bolas:
                    out.append({"chave": chave_unidade(b, "bola", o["id"]), "acao": b, "tipo": "bola", "objeto": o, "d": o["d"]})
                if not bolas:
                    out.append({"chave": chave_unidade(b), "acao": b, "tipo": None, "objeto": None, "d": None})
            elif b == "explorar":
                out.append({"chave": chave_unidade(b, "vagar"), "acao": b, "tipo": "vagar", "objeto": None, "d": None})
                if sens["ha_cheiro"]:
                    out.append({"chave": chave_unidade(b, "cheiro"), "acao": b, "tipo": "cheiro", "objeto": None, "d": None})
                if memoria is not None and memoria["recuperado"] is not None:
                    px, py = memoria["ponto"]
                    d = raiz_inteira((px - x) * (px - x) + (py - y) * (py - y))
                    out.append({"chave": chave_unidade(b, "ponto", (px, py)), "acao": b, "tipo": "ponto", "objeto": None, "d": d})
            else:
                out.append({"chave": chave_unidade(b), "acao": b, "tipo": None, "objeto": None, "d": None})
        return out

    def unidades(self, sens: dict, afeto: dict, contexto: dict, plast, memoria: dict | None, drives: tuple,
                 lembranca: tuple | None = None) -> tuple[list[dict], list]:
        """as unidades da decisao com os termos e a ativacao, e o z. `lembranca` = (o termo da M4, o `casa` do M-MEM) ou None; so com a
        `memoria_autobio` as unidades ganham o termo `lembranca` (L nas que casam com o episodio lembrado, 0 nas outras)"""
        S, a_max = self.S, self.p.a_max
        z = self.contexto_z(sens, afeto, contexto)
        inato_b = {b: sum(mul(w, zj, S) for w, zj in zip(self.w0[b], z) if w) for b in COMPORTAMENTOS_DIGIBRAIN}
        habito_b = {b: plast.habito(b, z) for b in COMPORTAMENTOS_DIGIBRAIN}
        incentivos: dict = {}
        persist = contexto["persistencia"]
        out = []
        for u in self.alvos(sens, memoria):
            b, o = u["acao"], u["objeto"]
            termos = dict.fromkeys(TERMOS + (("lembranca",) if self.cd.memoria_autobio else ()), 0)
            termos["inato"] = inato_b[b] + (self.w0_tipo.get(b, {}).get(u["tipo"], 0) if u["tipo"] is not None else 0)
            if o is not None:
                termos["prox"] = mul(self.w0_prox.get(b, 0), o["prox"], S)
                termos["nov"] = mul(self.w0_nov.get(b, 0), o["nov"], S)
                if b in ("comer", "brincar"):
                    c = o["classe"]
                    if c not in incentivos:
                        incentivos[c] = plast.incentivo(sens["pc"], c, drives)
                    termos["incentivo"] = mul(incentivos[c], o["prox"], S)
            termos["habito"] = habito_b[b]
            if u["tipo"] == "ponto":
                termos["memoria"] = memoria["M"]
            termos["persistencia"] = persist.get(u["chave"], 0)
            if lembranca is not None and lembranca[1](lembranca[0], u):
                termos["lembranca"] = lembranca[0]["L"]
            soma = sum(termos.values())
            out.append({**u, "termos": termos, "soma": soma, "a": phi(soma, a_max)})
        return out, z
