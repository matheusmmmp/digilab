"""Gabarito do cerebro A para o jogo web, pets v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 1; o G-PAR-L0 e o G-PAR-L1 das etapas 2
e 3).

O v11 e o da secao 3 da tarefa (PW-1, DECIDIDO 2026-10-17): os lobos com o aprendizado ligado, o sinal pela consequencia no corpo e os
gestos do dono (carinho e tapa), no mundo `padrao`, sem elogio nem bronca, sem mundo fisico, frutas, dois pets e planejamento. O ponto
(PW-2, DECIDIDO: o worker propoe pela calibracao) e o da calibracao do corpo, SEM numero novo e SEM validacao (secao "Ponto" abaixo).

Duas secoes:
  l0      o nucleo sem aprender e sem corpo: o cerebro tem de ser o instinto, decisao a decisao (G2 da L0); o TS confere contra o
          instinto dele e contra este traco;
  v11     as vidas do pet v11 inteiras: o log (o que o TS rejoga), os motivos de cada decisao (o que o painel DigiBrain mostra), os pesos,
          os pesos do corpo e o resumo do aprendizado no fim, e o sha256 do estado interno.

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
from dataclasses import replace
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


def vida_v11(b: bv.Bancada, dono: str, semente: int) -> dict:
    v = b.vida(bv.EspecVida(dono, BRACO_V11, semente))
    interno = v.motor.politica.estado_interno()
    return {"dono": dono, "semente": semente, "gestos": v.gestos, "log": _log(v.motor), "motivos": interno["motivos"],
            "pesos": interno["pesos"], "pesos_prior": interno["pesos_prior"], "pesos_corpo": interno["pesos_corpo"],
            "aprendizado": interno["aprendizado"], "corpo": interno["corpo"],
            "sha_interno": _sha(json.dumps(interno, sort_keys=True))}


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
