"""A bancada da cooperacao (docs/PLANO_ANALISE_V3_COOPERACAO.md, APROVADO em 2026-11-12; missao CB1): os braços, as vidas e as medidas.

Uma vida e um grupo de dois pets do mesmo dono (o atencioso nos dois, CB-4), nascidos juntos, por 8 dias (CB-5), com o DigiBrain modular
nos dois (a CB-2: o modular entrou no `Grupo` do Python pela CO6a; experiments/exportar_gabarito_co6.py) e a comida do dono no comedouro
comum (CB-3). Cada semente roda em todos os braços (secao 2.2 do plano); o motor e deterministico, e a diferenca entre braços e por semente.

Os braços (CB-6), todos com a cooperacao, a CO6 e a CO7 ligadas NO GRUPO (a medida e o `k`; a CO7 no grupo sozinha nao muda nada, o
`test_g2_a_co7_no_grupo_sem_ela_no_cerebro_e_a_vida_da_co6`), e o que muda e a configuracao que cada CEREBRO recebe:
  B0    o cerebro sem a CO7 (o sinal chega e ninguem usa; pelo G-SEM-DECISAO-CO6, a vida de hoje)
  B1    a CO7 inteira nos dois cerebros
  D0    B1 com os tetos do `k` x 0 (no grupo): o escudo e o peso nunca agem; so a culpa e a inveja
  DM    B1 com os tetos do `k` x 1/2 (o "D½" do plano)
  B1E   so o escudo (w_univ, w_culpa e w_inveja em 0)
  B1U   so o peso da universalizacao (o limiar do escudo na escala S, que o `k` nunca alcanca: o teto do adulto e 3/4 S; sem culpa e inveja)
  B1A   so a culpa e a inveja (sem o peso e sem o escudo)
  RM    a CO7 so no pet A; o B sem ela (o "R-" do plano: o irmao que nao retribui pela CO7)

As medidas (secao 3 do plano) saem do que o pet via ao decidir (a Observacao que o cerebro recebe) e do que o grupo registrou depois de cada
decisao (quem comeu o que, a fome e o humor), lidos por quem mede, igual em todos os braços, sem mudar nada dentro da vida:
  P1  a oportunidade (o outro aflito a vista indo para uma comida madura que o pet ve, a ate `r_escudo_celulas`, mais perto dela que na
      decisao anterior em que o pet o via; o proprio pet fora da privacao) e o desfecho (nas `JANELA_P1` decisoes seguintes do pet, quem comeu
      aquela comida foi o aflito). A conta da oportunidade e a do escudo (digilab/digibrain/dever.py: `social` e o laco de `situacao`),
      refeita aqui com a configuracao da medida (a CO7 padrao), e nao a do cerebro.
  P2  o piso diario do humor do par (D-MM-14: o menor dos dois primeiro), na media dos dias 1 a 8
  P3  a fracao das decisoes do proprio pet com a fome abaixo do piso (a privacao), dias 1 a 8 (H-CUSTO; por decisao, nao por tick: o
      grupo registra a fome na decisao)
  P4  os atos da CO3 (contencoes, disputas "anti" e encostos) por oportunidade, descritivo
  P5  o `k` medio de cada pet por estagio e a fracao das decisoes com o `k` no limiar do escudo ou acima
  P6  a distancia entre os habitos dos dois pets (L1 entre as frequencias das acoes escolhidas), descritivo

    python experiments/run_v3_cooperacao_bancada.py --sementes 101,202 --bracos B0,B1 --saida /tmp/x.jsonl    # a fumaca
    python experiments/run_v3_cooperacao_bancada.py --faixa 91101 40 --bracos B0,B1 --processos 4 --saida ...   # o piloto (CB2)

O adendo 1 (secao 12 do plano, DECIDIDO em 2026-11-12): `--mundo irmao_aleatorio` poe no B o cerebro aleatorio do gabarito do mundo (o
`CerebroAleatorio`, D-CO7b-6), que provoca a situacao; a CO7 so no A, nos sete braços sem o RM. As medidas ganham a P1-neg (a parte das
oportunidades em que o proprio pet comeu a comida proibida) e a contagem da culpa e da inveja (a parte das decisoes do pet, a partir do dia 1,
em que cada uma passou de 0, do campo `dever` dos motivos do modular).

Nenhuma vida principal roda antes do registro da analise (secao 10 do plano). O orquestrador recusa as faixas principais (91201 em diante,
fora dos pilotos 91101-91140 e 92101-92140) sem `--registro` apontando para o commit do registro.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co6 as e6  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

from digilab.config import CONFIG_COOPERACAO_CO7, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.digibrain import dever as dv  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import Grupo, PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402

DIAS = 8                                  # CB-5
DONO = "atencioso"                        # CB-4
LUGAR = "comedouro"                       # CB-3
JANELA_P1 = 4                             # decisoes do pet (plano, 3.1; PROPOSTO)
FAIXA_PILOTO = (91101, 91140)             # plano, secao 6
FAIXA_PILOTO_AD1 = (92101, 92140)         # plano, 12.5
MUNDOS = ("cb4", "irmao_aleatorio")
INICIO_PRINCIPAL = 91201
CMED = CONFIG_COOPERACAO_CO7              # a configuracao da medida (a CO7 padrao)
S = CMED.escala
CM = e6.CM
R_ESCUDO = CMED.r_escudo_celulas * CM.sub
BRACOS = ("B0", "B1", "D0", "DM", "B1E", "B1U", "B1A", "RM")


def _tetos(cfg, num: int, den: int):
    return replace(cfg, k_teto_bebe=cfg.k_teto_bebe * num // den, k_teto_crianca=cfg.k_teto_crianca * num // den,
                   k_teto_adolescente=cfg.k_teto_adolescente * num // den, k_teto_adulto=cfg.k_teto_adulto * num // den)


def configs(braco: str):
    """(a ConfigCooperacao do grupo, a do cerebro de A, a do cerebro de B); None no cerebro = sem a CO7"""
    c7 = CONFIG_COOPERACAO_CO7
    if braco == "B0":
        return c7, None, None
    if braco == "B1":
        return c7, c7, c7
    if braco == "D0":
        return _tetos(c7, 0, 1), c7, c7
    if braco == "DM":
        return _tetos(c7, 1, 2), c7, c7
    if braco == "B1E":
        e = replace(c7, w_univ=0, w_culpa=0, w_inveja=0)
        return c7, e, e
    if braco == "B1U":
        u = replace(c7, limiar_escudo=c7.escala, w_culpa=0, w_inveja=0)
        return c7, u, u
    if braco == "B1A":
        a = replace(c7, limiar_escudo=c7.escala, w_univ=0)
        return c7, a, a
    if braco == "RM":
        return c7, c7, None
    raise ValueError(f"braco desconhecido: {braco!r} (os do plano: {BRACOS})")


class Coleta:
    """o que quem mede le, por pet: antes de cada decisao (a Observacao do cerebro) e depois (o que o grupo registrou)"""

    def __init__(self) -> None:
        self.ident_de: dict[int, str] = {}           # id(cerebro) -> pet
        self.antes: dict[str, list] = {}             # pet -> [o que via em cada decisao]
        self.depois: dict[str, list] = {}            # pet -> [(tick, fome_antes, comeu, humor) de cada decisao]
        self._pos_antes: dict[str, dict] = {}        # pet -> {outro: a posicao em que o viu na ultima decisao em que o via}

    def ver(self, cerebro, obs) -> None:
        ident = self.ident_de.get(id(cerebro))
        if ident is None:
            return
        ps, mu = obs.social, obs.mundo
        pos = (mu.x, mu.y)
        antes = self._pos_antes.setdefault(ident, {})
        soc = dv.social(ps, pos, antes, R_ESCUDO)
        comidas = [(v[0], mu.x + v[2], mu.y + v[3]) for v in mu.vistos if v[1] in dv.COMIDAS_MADURAS]
        proibidas = []
        if soc is not None:
            for cid, cx, cy in comidas:                   # o laco de dever.situacao, com a configuracao da medida
                for o in soc["outros"]:
                    if not o["aflito"] or o["antes"] is None:
                        continue
                    agora = dv._d2(o["x"], o["y"], cx, cy)
                    if agora <= soc["r2_escudo"] and agora < dv._d2(o["antes"][0], o["antes"][1], cx, cy):
                        proibidas.append((cid, o["id"]))
                        break
            for o in soc["outros"]:                       # o estado do M-SENS da CO7, atualizado como ele (a posicao vista agora)
                antes[o["id"]] = (o["x"], o["y"])
        self.antes.setdefault(ident, []).append({"k": None if ps is None else ps.peso_dever, "proibidas": proibidas})

    def registrar(self, grupo, ident: str) -> None:
        m = grupo.motores[ident]
        ts = grupo._no_tick(m)
        comeu = None if ts is None or ts["comeu"] is None else ts["comeu"]["id"]
        self.depois.setdefault(ident, []).append((grupo.tick, m._fome_antes, comeu, m._estado.humor, m._acao_atual.value))


def _fabrica_cerebro(coleta: Coleta, ident: str, semente_pet: int, cco):
    cd = orq.config_do_braco(e6.BRACO, conserto=True)

    def fp(cfg=None):
        c = DigiBrain(cfg or CONFIG_PADRAO, cd, CM, semente=semente_pet, cfg_cooperacao=cco)
        coleta.ident_de[id(c)] = ident
        return c
    return fp


def _fabrica_motor(semente_pet: int, dias: int):
    from digilab.motor_corpo import com_corpo
    from digilab.mundo import MotorMundo
    from digilab.temperamento import NEUTRO
    cc = orq.bancada(dias, orq.ORCAMENTO_POR_DIA).cfg_corpo_de(orq.bv.EspecVida(DONO, orq.gl.BRACO_V11, semente_pet))

    def fm(politica, cfg, s, **kw):
        return com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc, **kw)
    return fm


def rodar_vida(semente: int, braco: str, dias: int = DIAS, mundo: str = "cb4"):
    """(o grupo, a coleta) de uma vida do braco; no `irmao_aleatorio` (o adendo 1), o B e o cerebro aleatorio, sem coleta de antes"""
    if mundo not in MUNDOS:
        raise ValueError(f"mundo desconhecido: {mundo!r} ({MUNDOS})")
    if mundo == "irmao_aleatorio" and braco == "RM":
        raise ValueError("o RM nao existe no adendo 1 (AD1-3): o irmao aleatorio nao retribui")
    cco_grupo, cco_a, cco_b = configs(braco)
    ss = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    coleta = Coleta()
    pets = []
    for ident, cco in (("A", cco_a), ("B", cco_b)):
        if mundo == "irmao_aleatorio" and ident == "B":
            from exportar_gabarito_mundo import CerebroAleatorio
            fp, rotulo = (lambda cfg=None: CerebroAleatorio(cfg or CONFIG_PADRAO)), "aleatorio"
        else:
            fp, rotulo = _fabrica_cerebro(coleta, ident, ss[ident], cco), "digibrain"
        d = DonoComLugar(criar_dono(DONO), LUGAR, ss[ident], DONO, CM)
        pets.append(PetDoGrupo(ident, 0, fp, _fabrica_motor(ss[ident], dias), d, DONO, rotulo))
    agir0, coop0 = DigiBrain.agir, Grupo._coop_decisao

    def agir(self, obs, rng):
        coleta.ver(self, obs)
        return agir0(self, obs, rng)

    def coop(self, ident, presentes):
        coop0(self, ident, presentes)
        coleta.registrar(self, ident)
    DigiBrain.agir, Grupo._coop_decisao = agir, coop
    try:
        g = simular_grupo(CM, semente, pets, dias, cfg_cooperacao=cco_grupo)
    finally:
        DigiBrain.agir, Grupo._coop_decisao = agir0, coop0
    for i in coleta.antes:
        if len(coleta.antes.get(i, [])) != len(coleta.depois.get(i, [])):
            raise RuntimeError(f"a coleta do pet {i} nao casou: {len(coleta.antes.get(i, []))} vistas x {len(coleta.depois.get(i, []))} decisoes")
    return g, coleta


def _estagio(tick: int) -> str:
    from digilab.config import ConfigExpressao
    ce, dia = ConfigExpressao(), tick / TICKS_POR_DIA
    return ("bebe" if dia < ce.dias_fim_bebe else "crianca" if dia < ce.dias_fim_crianca
            else "adolescente" if dia < ce.dias_fim_adolescente else "adulto")


def medidas(g, coleta: Coleta) -> dict:
    """as medidas P1 a P6 de uma vida (a docstring do modulo)"""
    piso = CMED.piso_fome
    ids = sorted(g.motores)
    comidas_comidas = {}                                  # id da comida -> (tick, quem comeu), a primeira vez
    for i in ids:
        for tick, _f, comeu, _h, _a in coleta.depois[i]:
            if comeu is not None and comeu not in comidas_comidas:
                comidas_comidas[comeu] = (tick, i)
    p1_op, p1_fav, por_pet = 0, 0, {}
    p3, p5, acoes, culpa_inveja = {}, {}, {}, {}
    for i in ids:
        acoes[i] = Counter(a for t, _f, _c, _h, a in coleta.depois[i] if t >= TICKS_POR_DIA)
    for i in [i for i in ids if i in coleta.antes]:
        vistas, depois = coleta.antes[i], coleta.depois[i]
        op_i = fav_i = neg_i = 0
        priv = dec = 0
        kk: dict[str, list] = {}
        no_limiar = 0
        for n, (vi, de) in enumerate(zip(vistas, depois)):
            tick, fome, _comeu, _h, _acao = de
            if tick < TICKS_POR_DIA:                      # a P1, a P3 e a P5 a partir do dia 1 (a crianca)
                continue
            dec += 1
            priv += fome < piso
            if vi["k"] is not None:
                kk.setdefault(_estagio(tick), []).append(vi["k"])
                no_limiar += vi["k"] >= CMED.limiar_escudo
            if fome < piso:
                continue
            fim = depois[min(n + JANELA_P1, len(depois) - 1)][0]
            for cid, aflito in vi["proibidas"]:
                op_i += 1
                quem = comidas_comidas.get(cid)
                fav_i += quem is not None and tick <= quem[0] <= fim and quem[1] == aflito
                neg_i += quem is not None and tick <= quem[0] <= fim and quem[1] == i
        p1_op, p1_fav = p1_op + op_i, p1_fav + fav_i
        por_pet[i] = {"oportunidades": op_i, "favoraveis": fav_i, "proprio_comeu": neg_i}
        p3[i] = priv / dec if dec else None
        p5[i] = {"k_medio": {e: sum(v) / len(v) for e, v in sorted(kk.items())}, "no_limiar": no_limiar / dec if dec else None}
        mot = getattr(g.motores[i].politica, "motivos", None) or []
        ds = [m.get("dever") for m, de in zip(mot, depois) if de[0] >= TICKS_POR_DIA]
        ds = [d for d in ds if d]
        culpa_inveja[i] = None if not ds else {"decisoes": len(ds), "culpa": sum(d.get("culpa", 0) > 0 for d in ds) / len(ds),
                                               "inveja": sum(d.get("inveja", 0) > 0 for d in ds) / len(ds)}
    # P2: o piso diario do humor do par
    pisos = []
    for dia in range(1, DIAS):
        medias = []
        for i in ids:
            hs = [h for t, _f, _c, h, _a in coleta.depois[i] if dia * TICKS_POR_DIA <= t < (dia + 1) * TICKS_POR_DIA]
            if hs:
                medias.append(sum(hs) / len(hs))
        if len(medias) == len(ids):
            pisos.append(min(medias))
    # P4: os atos da CO3
    atos = g.resumo()["cooperacao"]["atos"]
    p4 = {"contencao": sum(a["ato"] == "contencao" for a in atos), "encostar": sum(a["ato"] == "encostar" for a in atos),
          "disputa_anti": sum(a["ato"] == "disputa" and a.get("sinal", 0) < 0 for a in atos)}
    # P6: L1 entre as frequencias das acoes
    todas = sorted(set(acoes[ids[0]]) | set(acoes[ids[1]]))
    tot = [sum(acoes[i].values()) or 1 for i in ids]
    p6 = sum(abs(acoes[ids[0]][a] / tot[0] - acoes[ids[1]][a] / tot[1]) for a in todas)
    return {"P1": None if p1_op == 0 else p1_fav / p1_op, "P1_oportunidades": p1_op, "P1_favoraveis": p1_fav, "P1_por_pet": por_pet,
            "P2": sum(pisos) / len(pisos) if pisos else None, "P3": p3, "P4": p4, "P5": p5, "P6": p6, "culpa_inveja": culpa_inveja}


def conferir(g, coleta: Coleta, braco: str) -> None:
    """as travas da secao 5 que se conferem dentro de cada vida (falham alto)"""
    cco_grupo, cco_a, cco_b = configs(braco)
    if braco == "D0":
        for i in coleta.antes:
            ks = [v["k"] for v in coleta.antes[i] if v["k"] is not None]
            if any(k >= CMED.limiar_escudo for k in ks):
                raise RuntimeError(f"D0: o k do pet {i} chegou ao limiar do escudo")
    for i, cco in (("A", cco_a), ("B", cco_b)):           # o G-ESCUDO: nenhum cerebro com o escudo come a comida proibida
        if cco is None or i not in coleta.antes:
            continue
        for mt in [g.motores[i]]:
            for m in mt.politica.motivos:
                d, esc = m.get("dever"), m["escolha"]
                if d and d["escudo"] and d["proibidas"] and esc[0] == "comer" and esc[1] == "comida" and esc[2] in d["proibidas"]:
                    raise RuntimeError(f"G-ESCUDO: o pet {i} comeu a comida proibida ({braco}): {esc}")


def checar_faixa(sementes: list[int], registro: str | None) -> None:
    """a trava da secao 10: a faixa principal (91201 em diante) so com o commit do registro da analise"""
    def piloto(s: int) -> bool:
        return FAIXA_PILOTO[0] <= s <= FAIXA_PILOTO[1] or FAIXA_PILOTO_AD1[0] <= s <= FAIXA_PILOTO_AD1[1]
    if any(s >= INICIO_PRINCIPAL and not piloto(s) for s in sementes) and not registro:
        raise SystemExit("a faixa principal (91201 em diante) so roda com --registro (o commit do registro da analise, secao 10 do plano)")


def uma(args: tuple) -> dict:
    semente, braco, dias, mundo = args
    t0 = time.perf_counter()
    g, c = rodar_vida(semente, braco, dias, mundo)
    conferir(g, c, braco)
    return {"semente": semente, "braco": braco, "dias": dias, "mundo": mundo, "segundos": round(time.perf_counter() - t0, 2),
            "medidas": medidas(g, c)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    gr = ap.add_mutually_exclusive_group(required=True)
    gr.add_argument("--sementes", help="lista separada por virgula (a fumaca: as dos testes)")
    gr.add_argument("--faixa", nargs=2, type=int, metavar=("INICIO", "N"), help="N sementes a partir de INICIO, sem pular")
    ap.add_argument("--bracos", default=",".join(BRACOS))
    ap.add_argument("--dias", type=int, default=DIAS)
    ap.add_argument("--mundo", default="cb4", choices=MUNDOS, help="cb4 (a CB4) ou irmao_aleatorio (o adendo 1)")
    ap.add_argument("--processos", type=int, default=1, help="ate 4 (a maquina; memoria maquina-instavel-carga-total)")
    ap.add_argument("--registro", help="o commit do registro da analise (secao 10): exigido para a faixa principal")
    ap.add_argument("--saida", required=True, help="o .jsonl das vidas (fora do git: experiments/runs/cooperacao_bancada/)")
    a = ap.parse_args()
    sementes = ([int(x) for x in a.sementes.split(",")] if a.sementes else list(range(a.faixa[0], a.faixa[0] + a.faixa[1])))
    checar_faixa(sementes, a.registro)
    if a.processos > 4:
        raise SystemExit("no maximo 4 processos (a maquina)")
    bracos = a.bracos.split(",")
    if a.mundo == "irmao_aleatorio" and a.bracos == ",".join(BRACOS):
        bracos = [b for b in BRACOS if b != "RM"]
    for b in bracos:
        configs(b)
        if a.mundo == "irmao_aleatorio" and b == "RM":
            raise SystemExit("o RM nao existe no adendo 1 (AD1-3)")
    tarefas = [(s, b, a.dias, a.mundo) for s in sementes for b in bracos]
    saida = Path(a.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    feitas = set()
    if saida.exists():                                    # retomar: as vidas ja gravadas nao rodam de novo
        for linha in saida.read_text(encoding="utf-8").splitlines():
            r = json.loads(linha)
            feitas.add((r["semente"], r["braco"], r["dias"], r.get("mundo", "cb4")))
    tarefas = [t for t in tarefas if t not in feitas]
    t0 = time.perf_counter()
    with saida.open("a", encoding="utf-8") as f:
        if a.processos == 1:
            it = map(uma, tarefas)
        else:
            from multiprocessing import Pool
            pool = Pool(a.processos)
            it = pool.imap_unordered(uma, tarefas)
        for n, r in enumerate(it, 1):
            f.write(json.dumps(r, sort_keys=True) + "\n")
            f.flush()
            print(f"[{n}/{len(tarefas)}] {r['semente']} {r['braco']}: P1 {r['medidas']['P1']} "
                  f"({r['medidas']['P1_oportunidades']} oportunidades), {r['segundos']} s", flush=True)
    print(f"feito: {len(tarefas)} vidas em {time.perf_counter() - t0:.0f} s -> {saida}")


if __name__ == "__main__":
    main()
