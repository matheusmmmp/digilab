"""A validacao do pet que pensa (J5; docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, secoes 6 e 7, com o desenho do adendo 5 e os numeros do
adendo 6). Roda UMA vez.

Os 4 bracos x os 2 protocolos (T1, T2) nas unidades da validacao (bases 46101...46505, K_u do adendo 6, prefixo `pet_que_pensa`), pela
bancada do J5 (`rodar_pqp`, que grava as vidas e as rejoga do disco bit a bit), com o paladar e a fruta ao lado da racao, o `ganho_gosto`
e o `g_plano` da calibracao. Os gates de mecanismo (G-SEM-CREDITO, o congelamento, o G2) falham alto em toda vida, na medida.

**A config tem de trazer os numeros congelados:** com as bases do plano, o `ganho_gosto`, o `g_plano`, as margens e o K_u sao conferidos
contra os artefatos da calibracao (`calibracao`: a pasta dela), e um que difere falha alto. Recusa a pasta de saida que ja existe.

**A analise (secao 7):**
- **as premissas:** a G-APRENDEU (`f_antes` com o limite inferior do IC95 acima do limiar da config: 1/4 no adendo 5, PJ5-3), a
  G-OPORTUNIDADE (no maximo 25% das unidades sem oportunidade, por braco e teste) e a G-EXPOSICAO (no maximo 25% sem exposicao no T2);
- **os contrastes**, por unidade, pelo bootstrap agrupado por base (`metrics.contraste_pareado`, 10.000 reamostragens, semente 4242):
  - os primarios, G-T1 = q(P1-plan) - q(P1) e G-T2 = m(P1-plan) - m(P1-plan-desfecho), com o Holm de 2;
  - os secundarios, G-T1-DESF, G-T1-CONG, G-T2-HAB e G-T2-CONG, com o Holm de 4;
- **as categorias dos primarios**, exclusivas e nesta ordem, com a margem do teste (`Delta_T1` ou `Delta_T2`):
  1. passa (o limite inferior do IC95 > 0 e o Holm rejeita; "abaixo de Delta" se o superior do IC90 < a margem);
  2. oposto (o superior do IC95 < 0);
  3. equivalente (o IC90 dentro de +- a margem);
  4. inconclusivo.
  Um contraste cujos bracos falham numa premissa daquele teste sai **inconclusivo por premissa**, com a categoria do numero ao lado;
- **os secundarios** passam com o limite inferior do IC95 > 0 e o Holm de 4;
- **a leitura** da secao 7, montada das categorias.

    python experiments/run_v2_validacao_pet_que_pensa.py --config experiments/configs/v2_pet_que_pensa/validacao_ao_lado.json \\
        --saida artifacts_v2_pet_que_pensa/validacao_ao_lado --processos 4
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from experiments import bancada_v2 as bv  # noqa: E402
from experiments import run_v2_calibracao_pet_que_pensa as cpq  # noqa: E402
from digilab.metrics import contraste_pareado, dentro_da_margem, holm  # noqa: E402

CHAVE = "validacao"
PROTOCOLOS = ("T1", "T2")
PRIMARIOS = cpq.PRIMARIOS
SECUNDARIOS = cpq.SECUNDARIOS
TESTE_DO_GATE = {**{n: c[0] for n, c in PRIMARIOS.items()}, **{n: c[0] for n, c in SECUNDARIOS.items()}}


def validar(cfg: dict) -> dict:
    """A config da validacao: a do J5 (os 4 bracos, T1 e T2, o `g_plano` e o `ganho_gosto` dela) mais `validacao` = {margens, limiar_aprendeu,
    bootstrap, holm, calibracao}. Com as bases do plano, as bases tem de ser as da validacao e os numeros os da calibracao."""
    if CHAVE not in cfg:
        raise ValueError(f"config da validacao do J5 sem {CHAVE!r}")
    v = cfg[CHAVE]
    if set(v) - {"calibracao"} != {"margens", "limiar_aprendeu", "bootstrap", "holm"}:
        raise ValueError(f"{CHAVE}: margens, limiar_aprendeu, bootstrap, holm (e calibracao com as bases do plano), nao {sorted(v)}")
    if set(v["margens"]) != {"delta_t1", "delta_t2"} or any(not (isinstance(x, float) and x > 0) for x in v["margens"].values()):
        raise ValueError(f"margens da validacao: delta_t1 e delta_t2 > 0, nao {v['margens']}")
    if v["bootstrap"] != {"reamostragens": 10000, "semente": 4242} or v["holm"] != {"alfa": 0.05}:
        raise ValueError("bootstrap {10000, 4242} e Holm alfa 0,05 (secao 7)")
    if not 0 < v["limiar_aprendeu"] < 1:
        raise ValueError(f"limiar da G-APRENDEU {v['limiar_aprendeu']!r}")
    if list(cfg.get("bracos", [])) != list(bv.BRACOS_PQP) or list(cfg.get("protocolos", [])) != list(PROTOCOLOS):
        raise ValueError(f"a validacao roda os 4 bracos {list(bv.BRACOS_PQP)} nos protocolos {list(PROTOCOLOS)}")
    bv.validar_config_pqp(_config_bancada(cfg))
    if "unidades" in cfg:
        if not set(cfg["unidades"]["bases"]) <= set(bv.BASES_PET_QUE_PENSA["validacao"]):
            raise bv.SementeSemPlano(f"a validacao do J5 usa as bases {bv.BASES_PET_QUE_PENSA['validacao']} (secao 8)")
        if "calibracao" not in v:
            raise ValueError("a validacao com as bases do plano confere os numeros contra a calibracao: a chave 'calibracao'")
        conferir_congelados(cfg)
    return cfg


def conferir_congelados(cfg: dict) -> dict:
    """Os numeros da config contra os artefatos da calibracao (o adendo 6): o ganho_gosto, o g_plano, as margens e o K_u. Falha alto."""
    pasta = RAIZ / cfg[CHAVE]["calibracao"]
    gg = json.loads((pasta / "ganho_gosto" / "ganho_gosto.json").read_text(encoding="utf-8"))["escolha"]
    gp = json.loads((pasta / "g_plano" / "g_plano.json").read_text(encoding="utf-8"))["escolha"]
    pil = json.loads((pasta / "g_plano" / "piloto" / "piloto.json").read_text(encoding="utf-8"))
    rv = json.loads((pasta / "reval.json").read_text(encoding="utf-8"))
    esperado = {"ganho_gosto": gg["ganho_gosto"], "g_plano": gp["g_plano"], "delta_t1": pil["margens"]["delta_t1"],
                "delta_t2": pil["margens"]["delta_t2"], "k": pil["n"]["k"], "limiar_aprendeu": pil["regras"]["limiar_aprendeu"]}
    tem = {"ganho_gosto": cfg["consequencia"]["ganho_gosto"], "g_plano": cfg["g_plano"], **cfg[CHAVE]["margens"],
           "k": cfg["unidades"]["k"], "limiar_aprendeu": cfg[CHAVE]["limiar_aprendeu"]}
    if tem != esperado:
        raise ValueError(f"os numeros da validacao nao sao os da calibracao ({cfg[CHAVE]['calibracao']}): {tem} contra {esperado}")
    if not (rv["passa"] and pil["valida_validacao"]):
        raise ValueError("a calibracao nao deixa a validacao rodar (a G-REVAL-POSSIVEL ou as margens)")
    # o resto da config e o do piloto (o mundo, o corpo, o cerebro, o paladar, a fruta ao lado, os bracos): so as unidades mudam
    piloto = json.loads((pasta / "g_plano" / "piloto" / "meta.json").read_text(encoding="utf-8"))["config"]
    fora = {"descricao", "unidades", CHAVE}
    a, b = {k: v for k, v in piloto.items() if k not in fora}, {k: v for k, v in cfg.items() if k not in fora}
    if a != b:
        raise ValueError(f"a config da validacao difere da do piloto em {sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))}")
    return esperado


def _config_bancada(cfg: dict) -> dict:
    return {k: v for k, v in cfg.items() if k != CHAVE}


def categoria_primario(c: dict, delta: float, rejeita: bool) -> dict:
    """As categorias da secao 7, exclusivas e nesta ordem."""
    ic95, ic90 = c["ic95"], c["ic90"]
    if ic95 is None:
        return {"categoria": "inconclusivo", "motivo": c.get("motivo") or "sem IC"}
    if ic95["ic_inferior"] > 0.0 and rejeita:
        return {"categoria": "passa, abaixo de Delta" if ic90["ic_superior"] < delta else "passa"}
    if ic95["ic_superior"] < 0.0:
        return {"categoria": "oposto"}
    if dentro_da_margem(ic90, delta):
        return {"categoria": "equivalente"}
    return {"categoria": "inconclusivo"}


def premissa_do_gate(premissas: dict, nome: str, bracos: tuple) -> dict:
    """As premissas que um contraste pede (secao 7): a G-APRENDEU dos dois bracos, a G-OPORTUNIDADE dos dois no teste e, no T2, a
    G-EXPOSICAO dos dois. Devolve as que falham."""
    teste = TESTE_DO_GATE[nome]
    prot = "T1" if teste == "t1" else "T2"
    falham = [f"G-APRENDEU {b}" for b in bracos if not premissas["G-APRENDEU"][b]["passa"]]
    falham += [f"G-OPORTUNIDADE {b}/{prot}" for b in bracos if not premissas["G-OPORTUNIDADE"][f"{b}/{prot}"]["passa"]]
    if prot == "T2":
        falham += [f"G-EXPOSICAO {b}" for b in bracos if not premissas["G-EXPOSICAO"][b]["passa"]]
    return {"falham": falham, "passa": not falham}


def analisar(medidas: dict, cfg: dict) -> dict:
    v = cfg[CHAVE]
    boot = {**v["bootstrap"], "nivel": 0.95}
    por = cpq._por_unidade(medidas)
    prem = cpq.premissas(por, boot, v["limiar_aprendeu"])
    deltas = {"t1": v["margens"]["delta_t1"], "t2": v["margens"]["delta_t2"]}

    def contraste(nome, c):
        teste, campo, a, b = c
        difs = cpq._difs(por, teste, campo, a, b)
        r = contraste_pareado(cpq._agrupado(difs), boot["reamostragens"], boot["semente"])
        return {"contraste": f"{campo}({a}) - {campo}({b})", "unidades_com_valor": len(difs), "delta": deltas[teste], **r,
                "premissas": premissa_do_gate(prem, nome, (a, b))}

    prim = {n: contraste(n, c) for n, c in PRIMARIOS.items()}
    sec = {n: contraste(n, c) for n, c in SECUNDARIOS.items()}
    hp = holm({n: g["p_unilateral"] for n, g in prim.items()}, v["holm"]["alfa"])
    hs = holm({n: g["p_unilateral"] for n, g in sec.items()}, v["holm"]["alfa"])
    for n, g in prim.items():
        g["holm"] = hp[n]
        cat = categoria_primario(g, g["delta"], hp[n]["rejeita"])
        g["categoria_do_numero"] = cat["categoria"]
        g["categoria"] = cat["categoria"] if g["premissas"]["passa"] else "inconclusivo por premissa"
    for n, g in sec.items():
        g["holm"] = hs[n]
        g["passa_numero"] = g["ic95"] is not None and g["ic95"]["ic_inferior"] > 0.0 and hs[n]["rejeita"]
        g["passa"] = g["passa_numero"] and g["premissas"]["passa"]
    return {"premissas": prem, "primarios": prim, "secundarios": sec, "leitura": leitura(prim, sec),
            "regras": {"bootstrap": boot, "holm": v["holm"], "limiar_aprendeu": v["limiar_aprendeu"], "margens": v["margens"],
                       "limiar_sem": cpq.LIMIAR_SEM, "fonte": "PLANO_ANALISE_V2_PET_QUE_PENSA, secao 7, com os adendos 5 e 6"}}


def leitura(prim: dict, sec: dict) -> list[str]:
    """A leitura da secao 7, das categorias (sem interpretar alem dela)."""
    c1, c2 = prim["G-T1"]["categoria"], prim["G-T2"]["categoria"]
    p1, p2 = c1.startswith("passa"), c2.startswith("passa")
    out = []
    if p1 and p2:
        out.append("G-T1 e G-T2 passam: o pet com o planejador planeja no sentido da DS-1 (o rotulo 'pensou' so com o fator do plano no "
                   "motivo, R-7).")
    elif p1:
        out.append("So o G-T1 passa: o modelo do desfecho funciona e o mapa nao (ou o T2 nao mediu); os descritivos dizem qual.")
    elif p2:
        out.append("So o G-T2 passa: o mapa funciona e a revalorizacao pela mao nao chega a escolha.")
    elif "inconclusivo por premissa" not in (c1, c2):
        out.append("Nenhum primario passa: o planejador, como esta, nao muda a escolha do pet nestes testes; registrado como resultado "
                   "do J5, com a sonda e os modelos como diagnostico.")
    else:
        medidos = [n for n, c in (("G-T1", c1), ("G-T2", c2)) if c != "inconclusivo por premissa"]
        out.append("Nenhum primario passa, e a leitura 'nenhum passa' da secao 7 so vale para o primario com as premissas de pe "
                   f"({', '.join(medidos) or 'nenhum'}): o outro nao mediu.")
    for n, c in (("G-T1", c1), ("G-T2", c2)):
        if c == "oposto":
            out.append(f"{n} oposto: registrado; o planejador muda a escolha no sentido contrario ao modelo.")
        if c == "inconclusivo por premissa":
            out.append(f"{n} inconclusivo por premissa ({', '.join(prim[n]['premissas']['falham'])}).")
    for n in ("G-T1-DESF", "G-T2-HAB"):
        g = sec[n]
        if g["ic95"] is not None and g["ic95"]["ic_superior"] < 0.0:
            out.append(f"{n} com o sinal trocado: o habito sozinho mostra a assinatura (R-1); o primario do teste fica com o aviso "
                       "'a assinatura nao separa'.")
    return out


def config_do_braco(cfg: dict, braco: str) -> dict:
    c = {**_config_bancada(cfg), "bracos": [braco]}
    if not bv.BRACOS_PQP[braco].planejador:
        del c["g_plano"]
    return c


def rodar(cfg: dict, pasta: Path, processos: int = 1) -> dict:
    if pasta.exists():
        raise FileExistsError(f"{pasta}: a pasta da validacao do J5 ja existe (a validacao roda uma vez)")
    validar(cfg)
    pasta.mkdir(parents=True)
    t0 = time.time()
    tarefas = [(config_do_braco(cfg, b), str(pasta / b)) for b in bv.BRACOS_PQP]
    if processos > 1:
        with ProcessPoolExecutor(max_workers=min(processos, len(tarefas))) as ex:
            res = list(ex.map(cpq._rodar_ponto, *zip(*tarefas)))
    else:
        res = [cpq._rodar_ponto(*t) for t in tarefas]
    parede = time.time() - t0
    medidas = {nome: m for r in res for nome, m in r["medidas"].items()}
    g = cfg["g_plano"]
    if any(m["g_plano"] != (g if bv.BRACOS_PQP[m["braco"]].planejador else 0) for m in medidas.values()):
        raise RuntimeError("a validacao tem vida com o g_plano errado")
    out = analisar(medidas, cfg)
    cpu = {b: [m["custo"]["cpu_s"] for m in medidas.values() if m["braco"] == b] for b in bv.BRACOS_PQP}
    out["custo"] = {"cpu_s_por_vida": {b: sum(x) / len(x) for b, x in cpu.items()}, "parede_s": parede, "processos": processos,
                    "vidas": len(medidas)}
    out["unidades"] = len(cpq._por_unidade(medidas)[("P1", "T1")])
    bv._gravar(pasta / "validacao.json", bv._dump(out))
    bv._gravar(pasta / "meta.json", bv._dump({**bv.meta(_config_bancada(cfg)), "plano": bv.PLANO_PQP, "validacao": cfg[CHAVE],
                                              "modelo_mundo_sha256": bv._sha(RAIZ / "digilab" / "modelo_mundo.py"),
                                              "orquestrador_sha256": bv._sha(Path(__file__)),
                                              "orquestrador_calibracao_sha256": bv._sha(Path(cpq.__file__)), "processos": processos}))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="validacao do pet que pensa (PLANO_ANALISE_V2_PET_QUE_PENSA, secao 7, adendos 5 e 6)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--processos", type=int, default=1, help="os bracos em paralelo")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    r = rodar(cfg, Path(a.saida), a.processos)
    for n, g in r["primarios"].items():
        print(f"{n}: {g['categoria']} (media {g['media']}, IC95 {g['ic95']}, Holm {g['holm']['rejeita']}, {g['unidades_com_valor']} unidades)")
    for n, g in r["secundarios"].items():
        print(f"{n}: {'passa' if g['passa'] else 'nao passa'} (media {g['media']}, {g['unidades_com_valor']} unidades)")
    for linha in r["leitura"]:
        print(linha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
