"""O orgao da visao (e do ouvido) do pet: a lista fixa `ov-lista-1` e o resumo de quem grava o evento (V3, GOSTO_VISUAL, OV2;
docs/ESPEC_V3_ORGAO_VISAO.md, com as OV1-1 a OV1-14 DECIDIDAS pelo Matheus em 2026-11-12, pela recomendacao).

Componente puro, sem modelo: o reconhecimento de verdade (o SigLIP no navegador) e da OV3, e o Python so conhece o evento `percepcao_tela`
(digilab/events.py) e a TV do jogo com os conceitos por programa (digilab/tv.py). Aqui ficam:
  - a lista (secao 2 da espec; OV1-1 e OV1-13): 18 conceitos genericos da visao, 6 do som e as 56 especies que o
    `digilab_fala_livre/corpus.py` deixa entrar (o teste confere contra o `corpus.carregar()`), na ordem do desempate;
  - o brasao de cada especie no jogo (web/app/motor/nomes.ts, DIGIMON_DA_FORMA; o teste confere) e o patrono dele (OV1-4): brasa ->
    coragem, cirro -> amizade, ferrugem -> conhecimento, limo -> sinceridade (os deuses da E1, web/app/motor/lendas_e1.ts). A Diversao e o
    Myotismon ficam sem especie; as 4 especies fora do corpus (Valkyrimon, DemiVeemon, SlashAngemon, DinoBeemon) ficam fora da lista;
  - os conceitos sensiveis (OV1-7): `pessoa`, `rosto`, `texto` e `interface` nunca entram no evento com a fonte `tela` (a tela real);
  - os pares canonicos (conceito, nivel): nivel de NIVEL_CORTE a NIVEL_MAX (OV1-12), no maximo MAX_CONCEITOS, sem repeticao, na ordem do
    nivel (maior primeiro) e da lista no empate;
  - `ResumoOrgao`, o resumo da janela de quem grava (secao 5.2; OV1-6): o maximo do nivel de cada conceito nas classificacoes da janela, o
    corte, os k mais altos, e o evento so quando o conjunto muda.
Os numeros sao os da espec (DECIDIDOS como desenho; os valores PROPOSTOS, SEM FONTE)."""
from __future__ import annotations

from .events import Evento, percepcao_tela

VERSAO_LISTA = "ov-lista-1"
NIVEL_CORTE = 4                     # OV1-12: so sai um conceito com nivel >= 4 (PROPOSTO, SEM FONTE)
NIVEL_MAX = 15                      # o formato do evento (16 niveis, como o sentido_tela)
NIVEL_CERTO = 10                    # OV1-12: "certo" de 10 a 15, "acho" de 4 a 9 (o painel e a voz; PROPOSTO)
MAX_CONCEITOS = 3                   # secao 4.1: no maximo 3 por evento (a 10.5 da proposta)
CLASSIFICACOES_POR_JANELA = 5       # FA-11: uma classificacao a cada 2 s, resumida na janela de 10 s da GV-15

GENERICOS_VISAO = ("gato", "cachorro", "passaro", "peixe", "outro_bicho", "pessoa", "rosto", "comida", "planta", "agua", "ceu",
                   "carro", "cidade", "jogo", "desenho_animado", "texto", "interface", "fogo")
GENERICOS_SOM = ("musica", "fala", "risada", "latido", "miado", "estouro")
SENSIVEIS = ("pessoa", "rosto", "texto", "interface")
BRASOES = ("brasa", "cirro", "ferrugem", "limo")
PATRONO = {"brasa": "coragem", "cirro": "amizade", "ferrugem": "conhecimento", "limo": "sinceridade"}

# (id do conceito, o nome da especie no corpus e no jogo, o brasao no jogo), por brasao e nivel (In-Training ... Mega)
ESPECIES = (
("koromon", "Koromon", "brasa"),
    ("agumon", "Agumon", "brasa"),
    ("guilmon", "Guilmon", "brasa"),
    ("birdramon", "Birdramon", "brasa"),
    ("greymon", "Greymon", "brasa"),
    ("growlmon", "Growlmon", "brasa"),
    ("kyubimon", "Kyubimon", "brasa"),
    ("garudamon", "Garudamon", "brasa"),
    ("metalgreymon", "MetalGreymon", "brasa"),
    ("taomon", "Taomon", "brasa"),
    ("wargrowlmon", "WarGrowlmon", "brasa"),
    ("gallantmon", "Gallantmon", "brasa"),
    ("phoenixmon", "Phoenixmon", "brasa"),
    ("sakuyamon", "Sakuyamon", "brasa"),
    ("wargreymon", "WarGreymon", "brasa"),
    ("tsunomon", "Tsunomon", "cirro"),
    ("gabumon", "Gabumon", "cirro"),
    ("patamon", "Patamon", "cirro"),
    ("angemon", "Angemon", "cirro"),
    ("aquilamon", "Aquilamon", "cirro"),
    ("garurumon", "Garurumon", "cirro"),
    ("gatomon", "Gatomon", "cirro"),
    ("angewomon", "Angewomon", "cirro"),
    ("magnaangemon", "MagnaAngemon", "cirro"),
    ("silphymon", "Silphymon", "cirro"),
    ("weregarurumon", "WereGarurumon", "cirro"),
    ("magnadramon", "Magnadramon", "cirro"),
    ("metalgarurumon", "MetalGarurumon", "cirro"),
    ("seraphimon", "Seraphimon", "cirro"),
    ("armadillomon", "Armadillomon", "ferrugem"),
    ("veemon", "Veemon", "ferrugem"),
    ("ankylomon", "Ankylomon", "ferrugem"),
    ("exveemon", "ExVeemon", "ferrugem"),
    ("gargomon", "Gargomon", "ferrugem"),
    ("kabuterimon", "Kabuterimon", "ferrugem"),
    ("megakabuterimon", "MegaKabuterimon", "ferrugem"),
    ("paildramon", "Paildramon", "ferrugem"),
    ("rapidmon", "Rapidmon", "ferrugem"),
    ("shakkoumon", "Shakkoumon", "ferrugem"),
    ("herculeskabuterimon", "HerculesKabuterimon", "ferrugem"),
    ("imperialdramon_dragon_mode", "Imperialdramon Dragon Mode", "ferrugem"),
    ("megagargomon", "MegaGargomon", "ferrugem"),
    ("tanemon", "Tanemon", "limo"),
    ("gomamon", "Gomamon", "limo"),
    ("palmon", "Palmon", "limo"),
    ("ikkakumon", "Ikkakumon", "limo"),
    ("seadramon", "Seadramon", "limo"),
    ("stingmon", "Stingmon", "limo"),
    ("togemon", "Togemon", "limo"),
    ("lillymon", "Lillymon", "limo"),
    ("megaseadramon", "MegaSeadramon", "limo"),
    ("zudomon", "Zudomon", "limo"),
    ("imperialdramon_fighter_mode", "Imperialdramon Fighter Mode", "limo"),
    ("metalseadramon", "MetalSeadramon", "limo"),
    ("rosemon", "Rosemon", "limo"),
    ("vikemon", "Vikemon", "limo"),
)

ID_DA_ESPECIE = {nome: ident for ident, nome, _ in ESPECIES}
BRASAO = {ident: brasao for ident, _, brasao in ESPECIES}
CONCEITOS = GENERICOS_VISAO + GENERICOS_SOM + tuple(ident for ident, _, _ in ESPECIES)
INDICE = {c: i for i, c in enumerate(CONCEITOS)}
if len(INDICE) != len(CONCEITOS) or not set(SENSIVEIS) <= set(GENERICOS_VISAO):   # pragma: no cover - conferido na carga
    raise RuntimeError("a lista do orgao tem conceito repetido ou sensivel fora da visao")


class PercepcaoInvalida(ValueError):
    """Um par (conceito, nivel) fora da lista, do corte ou do formato, ou um conceito sensivel com a fonte `tela`."""


def e_especie(conceito: str) -> bool:
    return conceito in BRASAO


def patrono(conceito: str) -> str | None:
    """o deus patrono de uma especie (o do brasao dela no jogo); None num conceito generico"""
    b = BRASAO.get(conceito)
    return None if b is None else PATRONO[b]


def canonico(pares, fonte: str, lista: str = VERSAO_LISTA) -> tuple[tuple[str, int], ...]:
    """os pares validados e na ordem canonica (o nivel maior primeiro, a ordem da lista no empate). Falha alto em qualquer desvio."""
    if lista != VERSAO_LISTA:
        raise PercepcaoInvalida(f"lista do orgao desconhecida: {lista!r} (so {VERSAO_LISTA!r})")
    if type(pares) not in (tuple, list) or len(pares) > MAX_CONCEITOS:
        raise PercepcaoInvalida(f"de 0 a {MAX_CONCEITOS} pares (conceito, nivel): {pares!r}")
    vistos = set()
    out = []
    for par in pares:
        if type(par) not in (tuple, list) or len(par) != 2:
            raise PercepcaoInvalida(f"par malformado: {par!r}")
        c, n = par
        if c not in INDICE:
            raise PercepcaoInvalida(f"conceito fora da lista {VERSAO_LISTA}: {c!r}")
        if type(n) is not int or not NIVEL_CORTE <= n <= NIVEL_MAX:
            raise PercepcaoInvalida(f"nivel de {c} fora de {NIVEL_CORTE} a {NIVEL_MAX}: {n!r}")
        if c in vistos:
            raise PercepcaoInvalida(f"conceito repetido: {c!r}")
        if fonte == "tela" and c in SENSIVEIS:
            raise PercepcaoInvalida(f"o conceito sensivel {c!r} nao entra com a fonte `tela` (OV1-7)")
        vistos.add(c)
        out.append((c, n))
    return tuple(sorted(out, key=lambda p: (-p[1], INDICE[p[0]])))


class ResumoOrgao:
    """O resumo de quem grava o `percepcao_tela` (secao 5.2): recebe uma classificacao por vez (conceito -> nivel 0 a 15, so os da lista)
    e, a cada `janela` classificacoes, o maximo de cada conceito, o corte, os sensiveis fora com a fonte `tela` e os MAX_CONCEITOS mais
    altos; devolve o evento so quando os pares mudam (o primeiro, se nao vazio, sempre)."""

    def __init__(self, fonte: str, janela: int = CLASSIFICACOES_POR_JANELA) -> None:
        if type(janela) is not int or janela < 1:
            raise ValueError(f"janela do resumo do orgao inteira >= 1: {janela!r}")
        self.fonte, self.janela = fonte, janela
        self._maximo: dict[str, int] = {}
        self._n = 0
        self.ultimo: tuple | None = None

    def classificar(self, tick: int, niveis: dict) -> Evento | None:
        for c, n in niveis.items():
            if c not in INDICE:
                raise PercepcaoInvalida(f"conceito fora da lista {VERSAO_LISTA}: {c!r}")
            if type(n) is not int or not 0 <= n <= NIVEL_MAX:
                raise PercepcaoInvalida(f"nivel de {c} fora de 0 a {NIVEL_MAX}: {n!r}")
            self._maximo[c] = max(self._maximo.get(c, 0), n)
        self._n += 1
        if self._n < self.janela:
            return None
        acesos = [(c, n) for c, n in self._maximo.items() if n >= NIVEL_CORTE and not (self.fonte == "tela" and c in SENSIVEIS)]
        acesos.sort(key=lambda p: (-p[1], INDICE[p[0]]))
        pares = canonico(acesos[:MAX_CONCEITOS], self.fonte)
        self._maximo, self._n = {}, 0
        if pares == self.ultimo or (self.ultimo is None and not pares):
            return None
        self.ultimo = pares
        return percepcao_tela(tick, self.fonte, VERSAO_LISTA, pares)
