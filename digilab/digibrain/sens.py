"""M-SENS, a codificacao sensorial (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 2.1 e 4.2).

Le so a Observacao (a G-RECEPTOR: nenhum arquivo do pacote importa o digilab/corpo.py):
  - `obs.corpo` (a PercepcaoCorpo): a interocepcao, a falta de cada receptor do prototipo (RECEPTORES_DIGIBRAIN), pelas funcoes do A
    (`falta_receptor`, `leitura_receptor`). Os orgaos (o Olfato e a Audicao), o paladar e o banheiro ficam fora do prototipo (secao 6): um
    desses receptores presente falha alto;
  - `obs.mundo` (a PercepcaoMundo): a posicao, a regiao, os `vistos` e se ha cheiro (so `direcao_cheiro != 0`: a direcao fica no motor,
    o G-SEM-DIRECAO);
  - do `vetor_estado`, so a hora e o dormindo; o `ticks_desde_cuidado`.

As saidas, por decisao:
  - a falta de cada receptor presente, em [0, S];
  - o contexto: a noite e o dormindo (S ou 0) e o tempo sem cuidado, `min(S, div_arred(ticks x S, escala))` (o corte do A);
  - as linhas de objeto, uma por item dos `vistos` (no maximo `max_vistos`, na ordem deles): a classe (racao, a, b, c, podre, bola), a
    proximidade `prox = clamp(S - div_arred(d x S, R), 0, S)`, com R o raio da visao em subunidades, e a novidade `nov = S - hab[classe]`;
  - as conjuncoes: a comida a vista (a maior proximidade entre as comidas boas), sem comida (`S - comida a vista`) e a bola a vista.

O estado e a habituacao por classe (PE-11, um integrador por classe): `hab[c] <- hab[c] + mul(k_hab, visto_c x S - hab[c])`. A novidade
da decisao sai da habituacao de antes dela (a primeira vez que se ve uma classe, nov = S), e so depois a habituacao anda. Sem rng."""
from __future__ import annotations

from dataclasses import fields

from ..config import CONFIG_DIGIBRAIN_INATOS, RECEPTORES_DIGIBRAIN, TICKS_POR_DIA, Config, ConfigDigibrainInatos, ConfigMundo
from ..policies.lobos import div_arred, falta_receptor, leitura_receptor
from ._comum import clamp, ganho_de_tau, integrar

CLASSES_OBJETO = ("racao", "a", "b", "c", "podre", "bola")
COMIDAS_BOAS = ("racao", "a", "b", "c")


def classe_do_tipo(tipo: str) -> str:
    """a classe do item dos `vistos`: o tipo maduro, `podre` (qualquer `_podre`) ou `bola`"""
    if tipo.endswith("_podre"):
        return "podre"
    if tipo not in CLASSES_OBJETO:
        raise ValueError(f"M-SENS: tipo de objeto desconhecido {tipo!r}")
    return tipo


class Sens:
    """o M-SENS (docstring do modulo)"""

    def __init__(self, cfg: Config, cfg_mundo: ConfigMundo, inatos: ConfigDigibrainInatos | None = None) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.S = self.p.escala
        self.cfg = cfg
        self.raio = cfg_mundo.raio_visao_celulas * cfg_mundo.sub
        self.max_vistos = cfg_mundo.max_vistos
        self.k_hab = ganho_de_tau(self.p.tau_hab, cfg.intervalo_decisao_ticks, self.S)
        self.hab = {c: 0 for c in CLASSES_OBJETO}
        self.receptores: tuple | None = None          # os receptores presentes, fixados na primeira decisao

    def _receptores(self, pc) -> tuple:
        presentes = tuple(f.name for f in fields(pc) if getattr(pc, f.name) is not None)
        fora = [r for r in presentes if r not in RECEPTORES_DIGIBRAIN]
        if fora:
            raise ValueError(f"M-SENS: receptores fora do prototipo (os orgaos, o paladar, o banheiro; espec, secao 6): {fora}")
        if self.receptores is None:
            self.receptores = presentes
        elif presentes != self.receptores:
            raise ValueError(f"M-SENS: receptores {presentes}, na primeira decisao {self.receptores}")
        return presentes

    def proximidade(self, d: int) -> int:
        return clamp(self.S - div_arred(d * self.S, self.raio), 0, self.S)

    def codificar(self, obs) -> dict:
        S = self.S
        pc, pm = obs.corpo, obs.mundo
        recs = self._receptores(pc)
        falta = {r: falta_receptor(pc, r, S) for r in recs}
        leitura = {r: leitura_receptor(pc, r, S) for r in recs}
        hora, dormindo = obs.vetor_estado[7], obs.vetor_estado[6]
        minuto = int(round(hora * TICKS_POR_DIA)) % TICKS_POR_DIA     # a hora do dia em ticks (a fronteira da noite cai num multiplo de 15)
        ticks = obs.ticks_desde_cuidado
        if type(ticks) is not int or ticks < 0:
            raise ValueError(f"M-SENS: ticks_desde_cuidado {ticks!r}")
        contexto = {"noite": S if self.cfg.e_noite(minuto) else 0, "dormindo": S if dormindo != 0 else 0,
                    "sem_cuidado": min(S, div_arred(ticks * S, self.p.escala_cuidado))}
        if len(pm.vistos) > self.max_vistos:
            raise ValueError(f"M-SENS: {len(pm.vistos)} vistos, o maximo e {self.max_vistos}")
        objetos = []
        vistas = set()
        for ident, tipo, dx, dy, d in pm.vistos:
            c = classe_do_tipo(tipo)
            vistas.add(c)
            objetos.append({"id": ident, "tipo": tipo, "classe": c, "dx": dx, "dy": dy, "d": d, "prox": self.proximidade(d),
                            "nov": S - self.hab[c]})
        for c in CLASSES_OBJETO:                       # a habituacao anda depois da novidade da decisao
            self.hab[c] = integrar(self.hab[c], S if c in vistas else 0, self.k_hab, S)
        comida = max((o["prox"] for o in objetos if o["classe"] in COMIDAS_BOAS), default=0)
        bola = max((o["prox"] for o in objetos if o["classe"] == "bola"), default=0)
        return {"falta": falta, "leitura": leitura, "contexto": contexto, "objetos": objetos,
                "conjuncoes": {"comida_vista": comida, "sem_comida": S - comida, "bola_vista": bola},
                "ha_cheiro": pm.direcao_cheiro != 0, "pos": (pm.x, pm.y), "regiao": pm.regiao, "minuto": minuto, "pc": pc}

    def estado_interno(self) -> dict:
        return {"hab": dict(self.hab), "receptores": None if self.receptores is None else list(self.receptores)}
