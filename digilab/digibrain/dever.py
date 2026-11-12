"""Os deveres do pet com o outro (docs/ESPEC_V3_COOPERACAO_CO7.md; so com a subchave `co7` da ConfigCooperacao): as contas puras que o
M-SENS, o M-ARB e o M-AFETO chamam. Tudo em inteiros, sem rng, e so do que o pet ve (o G-RECEPTOR-SOCIAL, CO7-1): a posicao e a acao
visivel de cada outro a vista, a posicao das comidas que o pet ve, onde ele viu cada outro comer, o proprio `k` (o peso dos deveres da CO6)
e as proprias leituras do corpo. Nada aqui le o corpo ou o cerebro do outro.

  social       (M-SENS) a percepcao social da decisao em posicoes absolutas: cada outro a vista com a acao visivel, a aflicao (`emburrar`
               ou `chamar_atencao`, 2.1) e a posicao em que o pet o viu na decisao anterior em que o via; onde viu cada outro comer
               (com a idade); o proprio `k`.
  situacao     (M-ARB) as comidas para as quais um outro aflito esta indo (2.1): ele esta a ate `r_escudo_celulas` da comida e mais
               perto dela que na posicao anterior; a privacao do proprio pet (a leitura da fome abaixo do `piso_privacao_s`, CO7-3); se o
               escudo vale (k >= `limiar_escudo` e sem privacao, CO7-2); o `delta` da universalizacao, mul(k, w_univ) com o teto na
               urgencia mais forte (CO7-4); e se a comida em disputa e a unica comida a vista (a contencao da CO3).
  ajustar      (M-ARB) os pesos depois do escudo e da universalizacao (2.2 e 3.2): com o escudo, as unidades de comer uma comida proibida
               saem (peso 0: e o shielding, fora da soma); sem ele, elas reprovam e perdem o `delta` (sem passar de 0); com a comida
               proibida sendo a unica a vista, as outras unidades com peso aprovam e ganham o `delta` (deixar a comida). Se nenhuma unidade
               sobra, o `_escolher` do M-ARB fica com o ocioso. Com os atos de hoje, a universalizacao se reduz a tabela de sinais da CO3
               (CO7-5): disputar a comida do aflito reprova, deixar a unica comida para ele aprova, o resto e neutro.
  culpa_inveja (M-AFETO) os dois termos que a decisao tira da valencia (4; CO7-6): a culpa (`w_culpa`) com a leitura do humor a partir de
               `limiar_humor` e um outro aflito a vista; a inveja (`w_inveja`) com o humor abaixo e um outro visto comendo ha ate
               `janela_inveja` ticks. Os pesos sao os neutros: nenhuma faceta do M-PERS e de culpa ou de inveja (D-CO7b-5).
"""
from __future__ import annotations

from ._comum import mul

AFLICAO = ("emburrar", "chamar_atencao")
COMIDAS_MADURAS = ("racao", "a", "b", "c")


def _d2(ax: int, ay: int, bx: int, by: int) -> int:
    return (ax - bx) * (ax - bx) + (ay - by) * (ay - by)


def social(ps, pos: tuple[int, int], antes: dict[str, tuple[int, int]], r_escudo: int) -> dict | None:
    """a percepcao social da decisao (`ps`, a PercepcaoSocial com os campos da CO6) em posicoes absolutas; `antes` e a posicao em que o pet
    viu cada outro na ultima decisao em que o via (o estado do M-SENS, atualizado por quem chama); `r_escudo` em subunidades. None sem
    outro pet no grupo"""
    if ps is None:
        return None
    if ps.peso_dever is None:
        raise ValueError("deveres: a CO7 le o peso dos deveres da CO6 na percepcao social (a co6 desligada no grupo?)")
    x, y = pos
    outros = []
    for ident, dx, dy, _d, acao in ps.outros:
        if type(acao) is not str:
            raise ValueError(f"deveres: a acao visivel e o nome da acao: {acao!r}")
        a = antes.get(ident)
        outros.append({"id": ident, "x": x + dx, "y": y + dy, "acao": acao, "aflito": acao in AFLICAO,
                       "antes": None if a is None else [a[0], a[1]]})
    comeu = [{"id": ident, "x": cx, "y": cy, "idade": idade} for ident, cx, cy, idade in ps.onde_comeu]
    return {"k": ps.peso_dever, "outros": outros, "onde_comeu": comeu, "r2_escudo": r_escudo * r_escudo}


def situacao(sens: dict, urgencias: dict, cfg, S: int) -> dict:
    """o que o escudo e a universalizacao leem na decisao (a docstring do modulo); `sens["social"]` e o de `social`"""
    soc = sens["social"]
    k = soc["k"]
    fome = sens["leitura"].get("fome")
    if fome is None:
        raise RuntimeError("deveres: a privacao le a fome, e ela nao esta na percepcao do corpo")
    privacao = fome < cfg.piso_privacao_s
    x, y = sens["pos"]
    comidas = [o for o in sens["objetos"] if o["tipo"] in COMIDAS_MADURAS]
    proibidas = []
    for c in comidas:
        cx, cy = x + c["dx"], y + c["dy"]
        for o in soc["outros"]:
            if not o["aflito"] or o["antes"] is None:
                continue
            agora = _d2(o["x"], o["y"], cx, cy)
            if agora <= soc["r2_escudo"] and agora < _d2(o["antes"][0], o["antes"][1], cx, cy):
                proibidas.append(c["id"])
                break
    delta = min(mul(k, cfg.w_univ, S), max(urgencias.values(), default=0))
    return {"k": k, "privacao": privacao, "escudo": k >= cfg.limiar_escudo and not privacao, "proibidas": proibidas, "delta": delta,
            "unica": len(comidas) == 1}


def ajustar(unidades: list[dict], w: list[int], sit: dict) -> tuple[list[int], dict]:
    """(os pesos depois do escudo e da universalizacao, o registro: as chaves removidas, as que reprovaram e quantas aprovaram)"""
    w = list(w)
    removidas, reprovadas, aprovadas = [], [], 0
    proibidas = set(sit["proibidas"])
    for i, x in enumerate(unidades):
        ch = x["chave"]
        if ch[0] == "comer" and ch[1] == "comida" and ch[2] in proibidas:
            if sit["escudo"]:
                if w[i] > 0:
                    removidas.append(i)
                w[i] = 0
            else:
                if w[i] > 0:
                    reprovadas.append(i)
                w[i] = max(0, w[i] - sit["delta"])
    if sit["unica"] and proibidas and sit["delta"] > 0:
        for i, x in enumerate(unidades):
            ch = x["chave"]
            if w[i] > 0 and not (ch[0] == "comer" and ch[1] == "comida" and ch[2] in proibidas):
                w[i] += sit["delta"]
                aprovadas += 1
    return w, {"removidas": removidas, "reprovadas": reprovadas, "aprovadas": aprovadas}


def culpa_inveja(sens: dict, cfg) -> tuple[int, int]:
    """(a culpa, a inveja) da decisao, na escala S (a docstring do modulo)"""
    soc = sens["social"]
    if soc is None:
        return 0, 0
    humor = sens["leitura"].get("humor")
    if humor is None:
        raise RuntimeError("deveres: a culpa e a inveja leem o humor, e ele nao esta na percepcao do corpo")
    if humor >= cfg.limiar_humor:
        return (cfg.w_culpa if any(o["aflito"] for o in soc["outros"]) else 0), 0
    return 0, (cfg.w_inveja if any(c["idade"] <= cfg.janela_inveja for c in soc["onde_comeu"]) else 0)
