"""V2, BANCADA (docs/TAREFA_V2_BANCADA.md): um orquestrador unico para os bracos da pergunta maior.

    python experiments/bancada_v2.py --config experiments/configs/bancada/fumaca.json --saida <pasta>   # fumaca, NAO canonica

A pergunta maior (docs/ARQUITETURA_V2_VALIDACAO.md, secao 6) compara fontes de plasticidade no MESMO aprendiz (validacao
V1 do docs/ROADMAP_V2.md: a L1 separa de onde vem o sinal da regra de atualizacao). A bancada fixa isso em codigo:

  vida = (genoma, mundo, dono, braco, semente)
    genoma   None = sem genoma (MotorComFeedback, como a L1); um inteiro g = temperamento sorteado de g no
             MotorPersonalidade (a semente do genoma separada da do ambiente, como no E1 da linhagem).
    mundo    so "padrao" existe; os outros (casado, descasado, mutavel) chegam com as frutas (N4) e a rodada 4.
    dono     um dono sintetico; a rng do dono deriva de (semente, nome do dono), igual em todos os bracos e mundos.
    braco    P0..P3: o MESMO cerebro (PoliticaLobos, mesmo prior, mesma ConfigLobos); so a FONTE do sinal muda.
    semente  a do motor: rng de ambiente = semente, rng de politica = semente + 1_000_003 (engine.py, intocado).

  fontes (o campo `fonte` do braco):
    nenhuma       P0   so a predisposicao herdada: o aprendiz com o aprendizado DESLIGADO (o prior fixo). Nada do dono chega
                       a ele. Entregar "sinal nenhum" a um aprendiz ligado nao e P0: o credito do chamado expira por dentro
                       (Aprendiz._expirar) e vira sinal negativo do dono ausente.
    consequencia  P1   chega no N3 (NotImplementedError ate la).
    informacao    P2   (certa) e P2e (errada): chegam no N5 (NotImplementedError ate la).
    dono          P3   o feedback explicito (COACH): toda acao do dono chega ao aprendiz pelo gancho receber_acao_dono,
                       exatamente como na L1 (a vida e byte a byte a da L1: teste).

  modo acoplado (malha aberta; generaliza log_so_cuidado/vidas_acopladas de run_v2_l1.py): o registro de eventos de uma vida,
  com um filtro (nenhum, sem_sinais, sem_sinais_sem_carinho), e rejogado com o cerebro de outro braco. O motor acoplado guarda
  o log filtrado: o registro dele e o da origem com os eventos retirados, evento a evento.

  medidas (todas de digilab/metrics.py; nenhuma conta aqui): desempenho no proprio ambiente (tempo fora de privacao e saude
  media, amostrados em cada decisao; acerto na tarefa do dono, `acerto_na_tarefa`), custo da plasticidade (deriva ao prior
  por dia e tempo ate a metade do caminho, `custo_da_plasticidade`) e a tabela braco x condicao (`tabela_braco_condicao`).

Toda vida e rejogada do disco e comparada bit a bit (G1): divergencia levanta erro e para tudo. engine.py e lobos.py nao
mudam. Sementes: so as dos testes (101...505) sem plano; qualquer outra exige o plano de analise registrado (campo "plano").
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_DONOS, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO, TICKS_POR_DIA, ConfigLobos  # noqa: E402
from digilab.donos import criar_dono, julgar_acao  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.evolucao import politica_no_tick  # noqa: E402
from digilab.metrics import (acerto_na_tarefa, custo_da_plasticidade, desempenho_no_ambiente,  # noqa: E402
                             distribuicoes_de_acao, estados_sonda, jsd_media, tabela_braco_condicao)
from digilab.obediencia import MotorPersonalidade  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.temperamento import sortear as sortear_temperamento  # noqa: E402
from digilab.treino import MotorComFeedback, reproduzir_com_feedback, simular_vida  # noqa: E402

ACOES = tuple(a.value for a in AcaoPet)
SINAIS = frozenset({AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value})
SEMENTES_TESTE = frozenset({101, 202, 303, 404, 505})
MUNDOS = ("padrao",)
CEREBROS = ("lobos",)
FILTROS = {"nenhum": frozenset(), "sem_sinais": SINAIS,
           "sem_sinais_sem_carinho": SINAIS | {AcaoUsuario.ACARICIAR.value}}
MEDIDAS_TABELA = ("fracao_fora_de_privacao", "saude_media", "acerto_total", "deriva_final")
CHAVES_CONFIG = {"descricao", "plano", "bracos", "donos", "sementes", "genomas", "mundos", "dias", "orcamento", "sonda",
                 "bootstrap", "acoplados"}


class ReplayDivergiu(RuntimeError):
    pass


class SementeSemPlano(RuntimeError):
    pass


# ------------------------------------------------------------------ bracos e fonte do sinal


@dataclass(frozen=True)
class Braco:
    rotulo: str
    fonte: str                       # nenhuma | consequencia | informacao | dono
    no: str                          # o no do roadmap que liga a fonte
    informacao: str | None = None    # P2: "certa"; P2e: "errada"


BRACOS = {
    "P0": Braco("P0", "nenhuma", "N0"),
    "P1": Braco("P1", "consequencia", "N3"),
    "P2": Braco("P2", "informacao", "N5", "certa"),
    "P2e": Braco("P2e", "informacao", "N5", "errada"),
    "P3": Braco("P3", "dono", "N1"),
}
FONTES_IMPLEMENTADAS = ("nenhuma", "dono")


def braco_de(rotulo: str) -> Braco:
    if rotulo not in BRACOS:
        raise KeyError(f"braco desconhecido {rotulo!r}: {sorted(BRACOS)}")
    b = BRACOS[rotulo]
    if b.fonte not in FONTES_IMPLEMENTADAS:
        raise NotImplementedError(f"braco {b.rotulo}: a fonte {b.fonte!r} chega no {b.no} (docs/ROADMAP_V2.md)")
    return b


class PoliticaDoBraco:
    """O cerebro do braco com a fonte do sinal na frente dele. Decide, observa e serializa pelo cerebro; o que muda entre os
    bracos e so o que passa por `receber_acao_dono`: na fonte "dono" tudo, na "nenhuma" nada. Nao consome rng nem muda a
    ordem de nada: a vida do P3 e byte a byte a da L1 e a do P0 a do instinto (testes)."""

    def __init__(self, cerebro, braco: Braco) -> None:
        self.cerebro = cerebro
        self.braco = braco
        self.nome = cerebro.nome
        self.sinais_entregues = 0        # elogios e broncas que chegaram ao aprendiz (a eficiencia amostral conta estes)

    def agir(self, obs, rng):
        return self.cerebro.agir(obs, rng)

    def observar(self, transicao) -> None:
        self.cerebro.observar(transicao)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        if self.braco.fonte == "dono":
            self.sinais_entregues += acao.value in SINAIS
            self.cerebro.receber_acao_dono(acao, tick)
        elif self.braco.fonte != "nenhuma":          # pragma: no cover - braco_de ja barra
            raise NotImplementedError(self.braco.fonte)

    def estado_interno(self) -> dict:
        return {**self.cerebro.estado_interno(), "bancada": {"braco": self.braco.rotulo, "fonte": self.braco.fonte}}

    def __getattr__(self, nome):
        cerebro = self.__dict__.get("cerebro")
        if cerebro is None:
            raise AttributeError(nome)
        return getattr(cerebro, nome)


# ------------------------------------------------------------------ a vida


@dataclass(frozen=True)
class EspecVida:
    dono: str
    braco: str
    semente: int
    genoma: int | None = None
    mundo: str = "padrao"
    cerebro: str = "lobos"

    @property
    def nome(self) -> str:
        m = "" if self.mundo == "padrao" else f"~{self.mundo}"
        g = "" if self.genoma is None else f"~g{self.genoma}"
        return f"{self.dono}-{self.braco}{m}{g}@{self.semente}"

    @property
    def celula(self) -> tuple:
        """O que define o par de vidas que se comparam entre bracos: tudo menos o braco."""
        return (self.dono, self.semente, self.genoma, self.mundo)


@dataclass
class VidaBancada:
    espec: EspecVida
    motor: MotorComFeedback
    interacoes: int
    origem: str | None = None        # so no modo acoplado: o nome da vida de origem, o braco dela e o filtro
    origem_braco: str | None = None
    filtro: str | None = None

    @property
    def rotulo_braco(self) -> str:
        """O braco na tabela: "P3", ou "P0<P3:sem_sinais" para o P0 acoplado ao registro do P3 sem os sinais."""
        if self.origem is None:
            return self.espec.braco
        return f"{self.espec.braco}<{self.origem_braco}:{self.filtro}"

    @property
    def nome(self) -> str:
        if self.origem is None:
            return self.espec.nome
        e = self.espec
        return replace(e, braco=f"{e.braco}~de-{self.origem_braco}-{self.filtro}").nome


def filtrar_log(log: LogDeEventos, retirar: frozenset) -> LogDeEventos:
    """O mesmo log sem as acoes do dono em `retirar` (valores de AcaoUsuario); avancos e as outras acoes nos mesmos ticks."""
    return LogDeEventos([e for e in log if not (e.tipo == "acao_usuario" and str(e.valor) in retirar)])


def resumo_motor(motor) -> tuple:
    """Tudo que uma vida produz: log, estado final, acoes do pet, as rngs e, no motor de personalidade, obediencia, recusas,
    desejos e vinculo."""
    extra = ()
    if isinstance(motor, MotorPersonalidade):
        extra = (motor._rng_obediencia.getstate(), [r.para_dict() for r in motor.recusas],
                 [d.para_dict() for d in motor.desejos], motor.vinculo.para_dict())
    return (motor.log.para_jsonl(), motor.estado(), motor.acoes_recentes(10**9), motor._rng_politica.getstate(),
            motor._rng_ambiente.getstate(), *extra)


def _interno(motor) -> str:
    return json.dumps(motor.politica.estado_interno(), sort_keys=True)


@dataclass(frozen=True)
class Bancada:
    dias: int
    orcamento: int
    cfg_lobos: ConfigLobos = CONFIG_LOBOS_APRENDIZ    # o aprendiz de todos os bracos (o P0 o usa com o aprendizado desligado)

    def __post_init__(self) -> None:
        if self.dias <= 0 or self.orcamento <= 0:
            raise ValueError("dias e orcamento precisam ser positivos")
        if not self.cfg_lobos.aprendizado_ligado:
            raise ValueError("cfg_lobos e a do aprendiz (aprendizado ligado); o P0 desliga por conta propria")

    # ------------------------------------------------------------- fabricas

    def politica(self, espec: EspecVida, cfg=None) -> PoliticaDoBraco:
        if espec.cerebro not in CEREBROS:
            raise KeyError(f"cerebro {espec.cerebro!r}: so {CEREBROS} (outros cerebros sao a comparacao do N11)")
        b = braco_de(espec.braco)
        cl = self.cfg_lobos if b.fonte != "nenhuma" else replace(self.cfg_lobos, aprendizado_ligado=False)
        return PoliticaDoBraco(PoliticaLobos(cfg, cl), b)

    def fabrica_politica(self, espec: EspecVida):
        return lambda cfg=None: self.politica(espec, cfg)

    @staticmethod
    def fabrica_motor(espec: EspecVida):
        if espec.mundo not in MUNDOS:
            raise NotImplementedError(f"mundo {espec.mundo!r}: so {MUNDOS}; casado, descasado e mutavel chegam com o N4 "
                                      "(frutas) e a rodada 4")
        if espec.genoma is None:
            return lambda politica, cfg, semente: MotorComFeedback(politica=politica, cfg=cfg, semente=semente)
        temperamento = sortear_temperamento(espec.genoma)
        return lambda politica, cfg, semente: MotorPersonalidade(politica, cfg, semente, temperamento)

    # ------------------------------------------------------------- vidas

    def vida(self, espec: EspecVida) -> VidaBancada:
        fm = self.fabrica_motor(espec)
        v = simular_vida(f"{espec.dono}-{espec.braco}", criar_dono(espec.dono), self.politica(espec, CONFIG_PADRAO),
                         espec.semente, self.dias, self.orcamento, rotulo_dono=espec.dono, fabrica_motor=fm)
        if v.interacoes != self.orcamento:
            raise RuntimeError(f"{espec.nome}: {v.interacoes} interacoes, orcamento {self.orcamento}")
        vida = VidaBancada(espec, v.motor, v.interacoes)
        self.conferir_replay(vida)
        return vida

    def rejogar(self, log: LogDeEventos, espec: EspecVida):
        return reproduzir_com_feedback(log, self.fabrica_politica(espec), semente=espec.semente,
                                       fabrica_motor=self.fabrica_motor(espec))

    def acoplar(self, origem: VidaBancada, braco: str, filtro: str) -> VidaBancada:
        """Modo acoplado (malha aberta): o registro da vida de origem, sem as acoes do filtro, rejogado com o cerebro de outro
        braco (ou do mesmo). Os eventos sao os da origem nos mesmos ticks; so o cerebro (e o que ele faz deles) muda."""
        if filtro not in FILTROS:
            raise KeyError(f"filtro desconhecido {filtro!r}: {sorted(FILTROS)}")
        if origem.origem is not None:
            raise ValueError("acoplar uma vida ja acoplada nao e suportado: acople a partir da vida de origem")
        log = filtrar_log(origem.motor.log, FILTROS[filtro])
        espec = replace(origem.espec, braco=braco)
        m = self.rejogar(log, espec)
        vida = VidaBancada(espec, m, sum(1 for e in log if e.tipo == "acao_usuario"), origem=origem.nome,
                           origem_braco=origem.espec.braco, filtro=filtro)
        self.conferir_replay(vida)
        return vida

    def conferir_replay(self, vida: VidaBancada, texto_log: str | None = None) -> None:
        """G1: rejoga a vida a partir do log serializado (do disco, se vier o texto) e compara tudo bit a bit."""
        texto = vida.motor.log.para_jsonl() if texto_log is None else texto_log
        if texto != vida.motor.log.para_jsonl():
            raise ReplayDivergiu(f"{vida.nome}: o log do disco nao e o da vida")
        r = self.rejogar(LogDeEventos.de_jsonl(texto), vida.espec)
        if resumo_motor(r) != resumo_motor(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: log, estado, acoes ou rngs divergem no replay")
        if _interno(r) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: estado interno da politica diverge no replay")

    # ------------------------------------------------------------- medidas

    def medir(self, vida: VidaBancada, sonda: dict, piso: float | None = None) -> dict:
        """Desempenho no ambiente, acerto na tarefa e custo da plasticidade de uma vida. `piso` = acerto total do P0 na mesma
        celula (o prior herdado); sem ele, o da propria vida. O replay de medicao e conferido bit a bit contra a vida."""
        regs = []

        def fab(cfg=None):
            reg = _Registro(self.politica(vida.espec, cfg))
            regs.append(reg)
            return reg

        m = reproduzir_com_feedback(LogDeEventos.de_jsonl(vida.motor.log.para_jsonl()), fab, semente=vida.espec.semente,
                                    fabrica_motor=self.fabrica_motor(vida.espec))
        if resumo_motor(m) != resumo_motor(vida.motor) or _interno(m) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: o replay de medicao mudou a vida")
        reg = regs[0]
        desempenho = desempenho_no_ambiente(reg.amostras)
        tarefa = acerto_na_tarefa(reg.decisoes, _julgar, ACOES, TICKS_POR_DIA)
        sinais = []
        for d in tarefa["dias"]:
            ate = [s for (t, _, _), s in zip(reg.decisoes, reg.sinais_na_decisao) if t < (d + 1) * TICKS_POR_DIA]
            sinais.append(ate[-1] if ate else 0)
        deriva = self.deriva(vida, sonda)
        custo = custo_da_plasticidade(deriva, tarefa["acerto"], sinais,
                                      tarefa["acerto_total"] if piso is None else piso)
        return {"vida": vida.nome, "braco": vida.rotulo_braco, "fonte": braco_de(vida.espec.braco).fonte,
                "dono": vida.espec.dono, "semente": vida.espec.semente, "genoma": vida.espec.genoma,
                "mundo": vida.espec.mundo, "origem": vida.origem, "filtro": vida.filtro, "interacoes": vida.interacoes,
                **desempenho, "acerto_total": tarefa["acerto_total"], "acerto_por_dia": tarefa["acerto"],
                "teto_total": tarefa["teto_total"], "sinais_total": reg.sinais, "sinais_do_dono": reg.sinais_do_dono,
                "sinais_acumulados": sinais,
                "deriva_final": custo["deriva_final"], "custo_da_plasticidade": custo}

    def deriva(self, vida: VidaBancada, sonda: dict) -> list[float]:
        """JSD (bits) entre a politica no fim de cada dia e a do prior herdado (o P0 da mesma vida), nas mesmas sondas."""
        estados = estados_sonda(sonda["estados"], sonda["semente"])
        prior = self.politica(replace(vida.espec, braco="P0"), CONFIG_PADRAO)
        d_prior = distribuicoes_de_acao(prior, estados, sonda["amostras"], sonda["semente"])
        fab, fm = self.fabrica_politica(vida.espec), self.fabrica_motor(vida.espec)
        log = vida.motor.log
        serie = []
        for d in range(1, self.dias + 1):
            pol = politica_no_tick(log, fab, vida.espec.semente, d * TICKS_POR_DIA, fm)
            serie.append(jsd_media(distribuicoes_de_acao(pol, estados, sonda["amostras"], sonda["semente"]), d_prior))
        return serie


class _Registro:
    """Embrulha a politica do braco no replay de medicao: anota cada decisao (tick, estado como o dono o julga, acao), a
    amostra de estado (em privacao, saude), os sinais do dono que chegaram ao aprendiz ate ali e os que o dono deu. So le;
    repassa tudo."""

    def __init__(self, interna: PoliticaDoBraco) -> None:
        self.interna = interna
        self.nome = interna.nome
        self._tick_ultimo_cuidado = 0
        self.decisoes: list[tuple[int, dict, str]] = []
        self.amostras: list[tuple[bool, float]] = []
        self.sinais_na_decisao: list[int] = []
        self.sinais_do_dono = 0

    @property
    def sinais(self) -> int:
        return self.interna.sinais_entregues

    def agir(self, obs, rng):
        acao = self.interna.agir(obs, rng)
        v = obs.vetor_estado
        estado = {"fome": v[0], "higiene": v[1], "energia": v[2], "tick_do_dia": int(round(v[7] * TICKS_POR_DIA))}
        self.decisoes.append((obs.ticks_desde_cuidado + self._tick_ultimo_cuidado, estado, acao.value))
        self.amostras.append((Estado(fome=v[0], higiene=v[1], energia=v[2]).em_privacao(CONFIG_PADRAO), v[4]))
        self.sinais_na_decisao.append(self.interna.sinais_entregues)
        return acao

    def observar(self, transicao) -> None:
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao, tick) -> None:
        self._tick_ultimo_cuidado = tick          # toda acao do dono zera o relogio de cuidado (state.aplicar_acao_usuario)
        self.sinais_do_dono += acao.value in SINAIS
        self.interna.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _julgar(estado: dict, acao: str) -> int:
    return julgar_acao({**estado, "acao_atual": acao}, CONFIG_DONOS)


# ------------------------------------------------------------------ orquestrador


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def validar_config(cfg: dict) -> dict:
    faltam = {"bracos", "donos", "sementes", "dias", "orcamento", "sonda", "bootstrap"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    for b in cfg["bracos"]:
        braco_de(b)
    for a in cfg.get("acoplados", []):
        if set(a) != {"origem", "destino", "filtro"} or a["filtro"] not in FILTROS:
            raise ValueError(f"acoplado fora do formato: {a}")
        braco_de(a["destino"])
        if a["origem"] not in cfg["bracos"]:
            raise ValueError(f"acoplado de um braco que nao roda: {a['origem']}")
    genomas = [g for g in cfg.get("genomas", [None]) if g is not None]
    fora = sorted((set(cfg["sementes"]) | set(genomas)) - SEMENTES_TESTE)
    if fora:
        plano = cfg.get("plano")
        if not plano or not (RAIZ / plano).is_file():
            raise SementeSemPlano(f"sementes {fora} fora das dos testes {sorted(SEMENTES_TESTE)}: precisa do plano de analise "
                                  "registrado (campo 'plano', arquivo no repositorio)")
    return cfg


def rodar(cfg: dict, pasta: Path) -> dict:
    """Vidas de todos os bracos x donos x sementes (x genomas x mundos), gravadas e rejogadas do disco; os acoplados; as
    medidas por vida e as tabelas braco x condicao por dono e medida."""
    validar_config(cfg)
    bancada = Bancada(int(cfg["dias"]), int(cfg["orcamento"]))
    dir_vidas = pasta / "vidas"
    vidas: dict[str, VidaBancada] = {}

    def guardar(v: VidaBancada) -> None:
        _gravar(dir_vidas / f"{v.nome}.jsonl", v.motor.log.para_jsonl())
        _gravar(dir_vidas / f"{v.nome}.politica.json", _interno(v.motor))
        bancada.conferir_replay(v, (dir_vidas / f"{v.nome}.jsonl").read_text(encoding="utf-8"))
        vidas[v.nome] = v

    for g, mundo, dono, braco, s in product(cfg.get("genomas", [None]), cfg.get("mundos", ["padrao"]), cfg["donos"],
                                            cfg["bracos"], cfg["sementes"]):
        guardar(bancada.vida(EspecVida(dono, braco, int(s), g, mundo)))
    origens = list(vidas.values())
    for a in cfg.get("acoplados", []):
        for v in origens:
            if v.espec.braco == a["origem"]:
                guardar(bancada.acoplar(v, a["destino"], a["filtro"]))
    # o piso do tempo ate aprender e o acerto do P0 na mesma celula (o prior herdado); sem P0 na config, o da propria vida
    medidas, piso = {}, {}
    for nome, v in sorted(vidas.items()):
        if v.espec.braco == "P0" and v.origem is None:
            medidas[nome] = bancada.medir(v, cfg["sonda"])
            piso[v.espec.celula] = medidas[nome]["acerto_total"]
    for nome, v in sorted(vidas.items()):
        if nome not in medidas:
            medidas[nome] = bancada.medir(v, cfg["sonda"], piso.get(v.espec.celula))
    tabelas = tabelas_braco_condicao(medidas, cfg["bootstrap"])
    _gravar(pasta / "medidas.json", _dump(medidas))
    _gravar(pasta / "tabelas.json", _dump(tabelas))
    _gravar(pasta / "meta.json", _dump(meta(cfg)))
    return {"vidas": vidas, "medidas": medidas, "tabelas": tabelas}


def tabelas_braco_condicao(medidas: dict, boot: dict) -> dict:
    """Por dono e medida: tabela braco x condicao (mundo), unidade = vida (semente x genoma)."""
    out = {}
    for dono in sorted({m["dono"] for m in medidas.values()}):
        out[dono] = {}
        for medida in MEDIDAS_TABELA:
            valores: dict[tuple[str, str], list[float]] = {}
            for m in medidas.values():
                if m["dono"] == dono:
                    valores.setdefault((m["braco"], m["mundo"]), []).append(m[medida])
            out[dono][medida] = tabela_braco_condicao(valores, boot["reamostragens"], boot["semente"], boot["nivel"])
    return out


def meta(cfg: dict) -> dict:
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py mudou")
    return {"config": cfg, "python": platform.python_version(), "plataforma": platform.platform(),
            "engine_sha256": sha256_engine(), "lobos_sha256": _sha(RAIZ / "digilab" / "policies" / "lobos.py"),
            "config_sha256": _sha(RAIZ / "digilab" / "config.py"), "bancada_sha256": _sha(Path(__file__)),
            "metrics_sha256": _sha(RAIZ / "digilab" / "metrics.py")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="bancada da V2: bracos P0-P3 sobre o mesmo aprendiz (docs/TAREFA_V2_BANCADA.md)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True, help="pasta de saida (vidas/, medidas.json, tabelas.json, meta.json)")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    r = rodar(cfg, Path(a.saida))
    print(f"{len(r['vidas'])} vidas rejogadas do disco bit a bit; medidas e tabelas em {a.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
