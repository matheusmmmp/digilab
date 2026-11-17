"""SOCIAL_PAR, E1: a conferencia dos controles positivos (docs/ESPEC_V3_SOCIAL_PAR_E1.md, secao 3), como a espec os escreveu.

Nao e uma run de pesquisa: e a validacao do instrumento, nas sementes dos testes (101 a 505), sem faixa. Dois pares de regra fixa:
  seguidor x seguidor   a espec espera o reencontro mais rapido e o contato mais longo na VIVO do que na GRAV
  seguidor x evitador   a espec espera o contato mais curto na VIVO do que na GRAV
Em cada semente: a vida VIVO sem perturbacao da a gravacao de B; depois a VIVO e a GRAV com a mesma perturbacao (A levado a d0 = 5 celulas
de B no t0 sorteado do fluxo `intervencao-social`, no dia 1). As medidas sao as de digilab/metrics.py, a partir do passo da perturbacao.

    python experiments/conferir_controles_social_par_e1.py artifacts_v3_social_par_e1/controles_positivos.json
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
PARES = {"seguidor_x_seguidor": (lambda c: pc.Seguidor(c), lambda c: pc.Seguidor(c)),
         "seguidor_x_evitador": (lambda c: pc.Seguidor(c), lambda c: pc.Evitador(CM, c))}


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
    esperado = {
        "seguidor_x_seguidor": all(l["VIVO"]["tempo_ate_contato"] < l["GRAV"]["tempo_ate_contato"]
                                   and l["VIVO"]["fracao_contato"] > l["GRAV"]["fracao_contato"] for l in out["seguidor_x_seguidor"].values()),
        "seguidor_x_evitador": all(l["VIVO"]["fracao_contato"] < l["GRAV"]["fracao_contato"] for l in out["seguidor_x_evitador"].values()),
    }
    return {"espec": "docs/ESPEC_V3_SOCIAL_PAR_E1.md, secao 3", "dias": DIAS, "d0_celulas": D0, "sementes": list(SEMENTES),
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
