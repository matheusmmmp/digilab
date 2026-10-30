"""Os empates da direcao do cheiro no mundo fisico (MUNDO-CEREBROS; pedido do Gerente na etapa 3, sobre o achado do A no PR #226).

`mundo.direcao_do_cheiro` mede o cheiro inteiro (`A x (R - d) // R`) a 1 celula em cada uma das 8 direcoes (L, NE, N, NO, O, SO, S, SE)
e fica com a primeira que passa estritamente o maximo ate ali: no empate vence a que vem antes na ordem fixa. Um passo de 1 celula muda o
cheiro de uma fruta em ~1,3 (a racao em ~2,7), entao empates sao comuns. Exemplo do A: uma fruta 90 subunidades ao norte da 25 em N e em
NE, e o pet vai para NE.

So geometria, sem semente e sem vida: uma comida sozinha num campo aberto (sem o corte do mapa: o ponto da medida do cheiro nao e cortado
no motor, e o passo aqui tambem nao), com as funcoes do proprio motor (cheiro_em, direcao_do_cheiro, DIR16, div_arred, distancia) e os
numeros da ConfigMundo. Tres regras de desempate:
- `ordem`: a do motor (a primeira na ordem fixa);
- `dois`: entre as empatadas, a de maior cheiro a 2 celulas na mesma direcao; empate de novo, a ordem fixa (implementavel: o pet so le
  o cheiro em volta dele);
- `oraculo`: entre as empatadas, a mais perto do rumo verdadeiro da comida (nao implementavel: o pet nao sabe onde a comida esta; e o
  limite do que um desempate pode ganhar).

Parte A, a direcao: em toda posicao inteira com a comida fora da visao e dentro do raio do cheiro (96 < d < 384 subunidades), a fracao com
empate no maximo, a fracao sem direcao (nenhum vizinho passa o centro) e o erro angular da direcao escolhida ao rumo da comida.
Parte B, o comer: do ponto de partida (grade de 8 subunidades na mesma faixa), o alvo padrao do comer em cada decisao (a comida, se vista;
senao o alvo `cheiro`, 8 celulas na direcao do cheiro), 60 subunidades por decisao, ate comer; as decisoes e o caminho a mais que a reta.
Parte C, o explorar: o alvo padrao do explorar (continuar o alvo pendente; senao o cheiro, se passa do limiar; senao vagar), a partir de onde
o cheiro passa do limiar e a comida nao esta a vista; quantas decisoes ate a comida entrar na visao (dali o comer vai reto) e se o "achou e
comeu" acontece.
Parte D, as vidas: nas vidas do P0 com as sementes dos testes (101, 202), a fracao das decisoes com direcao de cheiro que sairam de um
empate (com todas as comidas do mapa) e em quantas o `dois` mudaria a direcao; e quantas tem cheiro sem direcao e nada visto.

    python experiments/analisar_empates_cheiro.py            # -> artifacts_v2_mundo_cerebros/empates_cheiro.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigMundo  # noqa: E402
from digilab.mundo import DIR16, ESCALA_DIR, cheiro_em, direcao_do_cheiro, distancia, div_arred  # noqa: E402

REGRAS = ("ordem", "dois", "oraculo")
NOMES_DIRECAO = ("L", "NE", "N", "NO", "O", "SO", "S", "SE")
MAX_DECISOES = 60
SEMENTES_VIDAS = (101, 202)          # so as sementes dos testes


def _ponto(x: int, y: int, k: int, comprimento: int) -> tuple[int, int]:
    """o ponto a `comprimento` na direcao k (1 a 8) do cheiro, sem corte (o mesmo calculo do motor)"""
    cx, cy = DIR16[2 * (k - 1)]
    return x + div_arred(cx * comprimento, ESCALA_DIR), y + div_arred(cy * comprimento, ESCALA_DIR)


def _passo(x: int, y: int, tx: int, ty: int, alcance: int) -> tuple[int, int]:
    """mundo.passo_ate sem o corte do mapa"""
    dx, dy = tx - x, ty - y
    d = distancia(dx, dy)
    if d <= alcance:
        return tx, ty
    return x + div_arred(dx * alcance, d), y + div_arred(dy * alcance, d)


def _rumo(x: int, y: int, fx: int, fy: int) -> float:
    """rumo da comida em graus, anti-horario a partir do leste, com o norte em y menor (o DIR16)"""
    return math.degrees(math.atan2(-(fy - y), fx - x)) % 360.0


def _erro(angulo_dir: float, rumo: float) -> float:
    """erro assinado em graus, em (-180, 180]: positivo = a direcao esta no sentido anti-horario do rumo"""
    e = (angulo_dir - rumo + 180.0) % 360.0 - 180.0
    return 180.0 if e == -180.0 else e


def _vizinhos(x: int, y: int, fontes: list, cm: ConfigMundo) -> tuple[int, list[int]]:
    """(cheiro no centro, cheiro a 1 celula em cada direcao 1 a 8): as medidas do mundo.direcao_do_cheiro"""
    return cheiro_em(x, y, fontes, cm), [cheiro_em(*_ponto(x, y, k, cm.sub), fontes, cm) for k in range(1, 9)]


def _escolher(regra: str, centro: int, vizinhos: list[int], x: int, y: int, fontes: list, cm: ConfigMundo,
              alvo_real: tuple[int, int]) -> tuple[int, list]:
    """(direcao escolhida 0 a 8, as empatadas no maximo). `ordem` e a regra do motor."""
    maximo = max(vizinhos)
    if maximo <= centro:
        return 0, []
    empatadas = [k for k in range(1, 9) if vizinhos[k - 1] == maximo]
    if regra == "ordem" or len(empatadas) == 1:
        return empatadas[0], empatadas
    if regra == "dois":
        dois = {k: cheiro_em(*_ponto(x, y, k, 2 * cm.sub), fontes, cm) for k in empatadas}
        m2 = max(dois.values())
        return next(k for k in empatadas if dois[k] == m2), empatadas
    if regra == "oraculo":
        r = _rumo(x, y, *alvo_real)
        return min(empatadas, key=lambda k: (abs(_erro((k - 1) * 45.0, r)), k)), empatadas
    raise ValueError(f"regra de desempate desconhecida: {regra!r}")


def direcao(x: int, y: int, fontes: list, cm: ConfigMundo, regra: str, alvo_real: tuple[int, int] | None = None) -> tuple[int, int, list]:
    """(cheiro no centro, direcao escolhida 0 a 8, as empatadas no maximo). `ordem` refaz o mundo.direcao_do_cheiro."""
    centro, vizinhos = _vizinhos(x, y, fontes, cm)
    k, empatadas = _escolher(regra, centro, vizinhos, x, y, fontes, cm, alvo_real)
    return centro, k, empatadas


def _resumo(valores: list[float]) -> dict:
    if not valores:
        return {"n": 0}
    v = sorted(valores)
    return {"n": len(v), "media": sum(v) / len(v), "p50": v[len(v) // 2], "p95": v[min(len(v) - 1, int(0.95 * len(v)))],
            "max": v[-1]}


def parte_a(cm: ConfigMundo, a: int, passo: int) -> dict:
    """a direcao em toda posicao (grade `passo`) com 96 < d < R da comida na origem; as tres regras sobre as mesmas medidas"""
    raio, visao = cm.raio_cheiro_celulas * cm.sub, cm.raio_visao_celulas * cm.sub
    fontes = [(0, 0, a)]
    acc = {regra: {"empates": 0, "sem_direcao": 0, "abs": [], "ass": [], "ass_empate": [], "escolhidas": [0] * 8} for regra in REGRAS}
    n = 0
    for y in range(-raio, raio + 1, passo):
        for x in range(-raio, raio + 1, passo):
            d = distancia(x, y)
            if not visao < d < raio:
                continue
            n += 1
            centro, vizinhos = _vizinhos(x, y, fontes, cm)
            rumo = _rumo(x, y, 0, 0)
            for regra in REGRAS:
                k, emp = _escolher(regra, centro, vizinhos, x, y, fontes, cm, (0, 0))
                if regra == "ordem" and (centro, k) != direcao_do_cheiro(x, y, fontes, cm):
                    raise RuntimeError(f"a regra `ordem` nao refaz o motor em ({x}, {y})")
                r = acc[regra]
                if k == 0:
                    r["sem_direcao"] += 1
                    continue
                e = _erro((k - 1) * 45.0, rumo)
                r["abs"].append(abs(e))
                r["ass"].append(e)
                if len(emp) > 1:
                    r["empates"] += 1
                    r["ass_empate"].append(e)
                    r["escolhidas"][k - 1] += 1
    saida = {}
    for regra, r in acc.items():
        saida[regra] = {
            "posicoes": n, "frac_empate": r["empates"] / n, "frac_sem_direcao": r["sem_direcao"] / n,
            "erro_abs_graus": _resumo(r["abs"]), "erro_assinado_medio_graus": sum(r["ass"]) / len(r["ass"]),
            "erro_assinado_medio_no_empate_graus": (sum(r["ass_empate"]) / len(r["ass_empate"])) if r["ass_empate"] else None,
            "escolhidas_no_empate": dict(zip(NOMES_DIRECAO, r["escolhidas"])),
        }
    return saida


def _comer(x: int, y: int, cm: ConfigMundo, alcance: int, a: int, regra: str | None) -> tuple[int, int, bool]:
    """(decisoes ate comer, caminho, travou). regra None = a reta (o alvo e sempre a comida)."""
    fontes = [(0, 0, a)]
    visao, pegar = cm.raio_visao_celulas * cm.sub, cm.raio_pegar_celulas * cm.sub
    caminho = 0
    for decisoes in range(1, MAX_DECISOES + 1):
        if regra is None or distancia(x, y) <= visao:
            tx, ty = 0, 0
        else:
            _, k, _ = direcao(x, y, fontes, cm, regra, (0, 0))
            if k == 0:
                return decisoes, caminho, True
            tx, ty = _ponto(x, y, k, cm.passo_cheiro_celulas * cm.sub)
        nx, ny = _passo(x, y, tx, ty, alcance)
        caminho += distancia(nx - x, ny - y)
        x, y = nx, ny
        if (tx, ty) == (0, 0) and distancia(x, y) <= pegar:
            return decisoes, caminho, False
    return MAX_DECISOES, caminho, True


def parte_b(cm: ConfigMundo, a: int, alcance: int, passo: int) -> dict:
    raio, visao = cm.raio_cheiro_celulas * cm.sub, cm.raio_visao_celulas * cm.sub
    partidas = [(x, y) for y in range(-raio, raio + 1, passo) for x in range(-raio, raio + 1, passo) if visao < distancia(x, y) < raio]
    reta = {p: _comer(*p, cm, alcance, a, None) for p in partidas}
    saida = {"partidas": len(partidas), "reta": {"decisoes": _resumo([r[0] for r in reta.values()]),
                                                  "caminho": _resumo([r[1] for r in reta.values()])}}
    for regra in REGRAS:
        extra_dec, extra_cam, travou = [], [], 0
        por_rumo = {nome: [] for nome in NOMES_DIRECAO}
        for p in partidas:
            dec, cam, trava = _comer(*p, cm, alcance, a, regra)
            if trava:
                travou += 1
                continue
            extra_dec.append(dec - reta[p][0])
            extra_cam.append(cam - reta[p][1])
            setor = NOMES_DIRECAO[int(((_rumo(p[0], p[1], 0, 0) + 22.5) % 360.0) // 45.0)]
            por_rumo[setor].append(dec - reta[p][0])
        saida[regra] = {
            "frac_travou": travou / len(partidas), "decisoes_a_mais": _resumo(extra_dec), "caminho_a_mais": _resumo(extra_cam),
            "energia_a_mais_media": (sum(extra_cam) / len(extra_cam)) * cm.custo_energia_por_subunidade if extra_cam else None,
            "decisoes_a_mais_por_rumo": {s: (sum(v) / len(v) if v else None) for s, v in por_rumo.items()},
        }
    return saida


def _explorar(x: int, y: int, cm: ConfigMundo, alcance: int, a: int, regra: str) -> tuple[int | None, bool, str]:
    """(decisoes ate a comida entrar na visao, achou e comeu, como acabou). O explorar do motor: continuar o alvo pendente; senao o
    cheiro, se passa do limiar; senao vagar (aqui o fim da busca: vagar e um sorteio)."""
    fontes = [(0, 0, a)]
    visao, pegar = cm.raio_visao_celulas * cm.sub, cm.raio_pegar_celulas * cm.sub
    alvo = None
    na_visao = None
    for decisoes in range(1, MAX_DECISOES + 1):
        if alvo is None:
            c, k, _ = direcao(x, y, fontes, cm, regra, (0, 0))
            if k == 0 or c <= cm.limiar_cheiro_explorar:
                return na_visao, False, "vagar"
            alvo = _ponto(x, y, k, cm.passo_cheiro_celulas * cm.sub)
        x, y = _passo(x, y, *alvo, alcance)
        if na_visao is None and distancia(x, y) <= visao:
            na_visao = decisoes
        if distancia(alvo[0] - x, alvo[1] - y) <= pegar:      # chegou ao alvo: o "achou e comeu" so olha o raio de pegar
            if distancia(x, y) <= pegar:
                return na_visao, True, "achou"
            alvo = None
    return na_visao, False, "limite"


def parte_c(cm: ConfigMundo, a: int, alcance: int, passo: int) -> dict:
    visao = cm.raio_visao_celulas * cm.sub
    raio = cm.raio_cheiro_celulas * cm.sub
    fontes = [(0, 0, a)]
    partidas = [(x, y) for y in range(-raio, raio + 1, passo) for x in range(-raio, raio + 1, passo)
                if distancia(x, y) > visao and cheiro_em(x, y, fontes, cm) > cm.limiar_cheiro_explorar]
    saida = {"partidas": len(partidas)}
    for regra in REGRAS:
        ate_visao, achou, fins = [], 0, {"achou": 0, "vagar": 0, "limite": 0}
        for p in partidas:
            nv, ac, fim = _explorar(*p, cm, alcance, a, regra)
            fins[fim] += 1
            achou += ac
            if nv is not None:
                ate_visao.append(nv)
        saida[regra] = {"frac_chega_a_visao": len(ate_visao) / len(partidas), "decisoes_ate_a_visao": _resumo(ate_visao),
                        "frac_achou_e_comeu": achou / len(partidas), "fins": fins}
    return saida


def exemplo_do_a(cm: ConfigMundo) -> dict:
    """a fruta 90 subunidades ao norte do pet (o exemplo do PR #226)"""
    fontes = [(0, -90, cm.cheiro_fruta)]
    vizinhos = {NOMES_DIRECAO[k - 1]: cheiro_em(*_ponto(0, 0, k, cm.sub), fontes, cm) for k in range(1, 9)}
    return {"vizinhos": vizinhos, "centro": cheiro_em(0, 0, fontes, cm),
            **{regra: NOMES_DIRECAO[direcao(0, 0, fontes, cm, regra, (0, -90))[1] - 1] for regra in REGRAS}}


def parte_vidas(cm: ConfigMundo = CONFIG_MUNDO_LIGADA, sementes: tuple = SEMENTES_VIDAS, dias: int = 7) -> dict:
    """Nas vidas do P0 (o instinto do mundo, os alvos padrao), so com as sementes dos testes: em quantas decisoes ha direcao de cheiro,
    em quantas ela saiu de um empate (com todas as comidas do mapa, nao so uma), em quantas o `dois` daria outra direcao; e quantas
    decisoes tem cheiro sem direcao e nada visto (o caso da leitura "para onde ir" da fome urgente, instinto_mundo.para_onde_comer)."""
    from digilab.donos import criar_dono
    from digilab.instinto_mundo import PoliticaInstintoMundo, comida_boa_vista
    from digilab.mundo import DonoComLugar, ESTILOS_LUGAR_V2, fabricas_mundo, simular_vida_mundo

    class Espiao(PoliticaInstintoMundo):
        def __init__(self, cfg=None) -> None:
            super().__init__(cfg)
            self.motor = None
            self.c = {"decisoes": 0, "com_direcao": 0, "empate": 0, "dois_muda": 0, "cheiro_sem_direcao_nada_visto": 0,
                      "fome_urgente_acordado": 0, "fome_urgente_sem_direcao_nada_visto": 0}

        def agir(self, obs, rng):
            p, c = obs.mundo, self.c
            c["decisoes"] += 1
            sem = p.cheiro > 0 and p.direcao_cheiro == 0 and not comida_boa_vista(p)
            c["cheiro_sem_direcao_nada_visto"] += sem
            if obs.vetor_estado[0] < 0.25 and obs.vetor_estado[2] >= 0.25:
                c["fome_urgente_acordado"] += 1
                c["fome_urgente_sem_direcao_nada_visto"] += sem
            if p.direcao_cheiro:
                c["com_direcao"] += 1
                fontes = self.motor._fontes_de_cheiro(self.motor._estado.tick)
                centro, viz = _vizinhos(p.x, p.y, fontes, cm)
                k, emp = _escolher("ordem", centro, viz, p.x, p.y, fontes, cm, (0, 0))
                if k != p.direcao_cheiro:
                    raise RuntimeError("a direcao recalculada nao e a da percepcao")
                if len(emp) > 1:
                    c["empate"] += 1
                    c["dois_muda"] += _escolher("dois", centro, viz, p.x, p.y, fontes, cm, (0, 0))[0] != k
            return super().agir(obs, rng)

    total: dict = {}
    for dono in ("atencioso", "relapso", "aleatorio", "incoerente"):
        for estilo in ESTILOS_LUGAR_V2:
            for semente in sementes:
                pol = Espiao(CONFIG_PADRAO)
                _, fm = fabricas_mundo(cm)
                fabrica = (lambda politica, cfg, s, fm=fm, pol=pol: setattr(pol, "motor", fm(politica, cfg, s)) or pol.motor)
                simular_vida_mundo(dono, DonoComLugar(criar_dono(dono), estilo, semente, dono, cm), pol, semente, dias,
                                   16 * dias, fabrica, rotulo_dono=dono)
                for k, v in pol.c.items():
                    total[k] = total.get(k, 0) + v
    return {"sementes": list(sementes), "dias": dias, "orcamento_por_dia": 16, "vidas": 4 * len(ESTILOS_LUGAR_V2) * len(sementes),
            **total}


def analisar(cm: ConfigMundo = CONFIG_MUNDO_LIGADA, passo_a: int = 1, passo_bc: int = 8) -> dict:
    alcance = cm.velocidade * CONFIG_PADRAO.intervalo_decisao_ticks
    fontes = {"fruta": cm.cheiro_fruta, "racao": cm.cheiro_racao}
    return {
        "parametros": {"sub": cm.sub, "raio_cheiro": cm.raio_cheiro_celulas * cm.sub, "raio_visao": cm.raio_visao_celulas * cm.sub,
                       "raio_pegar": cm.raio_pegar_celulas * cm.sub, "alcance_por_decisao": alcance,
                       "passo_cheiro": cm.passo_cheiro_celulas * cm.sub, "limiar_cheiro_explorar": cm.limiar_cheiro_explorar,
                       "A": fontes, "passo_grade_a": passo_a, "passo_grade_bc": passo_bc, "max_decisoes": MAX_DECISOES},
        "exemplo_do_a": exemplo_do_a(cm),
        "direcao": {nome: parte_a(cm, a, passo_a) for nome, a in fontes.items()},
        "comer": {nome: parte_b(cm, a, alcance, passo_bc) for nome, a in fontes.items()},
        "explorar": {nome: parte_c(cm, a, alcance, passo_bc) for nome, a in fontes.items()},
        "vidas": parte_vidas(cm),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", default=str(RAIZ / "artifacts_v2_mundo_cerebros" / "empates_cheiro.json"))
    args = ap.parse_args()
    resultado = analisar()
    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(resultado, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"exemplo_do_a": resultado["exemplo_do_a"], "vidas": resultado["vidas"]}, indent=1))
    for nome in ("fruta", "racao"):
        for regra in REGRAS:
            a, b, c = resultado["direcao"][nome][regra], resultado["comer"][nome][regra], resultado["explorar"][nome][regra]
            print(f"{nome:6s} {regra:8s} empate {a['frac_empate']:.3f} semdir {a['frac_sem_direcao']:.4f} "
                  f"erro {a['erro_abs_graus']['media']:.1f} vies {a['erro_assinado_medio_graus']:+.2f} | comer +dec "
                  f"{b['decisoes_a_mais'].get('media', float('nan')):.3f} trava {b['frac_travou']:.4f} | explorar visao "
                  f"{c['frac_chega_a_visao']:.3f} achou {c['frac_achou_e_comeu']:.3f}")


if __name__ == "__main__":
    main()
