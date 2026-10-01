"""Arvore de evolucao de cada especie no jogo (fato A1 da voz propria: "arvore da minha especie").

Os nomes sao os do mapa aprovado do jogo web (web/app/motor/nomes.ts, DIGIMON_DA_FORMA); tests/test_arvore_fala.py
confere as duas tabelas. No jogo qualquer Rookie da especie pode virar qualquer Champion dela (pelo carater), e cada
Champion segue a cadeia canonica ate o Mega (pets v5 em diante). Com este fato o pet sabe a propria arvore: "Agumon
vira Greymon" deixa de ser invencao. O servidor monta o texto; a pagina so manda a especie.
"""

from __future__ import annotations

ARVORE = {
    "brasa": {"bebe": "Koromon", "criancas": ("Agumon", "Guilmon"),
              "linhas": (("Greymon", "MetalGreymon", "WarGreymon"), ("Kyubimon", "Taomon", "Sakuyamon"),
                         ("Birdramon", "Garudamon", "Phoenixmon"), ("Growlmon", "WarGrowlmon", "Gallantmon"))},
    "cirro": {"bebe": "Tsunomon", "criancas": ("Patamon", "Gabumon"),
              "linhas": (("Garurumon", "WereGarurumon", "MetalGarurumon"), ("Angemon", "MagnaAngemon", "Seraphimon"),
                         ("Aquilamon", "Silphymon", "Valkyrimon"), ("Gatomon", "Angewomon", "Magnadramon"))},
    "ferrugem": {"bebe": "DemiVeemon", "criancas": ("Armadillomon", "Veemon"),
                 "linhas": (("ExVeemon", "Paildramon", "Imperialdramon Dragon Mode"),
                            ("Ankylomon", "Shakkoumon", "SlashAngemon"), ("Gargomon", "Rapidmon", "MegaGargomon"),
                            ("Kabuterimon", "MegaKabuterimon", "HerculesKabuterimon"))},
    "limo": {"bebe": "Tanemon", "criancas": ("Palmon", "Gomamon"),
             "linhas": (("Stingmon", "DinoBeemon", "Imperialdramon Fighter Mode"), ("Togemon", "Lillymon", "Rosemon"),
                        ("Seadramon", "MegaSeadramon", "MetalSeadramon"), ("Ikkakumon", "Zudomon", "Vikemon"))},
}
TIPO_ARVORE = "arvore da minha especie"


def texto_arvore(especie: str) -> str:
    """texto do fato A1; especie desconhecida falha alto"""
    a = ARVORE[especie]
    c1, c2 = a["criancas"]
    champs = [x[0] for x in a["linhas"]]
    cadeias = "; ".join(f"{c} vira {u} e depois {m}" for c, u, m in a["linhas"])
    return (f"{a['bebe']} vira {c1} ou {c2}; {c1} e {c2} viram {', '.join(champs[:-1])} ou {champs[-1]}, "
            f"conforme o jeito de cada um; {cadeias}")
