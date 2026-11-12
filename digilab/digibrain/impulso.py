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
**O passeio** (docs/TAREFA_V3_ACOES_NOVAS.md, 3.1; a subchave `passeio`): com um passeio em curso (`contexto["I"]`), a unidade dele
(`explorar`, `passeio`, (x, y)), com o tipo `vagar` e a distancia ao ponto, ocupa o lugar do `explorar/vagar`; o resto da ativacao e o do vagar.
**As unidades de fala** (docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, 3.1; a subchave `fala_unidades`): o `chamar_atencao` vira tres unidades,
(`chamar_atencao`, c, None) com c em CONTEUDOS_FALA (fome, higiene, solidao), sem tipo de alvo (o mundo e o corpo sao os do chamar). O inato
de cada uma e o W0[chamar_atencao].z de hoje termo a termo, com o termo do receptor do conteudo (TERMO_DO_CONTEUDO) multiplicado por
`ganho_conteudo` (mul) e os dos outros dois conteudos por zero; o habito e o da linha de H da unidade (`plast.linha_da_opcao`, uma por conteudo, no
M-PLAST). Desligada, a unidade e a de hoje.
**O olhar** (GOSTO_VISUAL, P1d; docs/ESPEC_GOSTO_VISUAL_P1.md, secao 6, GV-19; a subchave `olhar`, com a `ConfigOlhar`): o comportamento
novo `olhar`, com uma unidade (`olhar`, `tela`, id) por linha da classe `tela` do M-SENS (a TV a vista), no fim da lista (a ordem das
unidades de hoje nao muda). O inato e o W0[olhar].z (`ConfigOlhar.w0_olhar`: a urgencia do tedio e da curiosidade), a proximidade e a
novidade da linha (`w0_prox`, `w0_nov`), o incentivo e o G da classe `tela` vezes a proximidade (P1), o habito e a linha H[olhar] (P2) e o
termo novo `gosto` (so com a subchave, em todas as unidades: 0 fora da TV que o pet ja olhava), que o M-ADAPT entrega pronto. Desligada,
nenhuma unidade nem termo novo.
Sem estado e sem rng."""
from __future__ import annotations

from ..config import (CARACTERISTICAS_DIGIBRAIN, COMPORTAMENTO_OLHAR, COMPORTAMENTOS_DIGIBRAIN, CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS,
                      CONFIG_FALA_UNIDADES, CONFIG_OLHAR, CONTEUDOS_FALA, RECEPTORES_DIGIBRAIN, TERMO_DO_CONTEUDO, ConfigDigibrain,
                      ConfigDigibrainInatos, ConfigFalaUnidades, ConfigOlhar)
from ..modelo_mundo import raiz_inteira
from ._comum import chave_unidade, mul, phi
from .plast import linha_da_opcao

TERMOS = ("inato", "prox", "nov", "incentivo", "habito", "memoria", "persistencia")
FALA = "chamar_atencao"                          # o comportamento que vira as unidades de fala (so com a subchave `fala_unidades`)


class Impulso:
    """o M-IMPULSO (docstring do modulo)"""

    def __init__(self, inatos: ConfigDigibrainInatos | None = None, cfg_digibrain: ConfigDigibrain | None = None,
                 cfg_fala: ConfigFalaUnidades | None = None, cfg_olhar: ConfigOlhar | None = None) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.cd = cfg_digibrain or CONFIG_DIGIBRAIN
        self.cf = cfg_fala or CONFIG_FALA_UNIDADES
        if cfg_olhar is not None and not self.cd.olhar:
            raise ValueError("M-IMPULSO: a ConfigOlhar so com a subchave olhar")
        self.co = (cfg_olhar or CONFIG_OLHAR) if self.cd.olhar else None
        self.S = self.p.escala
        idx = {c: j for j, c in enumerate(CARACTERISTICAS_DIGIBRAIN)}
        self.w0 = {}
        linhas = self.p.w0 + (((COMPORTAMENTO_OLHAR, self.co.w0_olhar),) if self.co is not None else ())
        for b, linha in linhas:
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
        self.j_conteudo = {c: idx[termo] for c, termo in TERMO_DO_CONTEUDO}   # o indice em z do termo de cada conteudo (3.1)
        if tuple(self.j_conteudo) != CONTEUDOS_FALA:                            # pragma: no cover - conferido pela config
            raise RuntimeError("M-IMPULSO: TERMO_DO_CONTEUDO fora de CONTEUDOS_FALA")

    def inato_fala(self, z: list) -> dict:
        """o inato de cada unidade de fala (3.1): o W0[chamar_atencao].z termo a termo, com o termo do conteudo da unidade vezes o
        `ganho_conteudo` (mul) e os termos dos outros dois conteudos fora"""
        S, w = self.S, self.w0[FALA]
        termo = [mul(wj, zj, S) if wj else 0 for wj, zj in zip(w, z)]
        comum = sum(t for j, t in enumerate(termo) if j not in self.j_conteudo.values())
        return {c: comum + mul(self.cf.ganho_conteudo, termo[j], S) for c, j in self.j_conteudo.items()}

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
    def alvos(sens: dict, memoria: dict | None, passeio: tuple | None = None, fala: bool = False) -> list[dict]:
        """as unidades possiveis da decisao, na ordem fixa: {chave, acao, tipo (o tipo do alvo para o W0_tipo), objeto, d}. `passeio` = a chave
        (explorar, passeio, (x, y)) do passeio em curso (so com a subchave): a unidade dele ocupa o lugar do vagar, com o mesmo tipo. `fala`
        (so com a `fala_unidades`): o chamar vira as tres unidades de fala, na ordem de CONTEUDOS_FALA, sem tipo de alvo"""
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
                if passeio is None:
                    out.append({"chave": chave_unidade(b, "vagar"), "acao": b, "tipo": "vagar", "objeto": None, "d": None})
                else:
                    px, py = passeio[2]
                    d = raiz_inteira((px - x) * (px - x) + (py - y) * (py - y))
                    out.append({"chave": passeio, "acao": b, "tipo": "vagar", "objeto": None, "d": d})
                if sens["ha_cheiro"]:
                    out.append({"chave": chave_unidade(b, "cheiro"), "acao": b, "tipo": "cheiro", "objeto": None, "d": None})
                if memoria is not None and memoria["recuperado"] is not None:
                    px, py = memoria["ponto"]
                    d = raiz_inteira((px - x) * (px - x) + (py - y) * (py - y))
                    out.append({"chave": chave_unidade(b, "ponto", (px, py)), "acao": b, "tipo": "ponto", "objeto": None, "d": d})
            elif b == FALA and fala:
                for c in CONTEUDOS_FALA:
                    out.append({"chave": chave_unidade(b, c), "acao": b, "tipo": None, "objeto": None, "d": None})
            else:
                out.append({"chave": chave_unidade(b), "acao": b, "tipo": None, "objeto": None, "d": None})
        return out

    def unidades(self, sens: dict, afeto: dict, contexto: dict, plast, memoria: dict | None, drives: tuple,
                 lembranca: tuple | None = None, facetas: tuple | None = None, gosto: dict | None = None) -> tuple[list[dict], list]:
        """as unidades da decisao com os termos e a ativacao, e o z. `lembranca` = (o termo da M4, o `casa` do M-MEM) ou None; so com a
        `memoria_autobio` as unidades ganham o termo `lembranca` (L nas que casam com o episodio lembrado, 0 nas outras). `facetas` = (os
        valores das tres facetas, as classes de comida que ja tem episodio positivo); so com a `facetas_mem` as unidades ganham o termo
        `faceta` (6.2: cautela no `comer` de classe sem episodio positivo, apego no `chamar_atencao`, ousadia no `explorar` com alvo fora
        da vista: o lugar lembrado e o cheiro). `gosto` (so com a subchave `olhar`) = {id da TV: o termo `gosto` da unidade de olhar dela}
        (vazio se o pet nao olhava); com a subchave, todas as unidades ganham o termo `gosto` e as de olhar vem no fim"""
        S, a_max = self.S, self.p.a_max
        if (gosto is not None) != (self.co is not None):
            raise RuntimeError("M-IMPULSO: o termo gosto vem so com a subchave olhar, e com ela sempre")
        z = self.contexto_z(sens, afeto, contexto)
        inato_b = {b: sum(mul(w, zj, S) for w, zj in zip(self.w0[b], z) if w) for b in COMPORTAMENTOS_DIGIBRAIN}
        habito_b = {b: plast.habito(b, z) for b in COMPORTAMENTOS_DIGIBRAIN if not (self.cd.fala_unidades and b == FALA)}
        fala = self.cd.fala_unidades
        if fala:
            inato_fala = self.inato_fala(z)
            habito_b.update({f"{FALA}/{c}": plast.habito(f"{FALA}/{c}", z) for c in CONTEUDOS_FALA})
        incentivos: dict = {}
        persist = contexto["persistencia"]
        out = []
        em_passeio = contexto["I"] if self.cd.passeio and contexto["I"] is not None and contexto["I"][:2] == ("explorar", "passeio") else None
        olhar = self.co is not None
        if olhar:                                     # o olhar (P1d): o inato e o habito da linha nova
            inato_b[COMPORTAMENTO_OLHAR] = sum(mul(w, zj, S) for w, zj in zip(self.w0[COMPORTAMENTO_OLHAR], z) if w)
            habito_b[COMPORTAMENTO_OLHAR] = plast.habito(COMPORTAMENTO_OLHAR, z)
        lista = (self.alvos(sens, memoria, em_passeio) if self.cd.passeio else self.alvos(sens, memoria, fala=True) if fala
                 else self.alvos(sens, memoria))
        if olhar:                                     # uma unidade por TV a vista, no fim da lista
            lista = lista + [{"chave": chave_unidade(COMPORTAMENTO_OLHAR, o["classe"], o["id"]), "acao": COMPORTAMENTO_OLHAR,
                              "tipo": o["classe"], "objeto": o, "d": o["d"]} for o in sens["telas"]]
            if set(gosto) - {o["id"] for o in sens["telas"]}:
                raise RuntimeError(f"M-IMPULSO: o gosto de uma TV fora da vista: {gosto!r}")
        for u in lista:
            b, o = u["acao"], u["objeto"]
            termos = dict.fromkeys(TERMOS + (("lembranca",) if self.cd.memoria_autobio else ()) + (("faceta",) if self.cd.facetas_mem else ())
                                   + (("gosto",) if olhar else ()), 0)
            inato = inato_fala[u["chave"][1]] if fala and b == FALA else inato_b[b]
            termos["inato"] = inato + (self.w0_tipo.get(b, {}).get(u["tipo"], 0) if u["tipo"] is not None else 0)
            if b == COMPORTAMENTO_OLHAR:              # o olhar (P1d): a linha da TV, o incentivo da classe `tela` e o gosto
                termos["prox"] = mul(self.co.w0_prox, o["prox"], S)
                termos["nov"] = mul(self.co.w0_nov, o["nov"], S)
                if o["classe"] not in incentivos:
                    incentivos[o["classe"]] = plast.incentivo(sens["pc"], o["classe"], drives)
                termos["incentivo"] = mul(incentivos[o["classe"]], o["prox"], S)
                termos["gosto"] = gosto.get(o["id"], 0)
            elif o is not None:
                termos["prox"] = mul(self.w0_prox.get(b, 0), o["prox"], S)
                termos["nov"] = mul(self.w0_nov.get(b, 0), o["nov"], S)
                if b in ("comer", "brincar"):
                    c = o["classe"]
                    if c not in incentivos:
                        incentivos[c] = plast.incentivo(sens["pc"], c, drives)
                    termos["incentivo"] = mul(incentivos[c], o["prox"], S)
            termos["habito"] = habito_b[linha_da_opcao(u["chave"], fala)]
            if u["tipo"] == "ponto":
                termos["memoria"] = memoria["M"]
            termos["persistencia"] = persist.get(u["chave"], 0)
            if lembranca is not None and lembranca[1](lembranca[0], u):
                termos["lembranca"] = lembranca[0]["L"]
            if facetas is not None:
                f, positivas = facetas
                if b == "comer" and o is not None and o["classe"] not in positivas:
                    termos["faceta"] = -mul(f["cautela_comida"], S, S)
                elif b == "chamar_atencao":
                    termos["faceta"] = mul(f["apego_dono"], S, S)
                elif b == "explorar" and u["tipo"] in ("ponto", "cheiro"):
                    termos["faceta"] = mul(f["ousadia_longe"], S, S)
            soma = sum(termos.values())
            out.append({**u, "termos": termos, "soma": soma, "a": phi(soma, a_max)})
        return out, z
