"""SOCIAL_PAR, E1: a conferencia dos controles positivos do adendo 2 (docs/ESPEC_V3_SOCIAL_PAR_E1.md, secao 10, APROVADO em 2026-11-17).

Nao e uma run de pesquisa: e a validacao do instrumento, nas sementes dos testes (101 a 505), sem faixa. O pet focal (A) e sempre a
estatua, e o parceiro (B) e de regra pura (nao come, nao dorme, nao chama):
  C1   estatua x seguidor puro, d0 = 5 celulas   tem de sair: na VIVO B chega (nao censurado) e na GRAV nao chega (censurado), e a
                                                 fracao de contato maior na VIVO, em todas
  C2   estatua x evitador puro, d0 = 1 celula    tem de sair: a fracao de contato menor na VIVO, em todas
As medidas sao as de digilab/metrics.py, nas 8 decisoes depois do passo da perturbacao (A2-4). Em cada semente: a vida VIVO sem
perturbacao da a gravacao de B; depois a VIVO e a GRAV com a mesma perturbacao (A levado a d0 celulas de B no t0 sorteado do fluxo
`intervencao-social`, no dia 1).

As conferencias de antes estao no git e nao se refazem com o codigo de hoje: a da secao 3 em
artifacts_v3_social_par_e1/controles_positivos.json (D-SP-13) e a do adendo 1 em controles_positivos_ad1.json (D-SP-18).

    python experiments/conferir_controles_social_par_e1.py artifacts_v3_social_par_e1/controles_positivos_ad2.json
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
SEMENTES = (101, 202, 303, 404, 505)
CI = CONFIG_INTERVENCAO_SOCIAL_LIGADA
JANELA = 8                                  # A2-4: as 8 decisoes depois do t0, PROPOSTO, SEM FONTE
# A2-1 a A2-3: o pet focal (A) e sempre a estatua; (o cerebro de A, o de B, o d0 em celulas)
PARES = {"C1_estatua_x_seguidor_puro": (lambda c: pc.Estatua(c), lambda c: pc.SeguidorPuro(c), 5),
         "C2_estatua_x_evitador_puro": (lambda c: pc.Estatua(c), lambda c: pc.EvitadorPuro(CM, c), 1)}


def _dono(s):
    return DonoComLugar(criar_dono("atencioso"), "comedouro", s, "atencioso", CM)


def _membros(s, pa, pb, gravar_b):
    ss = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    return [pc.Membro("A", "vivo", e6.fabricas("atencioso", ss["A"])[1], pa, _dono(ss["A"]), "atencioso", "controle"),
            pc.Membro("B", "vivo", e6.fabricas("atencioso", ss["B"])[1], pb, _dono(ss["B"]), "atencioso", "controle", gravar=gravar_b)]


def medir(v) -> dict:
    """nas JANELA decisoes depois do passo da perturbacao (k): o passo k e o da distancia d0, e a janela sao os passos k+1 a k+JANELA"""
    d = pc.distancias_celulas(v, "A", "B")
    k = pc.indice_do_passo(v, v.t0)
    if k + JANELA >= len(d):
        raise RuntimeError(f"a janela passa do fim da vida: t0 {v.t0}, passo {k}, {len(d)} passos")
    t, censurado = mt.tempo_ate_raio(d[:k + JANELA + 1], CI.raio_contato_celulas, k, JANELA)
    return {"t0": v.t0, "distancia_no_t0": d[k], "distancias": d[k:k + JANELA + 1], "tempo_ate_contato": t, "censurado": censurado,
            "fracao_contato": mt.fracao_em_raio(d[k + 1:k + JANELA + 1], CI.raio_contato_celulas),
            "desvios_B": len(v.desvios.get("B", []))}


def conferir() -> dict:
    out = {}
    for nome, (pa, pb, d0) in PARES.items():
        linhas = {}
        for s in SEMENTES:
            ss = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
            t0, direcao = pc.sortear_perturbacao(s, TICKS_POR_DIA, 2 * TICKS_POR_DIA - 15, 15)
            pert = ("A", "B", t0, direcao, d0)
            base = pc.viver_par(CM, s, _membros(s, pa, pb, True), DIAS)
            vivo = pc.viver_par(CM, s, _membros(s, pa, pb, False), DIAS, perturbacao=pert)
            gb = pc.Membro("B", "gravado", e6.fabricas("atencioso", ss["B"])[1], gravacao=base.gravacoes["B"],
                           eventos_dono=pc.eventos_do_dono(base.grupo, "B"), rotulo_dono="atencioso", rotulo_cerebro="gravada")
            grav = pc.viver_par(CM, s, [_membros(s, pa, pb, False)[0], gb], DIAS, perturbacao=pert)
            linhas[str(s)] = {"VIVO": medir(vivo), "GRAV": medir(grav)}
        out[nome] = linhas
    c1, c2 = out["C1_estatua_x_seguidor_puro"].values(), out["C2_estatua_x_evitador_puro"].values()
    esperado = {
        "C1": all(not l["VIVO"]["censurado"] and l["GRAV"]["censurado"] and l["VIVO"]["fracao_contato"] > l["GRAV"]["fracao_contato"]
                  for l in c1),
        "C2": all(l["VIVO"]["fracao_contato"] < l["GRAV"]["fracao_contato"] for l in c2),
    }
    return {"espec": "docs/ESPEC_V3_SOCIAL_PAR_E1.md, secao 10 (o adendo 2)", "janela": JANELA, "dias": DIAS, "sementes": list(SEMENTES),
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
