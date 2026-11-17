"""SOCIAL_PAR, E1: a conferencia dos controles positivos do adendo 1 (docs/ESPEC_V3_SOCIAL_PAR_E1.md, secao 9, APROVADO em 2026-11-17).

Nao e uma run de pesquisa: e a validacao do instrumento, nas sementes dos testes (101 a 505), sem faixa. Os pares (A e o pet focal F, B o
parceiro P):
  C1   passivo x seguidor     tem de sair: o tempo ate o contato menor na VIVO e a fracao de contato maior na VIVO, em todas
  C2   seguidor x evitador    tem de sair: a fracao de contato menor na VIVO, em todas; e o G-MET-NULO na GRAV (contingencia None ou |c| <= 0,2)
  seguidor x seguidor          so descritivo (A1-3)
Em cada semente: a vida VIVO sem perturbacao da a gravacao de B; depois a VIVO e a GRAV com a mesma perturbacao (A levado a d0 = 5 celulas
de B no t0 sorteado do fluxo `intervencao-social`, no dia 1). As medidas sao as de digilab/metrics.py, a partir do passo da perturbacao.

A primeira conferencia (a secao 3, com o evitador de antes) esta em artifacts_v3_social_par_e1/controles_positivos.json (D-SP-13) e nao se
refaz com o codigo de hoje: o evitador mudou (A1-2).

    python experiments/conferir_controles_social_par_e1.py artifacts_v3_social_par_e1/controles_positivos_ad1.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co6 as e6  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from digilab import metrics as mt  # noqa: E402
from digilab.config import CONFIG_GRUPO_LIGADA, CONFIG_INTERVENCAO_SOCIAL_LIGADA, TICKS_POR_DIA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import sementes_do_grupo  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402

CM = e6.CM
DIAS = 2
D0 = 5                                      # celulas (a espec, 2.3: o d0 fixo pelo plano; aqui o da conferencia)
SEMENTES = (101, 202, 303, 404, 505)
CI = CONFIG_INTERVENCAO_SOCIAL_LIGADA
LIMIAR_NULO = 0.2                         # A1-4, PROPOSTO, SEM FONTE
PARES = {"C1_passivo_x_seguidor": (lambda c: pc.Passivo(c), lambda c: pc.Seguidor(c)),
         "C2_seguidor_x_evitador": (lambda c: pc.Seguidor(c), lambda c: pc.Evitador(CM, c)),
         "seguidor_x_seguidor": (lambda c: pc.Seguidor(c), lambda c: pc.Seguidor(c))}


def _dono(s):
    return DonoComLugar(criar_dono("atencioso"), "comedouro", s, "atencioso", CM)


def _membros(s, pa, pb, gravar_b):
    ss = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    return [pc.Membro("A", "vivo", e6.fabricas("atencioso", ss["A"])[1], pa, _dono(ss["A"]), "atencioso", "controle"),
            pc.Membro("B", "vivo", e6.fabricas("atencioso", ss["B"])[1], pb, _dono(ss["B"]), "atencioso", "controle", gravar=gravar_b)]


def medir(v) -> dict:
    d = pc.distancias_celulas(v, "A", "B")
    k = pc.indice_do_passo(v, v.t0)
    t, censurado = mt.tempo_ate_raio(d, CI.raio_contato_celulas, k, CI.janela_reencontro)
    c = mt.contingencia(v.posicoes["B"][k:], v.posicoes["A"][k:])
    return {"t0": v.t0, "distancia_no_t0": d[k], "tempo_ate_contato": t, "censurado": censurado,
            "fracao_contato": mt.fracao_em_raio(d, CI.raio_contato_celulas, k), "contingencia_B_de_A": c,
            "desvios_B": len(v.desvios.get("B", []))}


def conferir() -> dict:
    out = {}
    for nome, (pa, pb) in PARES.items():
        linhas = {}
        for s in SEMENTES:
            ss = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
            t0, direcao = pc.sortear_perturbacao(s, TICKS_POR_DIA, 2 * TICKS_POR_DIA - 15, 15)
            pert = ("A", "B", t0, direcao, D0)
            base = pc.viver_par(CM, s, _membros(s, pa, pb, True), DIAS)
            vivo = pc.viver_par(CM, s, _membros(s, pa, pb, False), DIAS, perturbacao=pert)
            gb = pc.Membro("B", "gravado", e6.fabricas("atencioso", ss["B"])[1], gravacao=base.gravacoes["B"],
                           eventos_dono=pc.eventos_do_dono(base.grupo, "B"), rotulo_dono="atencioso", rotulo_cerebro="gravada")
            grav = pc.viver_par(CM, s, [_membros(s, pa, pb, False)[0], gb], DIAS, perturbacao=pert)
            linhas[str(s)] = {"VIVO": medir(vivo), "GRAV": medir(grav)}
        out[nome] = linhas
    nulo = lambda c: c is None or abs(c) <= LIMIAR_NULO  # noqa: E731
    esperado = {
        "C1": all(l["VIVO"]["tempo_ate_contato"] < l["GRAV"]["tempo_ate_contato"]
                  and l["VIVO"]["fracao_contato"] > l["GRAV"]["fracao_contato"] for l in out["C1_passivo_x_seguidor"].values()),
        "C2": all(l["VIVO"]["fracao_contato"] < l["GRAV"]["fracao_contato"] for l in out["C2_seguidor_x_evitador"].values()),
        "G_MET_NULO": all(nulo(l["GRAV"]["contingencia_B_de_A"]) for l in out["C2_seguidor_x_evitador"].values()),
    }
    return {"espec": "docs/ESPEC_V3_SOCIAL_PAR_E1.md, secao 9 (o adendo 1)", "limiar_nulo": LIMIAR_NULO, "dias": DIAS, "d0_celulas": D0, "sementes": list(SEMENTES),
            "alcance_celulas_por_decisao": CM.velocidade * 15 / CM.sub, "pares": out, "o_que_a_espec_espera_saiu": esperado}


def main() -> None:
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    r = conferir()
    texto = json.dumps(r, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if saida is None:
        print(texto)
    else:
        saida.parent.mkdir(parents=True, exist_ok=True)
        saida.write_text(texto, encoding="utf-8", newline="\n")
        print(json.dumps(r["o_que_a_espec_espera_saiu"]))


if __name__ == "__main__":
    main()
