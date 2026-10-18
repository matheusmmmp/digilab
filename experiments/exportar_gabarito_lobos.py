"""Gabarito do cerebro A para o jogo web, pets v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 1; o G-PAR-L0 e o G-PAR-L1 das etapas 2
e 3).

O v11 e o da secao 3 da tarefa (PW-1, DECIDIDO 2026-10-17): os lobos com o aprendizado ligado, o sinal pela consequencia no corpo e os
gestos do dono (carinho e tapa), no mundo `padrao`, sem elogio nem bronca, sem mundo fisico, frutas, dois pets e planejamento. O ponto
(PW-2, DECIDIDO: o worker propoe pela calibracao) e o da calibracao do corpo, SEM numero novo e SEM validacao (secao "Ponto" abaixo).

Tres secoes:
  l0      o nucleo sem aprender e sem corpo: o cerebro tem de ser o instinto, decisao a decisao (G2 da L0); o TS confere contra o
          instinto dele e contra este traco;
  v11     as vidas do pet v11 inteiras: o log, os motivos de cada decisao (o que o painel DigiBrain mostra), os pesos, os pesos do corpo,
          o resumo do aprendizado, a memoria e emocao e os canais no fim, e o sha256 do estado interno. E os `ganchos` (etapa 3, o
          G-PAR-L1): cada chamada que o motor fez ao cerebro, na ordem, com o que ela levou (a observacao, os receptores do corpo, a acao
          do dono e o tick), gravadas num replay do log com a politica embrulhada (`_Gravador`, que so grava) e conferidas contra a
          vida. O TS rejoga os ganchos no cerebro dele: o corpo do v11 tem o metabolismo, que o corpo.ts ainda nao tem.
  vontade a vontade do v11 (PW-3; `desejo.desejo_lobos`, `PoliticaLobos.desvio_aprendido`): em cada vida da secao v11, o desejo e o
          desvio aprendido de cada acao do tempo livre em toda decisao, antes de o cerebro decidir (pelo replay do log, com um espiao que so
          le), e uma grade de observacoes sinteticas (as sondas do carater da web, com os receptores do corpo) contra o cerebro do fim da
          vida. As secoes l0 e v11 nao mudam com ela.
E `config_v11`: as configs que as vidas do v11 usaram de fato (a ConfigLobos do braco, a ConfigConsequencia e a ConfigCorpo do regime
`corpo`, com os drives novos, os gestos e o metabolismo); a `config` e a da bancada, de onde elas saem.

    python experiments/exportar_gabarito_lobos.py      # grava web/app/test/gabaritos/lobos_python.json e lobos_laco_python.json

O segundo arquivo (etapa 4, o gate do laco) traz, por vida do v11, o estado do motor no fim (`motor.estado()`: o tick, os drives, a
sujeira, o sono, os cuidados, a acao atual e o corpo com a quimica, a digestao, o estagio, a janela do tedio e o metabolismo) e as acoes
do pet com o tick. O TS roda o log pelo laco do corpo dele e confere os ganchos (os do primeiro arquivo) e este fim. Fica num arquivo
proprio para nao mexer no primeiro, que outras frentes estendem.

Ponto (PW-2), todos PROPOSTOS, nenhum validado (docs/RESULTADO_V2_CALIBRACAO_CORPO.md; docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md):
  - o aprendiz T3 (passo 512, teto 16 S, piso S/16), a montagem `completa` (canais ligados) e o ganho 4 da consequencia: os da config da
    calibracao do corpo (experiments/configs/v2_corpo/calibracao_adendo5.json); o ganho 4 nao fechou na calibracao conjunta;
  - o corpo: o gasto 4/5 (basal 300/150; o unico numero do corpo que fechou, adendo 5) e o ponto (m_sobe, m_reduz) = (2, 1) do adendo 4
    (nao fechou, e foi medido com o gasto em 1/2); o w_novos 2 (fechou, tambem com o gasto em 1/2).
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import random
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_calibracao_corpo as cal  # noqa: E402

from digilab.config import CONFIG_DESEJO, CONFIG_PADRAO, ConfigLobos  # noqa: E402
from digilab.desejo import desejo_lobos  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.metrics import estados_sonda  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.treino import reproduzir_com_feedback, simular_vida  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "lobos_python.json"
ARQUIVO_LACO = RAIZ / "web" / "app" / "test" / "gabaritos" / "lobos_laco_python.json"
CONFIG_CALIBRACAO = RAIZ / "experiments" / "configs" / "v2_corpo" / "calibracao_adendo5.json"
DIAS = 3
ORCAMENTO = 16 * DIAS
BRACO_V11 = "P1-c-tapa"
PONTO_CORPO = (2.0, 1.0)                 # (m_sobe, m_reduz) do adendo 4
W_NOVOS = 2                              # o w_novos do adendo 4
VIDAS_L0 = (("atencioso", 101), ("aleatorio", 202))
VIDAS_V11 = (("atencioso", 101), ("relapso", 202), ("aleatorio", 303), ("incoerente", 404))
# os receptores da PercepcaoCorpo do v11, na ordem dos ganchos: os de hoje e os novos do regime `corpo` sem o mundo fisico (sem a
# curiosidade, o banheiro, os orgaos e o paladar); um receptor a mais ou a menos falha alto
RECEPTORES_V11 = ("fome", "higiene", "energia", "humor", "saude", "tedio", "solidao", "estresse", "dor", "susto")


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def config_v11(dias: int = DIAS, orcamento: int = ORCAMENTO) -> dict:
    """A config da bancada do v11: a da calibracao do corpo, no mundo `padrao`, so com o braco do v11, nas sementes dos testes."""
    cfg = json.loads(CONFIG_CALIBRACAO.read_text(encoding="utf-8"))
    cfg = {**cfg, "dias": dias, "orcamento": orcamento, "unidades": {"bases": sorted(bv.SEMENTES_TESTE), "k": 1, "prefixo": "corpo"}}
    cfg.pop("plano")
    return cal.config_bancada(cfg, cal.corpo_do_ponto(cfg, *PONTO_CORPO), [BRACO_V11], ["padrao"])


def bancada_v11(dias: int = DIAS, orcamento: int = ORCAMENTO) -> bv.Bancada:
    b = bv.bancada_da_config(config_v11(dias, orcamento))
    cc = b.cfg_consequencia
    return replace(b, cfg_consequencia=replace(cc, pesos_drives_corpo=cal.pesos_com_novos(cc.pesos_drives_corpo, W_NOVOS)))


def configs_da_vida_v11(b: bv.Bancada) -> dict:
    """As configs que as vidas do v11 usaram (as mesmas nas quatro: o braco e o regime nao dependem do dono nem da semente)."""
    espec = bv.EspecVida(VIDAS_V11[0][0], BRACO_V11, VIDAS_V11[0][1])
    p = b.politica(espec, CONFIG_PADRAO)
    return {"lobos": p.cerebro.cl.__dict__, "consequencia": p.cfg_consequencia.__dict__, "corpo": b.cfg_corpo_de(espec).__dict__,
            "receptores": list(RECEPTORES_V11)}


def _log(motor) -> list:
    return [json.loads(linha) for linha in motor.log.para_jsonl().splitlines() if linha.strip()]


def vida_l0(dono: str, semente: int) -> dict:
    politica = PoliticaLobos(CONFIG_PADRAO, ConfigLobos())
    motor = simular_vida(f"{dono}-L0", criar_dono(dono), politica, semente, DIAS, ORCAMENTO, rotulo_dono=dono).motor
    interno = politica.estado_interno()
    return {"dono": dono, "semente": semente, "log": _log(motor), "motivos": interno["motivos"],
            "sha_interno": _sha(json.dumps(interno, sort_keys=True))}


def _corpo(pc) -> list[int]:
    """os receptores da PercepcaoCorpo na ordem de RECEPTORES_V11; um campo fora dela preenchido, ou um dela vazio, falha alto"""
    d = dataclasses.asdict(pc)
    fora = sorted(k for k, v in d.items() if v is not None and k not in RECEPTORES_V11)
    faltam = [k for k in RECEPTORES_V11 if d[k] is None]
    if fora or faltam:
        raise RuntimeError(f"PercepcaoCorpo fora do v11: a mais {fora}, faltando {faltam}")
    return [d[k] for k in RECEPTORES_V11]


def _obs(obs) -> list:
    """[Estado.vetor, ticks_desde_cuidado, receptores]"""
    return [list(obs.vetor_estado), obs.ticks_desde_cuidado, _corpo(obs.corpo)]


class _Gravador:
    """Embrulha a politica do braco e grava, na ordem, cada chamada do motor ao cerebro e o que ela levou; nao muda nada (a vida
    rejogada com ele e conferida contra a original). Os ganchos:
      ["agir", v, tdc, corpo]                                  a decisao (o u esta no motivo)
      ["observar", acao, v, tdc, corpo, v', tdc', corpo']      a transicao da decisao (o braco calcula o f_S e o repassa)
      ["consequencia_corpo", acao, ocorrido, v, tdc, corpo]    o gancho do corpo, depois dos estimulos da propria acao
      ["dono", acao, tick]                                     receber_acao_dono (no MotorCorpo com gestos: o cuidado e o tapa)
      ["carinho", v, tdc, corpo, v', tdc', corpo']             mudanca_no_corpo (antes e depois do carinho)"""

    def __init__(self, politica) -> None:
        self.politica = politica
        self.ganchos: list = []

    def agir(self, obs, rng):
        self.ganchos.append(["agir", *_obs(obs)])
        return self.politica.agir(obs, rng)

    def observar(self, transicao) -> None:
        self.ganchos.append(["observar", transicao.acao.value, *_obs(transicao.observacao), *_obs(transicao.observacao_seguinte)])
        self.politica.observar(transicao)

    def consequencia_corpo(self, acao, ocorrido: dict, obs_depois) -> None:
        if set(ocorrido) != {"acao", "estimulos"}:
            raise RuntimeError(f"ocorrido do corpo fora do v11: {sorted(ocorrido)}")
        o = {"acao": ocorrido["acao"], "estimulos": [list(e) for e in ocorrido["estimulos"]]}
        self.ganchos.append(["consequencia_corpo", acao.value, o, *_obs(obs_depois)])
        self.politica.consequencia_corpo(acao, ocorrido, obs_depois)

    def receber_acao_dono(self, acao, tick: int) -> None:
        self.ganchos.append(["dono", acao.value, tick])
        self.politica.receber_acao_dono(acao, tick)

    def mudanca_no_corpo(self, obs_antes, obs_depois) -> None:
        self.ganchos.append(["carinho", *_obs(obs_antes), *_obs(obs_depois)])
        self.politica.mudanca_no_corpo(obs_antes, obs_depois)

    def estado_interno(self) -> dict:
        return self.politica.estado_interno()

    def __getattr__(self, nome):
        politica = self.__dict__.get("politica")
        if politica is None:
            raise AttributeError(nome)
        return getattr(politica, nome)


def ganchos_v11(b: bv.Bancada, espec: bv.EspecVida, motor) -> list:
    """Rejoga o log da vida com a politica embrulhada pelo _Gravador e devolve os ganchos; o estado interno do replay tem de ser o
    da vida (falha alto)."""
    gravadores: list[_Gravador] = []

    def fabrica(cfg=None):
        gravadores.append(_Gravador(b.politica(espec, cfg)))
        return gravadores[-1]
    r = reproduzir_com_feedback(LogDeEventos.de_jsonl(motor.log.para_jsonl()), fabrica, semente=espec.semente,
                                fabrica_motor=b.fabrica_motor(espec))
    if len(gravadores) != 1 or r.politica is not gravadores[0]:
        raise RuntimeError("o replay dos ganchos nao usou o gravador")
    if r.politica.estado_interno() != motor.politica.estado_interno():
        raise RuntimeError(f"{espec.nome}: o replay com o gravador diverge da vida")
    return gravadores[0].ganchos


def vida_v11(b: bv.Bancada, dono: str, semente: int) -> dict:
    espec = bv.EspecVida(dono, BRACO_V11, semente)
    v = b.vida(espec)
    interno = v.motor.politica.estado_interno()
    return {"dono": dono, "semente": semente, "gestos": v.gestos, "log": _log(v.motor), "motivos": interno["motivos"],
            "pesos": interno["pesos"], "pesos_prior": interno["pesos_prior"], "pesos_corpo": interno["pesos_corpo"],
            "aprendizado": interno["aprendizado"], "corpo": interno["corpo"], "memoria_emocao": interno["memoria_emocao"],
            "canais": interno["canais"], "ganchos": ganchos_v11(b, espec, v.motor),
            "sha_interno": _sha(json.dumps(interno, sort_keys=True))}


# a vontade (PW-3): a grade usa as sondas do carater da web (CCP: 32 estados, semente 9001) com os receptores novos do corpo sorteados pela
# rng `sonda-corpo` da mesma semente, como a deriva da bancada (bancada.medidas.percepcao_da_sonda)
GRADE_ESTADOS, GRADE_SEMENTE = 32, 9001


def _desejo_dict(d) -> dict | None:
    return None if d is None else {"tipo": d.tipo, "alvo": d.alvo, "intensidade": d.intensidade}


class EspiaoVontade:
    """Embrulho que so le: antes de cada decisao, o desejo do v11 e o desvio aprendido do cerebro (o da decisao, antes de ele agir)."""

    def __init__(self, politica) -> None:
        self._p = politica
        self.decisoes: list[dict] = []

    def agir(self, obs, rng):
        c = self._p.cerebro
        k = len(self.decisoes)
        desvio = c.desvio_aprendido(obs)
        self.decisoes.append({"k": k, "desvio": {a.value: v for a, v in desvio.items()},
                              "desejo": _desejo_dict(desejo_lobos(obs, c, k, CONFIG_DESEJO))})
        return self._p.agir(obs, rng)

    def receber_acao_dono(self, acao, tick: int) -> None:
        # explicito: o isinstance do PoliticaTreinavel (Protocol) usa getattr_static e nao ve o __getattr__ (sem ele, os gestos nao
        # chegariam ao cerebro no replay)
        self._p.receber_acao_dono(acao, tick)

    def __getattr__(self, nome):
        return getattr(self._p, nome)


def vontade_v11(b: bv.Bancada, vida: dict) -> dict:
    """a vontade de uma vida da secao v11: pelo replay do texto do log com o espiao (o estado interno do replay e o da vida, conferido)"""
    espec = bv.EspecVida(vida["dono"], BRACO_V11, vida["semente"])
    fp, fm = b.fabrica_politica(espec), b.fabrica_motor(espec)
    espioes: list[EspiaoVontade] = []

    def fabrica(cfg=None):
        e = EspiaoVontade(fp(cfg))
        espioes.append(e)
        return e
    log = LogDeEventos.de_jsonl("\n".join(json.dumps(e, sort_keys=True) for e in vida["log"]) + "\n")
    motor = reproduzir_com_feedback(log, fabrica, semente=vida["semente"], fabrica_motor=fm)
    cerebro = motor.politica.cerebro
    if _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True)) != vida["sha_interno"]:
        raise RuntimeError(f"vontade: o replay com o espiao nao e a vida {vida['dono']}@{vida['semente']}")
    cc = b.cfg_corpo_de(espec)
    rng = random.Random(derivar_semente("sonda-corpo", GRADE_SEMENTE))
    grade = []
    for o in estados_sonda(GRADE_ESTADOS, GRADE_SEMENTE):
        obs = replace(o, corpo=bv.percepcao_da_sonda(o, cc, rng))
        desvio = cerebro.desvio_aprendido(obs)
        grade.append({"vetor": list(obs.vetor_estado), "ticks_desde_cuidado": obs.ticks_desde_cuidado,
                      "corpo": {k: v for k, v in vars(obs.corpo).items() if v is not None},
                      "desvio": {a.value: v for a, v in desvio.items()},
                      "desejo": _desejo_dict(desejo_lobos(obs, cerebro, 0, CONFIG_DESEJO))})
    return {"dono": vida["dono"], "semente": vida["semente"], "decisoes": espioes[0].decisoes, "grade": grade}


def gerar() -> dict:
    b = bancada_v11()
    pontos = {"lobos": b.cfg_lobos.__dict__, "consequencia": b.cfg_consequencia.__dict__, "corpo": b.cfg_corpo.__dict__}
    v11 = [vida_v11(b, d, s) for d, s in VIDAS_V11]
    return {"versao": 1, "braco": BRACO_V11, "dias": DIAS, "orcamento": ORCAMENTO,
            "config": json.loads(json.dumps(pontos, default=list)),
            "config_v11": json.loads(json.dumps(configs_da_vida_v11(b), default=list)),
            "l0": [vida_l0(d, s) for d, s in VIDAS_L0],
            "v11": v11,
            "vontade": {"regra": "tempo_livre", "limiar_vontade": CONFIG_DESEJO.limiar_vontade,
                        "limiar_necessidade": CONFIG_DESEJO.limiar_necessidade, "grade": {"estados": GRADE_ESTADOS,
                                                                                         "semente": GRADE_SEMENTE},
                        "vidas": [vontade_v11(b, v) for v in v11]}}


def laco_v11(b: bv.Bancada, dono: str, semente: int) -> dict:
    """O fim da vida do v11 pelo motor (etapa 4): o `estado()` do motor, com o corpo, e as acoes do pet com o tick."""
    espec = bv.EspecVida(dono, BRACO_V11, semente)
    motor = b.vida(espec).motor
    acoes = motor.acoes_recentes(10 ** 9)
    if not hasattr(motor, "corpo") or len(acoes) != len(motor.politica.estado_interno()["motivos"]):
        raise RuntimeError(f"{espec.nome}: a vida do v11 sem o corpo ou com acoes fora dos motivos")
    return {"dono": dono, "semente": semente, "estado": motor.estado(), "acoes_pet": [[t, a.value] for t, a in acoes]}


def gerar_laco() -> dict:
    b = bancada_v11()
    return {"versao": 1, "braco": BRACO_V11, "dias": DIAS, "v11": [laco_v11(b, d, s) for d, s in VIDAS_V11]}


def _gravar(arquivo: Path, g: dict) -> None:
    arquivo.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    g = gerar()
    _gravar(ARQUIVO, g)
    _gravar(ARQUIVO_LACO, gerar_laco())
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): "
          f"l0 {[len(v['motivos']) for v in g['l0']]}, v11 {[len(v['motivos']) for v in g['v11']]}; {ARQUIVO_LACO.name}")
