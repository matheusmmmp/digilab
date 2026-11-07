"""Conversa de 8 turnos pelo /api/fala-livre do servidor gravador (mesmo corpo que a pagina manda, sem "voz"),
com historico limpo, nos estagios adolescente e adulto. O estado imita o que estadoDoPet monta para um Guilmon."""
import json
import sys
import urllib.request

URL = "http://localhost:8790/api/fala-livre"
MSGS = ["oi! tudo bem com você?", "eu sou o Matheus, prazer", "lembra meu nome?", "por que você está bravo?",
        "hoje meu dia foi difícil no trabalho", "você lutou ontem, né?", "vai comer", "me conta alguma coisa sobre você"]


def estado(estagio, forma):
    return {"identidade": {"estagio": estagio, "especie": "brasa", "forma": forma},
            "estado": {"fome": 0.8, "higiene": 0.3, "energia": 0.3, "humor": 0.25, "saude": 0.9, "fadiga": 10,
                       "sobrecarga": 0, "sujo": True, "emocao": "raiva"},
            "temperamento": {"curiosidade": -0.3, "teimosia": 0.9, "sensibilidade": 0.1, "rancor": -0.3},
            "memorias": [{"espaco": "curto", "categoria": "demora", "evento": "você me deixou esperando", "ha_min": 22}],
            "desejo": {"tipo": "necessidade", "alvo": "comer"}, "vinculo": 0.5,
            "motivos": [{"acao": "dormir", "fatores": ["cansaço"], "evento_ref": "dia 2 09:10"}]}


def main(estagio, forma, semente0):
    hist, saida = [], []
    for i, m in enumerate(MSGS):
        corpo = {"estado": estado(estagio, forma), "situacao": "conversa", "fala_jogador": m, "historico": hist[-10:],
                 "semente": semente0 + i}
        req = urllib.request.Request(URL, data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json"})
        d = json.loads(urllib.request.urlopen(req, timeout=180).read())
        hist.append([m, d["fala"]])
        saida.append({"jogador": m, "pet": d["fala"], "fatos": d["fatos_citados"], "lat": d["latencia_s"],
                      "comando": d["comando"], "prompt": d["versao_prompt"], "erro": d["erro"]})
        print(f"{m!r:45} -> {d['fala']!r}  [{','.join(d['fatos_citados'])}] {d['latencia_s']:.1f}s", flush=True)
    return saida


if __name__ == "__main__":
    r = {"adolescente": main("adolescente", "Growlmon", 7000), "adulto": main("adulto", "WarGrowlmon", 7100)}
    json.dump(r, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
