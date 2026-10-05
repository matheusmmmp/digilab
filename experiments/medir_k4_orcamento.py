"""V2, K4 (docs/TAREFA_V2_K4_DONO_JULGA_FRUTA.md): quanto o julgamento da fruta, DENTRO do orcamento, tira da tarefa de sempre do P3.

Monta o P3 com o julgamento pela bancada SEM mudar `bancada_v2.py` (que o chat D liga na rodada 10): o mesmo motor do mundo das frutas
(`MotorFrutasMundo`, so com `cfg_julgamento` a mais), o mesmo calendario de ofertas, a mesma politica do P3 e o atencioso embrulhado no
`DonoJulgaFruta`, com o conhecimento de `Bancada.efeitos_reais` (o mesmo do informante do P2). `vida_p3_com_julgamento` e a receita
para o chat D.

So as sementes dos testes (101...505), 14 dias, orcamento 224, ponto T3 do experimento maior: e uma medida de mecanismo, nao resultado
de pesquisa. Grava `artifacts_v2_k4/orcamento.json`.

    python experiments/medir_k4_orcamento.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_BOLA, CONFIG_JULGAMENTO_FRUTA_LIGADA, CONFIG_PADRAO, ConfigJulgamentoFruta  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.frutas import DonoJulgaFruta, JulgadorFruta  # noqa: E402
from digilab.temperamento import NEUTRO, sortear as sortear_temperamento  # noqa: E402

SAIDA = RAIZ / "artifacts_v2_k4" / "orcamento.json"
MUNDOS = ("casado_frutas", "descasado", "mutavel")
SEMENTES = (101, 202, 303, 404, 505)
DIAS, ORCAMENTO = 14, 224
NECESSIDADE = (AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR)


def julgador_da_vida(bancada: bv.Bancada, espec: bv.EspecVida, cj: ConfigJulgamentoFruta = CONFIG_JULGAMENTO_FRUTA_LIGADA):
    """o conhecimento do dono do P3: os efeitos reais da bancada, os mesmos que `Bancada.informante` da ao P2 (e a troca do mutavel)"""
    ef = bancada.efeitos_reais(espec)
    troca = bancada.tick_troca if ef["depois"] is not None else None
    return JulgadorFruta(ef["antes"], ef["depois"], troca, cj)


def fabrica_motor_com_julgamento(bancada: bv.Bancada, espec: bv.EspecVida, cj: ConfigJulgamentoFruta):
    """a `Bancada.fabrica_motor` dos mundos das frutas, com `cfg_julgamento` a mais (so expoe os consumos no estado())"""
    mundo = bv.mundo_de(espec.mundo)
    if not mundo.frutas:
        raise ValueError(f"o julgamento da fruta so existe nos mundos das frutas, nao em {espec.mundo!r}")
    temperamento = NEUTRO if espec.genoma is None else sortear_temperamento(espec.genoma)
    condicao = mundo.condicao
    troca = bancada.tick_troca if condicao == "mutavel" else None
    return lambda politica, cfg, semente: bv.MotorFrutasMundo(
        politica, cfg, semente, temperamento, "brasa", obediencia_desligada=True, cfg_bola=CONFIG_BOLA, cfg_frutas=bancada.cfg_frutas,
        semente_genoma=espec.genoma, condicao=condicao, tick_troca=troca, cfg_informacao=bancada.cfg_informacao, cfg_julgamento=cj)


def vida_p3_com_julgamento(bancada: bv.Bancada, espec: bv.EspecVida,
                           cj: ConfigJulgamentoFruta = CONFIG_JULGAMENTO_FRUTA_LIGADA):
    """(motor, julgador): o P3 com o julgamento da fruta NO orcamento, como a `Bancada.vida` faria nos mundos das frutas"""
    if bv.braco_de(espec.braco).fonte != "dono":
        raise ValueError(f"o julgamento da fruta e do dono do P3, nao do braco {espec.braco!r}")
    julgador = julgador_da_vida(bancada, espec, cj)
    dono = DonoJulgaFruta(criar_dono(espec.dono), julgador)
    fm = fabrica_motor_com_julgamento(bancada, espec, cj)
    motor = bv.simular_vida_mundo(dono, bv.CalendarioFrutas(espec.semente, bancada.cfg_frutas), bancada.politica(espec, CONFIG_PADRAO),
                                  espec.semente, bancada.dias, bancada.orcamento, espec.dono, fm)
    return motor, julgador


def _acoes_do_dono(motor) -> Counter:
    fora = bv.FORA_DO_ORCAMENTO
    return Counter(str(e.valor) for e in motor.log if e.tipo == "acao_usuario" and str(e.valor) not in fora)


def medir() -> dict:
    bancada = bv.Bancada(DIAS, ORCAMENTO, cfg_lobos=bv.cfg_lobos_do_ponto("T3"))
    linhas = []
    for mundo in MUNDOS:
        for s in SEMENTES:
            espec = bv.EspecVida("atencioso", "P3", s, None, mundo, "lobos")
            sem = _acoes_do_dono(bancada.vida(espec).motor)
            motor, julgador = vida_p3_com_julgamento(bancada, espec)
            com = _acoes_do_dono(motor)
            julg = Counter(j[2] for j in julgador.julgados)
            fb = (AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value)
            julgamentos = julg[1] + julg[-1] - len(julgador.descartados)
            linhas.append({
                "mundo": mundo, "semente": s, "orcamento": ORCAMENTO,
                "acoes_sem": sum(sem.values()), "acoes_com": sum(com.values()),
                "consumos": len(julgador.julgados), "elogios_fruta": julg[1], "broncas_fruta": julg[-1], "neutras": julg[0],
                "descartados": len(julgador.descartados),
                "feedback_tarefa_sem": sum(sem[a] for a in fb),
                "feedback_tarefa_com": sum(com[a] for a in fb) - julgamentos,
                # cuidado de necessidade (alimentar, limpar, brincar) separado do carinho, que o atencioso usa para preencher o minimo
                "necessidade_sem": sum(sem[a.value] for a in NECESSIDADE), "necessidade_com": sum(com[a.value] for a in NECESSIDADE),
                "carinho_sem": sem[AcaoUsuario.ACARICIAR.value], "carinho_com": com[AcaoUsuario.ACARICIAR.value],
            })
    por_mundo = {}
    for mundo in MUNDOS:
        ls = [x for x in linhas if x["mundo"] == mundo]
        n = len(ls)
        por_mundo[mundo] = {k: sum(x[k] for x in ls) / n for k in
                            ("consumos", "elogios_fruta", "broncas_fruta", "neutras", "descartados", "feedback_tarefa_sem",
                             "feedback_tarefa_com", "necessidade_sem", "necessidade_com", "carinho_sem", "carinho_com")}
    return {"tarefa": "docs/TAREFA_V2_K4_DONO_JULGA_FRUTA.md", "dias": DIAS, "orcamento": ORCAMENTO, "ponto": "T3",
            "dono": "atencioso", "braco": "P3", "sementes": list(SEMENTES), "modo": "no_orcamento",
            "nota": "sementes dos testes; medida de mecanismo, nao resultado de pesquisa",
            "por_mundo_media": por_mundo, "vidas": linhas}


def main() -> None:
    r = medir()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(r, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    for mundo, m in r["por_mundo_media"].items():
        print(mundo, {k: round(v, 1) for k, v in m.items()})


if __name__ == "__main__":
    main()
