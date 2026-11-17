"""A sonda do E(P) da F5 (docs/ESPEC_V3_SONDA_EMPOWERMENT.md; APROVADO pelo Matheus em 2026-11-17, "Aprovo as recomendacoes"). So
leitura: nenhuma vida nova, nenhuma semente nova, nenhuma faixa. O motor, o `engine.py`, o corpo, o DigiBrain e a web nao mudam: a
leitura de cada decisao entra embrulhando, na instancia do cerebro, o `Impulso.unidades` (o jeito da auditoria da PET_VIVO,
`experiments/auditoria_pet_vivo.py`) e o `agir` (so para ver a rng de politica e conferir o G-S1). As contas sao puras e em inteiros.

A conta (espec, secao 2), em cada decisao e em cada lugar P:
  - os pontos de classe c: o `ponto` de cada episodio guardado do M-MEM (a memoria de lugar e a autobiografica) com
    `origem = "consumo"`, e a posicao de cada objeto visto (`pos + (dx, dy)`: a `sens` guarda o objeto relativo ao pet), com c em
    `CLASSES_DESFECHO`;
  - A(P), as classes com algum ponto a `dist <= d_max` de P, cada uma com o ponto mais perto;
  - as sequencias de 0, 1 ou 2 classes de A(P), sem repetir (D-F5-3, D-F5-4), com o caminho `d(P, c1)` mais, na segunda, a distancia
    entre os dois pontos;
  - o corpo previsto `v_r = clamp(leitura_r + sum d[c_i, r] + [r = energia] div_arred(andar x caminho, S), 0, S)`. O `andar` e a mudanca
    da energia por subunidade andada, x S (negativo quando andar cansa): ele entra somado, como no `valor_previsto` do lobos
    (`digilab/policies/lobos.py:2168`). A espec aprovada tinha o sinal trocado; a correcao esta anotada nela (secao 2.4);
  - a tupla `(_faixa(v_r, S) for r)`, com a faixa do M-MEM (D-F5-5). E(P) = o numero de tuplas distintas; CONT(P) = |A(P)|.
Os lugares P: o do pet, os dos episodios guardados e os dos alvos `explorar/ponto` das unidades da decisao, sem repetir, cada um pelo
centro. Nenhuma rng e chamada; o G-S1 confere o estado de cada rng antes e depois de cada leitura.

As vidas (D-F5-2, a (a)): os gabaritos das sementes dos testes, as mesmas da AN0 da PET_VIVO (`auditoria_pet_vivo.vidas_an0`), refeitas no
codigo de hoje e conferidas contra o gabarito (o G-S0: o log, o estado e os motivos).

    python experiments/sonda_empowerment_f5.py --medir-tempo        # so o tempo por decisao numa semente dos testes (sem medida)
    python experiments/sonda_empowerment_f5.py --processos 4         # a medida (SE2): so com o plano de analise commitado (D-F5-8)
grava artifacts_v3_f5_sonda/sonda.json e sonda_decisoes.json.gz (o `--medir-tempo` grava so tempo.json)

A (b2) do adendo 1 (docs/PLANO_ANALISE_V3_SONDA_EMPOWERMENT_ADENDO1.md, APROVADO em 2026-11-17, "Aprovo a (b2)"): as mesmas oito celulas
da AN0, vidas novas no CONFIG_MUNDO_ILHA com o sacudir ligado, as sementes dos testes. O gabarito vai num commit proprio, antes da medida.

    python experiments/sonda_empowerment_f5.py --gravar-gabarito-b2 --processos 4   # grava tests/gabaritos/sonda_f5_b2.json
    python experiments/sonda_empowerment_f5.py --b2 --processos 4                   # a medida da (b2): artifacts_v3_f5_sonda/b2/
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _p in (RAIZ, RAIZ / "experiments"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from digilab.digibrain._comum import clamp  # noqa: E402
from digilab.digibrain.base import div_arred  # noqa: E402
from digilab.digibrain.mem import _faixa  # noqa: E402
from digilab.digibrain.plast import CLASSES_DESFECHO  # noqa: E402
from digilab.modelo_mundo import raiz_inteira  # noqa: E402

SAIDA = RAIZ / "artifacts_v3_f5_sonda"
PLANO = RAIZ / "docs" / "PLANO_ANALISE_V3_SONDA_EMPOWERMENT.md"
MAX_PROCESSOS = 4                                                   # V3-D8
HORIZONTE = 2                                                       # D-F5-3
LIMIAR_PLANO = (1, 10)                                              # D-F5-7, PROPOSTO, SEM FONTE: amplitude >= 2 em menos de 1/10
LIMIAR_CONT = (1, 20)                                               # D-F5-7, PROPOSTO, SEM FONTE: pares discordantes abaixo de 1/20


# ================================================================== as contas puras (espec, secao 2)
def dist(a: tuple, b: tuple) -> int:
    dx, dy = a[0] - b[0], a[1] - b[1]
    return raiz_inteira(dx * dx + dy * dy)


def pontos_de(episodios: list[dict], objetos: list[dict], pos: tuple) -> list[tuple]:
    """[(classe, (x, y))]: os episodios de consumo na ordem guardada, depois os objetos vistos na ordem da `sens`"""
    out = [(e["classe"], (e["ponto"][0], e["ponto"][1])) for e in episodios
           if e["origem"] == "consumo" and e["classe"] in CLASSES_DESFECHO]
    out += [(o["classe"], (pos[0] + o["dx"], pos[1] + o["dy"])) for o in objetos if o["classe"] in CLASSES_DESFECHO]
    return out


def alcance(P: tuple, pontos: list[tuple], d_max: int) -> dict:
    """A(P): {classe: (distancia, ponto)} das classes com algum ponto a dist <= d_max de P, com o ponto mais perto (no empate, o
    primeiro da lista), na ordem de CLASSES_DESFECHO"""
    melhor: dict = {}
    for c, pt in pontos:
        d = dist(P, pt)
        if d <= d_max and (c not in melhor or d < melhor[c][0]):
            melhor[c] = (d, pt)
    return {c: melhor[c] for c in CLASSES_DESFECHO if c in melhor}


def corpos(alc: dict, leitura: list, desfecho: dict, andar: int, i_energia: int | None, S: int) -> set:
    """as tuplas de faixas distintas das sequencias de 0 a HORIZONTE classes de A(P), sem repetir classe (espec, 2.4)"""
    def tupla(classes: tuple, caminho: int) -> tuple:
        out = []
        for i, base in enumerate(leitura):
            v = base + sum(desfecho[c][i] for c in classes)
            if i == i_energia:
                v += div_arred(andar * caminho, S)
            out.append(_faixa(clamp(v, 0, S), S))
        return tuple(out)

    vistos = {tupla((), 0)}
    classes = list(alc)
    for c1 in classes:
        d1, p1 = alc[c1]
        vistos.add(tupla((c1,), d1))
        if HORIZONTE >= 2:
            for c2 in classes:
                if c2 != c1:
                    vistos.add(tupla((c1, c2), d1 + dist(p1, alc[c2][1])))
    return vistos


def e_de(alc: dict, leitura: list, desfecho: dict, andar: int, i_energia: int | None, S: int) -> int:
    return len(corpos(alc, leitura, desfecho, andar, i_energia, S))


def cont_de(alc: dict) -> int:
    return len(alc)


def centro(lugar: tuple, sub: int) -> tuple:
    return lugar[0] * sub + sub // 2, lugar[1] * sub + sub // 2


def episodios_de(memoria) -> list[dict]:
    """os episodios guardados do M-MEM: a memoria de lugar (`episodios`, o n_ep) e, com a memoria autobiografica, as tres camadas dela
    (`_guardados`), nessa ordem. As duas guardam consumos: a de lugar todo consumo, a autobiografica so o que passa do limiar"""
    return list(memoria.episodios) + (memoria._guardados() if getattr(memoria, "autobio", False) else [])


def ler_decisao(sens: dict, unidades: list[dict], plast, memoria) -> dict:
    """a leitura pura de uma decisao: {"lugar": o do pet, "P": [[lugar, E, CONT], ...], "candidatos": [lugar dos explorar/ponto]}"""
    S = plast.S
    recs = plast.receptores
    leitura = [sens["leitura"][r] for r in recs]
    i_en = recs.index("energia") if "energia" in recs else None
    sub, d_max = memoria.sub, memoria.p.d_max
    pos = tuple(sens["pos"])
    eps = episodios_de(memoria)
    pontos = pontos_de(eps, sens["objetos"], pos)
    lugar_pet = memoria.lugar_de(*pos)
    lugares = [lugar_pet]
    for e in eps:
        lg = tuple(e["lugar"])
        if lg not in lugares:
            lugares.append(lg)
    candidatos = []
    for u in unidades:
        ch = u["chave"]
        if ch[0] == "explorar" and ch[1] == "ponto":
            lg = memoria.lugar_de(*ch[2])
            candidatos.append(lg)
            if lg not in lugares:
                lugares.append(lg)
    linhas = []
    for lg in lugares:
        alc = alcance(centro(lg, sub), pontos, d_max)              # todo lugar pelo centro (espec, 2.2), o do pet tambem
        linhas.append([list(lg), e_de(alc, leitura, plast.desfecho, plast.andar, i_en, S), cont_de(alc)])
    return {"lugar": list(lugar_pet), "P": linhas, "candidatos": [list(c) for c in candidatos]}


# ================================================================== o coletor (o embrulho do Impulso.unidades e do agir)
def _rngs_soltas(cerebro) -> list:
    out = []
    for mod in vars(cerebro.m).values():
        for x in vars(mod).values() if hasattr(mod, "__dict__") else ():
            if isinstance(x, random.Random):
                out.append(x)
    return out


def _estado_rngs(rngs: list) -> str:
    h = hashlib.sha256(repr(random.getstate()).encode())
    for r in rngs:
        h.update(repr(r.getstate()).encode())
    return h.hexdigest()


class Coletor:
    """guarda, por decisao, a `ler_decisao` sobre o estado do M-PLAST e do M-MEM da decisao. Nao muda estado nem chama rng: o G-S1
    confere o estado da rng de politica (vista no `agir`), da `random` global e das rngs dos modulos antes e depois de cada leitura"""

    def __init__(self, cerebro) -> None:
        self.c, self.m = cerebro, cerebro.m
        self.orig_u, self.orig_agir = self.m.impulso.unidades, cerebro.agir
        self.rng = None
        self.soltas = _rngs_soltas(cerebro)
        self.registros: list[dict] = []
        self.leituras_rng = 0
        self.t = 0.0
        self.m.impulso.unidades = self.unidades
        cerebro.agir = self.agir

    def soltar(self) -> None:
        del self.m.impulso.unidades
        del self.c.agir

    def agir(self, obs, rng):
        self.rng = rng
        return self.orig_agir(obs, rng)

    def unidades(self, sens, *args, **kw):
        out = self.orig_u(sens, *args, **kw)
        if self.rng is None:
            raise RuntimeError("G-S1: a rng de politica nao passou pelo agir")
        rngs = [self.rng] + self.soltas
        antes = _estado_rngs(rngs)
        t0 = time.perf_counter()
        reg = ler_decisao(sens, out[0], self.m.plast, self.m.mem)
        self.t += time.perf_counter() - t0
        if _estado_rngs(rngs) != antes:
            raise RuntimeError(f"G-S1: a leitura da decisao {len(self.registros)} mudou uma rng")
        self.leituras_rng += 1
        reg["k"], reg["minuto"] = len(self.registros), sens["minuto"]
        self.registros.append(reg)
        return out


# ================================================================== as vidas (D-F5-2 (a)) e o G-S0
def vidas() -> list[tuple]:
    import auditoria_pet_vivo as aud
    return aud.vidas_an0()


def gabaritos() -> dict:
    import auditoria_pet_vivo as aud
    return aud.gabaritos()


def viver(arquivo: str, dono: str, lugar: str, semente: int, com_sonda: bool) -> tuple:
    """(o motor, o cerebro, o coletor ou None) da vida do gabarito, refeita no codigo de hoje"""
    import exportar_gabarito_digibrain_modular as gab
    from bancada.regras_mundo import simular_vida_fisico
    from digilab.config import CONFIG_PADRAO
    from digilab.donos import criar_dono
    from digilab.mundo import DonoComLugar
    orq = gab.orq
    fp, fm = orq.fabricas(gab.BRACO, dono, semente, gab.DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
    registro = fp(CONFIG_PADRAO)
    cerebro = orq.cerebro_de(registro)
    col = Coletor(cerebro) if com_sonda else None
    try:
        d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
        motor, _ = simular_vida_fisico(d, registro, semente, gab.DIAS, orq.ORCAMENTO_POR_DIA * gab.DIAS, dono, fm)
    finally:
        if col is not None:
            col.soltar()
    return motor, cerebro, col


def assinatura(motor, cerebro) -> dict:
    import exportar_gabarito_digibrain_modular as gab
    return {"log": hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest(),
            "estado": hashlib.sha256(gab._texto(gab.paraj(cerebro.estado_interno())).encode("utf-8")).hexdigest(),
            "motivos": [gab.paraj(x) for x in cerebro.motivos]}


def conferir_gs0(a: dict, gabarito: dict, rotulo: str) -> None:
    if a["log"] != gabarito["log"] and a["log"] != gabarito.get("log_sha256"):
        raise RuntimeError(f"G-S0: o log de {rotulo} nao e o do gabarito")
    if a["estado"] != gabarito["estado"]:
        raise RuntimeError(f"G-S0: o estado de {rotulo} nao e o do gabarito")
    if [x["motivo"] for x in gabarito["decisoes"]] != a["motivos"]:
        raise RuntimeError(f"G-S0: os motivos de {rotulo} nao sao os do gabarito")


def sondar(tarefa: tuple) -> dict:
    """uma vida: refeita com o coletor, o G-S0 contra o gabarito, e o registro por decisao com a escolha"""
    arquivo, dono, lugar, semente, _aj, gabarito = tarefa
    rotulo = f"{arquivo}|{dono}|{lugar}|{semente}"
    t0 = time.perf_counter()
    motor, cerebro, col = viver(arquivo, dono, lugar, semente, True)
    a = assinatura(motor, cerebro)
    conferir_gs0(a, gabarito, rotulo)
    if len(col.registros) != len(a["motivos"]) or col.leituras_rng != len(col.registros):
        raise RuntimeError(f"{rotulo}: {len(col.registros)} leituras para {len(a['motivos'])} decisoes")
    for reg, mot in zip(col.registros, a["motivos"]):
        esc = mot["escolha"]
        reg["escolha"] = esc
        reg["alvo"] = (list(cerebro.m.mem.lugar_de(*esc[2])) if esc[0] == "explorar" and esc[1] == "ponto" else None)
    return {"vida": rotulo, "dono": dono, "lugar": lugar, "semente": semente, "log_sha256": a["log"],
            "parede_s": {"total": time.perf_counter() - t0, "sonda": col.t}, "decisoes": col.registros}


# ================================================================== as medidas (espec, secao 5), descritivas e em inteiros
def _quantis(xs: list[int]) -> dict:
    """o minimo, os quartis e o maximo pela posicao inteira (o elemento de indice (n-1) x q / 4)"""
    if not xs:
        return {"n": 0}
    s = sorted(xs)
    n = len(s)
    return {"n": n, "min": s[0], "q1": s[(n - 1) // 4], "mediana": s[(n - 1) // 2], "q3": s[3 * (n - 1) // 4], "max": s[-1]}


def pares(linhas: list) -> dict:
    """os pares de lugares de uma decisao pela contagem de Kendall: concordantes, discordantes, empate so no E, so no CONT, nos dois"""
    out = {"conc": 0, "disc": 0, "emp_E": 0, "emp_CONT": 0, "emp_ambos": 0}
    for i in range(len(linhas)):
        for j in range(i + 1, len(linhas)):
            de = (linhas[i][1] > linhas[j][1]) - (linhas[i][1] < linhas[j][1])
            dc = (linhas[i][2] > linhas[j][2]) - (linhas[i][2] < linhas[j][2])
            if de == 0 and dc == 0:
                out["emp_ambos"] += 1
            elif de == 0:
                out["emp_E"] += 1
            elif dc == 0:
                out["emp_CONT"] += 1
            elif de == dc:
                out["conc"] += 1
            else:
                out["disc"] += 1
    return out


def medir(decisoes: list[dict]) -> dict:
    """M-S1, M-S2 e M-S3 sobre as decisoes dadas (de uma vida ou de todas)"""
    e_pet, amps, cont_pet = [], [], []
    soma_pares = {"conc": 0, "disc": 0, "emp_E": 0, "emp_CONT": 0, "emp_ambos": 0}
    s3 = {"decisoes": 0, "acertos": 0, "acaso_num": 0, "acaso_den": 1}
    acaso = Fraction(0)
    for d in decisoes:
        es = [x[1] for x in d["P"]]
        e_pet.append(d["P"][0][1])
        cont_pet.append(d["P"][0][2])
        amps.append(max(es) - min(es))
        for k, v in pares(d["P"]).items():
            soma_pares[k] += v
        if d.get("alvo") is not None and len(d["candidatos"]) >= 2:
            e_lugar = {tuple(x[0]): x[1] for x in d["P"]}
            ec = [e_lugar[tuple(c)] for c in d["candidatos"]]
            topo = max(ec)
            s3["decisoes"] += 1
            s3["acertos"] += e_lugar[tuple(d["alvo"])] == topo
            acaso += Fraction(sum(1 for x in ec if x == topo), len(ec))
    s3["acaso_num"], s3["acaso_den"] = acaso.numerator, acaso.denominator
    n = len(decisoes)
    total = sum(soma_pares.values())
    return {"decisoes": n,
            "M_S1": {"E_do_lugar_do_pet": _quantis(e_pet), "E_acima_de_1": [sum(1 for x in e_pet if x > 1), n],
                     "amplitude": _quantis(amps), "amplitude_2_ou_mais": [sum(1 for x in amps if x >= 2), n],
                     "CONT_do_lugar_do_pet_ate_1": [sum(1 for x in cont_pet if x <= 1), n]},
            "M_S2": {**soma_pares, "pares": total, "discordantes": [soma_pares["disc"], total]},
            "M_S3": s3}


def leitura(m: dict) -> dict:
    """a leitura registrada da espec, secao 5.4 (D-F5-7), em inteiros"""
    a, n = m["M_S1"]["amplitude_2_ou_mais"]
    d, t = m["M_S2"]["discordantes"]
    plano = n > 0 and a * LIMIAR_PLANO[1] < n * LIMIAR_PLANO[0]
    igual = None if t == 0 else d * LIMIAR_CONT[1] < t * LIMIAR_CONT[0]
    c1, nc = m["M_S1"].get("CONT_do_lugar_do_pet_ate_1", [0, n])
    pelas_entradas = bool(plano) and 2 * c1 > nc                    # o plano, secao 4 (D-F5-9, PROPOSTA)
    if pelas_entradas:
        linha = "plano pelas entradas: a F5 espera a decisao do Matheus sobre a opcao (b) da D-F5-2"
    elif plano or igual:
        linha = "a F5 acaba: " + " e ".join(x for x, f in (("plano", plano), ("igual ao CONT", igual)) if f)
    elif igual is None:
        linha = "sem pares de lugares: a M-S2 nao le"
    else:
        linha = "nem plano nem igual ao CONT: a H-EMP-1 vira um plano depois da F3"
    return {"plano": plano, "igual_ao_cont": igual, "plano_pelas_entradas": pelas_entradas, "linha": linha,
            "limiares": {"plano": list(LIMIAR_PLANO), "igual_ao_cont": list(LIMIAR_CONT)}}


# ================================================================== o principal
def medir_tempo(saida: Path = SAIDA) -> dict:
    gab = gabaritos()
    x = vidas()[0]
    v = sondar((*x, gab["vidas"][(x[0], x[1], x[2], x[3])]))
    n = len(v["decisoes"])
    out = {"vida": v["vida"], "decisoes": n, "parede_s": v["parede_s"], "sonda_por_decisao_ms": 1000 * v["parede_s"]["sonda"] / max(1, n)}
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "tempo.json").write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    return out


def principal(processos: int, saida: Path = SAIDA) -> dict:
    if not PLANO.exists():
        raise SystemExit(f"D-F5-8: o plano de analise {PLANO.name} nao existe; a medida espera ele commitado")
    if (saida / "sonda.json").exists():
        raise FileExistsError(f"{saida / 'sonda.json'} ja existe: a medida roda uma vez")
    if not 1 <= processos <= MAX_PROCESSOS:
        raise SystemExit(f"de 1 a {MAX_PROCESSOS} processos (V3-D8)")
    gab = gabaritos()
    tarefas = [(*x, gab["vidas"][(x[0], x[1], x[2], x[3])]) for x in vidas()]
    with ProcessPoolExecutor(max_workers=processos) as pool:
        res = list(pool.map(sondar, tarefas))
    todas = [d for v in res for d in v["decisoes"]]
    total = medir(todas)
    out = {"rotulo": "sonda descritiva do E(P) da F5, so leitura; nao e gate (espec, secao 5)",
           "fontes": {"gabaritos": gab["sha256"], "plano": hashlib.sha256(PLANO.read_bytes()).hexdigest()},
           "vidas": [{"vida": v["vida"], "log_sha256": v["log_sha256"], "parede_s": v["parede_s"], **medir(v["decisoes"])} for v in res],
           "todas": total, "leitura": leitura(total)}
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "sonda.json").write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    with gzip.open(saida / "sonda_decisoes.json.gz", "wt", encoding="utf-8") as f:
        json.dump([{"vida": v["vida"], "decisoes": v["decisoes"]} for v in res], f, sort_keys=True)
    return out


# ================================================================== a (b2) do adendo 1: vidas novas e curtas no mundo com arvores
ADENDO1 = RAIZ / "docs" / "PLANO_ANALISE_V3_SONDA_EMPOWERMENT_ADENDO1.md"
GABARITO_B2 = RAIZ / "tests" / "gabaritos" / "sonda_f5_b2.json"
SAIDA_B2 = SAIDA / "b2"
DONOS_B2 = ("atencioso", "relapso")                                 # adendo 1, secao 5: as celulas da AN0
LUGARES_B2 = ("comedouro", "longe_fixo")
SEMENTES_B2 = (101, 202)                                            # so as dos testes


def vidas_b2() -> list[tuple]:
    """as oito vidas da (b2): (dono, lugar, semente)"""
    return [(d, lu, s) for lu in LUGARES_B2 for d in DONOS_B2 for s in SEMENTES_B2]


def viver_b2(dono: str, lugar: str, semente: int, com_sonda: bool) -> tuple:
    """(o motor, o cerebro, o coletor ou None): a vida do gabarito da AN0 (o REL do conserto, 4 dias, o corpo do orquestrador), so com o
    CONFIG_MUNDO_ILHA (as tres frutiferas) e o sacudir ligado no motor, como o `sacudir_ilha` do tests/gabarito_limpeza_mecanicas.py;
    nenhum dono sacode, e as frutas caem sozinhas"""
    import exportar_gabarito_digibrain_modular as gab
    from bancada.regras_mundo import simular_vida_fisico
    from digilab.config import CONFIG_DIGIBRAIN_INATOS, CONFIG_MUNDO_ILHA, CONFIG_PADRAO, CONFIG_SACUDIR_LIGADA
    from digilab.digibrain import DigiBrain
    from digilab.donos import criar_dono
    from digilab.motor_corpo import com_corpo
    from digilab.mundo import DonoComLugar, MotorMundo
    from digilab.temperamento import NEUTRO
    orq, cm = gab.orq, CONFIG_MUNDO_ILHA
    cc = orq.bancada(gab.DIAS, orq.ORCAMENTO_POR_DIA).cfg_corpo_de(orq.bv.EspecVida(dono, orq.gl.BRACO_V11, semente))

    def fm(politica, cfg, s):
        return com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=cm, cfg_corpo=cc,
                                     cfg_sacudir=CONFIG_SACUDIR_LIGADA)

    cd = orq.config_do_braco(gab.BRACO, None, True)
    registro = orq.Registro(DigiBrain(CONFIG_PADRAO, cd, cm, semente=semente), CONFIG_DIGIBRAIN_INATOS.escala)
    cerebro = orq.cerebro_de(registro)
    col = Coletor(cerebro) if com_sonda else None
    try:
        d = DonoComLugar(criar_dono(dono), lugar, semente, dono, cm)
        motor, _ = simular_vida_fisico(d, registro, semente, gab.DIAS, orq.ORCAMENTO_POR_DIA * gab.DIAS, dono, fm)
    finally:
        if col is not None:
            col.soltar()
    return motor, cerebro, col


def _paraj(x):
    import exportar_gabarito_digibrain_modular as gab
    return gab.paraj(x)


def _sha_txt(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def assinatura_b2(motor, cerebro) -> dict:
    a = assinatura(motor, cerebro)
    return {"log": a["log"], "estado": a["estado"], "motivos": _sha_txt(a["motivos"]), "decisoes": len(a["motivos"])}


def entradas_b2(motor, cerebro) -> dict:
    """a conferencia das entradas (adendo 1, secao 5): as quedas de fruta no mundo e as classes dos episodios de consumo guardados no fim"""
    cont: dict = {}
    for e in episodios_de(cerebro.m.mem):
        if e["origem"] == "consumo":
            cont[e["classe"]] = cont.get(e["classe"], 0) + 1
    return {"quedas": len(motor.mundo.quedas), "consumos_guardados": dict(sorted(cont.items()))}


def _rotulo_b2(dono: str, lugar: str, semente: int) -> str:
    return f"ilha|{dono}|{lugar}|{semente}"


def _uma_b2(x: tuple) -> tuple:
    motor, cerebro, _ = viver_b2(*x, False)
    return _rotulo_b2(*x), assinatura_b2(motor, cerebro)


def gravar_gabarito_b2(processos: int, arquivo: Path = GABARITO_B2) -> dict:
    """o gabarito da (b2), sem o coletor, num commit proprio antes da medida (adendo 1, secao 5); recusa por cima de um que ja existe"""
    if arquivo.exists():
        raise FileExistsError(f"{arquivo} ja existe: o gabarito da (b2) e gravado uma vez")
    if not 1 <= processos <= MAX_PROCESSOS:
        raise SystemExit(f"de 1 a {MAX_PROCESSOS} processos (V3-D8)")
    with ProcessPoolExecutor(max_workers=processos) as pool:
        out = {"rotulo": "gabarito da (b2) da sonda da F5 (adendo 1): o log, o estado e os motivos de cada vida, sem o coletor",
               "vidas": dict(pool.map(_uma_b2, vidas_b2()))}
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return out


def sondar_b2(tarefa: tuple) -> dict:
    """uma vida da (b2): refeita com o coletor, o G-S0 contra o gabarito da (b2), o registro por decisao e as entradas"""
    dono, lugar, semente, gabarito = tarefa
    rotulo = _rotulo_b2(dono, lugar, semente)
    t0 = time.perf_counter()
    motor, cerebro, col = viver_b2(dono, lugar, semente, True)
    a = assinatura_b2(motor, cerebro)
    for k in ("log", "estado", "motivos", "decisoes"):
        if a[k] != gabarito[k]:
            raise RuntimeError(f"G-S0: {k} de {rotulo} nao e o do gabarito da (b2)")
    motivos = [_paraj(x) for x in cerebro.motivos]
    if len(col.registros) != len(motivos) or col.leituras_rng != len(col.registros):
        raise RuntimeError(f"{rotulo}: {len(col.registros)} leituras para {len(motivos)} decisoes")
    for reg, mot in zip(col.registros, motivos):
        esc = mot["escolha"]
        reg["escolha"] = esc
        reg["alvo"] = (list(cerebro.m.mem.lugar_de(*esc[2])) if esc[0] == "explorar" and esc[1] == "ponto" else None)
    return {"vida": rotulo, "dono": dono, "lugar": lugar, "semente": semente, "log_sha256": a["log"],
            "entradas": entradas_b2(motor, cerebro),
            "parede_s": {"total": time.perf_counter() - t0, "sonda": col.t}, "decisoes": col.registros}


def exigir_aprovado(caminho: Path) -> None:
    status = [x for x in caminho.read_text(encoding="utf-8").splitlines() if x.startswith("**Status:")]
    if not status or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise SystemExit(f"D-F5-8: {caminho.name} nao esta APROVADO pelo Matheus no cabecalho")


def principal_b2(processos: int, saida: Path = SAIDA_B2, gabarito: Path = GABARITO_B2) -> dict:
    """a medida da (b2), uma vez: o plano e o adendo 1 aprovados, o gabarito gravado antes, ate 4 processos"""
    exigir_aprovado(PLANO)
    exigir_aprovado(ADENDO1)
    if not gabarito.exists():
        raise SystemExit(f"o gabarito da (b2) {gabarito.name} nao existe: ele e gravado e commitado antes da medida")
    if (saida / "sonda.json").exists():
        raise FileExistsError(f"{saida / 'sonda.json'} ja existe: a medida roda uma vez")
    if not 1 <= processos <= MAX_PROCESSOS:
        raise SystemExit(f"de 1 a {MAX_PROCESSOS} processos (V3-D8)")
    gab = json.loads(gabarito.read_text(encoding="utf-8"))["vidas"]
    tarefas = [(*x, gab[_rotulo_b2(*x)]) for x in vidas_b2()]
    with ProcessPoolExecutor(max_workers=processos) as pool:
        res = list(pool.map(sondar_b2, tarefas))
    total = medir([d for v in res for d in v["decisoes"]])
    out = {"rotulo": "sonda descritiva do E(P) da F5, a (b2) do adendo 1, no mundo com arvores; so leitura, nao e gate",
           "fontes": {"plano": hashlib.sha256(PLANO.read_bytes()).hexdigest(), "adendo1": hashlib.sha256(ADENDO1.read_bytes()).hexdigest(),
                      "gabarito_b2": hashlib.sha256(gabarito.read_bytes()).hexdigest()},
           "vidas": [{"vida": v["vida"], "log_sha256": v["log_sha256"], "entradas": v["entradas"], "parede_s": v["parede_s"],
                      **medir(v["decisoes"])} for v in res],
           "todas": total, "leitura": leitura(total)}
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "sonda.json").write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    with gzip.open(saida / "sonda_decisoes.json.gz", "wt", encoding="utf-8") as f:
        json.dump([{"vida": v["vida"], "decisoes": v["decisoes"]} for v in res], f, sort_keys=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--medir-tempo", action="store_true")
    ap.add_argument("--gravar-gabarito-b2", action="store_true")
    ap.add_argument("--b2", action="store_true")
    ap.add_argument("--processos", type=int, default=4)
    a = ap.parse_args()
    if a.gravar_gabarito_b2:
        out = {"gravado": str(GABARITO_B2.relative_to(RAIZ)), "vidas": len(gravar_gabarito_b2(a.processos)["vidas"])}
    elif a.b2:
        out = principal_b2(a.processos)["leitura"]
    else:
        out = medir_tempo() if a.medir_tempo else principal(a.processos)["leitura"]
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
