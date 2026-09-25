"""Campanha contra os 3 NPCs no combate V2.1, SEM treino (TAREFA_TREINO_SOMBRIO, secao 5).

    python experiments/run_campanha.py

Contra cada tier (N partidas, lados trocados na metade):
  1. as 8 formas adultas canonicas x 4 especies (bots da bateria V2.1);
  2. os 4 adolescentes canonicos x 4 especies (o tier 2 sugere adolescente);
  3. os 40 pets de pesquisa evoluidos (artifacts_v21_pesquisa/formas.json), por braco,
     com IC bootstrap sobre os ovos (o total de stats deles e 60: sem normalizacao);
  4. o Soberano original x a correcao testada (resposta a luta de longe), contra os
     estilos da bateria V2 com stats neutros e contra as 8 formas.
Saida em artifacts_campanha/. Descritivo (sem gate): a campanha com treino espera a
tarefa de treino.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.campanha import gambit_npc, npc, perfil_de_stats  # noqa: E402
from digilab.combate_v2.v21.bots import ADOLESCENTES, ADULTOS, FORMAS, lutador_adolescente, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHAS, Forma, carater_canonico, perfil  # noqa: E402
from digilab.combate_v2.v21.partida import Lutador, jogar, reproduzir  # noqa: E402
from digilab.config import CONFIG_CAMPANHA, CONFIG_CATALOGO, CONFIG_COMBATE_V2, STATS_V21  # noqa: E402
from digilab.metrics import bootstrap_ic  # noqa: E402
from digilab.protocol import PROTOCOLO_ARENA_V1, derivar_semente  # noqa: E402

SAIDA = RAIZ / "artifacts_campanha"
TIERS = tuple(CONFIG_CAMPANHA.npcs)


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True)


def taxa(a: Lutador, b: Lutador, n: int, rotulo: str, amostra: list | None = None) -> float:
    pts = 0.0
    for k in range(n):
        s = derivar_semente("campanha", rotulo, a.nome, b.nome, k)
        if k < n // 2:
            p = jogar(a, b, s)
            pts += p.pontos_a
        else:
            p = jogar(b, a, s)
            pts += 1.0 - p.pontos_a
        if amostra is not None and k == 0:
            amostra.append((a, b, p))
    return pts / n


def main() -> int:
    n = CONFIG_CAMPANHA.partidas_por_par
    SAIDA.mkdir(parents=True, exist_ok=True)
    npcs = {t: npc(t) for t in TIERS}
    especies = list(CONFIG_CATALOGO.especies_ativas)
    amostra: list = []

    print("formas adultas ...", flush=True)
    adultos = {t: {f: {e: taxa(lutador_adulto(f, e), npcs[t], n, "adulto", amostra) for e in especies}
                   for f in FORMAS} for t in TIERS}
    print("adolescentes ...", flush=True)
    adolescentes = {t: {l: {e: taxa(lutador_adolescente(l, e, carater_canonico(
        next(f for f in FORMAS if f in CONFIG_CATALOGO.arquetipos_adulto[l]["formas"]))), npcs[t], n, "adol")
                           for e in especies} for l in LINHAS} for t in TIERS}

    print("pets de pesquisa ...", flush=True)
    formas_pesq = json.loads((RAIZ / "artifacts_v21_pesquisa" / "formas.json").read_text(encoding="utf-8"))
    pets = {}
    for f in formas_pesq:
        fm = f["forma"]
        forma = Forma(f["especie"], "adulto", fm["ramo"], fm["linha"], fm["adulta"])
        p = perfil(forma, f["temperamento"], f["carater_adulto"], f["condicao"])
        nome = f"{f['dono']}-{f['politica']}@{f['semente']}"
        pets[nome] = (f, Lutador(nome, p, ADULTOS[fm["adulta"]], CONFIG_COMBATE_V2.epsilon_bots))
    boot = (PROTOCOLO_ARENA_V1.v("bootstrap_reamostragens"), PROTOCOLO_ARENA_V1.v("bootstrap_semente"),
            PROTOCOLO_ARENA_V1.v("nivel_confianca"))
    por_pet = {nome: {t: taxa(lut, npcs[t], n, "pesquisa") for t in TIERS} for nome, (_, lut) in pets.items()}
    bracos = {}
    for pol in ("bandit", "instinto"):
        for dono in PROTOCOLO_ARENA_V1.v("bracos"):
            nomes = [nm for nm, (f, _) in pets.items() if f["dono"] == dono and f["politica"] == pol]
            bracos[f"{dono}-{pol}"] = {t: bootstrap_ic([por_pet[nm][t] for nm in sorted(nomes)], *boot) for t in TIERS}

    print("soberano original x correcao ...", flush=True)
    neutro = {k: 10.0 for k in STATS_V21}
    estilos = ("agressivo", "tartaruga", "atirador", "contragolpe", "adaptativo")
    soberano = {}
    for versao in ("adaptativo", "soberano_resposta_longe"):
        chefe = npc("tier3_soberano", versao)
        soberano[versao] = {
            "estilos_v2_stats_neutros": {e: taxa(Lutador(f"estilo:{e}", perfil_de_stats("neutro", neutro), gambit_npc(e),
                                                         CONFIG_COMBATE_V2.epsilon_bots), chefe, n, "soberano")
                                         for e in estilos},
            "formas_adultas_media_especies": {f: sum(taxa(lutador_adulto(f, e), chefe, n, "soberano") for e in especies)
                                              / len(especies) for f in FORMAS},
        }

    # replay de uma amostra, do disco
    (SAIDA / "amostra_replay.jsonl").write_text("".join(p.para_jsonl() for *_, p in amostra), encoding="utf-8",
                                                newline="\n")
    for a, b, p in amostra:
        la, lb = (a, b) if p.nome_a == a.nome else (b, a)
        reproduzir(list(p.log), la, lb)

    media = lambda d: sum(d.values()) / len(d)  # noqa: E731
    resumo = {
        "descricao": __doc__.splitlines()[0],
        "npcs": {t: {**CONFIG_CAMPANHA.npcs[t], "perfil": npcs[t].perfil.para_dict(),
                     "gambits": npcs[t].gambits.para_dict()} for t in TIERS},
        "formas_adultas_x_tier": {t: {f: {"media_especies": media(v), "por_especie": v} for f, v in d.items()}
                                  for t, d in adultos.items()},
        "adolescentes_x_tier": {t: {l: {"media_especies": media(v), "por_especie": v} for l, v in d.items()}
                                for t, d in adolescentes.items()},
        "pets_de_pesquisa_por_braco": bracos,
        "pets_de_pesquisa_por_pet": por_pet,
        "soberano": soberano,
        "replay_amostra_bit_a_bit": len(amostra),
        "partidas_por_par": n,
        "config_campanha": asdict(CONFIG_CAMPANHA),
        "fontes_sha256": hashlib.sha256(b"".join(
            (RAIZ / "digilab" / f).read_bytes().replace(b"\r\n", b"\n") for f in ("campanha.py",))).hexdigest(),
        "avisos": ["SEM treino: pets com o total de stats da especie (60) contra NPCs de 72/80/90",
                   "bateria V2.1 REPROVADA: a campanha herda isso", "numeros PROPOSTOS"],
        "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
    }
    (SAIDA / "campanha.json").write_text(_dump(resumo), encoding="utf-8", newline="\n")
    for t in TIERS:
        print(f"  {t}: formas adultas {({f: round(v['media_especies'], 2) for f, v in resumo['formas_adultas_x_tier'][t].items()})}")
        print(f"      adolescentes {({l: round(v['media_especies'], 2) for l, v in resumo['adolescentes_x_tier'][t].items()})}")
        print(f"      bracos bandit {({b: round(v[t]['media'], 2) for b, v in bracos.items() if b.endswith('bandit')})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
