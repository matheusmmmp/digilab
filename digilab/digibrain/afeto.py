"""M-AFETO, os afetos e os moduladores (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.3).

Na decisao (`ler`), da interocepcao do M-SENS:
  - a urgencia de cada receptor, `u_r = clamp(mul(a_r, falta) + mul(b_r, max(0, falta - lambda_r)), 0, S)`, a curva inata;
  - o ganho da aprendizagem `g_apr` (PE-4, a D-1: a excitacao no `g_apr` e HIPOTESE EXPERIMENTAL), pela `ConfigDigibrain`:
      sem `modula_g_apr`:                    g0 (o primeiro braco);
      com `modula_g_apr`:                    clamp(g0 + mul(beta_E, E), g_min, g_max), com E a excitacao desta vida;
      com o controle "embaralhado":          a mesma conta com a E da vida doadora na mesma decisao (a serie dada ao construir);
      com o controle "constante":            o `g_apr_constante`;
  - o ganho da exploracao `g_exp = clamp(e0 + mul(beta_T, falta do tedio) - mul(beta_U, max_r u_r), 0, e_max)`.
Na consequencia (`consequencia`), dos receptores de antes e de depois:
  - o sinal homeostatico `r = sinal_corpo(antes, depois, drives, ganho, S)` do A (lobos.py), sobre os receptores presentes menos os de
    `fora_do_r` (o susto, como no A), com os canais por drive (`canais_do_sinal`: a soma telescopica e o escalar, K-6);
  - `r_n = clamp(div_arred(r, R_n), -S, S)`;
  - a valencia `V <- V + mul(k_V, r_n - V)` e a excitacao `E <- E + mul(k_E, max(|r_n|, dor, susto, estresse) - E)` (forma I).
A serie da excitacao lida em cada decisao fica em `serie_e` (a doadora do M4-emb e a serie de uma vida M4). Sem rng."""
from __future__ import annotations

from ..config import CONFIG_DIGIBRAIN_INATOS, Config, ConfigDigibrain, ConfigDigibrainInatos
from ..policies.lobos import contribuicoes_corpo, div_arred, falta_receptor, sinal_corpo
from ._comum import clamp, ganho_de_tau, integrar, mul

EXCITANTES = ("dor", "susto", "estresse")


def canais_do_sinal(antes, depois, drives: tuple, ganho: int, S: int) -> dict[str, int]:
    """o r separado por drive, na ordem de `drives`: f_d = div_arred(ganho x (c_1 + ... + c_d), S) - div_arred(ganho x (c_1 + ... +
    c_(d-1)), S), com c_d a contribuicao do drive (`contribuicoes_corpo` do A). A soma e o `sinal_corpo` (a soma telescopa). E a conta
    do `sinal_corpo_canais` do A, refeita aqui porque a do A nao tem canal para a saude."""
    canais: dict[str, int] = {}
    acumulado, anterior = 0, 0
    for d, c in contribuicoes_corpo(antes, depois, drives, S).items():
        acumulado += c
        parcial = div_arred(ganho * acumulado, S)
        canais[d] = parcial - anterior
        anterior = parcial
    return canais


class Afeto:
    """o M-AFETO (docstring do modulo)"""

    def __init__(self, cfg: Config, cfg_digibrain: ConfigDigibrain, inatos: ConfigDigibrainInatos | None = None,
                 serie_e_doadora: tuple | None = None) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.cd = cfg_digibrain
        self.S = self.p.escala
        delta = cfg.intervalo_decisao_ticks
        self.k_v = ganho_de_tau(self.p.tau_v, delta, self.S)
        self.k_e = ganho_de_tau(self.p.tau_e, delta, self.S)
        embaralhado = self.cd.controle_g_apr == "embaralhado"
        if embaralhado != (serie_e_doadora is not None):
            raise ValueError("a serie E da vida doadora vem so com o controle embaralhado (e e obrigatoria nele)")
        if serie_e_doadora is not None and any(type(e) is not int or not 0 <= e <= self.S for e in serie_e_doadora):
            raise ValueError("a serie E da vida doadora: inteiros em [0, S]")
        self.doadora = None if serie_e_doadora is None else tuple(serie_e_doadora)
        self.V = 0
        self.E = 0
        self.decisoes = 0
        self.serie_e: list[int] = []
        self.ultimo: dict | None = None

    def urgencia(self, falta: int) -> int:
        p, S = self.p, self.S
        return clamp(mul(p.urgencia_a, falta, S) + mul(p.urgencia_b, max(0, falta - p.urgencia_lambda), S), 0, S)

    def g_apr_de(self, e: int) -> int:
        """o g_apr modulado por uma excitacao e"""
        p = self.p
        return clamp(p.g0 + mul(p.beta_e, e, self.S), p.g_min, p.g_max)

    def ler(self, sens: dict) -> dict:
        p, S, cd = self.p, self.S, self.cd
        falta = sens["falta"]
        urg = {r: self.urgencia(f) for r, f in falta.items()}
        e_usada = None
        if cd.controle_g_apr == "constante":
            g_apr = cd.g_apr_constante
        elif cd.modula_g_apr:
            if cd.controle_g_apr == "embaralhado":
                if self.decisoes >= len(self.doadora):
                    raise RuntimeError(f"M-AFETO: a serie E da vida doadora tem {len(self.doadora)} decisoes; esta e a {self.decisoes + 1}")
                e_usada = self.doadora[self.decisoes]
            else:
                e_usada = self.E
            g_apr = self.g_apr_de(e_usada)
        else:
            g_apr = p.g0
        g_exp = clamp(p.e0 + mul(p.beta_t, falta.get("tedio", 0), S) - mul(p.beta_u, max(urg.values()), S), 0, p.e_max)
        self.serie_e.append(self.E)
        self.decisoes += 1
        return {"urgencias": urg, "V": self.V, "E": self.E, "e_usada": e_usada, "g_apr": g_apr, "g_exp": g_exp}

    def drives(self, receptores: tuple) -> tuple:
        return tuple(r for r in receptores if r not in self.p.fora_do_r)

    def consequencia(self, pc_antes, pc_depois, receptores: tuple) -> dict:
        p, S = self.p, self.S
        drives = self.drives(receptores)
        r = sinal_corpo(pc_antes, pc_depois, drives, p.ganho_r, S)
        canais = canais_do_sinal(pc_antes, pc_depois, drives, p.ganho_r, S)
        r_n = clamp(div_arred(r, p.r_norm), -S, S)
        self.V = integrar(self.V, r_n, self.k_v, S)
        exc = max([abs(r_n)] + [falta_receptor(pc_depois, x, S) for x in EXCITANTES if x in receptores])
        self.E = integrar(self.E, exc, self.k_e, S)
        self.ultimo = {"r": r, "r_n": r_n, "canais": canais, "V": self.V, "E": self.E}
        return self.ultimo

    def estado_interno(self) -> dict:
        return {"V": self.V, "E": self.E, "decisoes": self.decisoes, "ultimo": self.ultimo}
