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
da decisao sai da habituacao de antes dela (a primeira vez que se ve uma classe, nov = S), e so depois a habituacao anda. Sem rng.

**A tela** (GOSTO_VISUAL, P1d; docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 5 e 6; so com a subchave `olhar`, `Sens(olhar=ConfigOlhar,
genoma=GenomaVisao)`). Desligada, um receptor da tela presente falha alto, como hoje; ligada, a porta se abre so para eles:
  - os receptores da tela (`tela_<canal>`, o nivel em [0, S], e `novidade_tela`) sao lidos a parte, em `tela_niveis` e `tela_novidade`,
    e ficam fora dos `receptores` (a falta, a urgencia, o r e o P1 sao os dos onze de hoje);
  - as linhas da classe `tela`, uma por TV a vista, chegam do motor pelo gancho `ver_tela` do M-ADAPT (id, dx, dy, d), em `telas`, com a
    proximidade e a novidade da linha de objeto (`nov = S - hab[tela]`, a habituacao da classe `tela`); ficam fora de `objetos` (as
    unidades de comer, de brincar e da memoria nao as veem);
  - o gosto: o agrado do nivel visto e o pico em inteiros sobre a distancia ao alvo, por canal k,
        pico(x, l) = max(0, S - div_arred(|x| x S, l)),  A = div_arred(sum_k pico(n_k - alvo_k, l_k), 7)        em [0, S],
    com o alvo = o otimo do genoma (na escala S) + o deslocamento aprendido, e `agrado_inato` o mesmo contra o otimo so;
  - a exposicao (Zajonc 1968, `10.1037/h0025848`; espec, 5.3): o estado novo, o deslocamento do alvo por canal, so quando o pet olhou
    (`expor`): `desloc_k <- clamp(desloc_k + mul(k_expo, n_k - (o_k + desloc_k)), -teto, teto)`, com k_expo da `tau_exposicao`."""
from __future__ import annotations

from dataclasses import fields

from ..config import (CANAIS_TELA, CONFIG_DIGIBRAIN_INATOS, RECEPTORES_DIGIBRAIN, TICKS_POR_DIA, Config, ConfigDigibrainInatos, ConfigMundo,
                      ConfigOlhar)
from ..genoma_visao import GenomaVisao
from ..policies.lobos import div_arred, falta_receptor, leitura_receptor
from ._comum import clamp, ganho_de_tau, integrar, mul

CLASSES_OBJETO = ("racao", "a", "b", "c", "podre", "bola")
COMIDAS_BOAS = ("racao", "a", "b", "c")
CLASSE_TELA = "tela"                                   # a classe da TV (so com a subchave `olhar`)
RECEPTORES_TELA = tuple(f"tela_{c}" for c in CANAIS_TELA) + ("novidade_tela",)


def pico(x: int, largura: int, S: int) -> int:
    """o pico em inteiros sobre a distancia x ao alvo: S em x = 0, 0 a partir de |x| = largura (a forma do agrado, GV-7)"""
    if type(largura) is not int or largura <= 0:
        raise ValueError(f"M-SENS: largura do pico {largura!r}")
    return max(0, S - div_arred(abs(x) * S, largura))


def classe_do_tipo(tipo: str) -> str:
    """a classe do item dos `vistos`: o tipo maduro, `podre` (qualquer `_podre`) ou `bola`"""
    if tipo.endswith("_podre"):
        return "podre"
    if tipo not in CLASSES_OBJETO:
        raise ValueError(f"M-SENS: tipo de objeto desconhecido {tipo!r}")
    return tipo


class Sens:
    """o M-SENS (docstring do modulo)"""

    def __init__(self, cfg: Config, cfg_mundo: ConfigMundo, inatos: ConfigDigibrainInatos | None = None,
                 olhar: ConfigOlhar | None = None, genoma: GenomaVisao | None = None) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.S = self.p.escala
        self.cfg = cfg
        self.raio = cfg_mundo.raio_visao_celulas * cfg_mundo.sub
        self.max_vistos = cfg_mundo.max_vistos
        self.k_hab = ganho_de_tau(self.p.tau_hab, cfg.intervalo_decisao_ticks, self.S)
        self.hab = {c: 0 for c in CLASSES_OBJETO}
        self.receptores: tuple | None = None          # os receptores presentes, fixados na primeira decisao
        self.olhar = olhar                            # a tela (P1d): so com a subchave `olhar`; None desligada
        if (olhar is None) != (genoma is None):
            raise ValueError("M-SENS: a ConfigOlhar e o GenomaVisao vem juntos (so com a subchave `olhar`)")
        if olhar is not None:
            if not isinstance(olhar, ConfigOlhar) or not isinstance(genoma, GenomaVisao):
                raise TypeError(f"M-SENS: a tela pede a ConfigOlhar e o GenomaVisao: {olhar!r}, {genoma!r}")
            self.hab[CLASSE_TELA] = 0
            self.otimo, self.largura = genoma.na_escala(self.S, olhar.escala)
            self.desloc = {c: 0 for c in CANAIS_TELA}
            self.k_expo = ganho_de_tau(olhar.tau_exposicao, cfg.intervalo_decisao_ticks, self.S)
            self.exposicoes = 0
            self.tela_presente: bool | None = None    # se os receptores da tela estao no corpo, fixado na primeira decisao
        self.ir_ate_tv = False                        # a TV no jogo (D-GV-TVJOGO-3): as linhas da TV fora do raio, so com `ligar_ir_ate_tv`

    def ligar_ir_ate_tv(self) -> None:
        """a decisao D (D-GV-TVJOGO-3; so com a subchave `olhar`): o motor manda a linha da TV tambem fora do raio da visao (o pet sabe onde
        ela fica). A linha longe tem a proximidade 0 (a conta de sempre) e nao conta como vista na habituacao da classe `tela`"""
        self._exigir_olhar("ligar_ir_ate_tv")
        self.ir_ate_tv = True

    def longe(self, linha: dict) -> bool:
        """a linha da TV esta fora do raio da visao (so com o ir ate a TV)"""
        return linha["d"] > self.raio

    def _receptores(self, pc) -> tuple:
        presentes = tuple(f.name for f in fields(pc) if getattr(pc, f.name) is not None)
        if self.olhar is not None:                    # a tela (P1d): os receptores dela ficam a parte, fora dos `receptores`
            tela = tuple(r for r in presentes if r in RECEPTORES_TELA)
            if tela and tela != RECEPTORES_TELA:
                raise ValueError(f"M-SENS: os receptores da tela vem todos juntos: {tela}")
            if self.tela_presente is None:
                self.tela_presente = bool(tela)
            elif bool(tela) != self.tela_presente:
                raise ValueError("M-SENS: os receptores da tela mudaram desde a primeira decisao")
            presentes = tuple(r for r in presentes if r not in RECEPTORES_TELA)
        fora = [r for r in presentes if r not in RECEPTORES_DIGIBRAIN]
        if fora:
            raise ValueError(f"M-SENS: receptores fora do prototipo (os orgaos, o paladar, o banheiro; espec, secao 6): {fora}")
        if self.receptores is None:
            self.receptores = presentes
        elif presentes != self.receptores:
            raise ValueError(f"M-SENS: receptores {presentes}, na primeira decisao {self.receptores}")
        return presentes

    # ------------------------------------------------------------ a tela (P1d, so com a subchave `olhar`)
    def _exigir_olhar(self, onde: str) -> ConfigOlhar:
        if self.olhar is None:
            raise RuntimeError(f"M-SENS: {onde} sem a subchave olhar")
        return self.olhar

    def niveis_tela(self, pc) -> dict | None:
        """os niveis da tela na percepcao do corpo (canal -> [0, S]), ou None sem os receptores da tela"""
        self._exigir_olhar("niveis_tela")
        if getattr(pc, "tela_cor", None) is None:
            return None
        niveis = {c: getattr(pc, f"tela_{c}") for c in CANAIS_TELA}
        if any(type(v) is not int or not 0 <= v <= self.S for v in niveis.values()):
            raise ValueError(f"M-SENS: niveis da tela fora de [0, S]: {niveis!r}")
        return niveis

    def _agrado(self, niveis: dict, desloc: dict) -> int:
        S = self.S
        if tuple(niveis) != CANAIS_TELA:
            raise ValueError(f"M-SENS: os niveis da tela por canal, na ordem {CANAIS_TELA}: {niveis!r}")
        return div_arred(sum(pico(niveis[c] - (self.otimo[c] + desloc[c]), self.largura[c], S) for c in CANAIS_TELA), len(CANAIS_TELA))

    def agrado(self, niveis: dict) -> int:
        """o agrado do nivel visto contra o alvo (o otimo do genoma mais o deslocamento da exposicao), em [0, S]"""
        self._exigir_olhar("agrado")
        return self._agrado(niveis, self.desloc)

    def agrado_inato(self, niveis: dict) -> int:
        """o agrado do nivel visto contra o otimo do genoma so (o inato, fixo na vida)"""
        self._exigir_olhar("agrado_inato")
        return self._agrado(niveis, dict.fromkeys(CANAIS_TELA, 0))

    def expor(self, niveis: dict) -> None:
        """a exposicao: o alvo de cada canal anda para o nivel visto, com o teto do deslocamento (so quando o pet olhou)"""
        co = self._exigir_olhar("expor")
        S = self.S
        for c in CANAIS_TELA:
            alvo = self.otimo[c] + self.desloc[c]
            self.desloc[c] = clamp(self.desloc[c] + mul(self.k_expo, niveis[c] - alvo, S), -co.teto_exposicao, co.teto_exposicao)
        self.exposicoes += 1

    def _linhas_tela(self, telas: list | None) -> list[dict]:
        """as linhas da classe `tela` (a TV a vista, do motor): a proximidade e a novidade da linha; a habituacao anda depois"""
        S = self.S
        out = []
        for linha in telas or ():
            if type(linha) not in (tuple, list) or len(linha) != 4 or any(type(v) is not int for v in linha) or linha[3] < 0:
                raise ValueError(f"M-SENS: linha da tela malformada (id, dx, dy, d inteiros): {linha!r}")
            ident, dx, dy, d = linha
            if d > self.raio and not self.ir_ate_tv:
                raise ValueError(f"M-SENS: linha da tela fora do raio da visao ({d} > {self.raio}) sem o ir ate a TV: {linha!r}")
            out.append({"id": ident, "tipo": CLASSE_TELA, "classe": CLASSE_TELA, "dx": dx, "dy": dy, "d": d, "prox": self.proximidade(d),
                        "nov": S - self.hab[CLASSE_TELA]})
        if len({o["id"] for o in out}) != len(out):
            raise ValueError(f"M-SENS: duas linhas da tela com o mesmo id: {telas!r}")
        return out

    def proximidade(self, d: int) -> int:
        return clamp(self.S - div_arred(d * self.S, self.raio), 0, self.S)

    def resumir_lutas(self, lutas: list[dict]) -> list[dict]:
        """o resumo da luta na Observacao (ponte da luta, PE2): os resumos que chegaram desde a decisao anterior, na ordem, em inteiros
        (o rival, o resultado -1, 0, +1, a vida perdida em S e o tick). Falha alto num resumo malformado"""
        out = []
        for r in lutas:
            if (type(r.get("rival")) is not str or not r["rival"] or r.get("resultado") not in (-1, 0, 1)
                    or type(r.get("resultado")) is not int or type(r.get("vida_perdida_s")) is not int or r["vida_perdida_s"] < 0
                    or type(r.get("tick")) is not int):
                raise ValueError(f"M-SENS: resumo da luta malformado {r!r}")
            out.append({"rival": r["rival"], "resultado": r["resultado"], "vida_perdida_s": r["vida_perdida_s"], "tick": r["tick"]})
        return out

    def codificar(self, obs, lutas: list[dict] | None = None, telas: list | None = None) -> dict:
        S = self.S
        if telas is not None and self.olhar is None:
            raise RuntimeError("M-SENS: as linhas da tela sem a subchave olhar")
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
        linhas_tela = self._linhas_tela(telas) if self.olhar is not None else None
        for c in CLASSES_OBJETO:                       # a habituacao anda depois da novidade da decisao
            self.hab[c] = integrar(self.hab[c], S if c in vistas else 0, self.k_hab, S)
        if linhas_tela is not None:                    # a classe `tela` (P1d), no fim, com a mesma regra
            # o ir ate a TV (D-GV-TVJOGO-3): a linha longe nao conta como vista (sem ele, toda linha esta no raio: a conta de hoje)
            vista = any(not self.longe(o) for o in linhas_tela)
            self.hab[CLASSE_TELA] = integrar(self.hab[CLASSE_TELA], S if vista else 0, self.k_hab, S)
        comida = max((o["prox"] for o in objetos if o["classe"] in COMIDAS_BOAS), default=0)
        bola = max((o["prox"] for o in objetos if o["classe"] == "bola"), default=0)
        out = {"falta": falta, "leitura": leitura, "contexto": contexto, "objetos": objetos,
               "conjuncoes": {"comida_vista": comida, "sem_comida": S - comida, "bola_vista": bola},
               "ha_cheiro": pm.direcao_cheiro != 0, "pos": (pm.x, pm.y), "regiao": pm.regiao, "minuto": minuto, "pc": pc}
        if lutas is not None:                          # a ponte da luta (PE2): desligada, nenhum campo novo
            out["lutas"] = self.resumir_lutas(lutas)
        if self.olhar is not None:                     # a tela (P1d): desligada, nenhum campo novo
            out["telas"] = linhas_tela
            out["tela_niveis"] = self.niveis_tela(pc)
            out["tela_novidade"] = getattr(pc, "novidade_tela", None)
        return out

    def estado_interno(self) -> dict:
        out = {"hab": dict(self.hab), "receptores": None if self.receptores is None else list(self.receptores)}
        if self.olhar is not None:                     # a tela (P1d): desligada, o estado e o de hoje, byte a byte
            out["tela"] = {"otimo": dict(self.otimo), "largura": dict(self.largura), "desloc": dict(self.desloc),
                           "exposicoes": self.exposicoes}
        return out
