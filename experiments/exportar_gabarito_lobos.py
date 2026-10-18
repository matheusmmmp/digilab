"""Gabarito do cerebro A para o jogo web, pets v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 1; o G-PAR-L0 e o G-PAR-L1 das etapas 2
e 3).

O v11 e o da secao 3 da tarefa (PW-1, DECIDIDO 2026-10-17): os lobos com o aprendizado ligado, o sinal pela consequencia no corpo e os
gestos do dono (carinho e tapa), no mundo `padrao`, sem elogio nem bronca, sem mundo fisico, frutas, dois pets e planejamento. O ponto
(PW-2, DECIDIDO: o worker propoe pela calibracao) e o da calibracao do corpo, SEM numero novo e SEM validacao (secao "Ponto" abaixo).

Duas secoes:
  l0      o nucleo sem aprender e sem corpo: o cerebro tem de ser o instinto, decisao a decisao (G2 da L0); o TS confere contra o
          instinto dele e contra este traco;
  v11     as vidas do pet v11 inteiras: o log (o que o TS rejoga), os motivos de cada decisao (o que o painel DigiBrain mostra), os pesos,
          os pesos do corpo e o resumo do aprendizado no fim, e o sha256 do estado interno. Desde a etapa 3 (G-PAR-L1), mais dois campos:
            traco    as chamadas que chegam ao cerebro, na ordem (o que o lobos.ts rejoga sem o motor, que e a etapa 4): agir, a
                     consequencia da decisao (a transicao do engine e o f_S do braco), o gancho do corpo, o tapa (receber_acao_dono) e o
                     carinho (mudanca_no_corpo), com as observacoes inteiras (o Estado.vetor, o ticks_desde_cuidado e os receptores do
                     corpo que existem);
            interno  o estado_interno do cerebro sem os motivos (os contadores da memoria, o aprendizado, os pesos, os canais): com os
                     motivos, e o que o sha256 resume, conferido campo a campo no TS.

    python experiments/exportar_gabarito_lobos.py      # grava web/app/test/gabaritos/lobos_python.json

Ponto (PW-2), todos PROPOSTOS, nenhum validado (docs/RESULTADO_V2_CALIBRACAO_CORPO.md; docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md):
  - o aprendiz T3 (passo 512, teto 16 S, piso S/16), a montagem `completa` (canais ligados) e o ganho 4 da consequencia: os da config da
    calibracao do corpo (experiments/configs/v2_corpo/calibracao_adendo5.json); o ganho 4 nao fechou na calibracao conjunta;
  - o corpo: o gasto 4/5 (basal 300/150; o unico numero do corpo que fechou, adendo 5) e o ponto (m_sobe, m_reduz) = (2, 1) do adendo 4
    (nao fechou, e foi medido com o gasto em 1/2); o w_novos 2 (fechou, tambem com o gasto em 1/2).
"""
from __future__ import annotations

import hashlib
import json
import sys
from contextlib import contextmanager
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_calibracao_corpo as cal  # noqa: E402

from digilab.config import CONFIG_PADRAO, ConfigLobos  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "lobos_python.json"
CONFIG_CALIBRACAO = RAIZ / "experiments" / "configs" / "v2_corpo" / "calibracao_adendo5.json"
DIAS = 3
ORCAMENTO = 16 * DIAS
BRACO_V11 = "P1-c-tapa"
PONTO_CORPO = (2.0, 1.0)                 # (m_sobe, m_reduz) do adendo 4
W_NOVOS = 2                              # o w_novos do adendo 4
VIDAS_L0 = (("atencioso", 101), ("aleatorio", 202))
VIDAS_V11 = (("atencioso", 101), ("relapso", 202), ("aleatorio", 303), ("incoerente", 404))


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


def _log(motor) -> list:
    return [json.loads(linha) for linha in motor.log.para_jsonl().splitlines() if linha.strip()]


def vida_l0(dono: str, semente: int) -> dict:
    politica = PoliticaLobos(CONFIG_PADRAO, ConfigLobos())
    motor = simular_vida(f"{dono}-L0", criar_dono(dono), politica, semente, DIAS, ORCAMENTO, rotulo_dono=dono).motor
    interno = politica.estado_interno()
    return {"dono": dono, "semente": semente, "log": _log(motor), "motivos": interno["motivos"],
            "sha_interno": _sha(json.dumps(interno, sort_keys=True))}


def _obs(o) -> dict:
    """A observacao que o cerebro le: o Estado.vetor, o ticks_desde_cuidado e os receptores do corpo que existem (os None nao existem)."""
    if o.corpo is None:
        raise RuntimeError("v11: observacao sem o corpo")
    return {"v": list(o.vetor_estado), "tdc": o.ticks_desde_cuidado,
            "corpo": {k: v for k, v in asdict(o.corpo).items() if v is not None}}


# os ganchos do cerebro que o v11 nao usa (o mundo fisico, as frutas): se algum chegar, o traco nao e o do v11
GANCHOS_FORA_DO_V11 = ("observar", "consequencia_mundo", "fruta_comida", "fruta_na_mao")


@contextmanager
def _gravando(tracos: dict, cc):
    """Grava, na ordem, as chamadas que chegam a cada PoliticaLobos (pela PoliticaDoBraco, que ja filtrou a fonte do sinal), um traco por
    cerebro (a bancada refaz a vida pelo log para conferir o replay, com outro cerebro). So le e repassa: a vida e a mesma (o teste do
    gabarito confere que o log e os motivos nao mudam)."""
    originais = {n: getattr(PoliticaLobos, n) for n in ("agir", "observar_consequencia", "consequencia_corpo", "receber_acao_dono",
                                                         "mudanca_no_corpo") + GANCHOS_FORA_DO_V11}
    ultima_obs = {}

    def do(self) -> list:
        return tracos.setdefault(id(self), (self, []))[1]

    def agir(self, obs, rng):
        do(self).append({"t": "agir", "obs": _obs(obs)})
        ultima_obs[id(self)] = obs
        return originais["agir"](self, obs, rng)

    def observar_consequencia(self, transicao, f_S, cfg_consequencia=None):
        if transicao.observacao != ultima_obs[id(self)] or cfg_consequencia != cc:
            raise RuntimeError("v11: a transicao nao comeca na observacao da decisao, ou a ConfigConsequencia nao e a da bancada")
        do(self).append({"t": "consequencia", "acao": transicao.acao.value, "depois": _obs(transicao.observacao_seguinte), "f_S": f_S})
        return originais["observar_consequencia"](self, transicao, f_S, cfg_consequencia)

    def consequencia_corpo(self, acao, ocorrido, obs_depois):
        do(self).append({"t": "corpo", "acao": acao.value, "ocorrido": json.loads(json.dumps(ocorrido)), "depois": _obs(obs_depois)})
        return originais["consequencia_corpo"](self, acao, ocorrido, obs_depois)

    def receber_acao_dono(self, acao, tick):
        do(self).append({"t": "dono", "acao": acao.value, "tick": tick})
        return originais["receber_acao_dono"](self, acao, tick)

    def mudanca_no_corpo(self, obs_antes, obs_depois):
        do(self).append({"t": "carinho", "antes": _obs(obs_antes), "depois": _obs(obs_depois)})
        return originais["mudanca_no_corpo"](self, obs_antes, obs_depois)

    def fora(nome):
        def gancho(self, *a, **k):
            raise RuntimeError(f"v11: o gancho {nome} nao faz parte do v11")
        return gancho

    novos = {"agir": agir, "observar_consequencia": observar_consequencia, "consequencia_corpo": consequencia_corpo,
             "receber_acao_dono": receber_acao_dono, "mudanca_no_corpo": mudanca_no_corpo,
             **{n: fora(n) for n in GANCHOS_FORA_DO_V11}}
    try:
        for n, f in novos.items():
            setattr(PoliticaLobos, n, f)
        yield
    finally:
        for n, f in originais.items():
            setattr(PoliticaLobos, n, f)


def vida_v11(b: bv.Bancada, dono: str, semente: int) -> dict:
    tracos: dict = {}
    with _gravando(tracos, b.cfg_consequencia):
        v = b.vida(bv.EspecVida(dono, BRACO_V11, semente))
    interno = v.motor.politica.estado_interno()
    dono_do_traco, traco = tracos[id(v.motor.politica.cerebro)]
    if dono_do_traco is not v.motor.politica.cerebro or len(tracos) != 2:
        raise RuntimeError("v11: esperados dois cerebros, o da vida e o do replay")
    cerebro = {k: x for k, x in v.motor.politica.cerebro.estado_interno().items() if k != "motivos"}
    return {"dono": dono, "semente": semente, "gestos": v.gestos, "log": _log(v.motor), "motivos": interno["motivos"],
            "pesos": interno["pesos"], "pesos_prior": interno["pesos_prior"], "pesos_corpo": interno["pesos_corpo"],
            "aprendizado": interno["aprendizado"], "corpo": interno["corpo"],
            "sha_interno": _sha(json.dumps(interno, sort_keys=True)), "traco": traco, "interno": cerebro}


def gerar() -> dict:
    b = bancada_v11()
    pontos = {"lobos": b.cfg_lobos.__dict__, "consequencia": b.cfg_consequencia.__dict__, "corpo": b.cfg_corpo.__dict__}
    return {"versao": 1, "braco": BRACO_V11, "dias": DIAS, "orcamento": ORCAMENTO,
            "config": json.loads(json.dumps(pontos, default=list)),
            "l0": [vida_l0(d, s) for d, s in VIDAS_L0],
            "v11": [vida_v11(b, d, s) for d, s in VIDAS_V11]}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): "
          f"l0 {[len(v['motivos']) for v in g['l0']]}, v11 {[len(v['motivos']) for v in g['v11']]}")
