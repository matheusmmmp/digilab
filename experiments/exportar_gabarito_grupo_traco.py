"""Gabarito do TRACO do grupo de dois pets, Python x TS (docs/TAREFA_V3_COOPERACAO.md, etapa CO2a; o G-PAR-GRUPO da CO2c).

O `grupo_python.json.gz` da CO1 (experiments/exportar_gabarito_grupo.py) guarda o resultado de cada vida. Este guarda o traco por decisao de
cada pet, para o `motor/grupo.ts` rejogar a camada do grupo e do mundo sem o engine, a politica e o dono do Python, no molde do
`mundo_python.json` (experiments/exportar_gabarito_mundo.py, MotorMundoGravado): o mundo e um componente, e o grupo tambem.

Gravado com o codigo da `main` de hoje; nada de `digilab/` muda. As vidas sao as mesmas cinco da CO1 (`exportar_gabarito_grupo.VIDAS`), com
o motor de cada pet trocado pelo que grava o traco (o mesmo motor, com o corpo por cima na vida dos drives). De cada pet, na ordem:
  decisao        o tick do pet e o do mundo, a fome antes, a percepcao do mundo antes, a percepcao social (`obs.social`, o que o
                 `perceber_social` do grupo deu: os outros a vista, onde os viu comer, o ultimo toque), a acao, a regra, os candidatos,
                 o ocorrido, o estado e a percepcao depois, e o `_tick_social` que o grupo le no fim do tick (a disputa e o seguir);
  deixar_comida  e deixar_bola, quando o dono poe no mundo pelo pet.
O traco de cada pet e o resumo do grupo da CO1 (as vezes, os contatos, as disputas) sao o alvo do TS. O sha256 do resumo de cada vida tem de
ser o mesmo do gabarito da CO1 (o motor que grava nao muda a vida), e o teste confere.

    python experiments/exportar_gabarito_grupo_traco.py              # grava web/app/test/gabaritos/grupo_traco_python.json.gz
    python experiments/exportar_gabarito_grupo_traco.py --conferir   # refaz e compara com o gravado (falha alto se diferir)
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_grupo as eg  # noqa: E402
from exportar_gabarito_mundo import MotorMundoGravado  # noqa: E402

from digilab.config import CONFIG_GRUPO_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "grupo_traco_python.json.gz"


def _jsonavel(obj):
    """o objeto em JSON puro (os alvos pelo `para_dict`, as tuplas como listas)"""
    return json.loads(json.dumps(obj, sort_keys=True, default=lambda o: o.para_dict() if hasattr(o, "para_dict") else repr(o)))


class MotorGrupoGravado(MotorMundoGravado):
    """O MotorMundoGravado com o que o grupo pede a mais: o tick do mundo, a percepcao social e o `_tick_social`; nao muda nada da vida."""

    def _antes_da_decisao(self):
        p = super()._antes_da_decisao()
        social = getattr(self, "_social", None)
        self._op.update(tick_mundo=self._tm(self._estado.tick), social=None if social is None else _jsonavel(asdict(social)))
        return p

    def _consequencia(self, acao):
        ocorrido = super()._consequencia(acao)
        ts = getattr(self, "_tick_social", None)
        op = self.traco[-1]
        op["tick_social"] = None if ts is None or ts["tick"] != op["tick_mundo"] else _jsonavel(ts)
        op["ocorrido"] = _jsonavel(op["ocorrido"])
        return ocorrido


MotorGrupoGravadoCorpo = com_corpo(MotorGrupoGravado)


def _fabricas(layout: str, corpo: str, cerebro: str):
    """as fabricas do exportador da CO1, com o motor que grava o traco"""
    cm, cc = eg.LAYOUTS[layout], eg.CORPOS[corpo]
    if cerebro == "instinto":
        fp = lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
    elif cerebro == "lobos":
        fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=cm, cfg_corpo=cc)  # noqa: E731
    else:
        raise ValueError(f"cerebro desconhecido: {cerebro!r}")
    if cc is None:
        fm = lambda p, cfg, s, **kw: MotorGrupoGravado(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, **kw)  # noqa: E731
    else:
        fm = lambda p, cfg, s, **kw: MotorGrupoGravadoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm,  # noqa: E731
                                                            cfg_corpo=cc, **kw)
    return fp, fm


def vida(semente: int, layout: str, corpo: str, cerebros: tuple, donos: tuple, entrada_b: int, lugar: str) -> dict:
    pets = []
    sementes = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    for ident, cerebro, dono, entrada in (("A", cerebros[0], donos[0], 0), ("B", cerebros[1], donos[1], entrada_b * TICKS_POR_DIA)):
        fp, fm = _fabricas(layout, corpo, cerebro)
        d = DonoComLugar(criar_dono(dono), lugar, sementes[ident], dono, eg.LAYOUTS[layout])
        pets.append(PetDoGrupo(ident, entrada, fp, fm, d, dono, cerebro))
    g = simular_grupo(eg.LAYOUTS[layout], semente, pets, eg.DIAS)
    resumo_sha = eg._sha(eg._json(json.loads(eg._json(g.resumo()))))
    return {"semente": semente, "resumo_sha256": resumo_sha,
            "tracos": {i: _jsonavel(m.traco) for i, m in sorted(g.motores.items())},
            "n_decisoes": {i: sum(1 for op in m.traco if op["op"] == "decisao") for i, m in sorted(g.motores.items())}}


def gerar() -> dict:
    return {"fonte": "experiments/exportar_gabarito_grupo_traco.py", "vidas": [vida(*v) for v in eg.VIDAS]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--conferir", action="store_true", help="refaz e compara com o gabarito gravado")
    args = ap.parse_args()
    g = gerar()
    texto = json.dumps(g, sort_keys=True, separators=(",", ":"))
    if args.conferir:
        gravado = json.loads(gzip.decompress(ARQUIVO.read_bytes()).decode())
        if gravado != json.loads(texto):
            raise SystemExit(f"o gabarito do traco do grupo mudou: {ARQUIVO}")
        print(f"igual ao gravado: {ARQUIVO}")
        return
    ARQUIVO.write_bytes(gzip.compress(texto.encode(), mtime=0))
    for v in g["vidas"]:
        print(f"vida {v['semente']}: decisoes {v['n_decisoes']}, resumo {v['resumo_sha256'][:12]}")
    print(f"gravado: {ARQUIVO} ({ARQUIVO.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
