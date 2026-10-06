"""DigiBrain C, Fly-like (V2, CEREBRO-C: docs/TAREFA_V2_CEREBRO_C.md; contrato da secao 1 de docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md).

A familia e a da Drosophila em docs/research/digibrain/synthesis/brain_comparison.md: circuitos especializados, canais de reforco
paralelos, plasticidade local, competicao de comportamentos e memoria dependente de estado. "Inspirado em" fala deste cerebro, nao da
mosca (problema 4 de brain_comparison.md): nada aqui corresponde literalmente a um neuronio, e as fontes (Aso e Rubin 2016; Tsao et al.
2018; Jiang e Litwin-Kumar 2021) sao CORPUS, pista e nao evidencia.

  O HERDADO (C-1, comum aos tres cerebros): a regra do instinto e os candidatos que ela propoe (lobos.impulsos, a sonda do proprio
  PoliticaInstinto/PoliticaInstintoFrutas) e o prior deles (o mesmo do A: lobos.PoliticaLobos._tabela_prior, ativacao em ponto fixo).
  Com o aprendizado desligado o C e o instinto byte a byte, como o P0 do A.

  CIRCUITOS (por classe de estimulo, H-ACT-02, no que o mundo tem): cada um transforma a Observacao em celulas binarias esparsas (as
  "Kenyon cells" do cerebro: faixas e conjuncoes fixas, herdadas, sem aprendizado):
    corpo    interocepcao: a faixa de fome, higiene, energia, humor, saude, sujeira, dormindo e da hora (22 celulas);
    social   o dono: a faixa do tempo sem cuidado e a conjuncao hora x tempo sem cuidado (15);
    objeto   o mundo: bola presente, cada fruta presente, fome x fruta presente, energia x bola presente (16).
  Na escolha da fruta (a sub-decisao de comer), um circuito da fruta: a identidade de cada fruta e o que o dono informou dela (bem ou
  mal; a entrada da informacao do N5) (5 celulas).

  SAIDA E COMPETICAO: cada celula ativa tem, para cada acao, duas sinapses de saida inteiras, uma no compartimento APETITIVO e outra no
  AVERSIVO (0 <= w <= teto). O impulso aprendido de uma acao e L_a = soma, nas celulas ativas, de apetitivo x gate - aversivo; o peso
  efetivo do candidato e o do instinto mais L_a / S (com o piso no peso efetivo, so com o aprendizado ligado, como o A). Os comportamentos
  competem pelo sorteio proporcional de sempre (uma chamada de rng.random(), a conta de random.choices).

  MEMORIA DEPENDENTE DE ESTADO: a memoria apetitiva de COMER so se expressa na medida da fome (gate = S - arred(fome x S), Tsao et al. 2018
  como pista); a aversiva se expressa sempre. As conjuncoes fome x fruta guardam onde a fruta foi boa ou ruim.

  CANAIS DE REFORCO PARALELOS: o sinal chega separado por canal e cada canal so mexe no circuito dele:
    consequencia (P1, P2): o sinal homeostatico por drive (lobos.sinal_homeostatico_canais/_fruta_canais, a soma dos canais e o escalar
      da bancada, conferida em toda decisao): fome, higiene e energia vao aos circuitos corpo e social; o humor (o da fruta, E2) vai ao
      objeto e a escolha da fruta. No C os canais sao a arquitetura, sempre ligados (no A sao a chave canais_ligados).
    dono (P3): elogio, bronca e o chamado com latencia, na janela da v1 do A, chegam a todos os circuitos da decisao.
  PLASTICIDADE LOCAL (tres fatores): so mudam as sinapses das celulas ATIVAS na decisao, para a ACAO executada, no compartimento do sinal:
    sinal f > 0: apetitivo += div_arred(passo x f, S);  sinal f < 0: aversivo += div_arred(passo x (-f), S);  cortado em teto.
  Nada depende da probabilidade da politica (diferente da regra do A). Decisao com um candidato so nao aprende (nada a escolher), como no A.

  SONDA DO APRENDIDO (contrato 1.1): toda decisao guarda a acao que sairia com a parte aprendida zerada e o mesmo u
  (`motivos[-1]["sonda"]`), e a escolha da fruta, a fruta sem o aprendido e sem a informacao (`motivos[-1]["fruta"]["sonda"]`).

Tudo em inteiros na escala S, sem funcoes transcendentais (o criterio 3 do M6: o porte para a web). So biblioteca padrao.
"""

from __future__ import annotations

import random
from dataclasses import fields, replace

from ..config import (CONFIG_BOLA, CONFIG_CEREBRO_C, CONFIG_CONSEQUENCIA, CONFIG_FRUTAS, CONFIG_PADRAO, Config, ConfigBola,
                      ConfigCerebroC, ConfigConsequencia, ConfigFrutas)
from ..events import FRUTAS, AcaoPet, AcaoUsuario
from ..policy import Observacao, PoliticaInstinto, Transicao
from . import lobos
from .lobos import (ACOES, ENTRADAS, ENTRADAS_MUNDO, REGRAS, REGRAS_MUNDO, _sortear_frutas, arred, ativacao, div_arred, impulsos,
                    sinal_homeostatico_canais, sinal_homeostatico_fruta_canais, sortear)

CIRCUITOS = ("corpo", "social", "objeto")
COMPARTIMENTOS = ("apetitivo", "aversivo")
# o canal de cada drive vai ao(s) circuito(s) dele; o dono vai a todos (lobos.CANAL_DO_DRIVE da o nome do canal pelo drive)
ROTA_CANAIS_C = {"fome": ("corpo", "social"), "higiene": ("corpo", "social"), "energia": ("corpo", "social"),
                 "humor": ("objeto", "fruta")}
FEEDBACK = frozenset({AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER})

# Status e fonte de cada campo da ConfigCerebroC. Todos PROPOSTOS, nenhum referendado; fora de todo hash.
PARAMETROS_CEREBRO_C: dict[str, tuple[str, str]] = {
    "aprendizado_ligado": ("PROPOSTO", "desligado = o instinto byte a byte (C-1); a bancada liga nos bracos que aprendem"),
    "bits_ponto_fixo": ("PROPOSTO", "o mesmo do A (ConfigLobos): S potencia de dois, divisao exata"),
    "escala_ticks_desde_cuidado": ("PROPOSTO", "o mesmo do A (ConfigLobos)"),
    "maximo_pesos": ("PROPOSTO", "o teto do plano da V2, como o A"),
    "passo": ("PROPOSTO", "livre, adendo de calibracao do C (grade {S/32, S/16, S/8})"),
    "teto": ("PROPOSTO", "livre, adendo de calibracao do C (grade {S, 4S, 16S})"),
    "piso_peso": ("PROPOSTO", "o mesmo do A (ConfigLobos.piso_peso)"),
    "janela_latencia_ticks": ("PROPOSTO", "o mesmo do A: a janela de credito da v1 (fonte do sinal comum)"),
    "recompensa_pedido_ignorado": ("PROPOSTO", "o mesmo do A"),
    "recompensa_elogio": ("PROPOSTO", "o mesmo do A"),
    "recompensa_repreensao": ("PROPOSTO", "o mesmo do A"),
    "w0_info": ("PROPOSTO", "livre, adendo de calibracao do C (grade {S/4, S/2, 3S/4}, regra K-3)"),
    "cortes_necessidade": ("PROPOSTO", "estrutura: os limiares do instinto (0,25 urgente; 0,5 o pedido do dono)"),
    "cortes_binarios": ("PROPOSTO", "estrutura: o meio da faixa"),
    "cortes_hora": ("PROPOSTO", "estrutura: quatro quartos do dia"),
    "cortes_sem_cuidado": ("PROPOSTO", "estrutura: os mesmos cortes da necessidade, na escala do tempo sem cuidado"),
}


def validar_parametros_cerebro_c(cfg: ConfigCerebroC | None = None) -> None:
    """Todo campo da ConfigCerebroC tem status registrado; nenhum campo registrado sem existir."""
    campos = {f.name for f in fields(cfg or CONFIG_CEREBRO_C)}
    if campos != set(PARAMETROS_CEREBRO_C):
        raise ValueError(f"sem registro: {sorted(campos - set(PARAMETROS_CEREBRO_C))}; "
                         f"registro sem campo: {sorted(set(PARAMETROS_CEREBRO_C) - campos)}")
    for nome, (status, fonte) in PARAMETROS_CEREBRO_C.items():
        if status not in ("PROPOSTO", "DECIDIDO") or not fonte:
            raise ValueError(f"{nome}: status {status!r} ou fonte vazia")


def faixa(v: float, cortes: tuple) -> int:
    """Indice da faixa de v: quantos cortes ficam em ou abaixo de v (0..len(cortes))."""
    return sum(1 for c in cortes if v >= c)


def celulas(cfg: ConfigCerebroC) -> dict[str, tuple[str, ...]]:
    """Os nomes das celulas de cada circuito, na ordem fixa (a estrutura herdada; nao depende do mundo)."""
    n_nec, n_bin = len(cfg.cortes_necessidade) + 1, len(cfg.cortes_binarios) + 1
    n_hora, n_soc = len(cfg.cortes_hora) + 1, len(cfg.cortes_sem_cuidado) + 1
    corpo = tuple(f"{v}:{k}" for v in ("fome", "higiene", "energia", "humor") for k in range(n_nec))
    corpo += tuple(f"{v}:{k}" for v in ("saude", "sujeira", "dormindo") for k in range(n_bin))
    corpo += tuple(f"hora:{k}" for k in range(n_hora))
    social = tuple(f"sem_cuidado:{k}" for k in range(n_soc))
    social += tuple(f"hora:{h}*sem_cuidado:{k}" for h in range(n_hora) for k in range(n_soc))
    objeto = ("bola",) + tuple(f"fruta_{f}" for f in FRUTAS)
    objeto += tuple(f"fome:{k}*fruta_{f}" for k in range(n_nec) for f in FRUTAS)
    objeto += tuple(f"energia:{k}*bola" for k in range(n_nec))
    return {"corpo": corpo, "social": social, "objeto": objeto}


CELULAS_FRUTA = tuple(f"id_{f}" for f in FRUTAS) + ("info_bem", "info_mal")


class PoliticaCerebroC:
    """O DigiBrain C sob o Protocol Politica (agir, observar, estado_interno) e os ganchos da bancada (receber_acao_dono,
    observar_consequencia, escolher_fruta, fruta_comida). Mesma assinatura do PoliticaLobos: ve a bola e as frutas so com a chave
    delas ligada. Nao altera engine.py nem lobos.py (so importa as funcoes publicas e a sonda do instinto)."""

    nome = "cerebro_c"

    def __init__(self, cfg: Config | None = None, cfg_c: ConfigCerebroC | None = None,
                 cfg_bola: ConfigBola | None = None, cfg_frutas: ConfigFrutas | None = None) -> None:
        self.cfg = cfg or CONFIG_PADRAO
        self.cl = cfg_c or CONFIG_CEREBRO_C             # `cl`: a bancada le cl.escala para o sinal da consequencia
        cl = self.cl
        if cl.bits_ponto_fixo < 1:
            raise ValueError("bits_ponto_fixo precisa ser >= 1")
        for nome in ("passo", "teto", "piso_peso", "janela_latencia_ticks", "w0_info"):
            if type(getattr(cl, nome)) is not int:
                raise TypeError(f"ConfigCerebroC.{nome} precisa ser inteiro")
        if cl.passo <= 0 or cl.teto <= 0 or cl.piso_peso <= 0 or cl.janela_latencia_ticks <= 0 or cl.w0_info < 0:
            raise ValueError("passo, teto, piso_peso e janela_latencia_ticks positivos; w0_info >= 0")
        self._escala = S = cl.escala
        # o herdado (C-1): o mesmo instinto e o mesmo prior do A, com o mundo so com a chave dele ligada
        self._ve_bola = cfg_bola is not None and cfg_bola.ligada
        self._ve_frutas = cfg_frutas is not None and cfg_frutas.ligada
        self._ve_mundo = self._ve_bola or self._ve_frutas
        if self._ve_mundo:
            from ..frutas import PoliticaInstintoFrutas        # importacao tardia: frutas importa o motor inteiro
            cb = cfg_bola if self._ve_bola else replace(cfg_bola or CONFIG_BOLA, ligada=False)
            cf = cfg_frutas if self._ve_frutas else replace(cfg_frutas or CONFIG_FRUTAS, ligada=False)
            self.entradas = ENTRADAS + ENTRADAS_MUNDO
            self._prior = lobos.PoliticaLobos._tabela_prior(S, REGRAS + REGRAS_MUNDO, self.entradas,
                                                            lobos.PoliticaLobos._prior_mundo(cb, cf))
            self._instinto = PoliticaInstintoFrutas(self.cfg, cb, cf)
        else:
            self.entradas = ENTRADAS
            self._prior = lobos.PoliticaLobos._tabela_prior(S)
            self._instinto = PoliticaInstinto(self.cfg)
        # a estrutura: as celulas e as sinapses de saida (dois compartimentos por celula e acao; a fruta: dois por celula)
        self._celulas = celulas(cl)
        self._indice = {c: {nome: i for i, nome in enumerate(nomes)} for c, nomes in self._celulas.items()}
        self._sinapses = {c: {comp: {a: [0] * len(nomes) for a in ACOES} for comp in COMPARTIMENTOS}
                          for c, nomes in self._celulas.items()}
        self._sinapses_fruta = {comp: [0] * len(CELULAS_FRUTA) for comp in COMPARTIMENTOS}
        n = self.n_pesos()
        if n >= cl.maximo_pesos:
            raise ValueError(f"{n} parametros, teto {cl.maximo_pesos}")
        self._aprende = bool(cl.aprendizado_ligado)
        self._piso = cl.piso_peso / S
        self.motivos: list[dict] = []
        self._ultima_regra: str | None = None
        self._registro_decisao: dict | None = None
        self._ultima: dict | None = None
        self._pendentes: list[tuple[int, dict]] = []
        self._consequencia_pendente: tuple | None = None
        self._fruta_na_decisao = False
        self._fome_na_decisao = 0.0
        self._info_na_decisao: tuple = ()
        self._tick_ultimo_cuidado = 0
        self._tick_ultima_decisao = -1
        self._n_decisoes = 0
        self._n_recompensas: dict[str, int] = {"elogio": 0, "repreensao": 0, "latencia": 0, "ignorado": 0}
        self._n_atualizacoes = 0
        self._cortes_teto = 0
        self._canais = {"creditos": 0, "por_canal": {}, "por_circuito": {c: 0 for c in CIRCUITOS + ("fruta",)}}

    # ------------------------------------------------------------- leitura

    @property
    def ultima_regra(self) -> str | None:
        return self._ultima_regra

    @property
    def ultimo_motivo(self) -> dict | None:
        return self.motivos[-1] if self.motivos else None

    @property
    def aprende(self) -> bool:
        return self._aprende

    @property
    def ve_mundo(self) -> bool:
        return self._ve_mundo

    def n_pesos(self) -> int:
        """Parametros aprendiveis (contrato 1.3): toda sinapse de saida das celulas, nos dois compartimentos, para toda acao, mais as
        da escolha da fruta. As celulas (faixas e conjuncoes) e o prior do instinto sao fixos (herdados) e nao contam."""
        return (sum(len(nomes) * len(ACOES) * len(COMPARTIMENTOS) for nomes in self._celulas.values())
                + len(CELULAS_FRUTA) * len(COMPARTIMENTOS))

    def _todas(self):
        for c in self._sinapses:
            for comp in COMPARTIMENTOS:
                for a in ACOES:
                    yield from self._sinapses[c][comp][a]
        for comp in COMPARTIMENTOS:
            yield from self._sinapses_fruta[comp]

    def pesos_mudaram(self) -> bool:
        return any(w != 0 for w in self._todas())

    def desvio_maximo(self) -> int:
        return max(self._todas())

    def pesos_no_teto(self) -> int:
        return sum(w == self.cl.teto for w in self._todas())

    # ------------------------------------------------------------- percepcao: as celulas ativas

    def percepcao(self, obs: Observacao) -> list[float]:
        """A entrada do prior (a mesma do A): lobos.percepcao, mais bola e fruta quando ve o mundo."""
        x = lobos.percepcao(obs, self.cl.escala_ticks_desde_cuidado)
        if self._ve_mundo:
            x.extend((obs.bola, obs.fruta))
        return x

    def ativas(self, obs: Observacao) -> dict[str, list[int]]:
        """Os indices das celulas ativas em cada circuito (binarias, esparsas)."""
        cl = self.cl
        v = obs.vetor_estado
        nec = [faixa(v[i], cl.cortes_necessidade) for i in range(4)]          # fome, higiene, energia, humor
        hora = faixa(v[7], cl.cortes_hora)
        soc = faixa(min(1.0, obs.ticks_desde_cuidado / cl.escala_ticks_desde_cuidado), cl.cortes_sem_cuidado)
        ix = self._indice
        corpo = [ix["corpo"][f"{n}:{k}"] for n, k in zip(("fome", "higiene", "energia", "humor"), nec)]
        corpo += [ix["corpo"][f"{n}:{faixa(v[i], cl.cortes_binarios)}"] for n, i in (("saude", 4), ("sujeira", 5), ("dormindo", 6))]
        corpo.append(ix["corpo"][f"hora:{hora}"])
        social = [ix["social"][f"sem_cuidado:{soc}"], ix["social"][f"hora:{hora}*sem_cuidado:{soc}"]]
        objeto = []
        if obs.bola > 0.0:
            objeto += [ix["objeto"]["bola"], ix["objeto"][f"energia:{nec[2]}*bola"]]
        for f, p in zip(FRUTAS, obs.frutas_cenario):
            if p > 0.0:
                objeto += [ix["objeto"][f"fruta_{f}"], ix["objeto"][f"fome:{nec[0]}*fruta_{f}"]]
        return {"corpo": corpo, "social": social, "objeto": sorted(objeto)}

    # ------------------------------------------------------------- decisao

    def _aprendido(self, ativas: dict, candidatos: tuple, fome: float) -> dict[str, dict[AcaoPet, int]]:
        """L_a por circuito, em inteiros na escala S: soma nas celulas ativas de apetitivo x gate - aversivo. O gate (memoria
        dependente de estado) so age no apetitivo de COMER: gate = S - arred(fome x S) (a fome e o deficit: 1 = saciado)."""
        S = self._escala
        gate_comer = S - arred(fome * S)
        por_circ = {}
        for c in CIRCUITOS:
            app, av = self._sinapses[c]["apetitivo"], self._sinapses[c]["aversivo"]
            d = {}
            for a in candidatos:
                soma_app = 0
                soma_av = 0
                for k in ativas[c]:
                    soma_app += app[a][k]
                    soma_av += av[a][k]
                if a is AcaoPet.COMER and soma_app:
                    soma_app = div_arred(soma_app * gate_comer, S)
                d[a] = soma_app - soma_av
            por_circ[c] = d
        return por_circ

    def _efetivos(self, regra: str, candidatos: tuple, x: list[float], aprendido: dict | None) -> tuple[dict, dict]:
        """(contribuicoes, peso efetivo por candidato). Impulso (o prior do instinto, a mesma conta do A) + aprendido / S + piso (so com
        o aprendizado ligado). Com o aprendido zero e o aprendizado desligado, o peso e o do instinto, byte a byte."""
        S = self._escala
        prior = self._prior[regra]
        imp = {a: ativacao(prior[a], x, S) for a in candidatos}
        apr = {a: 0.0 for a in candidatos}
        if aprendido is not None:
            for a in candidatos:
                total = 0
                for c in CIRCUITOS:
                    total += aprendido[c][a]
                apr[a] = total / S
        soma = {a: imp[a] + apr[a] for a in candidatos}
        if self._aprende:
            piso = {a: (self._piso - soma[a] if soma[a] < self._piso else 0.0) for a in candidatos}
        else:
            piso = {a: 0.0 for a in candidatos}
        efetivos = {a: soma[a] + piso[a] for a in candidatos}
        return {"impulsos": imp, "aprendido": apr, "piso": piso}, efetivos

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        if self._consequencia_pendente is not None:
            raise RuntimeError("E2: o comer com fruta da decisao anterior ficou sem fruta_comida")
        x = self.percepcao(obs)
        regra, candidatos = impulsos(self._instinto, obs)
        ativas = self.ativas(obs)
        aprendido = self._aprendido(ativas, candidatos, obs.vetor_estado[0]) if self._aprende else None
        contrib, pesos = self._efetivos(regra, candidatos, x, aprendido)
        if len(candidatos) == 1:
            u, acao = None, candidatos[0]
            sem = acao
        else:
            u = rng.random()
            acao = candidatos[sortear([pesos[a] for a in candidatos], u)]
            if aprendido is None:
                sem = acao
            else:
                # a sonda do aprendido (contrato 1.1): a mesma decisao com a parte aprendida zerada e o mesmo u; so le
                _, p0 = self._efetivos(regra, candidatos, x, None)
                sem = candidatos[sortear([p0[a] for a in candidatos], u)]
        self._ultima_regra = regra
        self._fruta_na_decisao = self._ve_frutas and obs.fruta > 0.0
        self._fome_na_decisao = obs.vetor_estado[0]
        self._info_na_decisao = obs.info_frutas
        self._registro_decisao = ({"regra": regra, "candidatos": candidatos, "acao": acao, "ativas": ativas}
                                  if self._aprende else None)
        self.motivos.append({
            "n": len(self.motivos), "regra": regra, "candidatos": [a.value for a in candidatos],
            "percepcao": dict(zip(self.entradas, x)),
            "contribuicoes": {k: {a.value: v for a, v in d.items()} for k, d in contrib.items()},
            "circuitos": ({c: {a.value: aprendido[c][a] / self._escala for a in candidatos} for c in CIRCUITOS}
                          if aprendido is not None else None),
            "celulas": {c: [self._celulas[c][k] for k in ativas[c]] for c in CIRCUITOS},
            "pesos": {a.value: v for a, v in pesos.items()},
            "u": u, "acao": acao.value,
            "sonda": {"acao_sem_aprendido": sem.value, "aprendido_decidiu": sem is not acao},
        })
        return acao

    # ------------------------------------------------------------- a escolha da fruta (sub-decisao de comer)

    def _ativas_fruta(self, f: str) -> list[int]:
        ativas = [CELULAS_FRUTA.index(f"id_{f}")]
        info = self._info_na_decisao[FRUTAS.index(f)] if self._info_na_decisao else 0.0
        if info > 0.0:
            ativas.append(CELULAS_FRUTA.index("info_bem"))
        elif info < 0.0:
            ativas.append(CELULAS_FRUTA.index("info_mal"))
        return ativas

    def _pesos_frutas(self, presentes: list[str], incentivos: dict, com_aprendido: bool, com_info: bool) -> list[float]:
        """Peso de cada fruta = ((S + L_f) / S) x incentivo_f (+ (w0_info / S) x info_f, com o piso na fruta informada). L_f = soma nas
        celulas ativas da fruta de apetitivo - aversivo; com as celulas de informacao so se `com_info`. No prior (L = 0, w0_info 0) e a
        escolha de sempre do MotorFrutas, byte a byte."""
        S = self._escala
        app, av = self._sinapses_fruta["apetitivo"], self._sinapses_fruta["aversivo"]
        pesos = []
        for f in presentes:
            L = 0
            if com_aprendido:
                for k in self._ativas_fruta(f):
                    if not com_info and CELULAS_FRUTA[k].startswith("info_"):
                        continue
                    L += app[k] - av[k]
            c = (S + L) / S
            if self._aprende and c < self._piso:
                c = self._piso
            p = c * incentivos[f]
            info = self._info_na_decisao[FRUTAS.index(f)] if self._info_na_decisao else 0.0
            if com_info and self.cl.w0_info and info != 0.0:
                p = p + (self.cl.w0_info / S) * info
                if p < self._piso:
                    p = self._piso
            pesos.append(p)
        return pesos

    def escolher_fruta(self, presentes: list[str], incentivos: dict, u: float) -> str | None:
        """Gancho do MotorFrutas: qual fruta comer, com o mesmo u da rng_fruta e o sorteio do MotorFrutas._escolher. Sem ver as frutas,
        None (o motor escolhe como sempre). Sonda: a fruta com o aprendido zerado e a fruta sem a informacao (inata e aprendida)."""
        if not self._ve_frutas:
            return None
        pesos = self._pesos_frutas(presentes, incentivos, self._aprende, True)
        escolhida = _sortear_frutas(presentes, pesos, u)
        sem_aprendido = _sortear_frutas(presentes, self._pesos_frutas(presentes, incentivos, False, True), u)
        sem_info = _sortear_frutas(presentes, self._pesos_frutas(presentes, incentivos, self._aprende, False), u)
        if self.motivos:
            self.motivos[-1]["fruta"] = {
                "presentes": list(presentes), "pesos": dict(zip(presentes, pesos)), "u": u, "escolhida": escolhida,
                "info": {f: (self._info_na_decisao[FRUTAS.index(f)] if self._info_na_decisao else 0.0) for f in presentes},
                "sonda": {"escolha_sem_aprendido": sem_aprendido, "aprendido_decidiu": sem_aprendido != escolhida,
                          "escolha_sem_info": sem_info, "info_decidiu": sem_info != escolhida},
            }
        if self._aprende:
            registro = self._registro_decisao
            if registro is None or registro["acao"] is not AcaoPet.COMER or "fruta" in registro:
                raise RuntimeError("escolha da fruta sem uma decisao de comer registrada")
            registro["fruta"] = {"candidatos": tuple(presentes), "acao": escolhida, "ativas": self._ativas_fruta(escolhida)}
        return escolhida

    # ------------------------------------------------------------- o credito

    def observar(self, transicao: Transicao) -> None:
        """Fontes dono e nenhuma: a decisao observada vira a ultima (elogio e bronca creditam a ela) e o chamado fica pendente."""
        self._n_decisoes += 1
        if not self._aprende:
            return
        obs = transicao.observacao
        tick = obs.ticks_desde_cuidado + self._tick_ultimo_cuidado
        if obs.ticks_desde_cuidado < 0 or tick <= self._tick_ultima_decisao:
            raise RuntimeError(f"relogio inconsistente: decisao em {tick}, anterior {self._tick_ultima_decisao}")
        self._tick_ultima_decisao = tick
        self._expirar(tick)
        registro = self._registro_decisao
        if registro is None or registro["acao"] is not transicao.acao:
            raise RuntimeError("registro da decisao nao corresponde a acao observada")
        self._ultima = registro
        if transicao.acao is AcaoPet.CHAMAR_ATENCAO:
            self._pendentes.append((tick, registro))

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """O canal do dono, com a janela da v1 do A: elogio e bronca na ultima decisao; o chamado atendido paga 1 - L/janela; o
        expirado, recompensa_pedido_ignorado. Chega a todos os circuitos da decisao."""
        if not self._aprende:
            return
        if tick < self._tick_ultimo_cuidado:
            raise RuntimeError(f"acao do dono no passado: {tick} < {self._tick_ultimo_cuidado}")
        self._tick_ultimo_cuidado = tick
        self._expirar(tick)
        S = self._escala
        if acao in FEEDBACK:
            if self._ultima is None:
                return
            if acao is AcaoUsuario.ELOGIAR:
                self._creditar(self._ultima, {"dono": arred(self.cl.recompensa_elogio * S)})
                self._n_recompensas["elogio"] += 1
            else:
                self._creditar(self._ultima, {"dono": arred(self.cl.recompensa_repreensao * S)})
                self._n_recompensas["repreensao"] += 1
        elif acao in lobos.CUIDADOS:
            janela = self.cl.janela_latencia_ticks
            for tick_pedido, registro in self._pendentes:
                self._creditar(registro, {"dono": S - div_arred((tick - tick_pedido) * S, janela)})
                self._n_recompensas["latencia"] += 1
            self._pendentes = []

    def _expirar(self, tick: int) -> None:
        janela = self.cl.janela_latencia_ticks
        vivos = []
        for tick_pedido, registro in self._pendentes:
            if tick - tick_pedido > janela:
                self._creditar(registro, {"dono": arred(self.cl.recompensa_pedido_ignorado * self._escala)})
                self._n_recompensas["ignorado"] += 1
            else:
                vivos.append((tick_pedido, registro))
        self._pendentes = vivos

    def observar_consequencia(self, transicao: Transicao, f_S: int, cfg_consequencia: ConfigConsequencia | None = None) -> None:
        """Fonte consequencia (P1, P2): o sinal homeostatico da propria acao, por canal (a soma dos canais e o `f_S` escalar da bancada,
        conferida). Comer com fruta no cenario espera a fruta_comida (a E2, como no A)."""
        self._n_decisoes += 1
        if not self._aprende:
            return
        if self._consequencia_pendente is not None:
            raise RuntimeError("E2: o comer com fruta da decisao anterior ficou sem fruta_comida")
        registro = self._registro_decisao
        if registro is None or registro["acao"] is not transicao.acao:
            raise RuntimeError("registro da decisao nao corresponde a acao observada")
        self._ultima = registro
        cc = cfg_consequencia or CONFIG_CONSEQUENCIA
        self._n_recompensas["consequencia"] = self._n_recompensas.get("consequencia", 0) + 1
        if self._fruta_na_decisao and transicao.acao is AcaoPet.COMER:
            self._consequencia_pendente = (registro, transicao, cc)
            return
        canais = sinal_homeostatico_canais(transicao, self._escala, cc)
        if sum(canais.values()) != f_S:
            raise RuntimeError(f"canais {canais} nao somam o sinal escalar {f_S}")
        self._creditar(registro, canais)

    def fruta_comida(self, fruta: str, obs_depois: Observacao) -> None:
        """Gancho do MotorFrutas logo depois de comer: o comer pendente recebe o sinal da fruta por canal (a E2: o humor entra)."""
        pendente, self._consequencia_pendente = self._consequencia_pendente, None
        if pendente is None:
            return
        registro, transicao, cc = pendente
        sub = registro.get("fruta")
        if sub is None or sub["acao"] != fruta:
            raise RuntimeError(f"E2: fruta comida {fruta!r} nao e a da escolha registrada")
        self._n_recompensas["consequencia_fruta"] = self._n_recompensas.get("consequencia_fruta", 0) + 1
        canais = sinal_homeostatico_fruta_canais(transicao.observacao, obs_depois, self._escala, cc)
        self._creditar(registro, canais)

    def _creditar(self, registro: dict, canais: dict[str, int]) -> None:
        """A plasticidade local: cada canal vai ao(s) circuito(s) dele (ROTA_CANAIS_C; o dono a todos); em cada circuito, as sinapses
        das celulas ATIVAS para a acao EXECUTADA, no compartimento do sinal (f > 0 apetitivo, f < 0 aversivo), += div_arred(passo x
        |f|, S), cortadas em teto. Decisao com um candidato so nao aprende; a escolha da fruta, so com duas frutas ou mais."""
        alvos = {c: 0 for c in CIRCUITOS + ("fruta",)}
        for canal, f in canais.items():
            destinos = CIRCUITOS + ("fruta",) if canal == "dono" else ROTA_CANAIS_C[canal]
            for c in destinos:
                alvos[c] += f
            self._canais["por_canal"][canal] = self._canais["por_canal"].get(canal, 0) + f
        self._canais["creditos"] += 1
        for c, f in alvos.items():
            self._canais["por_circuito"][c] += f
        S, passo, teto = self._escala, self.cl.passo, self.cl.teto
        if len(registro["candidatos"]) > 1:
            a = registro["acao"]
            for c in CIRCUITOS:
                f = alvos[c]
                if f == 0:
                    continue
                comp = "apetitivo" if f > 0 else "aversivo"
                delta = div_arred(passo * abs(f), S)
                if delta == 0:
                    continue
                w = self._sinapses[c][comp][a]
                for k in registro["ativas"][c]:
                    novo = w[k] + delta
                    if novo > teto:
                        novo = teto
                        self._cortes_teto += 1
                    w[k] = novo
        sub = registro.get("fruta")
        if sub is not None and len(sub["candidatos"]) > 1 and alvos["fruta"] != 0:
            f = alvos["fruta"]
            comp = "apetitivo" if f > 0 else "aversivo"
            delta = div_arred(passo * abs(f), S)
            w = self._sinapses_fruta[comp]
            for k in sub["ativas"]:
                novo = w[k] + delta
                if novo > teto:
                    novo = teto
                    self._cortes_teto += 1
                w[k] = novo
        self._n_atualizacoes += 1

    # ------------------------------------------------------------- serializacao

    def estado_interno(self) -> dict:
        def registro_dict(r):
            if r is None:
                return None
            d = {"regra": r["regra"], "candidatos": [a.value for a in r["candidatos"]], "acao": r["acao"].value,
                 "ativas": {c: list(v) for c, v in r["ativas"].items()}}
            if "fruta" in r:
                d["fruta"] = {"candidatos": list(r["fruta"]["candidatos"]), "acao": r["fruta"]["acao"],
                              "ativas": list(r["fruta"]["ativas"])}
            return d
        d = {
            "nome": self.nome,
            "parametros_aprendidos": self.n_pesos(),
            "aprendizado_ligado": self._aprende,
            "escala": self._escala,
            "entradas": list(self.entradas),
            "celulas": {c: list(v) for c, v in self._celulas.items()},
            "celulas_fruta": list(CELULAS_FRUTA),
            "sinapses": {c: {comp: {a.value: list(w) for a, w in por_acao.items()} for comp, por_acao in d2.items()}
                         for c, d2 in self._sinapses.items()},
            "sinapses_fruta": {comp: list(w) for comp, w in self._sinapses_fruta.items()},
            "n_decisoes": len(self.motivos),
            "motivos": [dict(m) for m in self.motivos],
            "aprendizado": {
                "passo": self.cl.passo, "teto": self.cl.teto, "piso_peso": self.cl.piso_peso, "w0_info": self.cl.w0_info,
                "n_atualizacoes": self._n_atualizacoes, "cortes_teto": self._cortes_teto, "recompensas": dict(self._n_recompensas),
                "desvio_maximo": self.desvio_maximo(), "pesos_no_teto": self.pesos_no_teto(),
                "tick_ultimo_cuidado": self._tick_ultimo_cuidado, "tick_ultima_decisao": self._tick_ultima_decisao,
                "pendentes": [[t, registro_dict(r)] for t, r in self._pendentes],
                "ultima": registro_dict(self._ultima),
                "canais": {"creditos": self._canais["creditos"], "por_canal": dict(self._canais["por_canal"]),
                           "por_circuito": dict(self._canais["por_circuito"])},
            },
        }
        if self._consequencia_pendente is not None:
            d["aprendizado"]["consequencia_pendente"] = registro_dict(self._consequencia_pendente[0])
        return d


def fabrica_cerebro_c(cfg_c: ConfigCerebroC | None = None, cfg_bola: ConfigBola | None = None,
                      cfg_frutas: ConfigFrutas | None = None):
    """A fabrica para a bancada (o chat D liga): `lambda cfg=None: PoliticaCerebroC(cfg, cfg_c, cfg_bola, cfg_frutas)`."""
    return lambda cfg=None: PoliticaCerebroC(cfg, cfg_c, cfg_bola, cfg_frutas)
