"""DigiBrain B, CfC + ator-critico + elegibilidade (V2, CEREBRO-B: docs/TAREFA_V2_CEREBRO_B.md; contrato da secao 1 de
docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md).

A familia e a do NORNBRAIN em docs/research/digibrain/synthesis/brain_comparison.md: uma celula recorrente de tempo continuo em forma
fechada (CfC, Hasani et al. 2022), um ator e um critico treinados por gradiente, com traco de elegibilidade. "Inspirado em" fala deste
cerebro, nao do NORNBRAIN (problema 4 de brain_comparison.md): o NORNBRAIN, o CfC e o NCP sao CORPUS ou software nao revisado, pista e nao
evidencia. Ponto flutuante e permitido (tarefa, secao 1): a celula usa exp e tanh da libm, entao o replay e bit a bit no MESMO runtime (o
criterio 3 do M6 cobra o porte; aqui so a pesquisa).

  O HERDADO (C-1, comum aos tres cerebros): a regra do instinto e os candidatos que ela propoe (lobos.impulsos) e o peso de cada um (o
  prior do A: lobos.PoliticaLobos._tabela_prior, ativacao em ponto fixo). O B aprende POR CIMA: o peso de cada candidato e
      w_a = w_instinto(a) x exp(z_a),   z_a o logit aprendido (a cabeca do ator), iniciado em zero.
  exp(0) = 1,0 exato, entao no comeco (e sempre com o aprendizado desligado) o peso e o do instinto, byte a byte: o mesmo sorteio
  proporcional de sempre (uma chamada de rng.random(), a conta de random.choices). Em logaritmo: log w_a = log w_instinto(a) + z_a.

  A CELULA (CfC): a percepcao x (as 9 entradas do A sem o vies, mais bola, fruta e a presenca de cada fruta: 14) e o estado oculto
  anterior h' entram juntos, v = (x, h'). Tres camadas lineares com tanh: F = tanh(W_f v + b_f), G = tanh(W_g v + b_g), K = tanh(W_k v +
  b_k); o portao de tempo s = sigma(-F x dt); o estado novo h = s * G + (1 - s) * K (a forma fechada do CfC). n_ocultos = 9. O estado
  oculto e a memoria do B (C-2: memoria propria, nao a do A); nao e parametro (contrato 1.3). Os pesos da celula comecam sorteados por uma
  rng PROPRIA e fixa (semente_pesos: herdada, a mesma em todo pet), U(-r, r), r = escala_inicial / sqrt(14 + 9); os vieses em zero.

  O ATOR: z = A h + b_A (uma linha por acao de AcaoPet), so nos candidatos. A ESCOLHA DA FRUTA (a sub-decisao de comer): o peso de cada
  fruta presente e incentivo_f x exp(q_f), q_f = F_f . h + b_f + theta_info x info_f (a entrada da informacao do N5: +1 bem, -1 mal);
  theta_info comeca em w0_info, o resto em zero, entao no comeco a escolha e a do MotorFrutas, byte a byte (com w0_info 0).

  O CRITICO: V(h) = C . h + c0, iniciado em zero.

  O CREDITO (ator-critico com elegibilidade): toda decisao com o aprendizado ligado calcula o gradiente g do log da probabilidade da
  escolha (a acao entre os candidatos e, quando comeu com duas frutas ou mais, a fruta) em relacao a TODOS os parametros do ator: a
  cabeca, e a celula por retropropagacao de um passo (o estado anterior h' fica como dado: o gradiente e truncado em um passo, a conta
  do traco de elegibilidade e que leva o credito para tras). O traco: e <- lambda x e + g, a cada decisao. Quando um sinal r chega:
      delta = r - V(h da decisao);  ator: theta += taxa_ator x delta x e;  critico: C += taxa_critico x delta x h, c0 += taxa_critico x delta.
  As fontes do sinal sao as da bancada, as mesmas do A e do C (r na unidade 1,0):
    consequencia (P1, P2): r = f_S / S, o sinal homeostatico escalar da bancada; comer com fruta no cenario espera a fruta_comida (a E2:
      r = sinal_homeostatico_fruta / S, o humor entra);
    dono (P3), com a janela da v1 do A: elogio e bronca na ultima decisao (pelo traco); o chamado atendido paga 1 - L / janela e o
      expirado recompensa_pedido_ignorado, na decisao do chamado, so pelo gradiente DELA (o traco ja andou).
  Uma decisao com um candidato so tem gradiente zero (nada a escolher), como no A; o traco ainda leva o sinal as anteriores.
  A MEMORIA E O TRACO SO ANDAM COM A DECISAO OBSERVADA: `agir` calcula o estado oculto novo e o gradiente e os guarda no registro; eles
  entram no cerebro (h, e <- lambda e + g) quando o motor observa a decisao (`observar`/`observar_consequencia`). Numa vida e o mesmo
  (toda decisao e observada antes da proxima); numa sonda (`metrics.distribuicoes_de_acao`, varios `agir` sem observar) o B responde
  sempre com a memoria do fim do dia, como o A, cujo `agir` nao muda nada do que ele aprendeu.

  SONDA DO APRENDIDO (contrato 1.1): toda decisao guarda a acao que sairia com a parte aprendida zerada (z = 0) e o mesmo u
  (`motivos[-1]["sonda"]`), e a escolha da fruta, a fruta com q = theta_info inato x info (sem o aprendido) e a fruta sem a informacao
  (`motivos[-1]["fruta"]["sonda"]`).

So biblioteca padrao.
"""

from __future__ import annotations

import math
import random
from dataclasses import fields, replace

from ..config import (CONFIG_BOLA, CONFIG_CEREBRO_B, CONFIG_CONSEQUENCIA, CONFIG_FRUTAS, CONFIG_PADRAO, Config, ConfigBola,
                      ConfigCerebroB, ConfigConsequencia, ConfigFrutas)
from ..events import FRUTAS, AcaoPet, AcaoUsuario
from ..policy import Observacao, PoliticaInstinto, Transicao
from . import lobos
from .lobos import (ACOES, ENTRADAS, ENTRADAS_MUNDO, REGRAS, REGRAS_MUNDO, _sortear_frutas, ativacao, impulsos, sinal_homeostatico,
                    sinal_homeostatico_fruta, sortear)

PORTAS = ("f", "g", "k")
ENTRADAS_B = ("fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora", "sem_cuidado", "bola", "fruta",
              *(f"presenca_{f}" for f in FRUTAS))
N_ENTRADAS_B = len(ENTRADAS_B)
FEEDBACK = frozenset({AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER})

# Status e fonte de cada campo da ConfigCerebroB. Todos PROPOSTOS, nenhum referendado; fora de todo hash.
PARAMETROS_CEREBRO_B: dict[str, tuple[str, str]] = {
    "aprendizado_ligado": ("PROPOSTO", "desligado = o instinto byte a byte (C-1); a bancada liga nos bracos que aprendem"),
    "bits_ponto_fixo": ("PROPOSTO", "o mesmo do A (ConfigLobos): o prior herdado e o sinal da consequencia em inteiros"),
    "escala_ticks_desde_cuidado": ("PROPOSTO", "o mesmo do A (ConfigLobos)"),
    "maximo_pesos": ("PROPOSTO", "o teto do plano da V2, como o A"),
    "n_ocultos": ("PROPOSTO", "estrutura: o tamanho que poe a capacidade em [0,9; 1,1] x A (contrato 1.3): 759 parametros"),
    "delta_t": ("PROPOSTO", "estrutura: uma decisao = uma unidade de tempo da celula (as decisoes sao a cada 15 ticks)"),
    "semente_pesos": ("PROPOSTO", "estrutura: a inicializacao herdada da celula, a mesma em todo pet (rng propria)"),
    "escala_inicial": ("PROPOSTO", "estrutura: U(-r, r), r = escala / sqrt(entradas + ocultos), a inicializacao de praxe"),
    "limite_logit": ("PROPOSTO", "estrutura: o logit aprendido cortado em +-limite (exp sem estouro)"),
    "taxa_ator": ("PROPOSTO", "livre, adendo de calibracao do B (grade {0,01; 0,03; 0,1})"),
    "taxa_critico": ("PROPOSTO", "livre, adendo de calibracao do B (grade {0,01; 0,03; 0,1})"),
    "lambda_elegibilidade": ("PROPOSTO", "livre, adendo de calibracao do B (grade {0,5; 0,8; 0,95})"),
    "w0_info": ("PROPOSTO", "livre, adendo de calibracao do B (grade {0,5; 1,0; 2,0}, regra K-3 do A)"),
    "janela_latencia_ticks": ("PROPOSTO", "o mesmo do A: a janela de credito da v1 (fonte do sinal comum)"),
    "recompensa_pedido_ignorado": ("PROPOSTO", "o mesmo do A"),
    "recompensa_elogio": ("PROPOSTO", "o mesmo do A"),
    "recompensa_repreensao": ("PROPOSTO", "o mesmo do A"),
}


def validar_parametros_cerebro_b(cfg: ConfigCerebroB | None = None) -> None:
    """Todo campo da ConfigCerebroB tem status registrado; nenhum campo registrado sem existir."""
    campos = {f.name for f in fields(cfg or CONFIG_CEREBRO_B)}
    if campos != set(PARAMETROS_CEREBRO_B):
        raise ValueError(f"sem registro: {sorted(campos - set(PARAMETROS_CEREBRO_B))}; "
                         f"registro sem campo: {sorted(set(PARAMETROS_CEREBRO_B) - campos)}")
    for nome, (status, fonte) in PARAMETROS_CEREBRO_B.items():
        if status not in ("PROPOSTO", "DECIDIDO") or not fonte:
            raise ValueError(f"{nome}: status {status!r} ou fonte vazia")


def sigmoide(v: float) -> float:
    """1 / (1 + exp(-v)), sem estouro nos extremos."""
    if v >= 0.0:
        return 1.0 / (1.0 + math.exp(-v))
    e = math.exp(v)
    return e / (1.0 + e)


class Layout:
    """O vetor plano dos parametros do ATOR (theta) e onde cada bloco fica. O critico e um vetor a parte."""

    def __init__(self, n_entradas: int, n_ocultos: int) -> None:
        self.D, self.H = n_entradas, n_ocultos
        self.V = n_entradas + n_ocultos                     # a entrada da celula: (x, h')
        i = 0
        self.W, self.b = {}, {}
        for p in PORTAS:
            self.W[p] = i
            i += self.H * self.V
            self.b[p] = i
            i += self.H
        self.A = i
        i += len(ACOES) * self.H
        self.bA = i
        i += len(ACOES)
        self.Fr = i
        i += len(FRUTAS) * self.H
        self.bF = i
        i += len(FRUTAS)
        self.info = i
        i += 1
        self.n_ator = i
        self.n_critico = self.H + 1


class PoliticaCerebroB:
    """O DigiBrain B sob o Protocol Politica (agir, observar, estado_interno) e os ganchos da bancada (receber_acao_dono,
    observar_consequencia, escolher_fruta, fruta_comida). Mesma assinatura do PoliticaLobos e do PoliticaCerebroC: ve a bola e as frutas
    so com a chave delas ligada. Nao altera engine.py nem lobos.py (so importa as funcoes publicas e a sonda do instinto)."""

    nome = "cerebro_b"

    def __init__(self, cfg: Config | None = None, cfg_b: ConfigCerebroB | None = None,
                 cfg_bola: ConfigBola | None = None, cfg_frutas: ConfigFrutas | None = None) -> None:
        self.cfg = cfg or CONFIG_PADRAO
        self.cl = cfg_b or CONFIG_CEREBRO_B            # `cl`: a bancada le cl.escala para o sinal da consequencia
        cl = self.cl
        if cl.bits_ponto_fixo < 1:
            raise ValueError("bits_ponto_fixo precisa ser >= 1")
        for nome in ("n_ocultos", "semente_pesos", "janela_latencia_ticks"):
            if type(getattr(cl, nome)) is not int:
                raise TypeError(f"ConfigCerebroB.{nome} precisa ser inteiro")
        for nome in ("delta_t", "escala_inicial", "limite_logit", "taxa_ator", "taxa_critico", "lambda_elegibilidade", "w0_info"):
            if type(getattr(cl, nome)) is not float:
                raise TypeError(f"ConfigCerebroB.{nome} precisa ser float")
        if cl.n_ocultos <= 0 or cl.janela_latencia_ticks <= 0 or cl.delta_t <= 0.0 or cl.limite_logit <= 0.0:
            raise ValueError("n_ocultos, janela_latencia_ticks, delta_t e limite_logit positivos")
        if cl.taxa_ator < 0.0 or cl.taxa_critico < 0.0 or not 0.0 <= cl.lambda_elegibilidade <= 1.0 or cl.escala_inicial < 0.0:
            raise ValueError("taxas e escala_inicial >= 0; lambda_elegibilidade em [0, 1]")
        self._escala = S = cl.escala
        # o herdado (C-1): o mesmo instinto e o mesmo prior do A, com o mundo so com a chave dele ligada
        self._ve_bola = cfg_bola is not None and cfg_bola.ligada
        self._ve_frutas = cfg_frutas is not None and cfg_frutas.ligada
        self._ve_mundo = self._ve_bola or self._ve_frutas
        if self._ve_mundo:
            from ..frutas import PoliticaInstintoFrutas        # importacao tardia: frutas importa o motor inteiro
            cb = cfg_bola if self._ve_bola else replace(cfg_bola or CONFIG_BOLA, ligada=False)
            cf = cfg_frutas if self._ve_frutas else replace(cfg_frutas or CONFIG_FRUTAS, ligada=False)
            self.entradas = ENTRADAS + ENTRADAS_MUNDO
            self._prior = lobos.PoliticaLobos._tabela_prior(S, REGRAS + REGRAS_MUNDO, self.entradas,
                                                            lobos.PoliticaLobos._prior_mundo(cb, cf))
            self._instinto = PoliticaInstintoFrutas(self.cfg, cb, cf)
        else:
            self.entradas = ENTRADAS
            self._prior = lobos.PoliticaLobos._tabela_prior(S)
            self._instinto = PoliticaInstinto(self.cfg)
        # a rede: a celula sorteada pela rng propria (herdada), as cabecas e o critico em zero
        self._L = L = Layout(N_ENTRADAS_B, cl.n_ocultos)
        theta = [0.0] * L.n_ator
        rng = random.Random(cl.semente_pesos)
        r = cl.escala_inicial / math.sqrt(L.V)
        for p in PORTAS:
            for i in range(L.H * L.V):
                theta[L.W[p] + i] = rng.uniform(-r, r)
        theta[L.info] = cl.w0_info
        self._theta = theta
        self._theta0 = list(theta)                         # o inato (a sonda do aprendido zera so o que mudou nas cabecas)
        self._critico = [0.0] * L.n_critico
        self._traco = [0.0] * L.n_ator
        self._h = [0.0] * L.H
        n = self.n_pesos()
        if n >= cl.maximo_pesos:
            raise ValueError(f"{n} parametros, teto {cl.maximo_pesos}")
        self._aprende = bool(cl.aprendizado_ligado)
        self.motivos: list[dict] = []
        self._ultima_regra: str | None = None
        self._registro_decisao: dict | None = None
        self._ultima: dict | None = None
        self._pendentes: list[tuple[int, dict]] = []
        self._consequencia_pendente: tuple | None = None
        self._fruta_na_decisao = False
        self._info_na_decisao: tuple = ()
        self._tick_ultimo_cuidado = 0
        self._tick_ultima_decisao = -1
        self._n_decisoes = 0
        self._n_recompensas: dict[str, int] = {"elogio": 0, "repreensao": 0, "latencia": 0, "ignorado": 0}
        self._n_atualizacoes = 0
        self._soma_delta = 0.0
        self._cortes_limite = 0                         # decisoes reais com um logit aprendido cortado em +-limite_logit

    # ------------------------------------------------------------- leitura

    @property
    def ultima_regra(self) -> str | None:
        return self._ultima_regra

    @property
    def ultimo_motivo(self) -> dict | None:
        return self.motivos[-1] if self.motivos else None

    @property
    def aprende(self) -> bool:
        return self._aprende

    @property
    def ve_mundo(self) -> bool:
        return self._ve_mundo

    def n_pesos(self) -> int:
        """Parametros aprendiveis (contrato 1.3): os da celula (tres camadas e vieses), a cabeca das acoes, a cabeca da fruta com o peso
        da informacao, e o critico. O estado oculto e o traco nao sao parametros; o prior do instinto e fixo (herdado)."""
        return self._L.n_ator + self._L.n_critico

    def pesos_mudaram(self) -> bool:
        return self._theta != self._theta0 or any(c != 0.0 for c in self._critico)

    # ------------------------------------------------------------- percepcao e a celula

    def percepcao(self, obs: Observacao) -> list[float]:
        """A entrada do prior (a mesma do A): lobos.percepcao, mais bola e fruta quando ve o mundo."""
        x = lobos.percepcao(obs, self.cl.escala_ticks_desde_cuidado)
        if self._ve_mundo:
            x.extend((obs.bola, obs.fruta))
        return x

    def entrada_celula(self, obs: Observacao) -> list[float]:
        """As 14 entradas da celula: as do A sem o vies, e o mundo so com a chave dele (fora dela, zero)."""
        x = [*obs.vetor_estado, min(1.0, obs.ticks_desde_cuidado / self.cl.escala_ticks_desde_cuidado)]
        x.append(obs.bola if self._ve_bola else 0.0)
        x.append(obs.fruta if self._ve_frutas else 0.0)
        x.extend(obs.frutas_cenario if self._ve_frutas else (0.0,) * len(FRUTAS))
        if len(x) != N_ENTRADAS_B:
            raise ValueError(f"entrada da celula com {len(x)} valores, esperados {N_ENTRADAS_B}")
        return x

    def _celula(self, v: list[float]) -> dict:
        """A forma fechada do CfC: F, G, K = tanh(W v + b); s = sigmoide(-F dt); h = s G + (1 - s) K."""
        L, th, dt = self._L, self._theta, self.cl.delta_t
        saida = {}
        for p in PORTAS:
            base, vies = L.W[p], L.b[p]
            ativ = []
            for i in range(L.H):
                a = th[vies + i]
                linha = base + i * L.V
                for j in range(L.V):
                    a += th[linha + j] * v[j]
                ativ.append(math.tanh(a))
            saida[p] = ativ
        s = [sigmoide(-f * dt) for f in saida["f"]]
        h = [s[i] * saida["g"][i] + (1.0 - s[i]) * saida["k"][i] for i in range(L.H)]
        return {"v": v, "F": saida["f"], "G": saida["g"], "K": saida["k"], "s": s, "h": h}

    def _logit(self, a: AcaoPet, h: list[float]) -> float:
        L, th = self._L, self._theta
        k = ACOES.index(a)
        z = th[L.bA + k]
        linha = L.A + k * L.H
        for j in range(L.H):
            z += th[linha + j] * h[j]
        lim = self.cl.limite_logit
        return lim if z > lim else (-lim if z < -lim else z)

    def _retropropagar(self, cel: dict, dh: list[float], grad: list[float]) -> None:
        """Soma em `grad` o gradiente da celula para d(objetivo)/dh = dh (um passo; o h' anterior fica como dado)."""
        L, dt = self._L, self.cl.delta_t
        v, F, G, K, s = cel["v"], cel["F"], cel["G"], cel["K"], cel["s"]
        for i in range(L.H):
            if dh[i] == 0.0:
                continue
            da = {"g": dh[i] * s[i] * (1.0 - G[i] * G[i]),
                  "k": dh[i] * (1.0 - s[i]) * (1.0 - K[i] * K[i]),
                  "f": dh[i] * (G[i] - K[i]) * (-dt * s[i] * (1.0 - s[i])) * (1.0 - F[i] * F[i])}
            for p in PORTAS:
                d = da[p]
                grad[L.b[p] + i] += d
                linha = L.W[p] + i * L.V
                for j in range(L.V):
                    grad[linha + j] += d * v[j]

    # ------------------------------------------------------------- decisao

    def _instinto_pesos(self, regra: str, candidatos: tuple, x: list[float]) -> dict[AcaoPet, float]:
        prior = self._prior[regra]
        return {a: ativacao(prior[a], x, self._escala) for a in candidatos}

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        if self._consequencia_pendente is not None:
            raise RuntimeError("E2: o comer com fruta da decisao anterior ficou sem fruta_comida")
        x = self.percepcao(obs)
        regra, candidatos = impulsos(self._instinto, obs)
        inst = self._instinto_pesos(regra, candidatos, x)
        cel = None
        z = {a: 0.0 for a in candidatos}
        if self._aprende:
            cel = self._celula(self.entrada_celula(obs) + self._h)
            z = {a: self._logit(a, cel["h"]) for a in candidatos}
            pesos = {a: inst[a] * math.exp(z[a]) for a in candidatos}
        else:
            pesos = inst
        if len(candidatos) == 1:
            u, acao = None, candidatos[0]
            sem = acao
        else:
            u = rng.random()
            acao = candidatos[sortear([pesos[a] for a in candidatos], u)]
            # a sonda do aprendido (contrato 1.1): a mesma decisao com o aprendido zerado (z = 0: o instinto) e o mesmo u; so le
            sem = acao if cel is None else candidatos[sortear([inst[a] for a in candidatos], u)]
        self._ultima_regra = regra
        self._fruta_na_decisao = self._ve_frutas and obs.fruta > 0.0
        self._info_na_decisao = obs.info_frutas
        valor = None
        if self._aprende:
            total = 0.0
            for a in candidatos:
                total += pesos[a]
            p = {a: pesos[a] / total for a in candidatos}
            grad = [0.0] * self._L.n_ator
            if len(candidatos) > 1:
                self._gradiente_acao(cel, candidatos, acao, p, grad)
            valor = self._valor(cel["h"])
            lim = self.cl.limite_logit
            no_limite = any(abs(z[a]) == lim for a in candidatos)
            self._registro_decisao = {"regra": regra, "candidatos": candidatos, "acao": acao, "cel": cel, "grad": grad, "n": len(self.motivos),
                                      "no_limite": no_limite}
        else:
            self._registro_decisao = None
        self.motivos.append({
            "n": len(self.motivos), "regra": regra, "candidatos": [a.value for a in candidatos],
            "instinto": {a.value: v for a, v in inst.items()},
            "aprendido": ({a.value: z[a] for a in candidatos} if cel is not None else None),
            "pesos": {a.value: v for a, v in pesos.items()},
            "valor": valor, "u": u, "acao": acao.value,
            "sonda": {"acao_sem_aprendido": sem.value, "aprendido_decidiu": sem is not acao},
        })
        return acao

    def _comprometer(self, registro: dict) -> None:
        """A decisao foi observada: o estado oculto dela vira a memoria do B, o traco anda (e <- lambda e + g) e o corte no limite conta."""
        self._h = registro["cel"]["h"]
        lam = self.cl.lambda_elegibilidade
        self._traco = [lam * e + g for e, g in zip(self._traco, registro["grad"])]
        self._cortes_limite += registro["no_limite"]

    def _gradiente_acao(self, cel: dict, candidatos: tuple, acao: AcaoPet, p: dict, grad: list[float]) -> None:
        """d log p(acao) / d theta: dz_a = 1[a = acao] - p_a nos candidatos; a cabeca e, por h, a celula."""
        L, h = self._L, cel["h"]
        dh = [0.0] * L.H
        for a in candidatos:
            dz = (1.0 if a is acao else 0.0) - p[a]
            k = ACOES.index(a)
            grad[L.bA + k] += dz
            linha = L.A + k * L.H
            for j in range(L.H):
                grad[linha + j] += dz * h[j]
                dh[j] += dz * self._theta[linha + j]
        self._retropropagar(cel, dh, grad)

    def _valor(self, h: list[float]) -> float:
        c = self._critico
        v = c[-1]
        for j in range(self._L.H):
            v += c[j] * h[j]
        return v

    # ------------------------------------------------------------- a escolha da fruta (sub-decisao de comer)

    def _q_frutas(self, presentes: list[str], h: list[float] | None, theta_info: float, com_aprendido: bool) -> dict[str, float]:
        """q_f = (b_f + Fr_f . h, so com o aprendido) + theta_info x info_f. Sem o aprendido e com theta_info 0, q = 0."""
        L, th, lim = self._L, self._theta, self.cl.limite_logit
        q = {}
        for f in presentes:
            k = FRUTAS.index(f)
            v = 0.0
            if com_aprendido and h is not None:
                v = th[L.bF + k]
                linha = L.Fr + k * L.H
                for j in range(L.H):
                    v += th[linha + j] * h[j]
            info = self._info_na_decisao[k] if self._info_na_decisao else 0.0
            if theta_info != 0.0 and info != 0.0:
                v += theta_info * info
            q[f] = lim if v > lim else (-lim if v < -lim else v)
        return q

    @staticmethod
    def _pesos_de(presentes: list[str], incentivos: dict, q: dict) -> list[float]:
        """incentivo_f x exp(q_f); com q = 0, o incentivo (a escolha de sempre do MotorFrutas, byte a byte)."""
        return [incentivos[f] * math.exp(q[f]) if q[f] != 0.0 else incentivos[f] for f in presentes]

    def escolher_fruta(self, presentes: list[str], incentivos: dict, u: float) -> str | None:
        """Gancho do MotorFrutas: qual fruta comer, com o mesmo u da rng_fruta e o sorteio do MotorFrutas._escolher. Sem ver as frutas,
        None (o motor escolhe como sempre). Sonda: a fruta sem o aprendido (theta_info inato) e a fruta sem a informacao."""
        if not self._ve_frutas:
            return None
        registro = self._registro_decisao
        h = registro["cel"]["h"] if (self._aprende and registro is not None) else None
        L = self._L
        q = self._q_frutas(presentes, h, self._theta[L.info], self._aprende)
        if self._aprende and any(abs(v) == self.cl.limite_logit for v in q.values()):
            self._cortes_limite += 1
        pesos = self._pesos_de(presentes, incentivos, q)
        escolhida = _sortear_frutas(presentes, pesos, u)
        q0 = self._q_frutas(presentes, None, self._theta0[L.info], False)
        sem_aprendido = _sortear_frutas(presentes, self._pesos_de(presentes, incentivos, q0), u)
        qi = self._q_frutas(presentes, h, 0.0, self._aprende)
        sem_info = _sortear_frutas(presentes, self._pesos_de(presentes, incentivos, qi), u)
        if self.motivos:
            self.motivos[-1]["fruta"] = {
                "presentes": list(presentes), "pesos": dict(zip(presentes, pesos)), "q": q, "u": u, "escolhida": escolhida,
                "info": {f: (self._info_na_decisao[FRUTAS.index(f)] if self._info_na_decisao else 0.0) for f in presentes},
                "sonda": {"escolha_sem_aprendido": sem_aprendido, "aprendido_decidiu": sem_aprendido != escolhida,
                          "escolha_sem_info": sem_info, "info_decidiu": sem_info != escolhida},
            }
        if self._aprende:
            if registro is None or registro["acao"] is not AcaoPet.COMER or "fruta" in registro:
                raise RuntimeError("escolha da fruta sem uma decisao de comer registrada")
            registro["fruta"] = escolhida
            if len(presentes) > 1:
                g = [0.0] * L.n_ator
                total = 0.0
                for w in pesos:
                    total += w
                dh = [0.0] * L.H
                for f, w in zip(presentes, pesos):
                    k = FRUTAS.index(f)
                    dq = (1.0 if f == escolhida else 0.0) - w / total
                    g[L.bF + k] += dq
                    info = self._info_na_decisao[k] if self._info_na_decisao else 0.0
                    g[L.info] += dq * info
                    linha = L.Fr + k * L.H
                    for j in range(L.H):
                        g[linha + j] += dq * h[j]
                        dh[j] += dq * self._theta[linha + j]
                self._retropropagar(registro["cel"], dh, g)
                registro["grad"] = [a + b for a, b in zip(registro["grad"], g)]
                self._traco = [e + b for e, b in zip(self._traco, g)]
        return escolhida

    # ------------------------------------------------------------- o credito

    def observar(self, transicao: Transicao) -> None:
        """Fontes dono e nenhuma: a decisao observada vira a ultima (elogio e bronca creditam a ela) e o chamado fica pendente."""
        self._n_decisoes += 1
        if not self._aprende:
            return
        obs = transicao.observacao
        tick = obs.ticks_desde_cuidado + self._tick_ultimo_cuidado
        if obs.ticks_desde_cuidado < 0 or tick <= self._tick_ultima_decisao:
            raise RuntimeError(f"relogio inconsistente: decisao em {tick}, anterior {self._tick_ultima_decisao}")
        self._tick_ultima_decisao = tick
        self._expirar(tick)
        registro = self._registro_decisao
        if registro is None or registro["acao"] is not transicao.acao:
            raise RuntimeError("registro da decisao nao corresponde a acao observada")
        self._comprometer(registro)
        self._ultima = registro
        if transicao.acao is AcaoPet.CHAMAR_ATENCAO:
            self._pendentes.append((tick, registro))

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """O canal do dono, com a janela da v1 do A: elogio e bronca na ultima decisao (pelo traco); o chamado atendido paga
        1 - L/janela, o expirado recompensa_pedido_ignorado (pelo gradiente da decisao do chamado)."""
        if not self._aprende:
            return
        if tick < self._tick_ultimo_cuidado:
            raise RuntimeError(f"acao do dono no passado: {tick} < {self._tick_ultimo_cuidado}")
        self._tick_ultimo_cuidado = tick
        self._expirar(tick)
        if acao in FEEDBACK:
            if self._ultima is None:
                return
            if acao is AcaoUsuario.ELOGIAR:
                self._creditar(self._ultima, self.cl.recompensa_elogio)
                self._n_recompensas["elogio"] += 1
            else:
                self._creditar(self._ultima, self.cl.recompensa_repreensao)
                self._n_recompensas["repreensao"] += 1
        elif acao in lobos.CUIDADOS:
            janela = self.cl.janela_latencia_ticks
            for tick_pedido, registro in self._pendentes:
                self._creditar(registro, 1.0 - (tick - tick_pedido) / janela, pelo_traco=False)
                self._n_recompensas["latencia"] += 1
            self._pendentes = []

    def _expirar(self, tick: int) -> None:
        janela = self.cl.janela_latencia_ticks
        vivos = []
        for tick_pedido, registro in self._pendentes:
            if tick - tick_pedido > janela:
                self._creditar(registro, self.cl.recompensa_pedido_ignorado, pelo_traco=False)
                self._n_recompensas["ignorado"] += 1
            else:
                vivos.append((tick_pedido, registro))
        self._pendentes = vivos

    def observar_consequencia(self, transicao: Transicao, f_S: int, cfg_consequencia: ConfigConsequencia | None = None) -> None:
        """Fonte consequencia (P1, P2): r = f_S / S, o sinal homeostatico escalar da bancada (conferido). Comer com fruta no cenario
        espera a fruta_comida (a E2, como no A e no C)."""
        self._n_decisoes += 1
        if not self._aprende:
            return
        if self._consequencia_pendente is not None:
            raise RuntimeError("E2: o comer com fruta da decisao anterior ficou sem fruta_comida")
        registro = self._registro_decisao
        if registro is None or registro["acao"] is not transicao.acao:
            raise RuntimeError("registro da decisao nao corresponde a acao observada")
        self._comprometer(registro)
        self._ultima = registro
        cc = cfg_consequencia or CONFIG_CONSEQUENCIA
        self._n_recompensas["consequencia"] = self._n_recompensas.get("consequencia", 0) + 1
        if self._fruta_na_decisao and transicao.acao is AcaoPet.COMER:
            self._consequencia_pendente = (registro, transicao, cc)
            return
        if sinal_homeostatico(transicao, self._escala, cc) != f_S:
            raise RuntimeError(f"o sinal da bancada {f_S} nao e o sinal homeostatico da transicao")
        self._creditar(registro, f_S / self._escala)

    def fruta_comida(self, fruta: str, obs_depois: Observacao) -> None:
        """Gancho do MotorFrutas logo depois de comer: o comer pendente recebe o sinal da fruta (a E2: o humor entra)."""
        pendente, self._consequencia_pendente = self._consequencia_pendente, None
        if pendente is None:
            return
        registro, transicao, cc = pendente
        if registro.get("fruta") != fruta:
            raise RuntimeError(f"E2: fruta comida {fruta!r} nao e a da escolha registrada")
        self._n_recompensas["consequencia_fruta"] = self._n_recompensas.get("consequencia_fruta", 0) + 1
        f = sinal_homeostatico_fruta(transicao.observacao, obs_depois, self._escala, cc)
        self._creditar(registro, f / self._escala)

    def _creditar(self, registro: dict, r: float, pelo_traco: bool = True) -> None:
        """Ator-critico: delta = r - V(h da decisao). O ator anda taxa_ator x delta pelo traco (o sinal da decisao mais recente) ou pelo
        gradiente da propria decisao (um chamado antigo); o critico anda taxa_critico x delta pelo h da decisao."""
        h = registro["cel"]["h"]
        delta = r - self._valor(h)
        e = self._traco if (pelo_traco and registro is self._registro_decisao) else registro["grad"]
        passo = self.cl.taxa_ator * delta
        if passo != 0.0:
            self._theta = [t + passo * g for t, g in zip(self._theta, e)]
        pc = self.cl.taxa_critico * delta
        c = self._critico
        for j in range(self._L.H):
            c[j] += pc * h[j]
        c[-1] += pc
        self._n_atualizacoes += 1
        self._soma_delta += delta

    # ------------------------------------------------------------- serializacao

    def pesos(self) -> dict:
        """Os parametros por bloco (leitura)."""
        L, th = self._L, self._theta
        celula = {p: {"W": [th[L.W[p] + i * L.V:L.W[p] + (i + 1) * L.V] for i in range(L.H)], "b": th[L.b[p]:L.b[p] + L.H]}
                  for p in PORTAS}
        ator = {a.value: th[L.A + k * L.H:L.A + (k + 1) * L.H] + [th[L.bA + k]] for k, a in enumerate(ACOES)}
        fruta = {f: th[L.Fr + k * L.H:L.Fr + (k + 1) * L.H] + [th[L.bF + k]] for k, f in enumerate(FRUTAS)}
        return {"celula": celula, "ator": ator, "fruta": fruta, "theta_info": th[L.info], "critico": list(self._critico)}

    def estado_interno(self) -> dict:
        def registro_dict(r):
            if r is None:
                return None
            d = {"n": r["n"], "regra": r["regra"], "candidatos": [a.value for a in r["candidatos"]], "acao": r["acao"].value,
                 "h": list(r["cel"]["h"])}
            if "fruta" in r:
                d["fruta"] = r["fruta"]
            return d
        d = {
            "nome": self.nome,
            "parametros_aprendidos": self.n_pesos(),
            "aprendizado_ligado": self._aprende,
            "escala": self._escala,
            "entradas": list(self.entradas),
            "entradas_celula": list(ENTRADAS_B),
            "n_ocultos": self._L.H,
            "pesos": self.pesos(),
            "oculto": list(self._h),
            "traco": list(self._traco),
            "n_decisoes": len(self.motivos),
            "motivos": [dict(m) for m in self.motivos],
            "aprendizado": {
                "taxa_ator": self.cl.taxa_ator, "taxa_critico": self.cl.taxa_critico,
                "lambda_elegibilidade": self.cl.lambda_elegibilidade, "w0_info": self.cl.w0_info,
                "n_atualizacoes": self._n_atualizacoes, "soma_delta": self._soma_delta, "recompensas": dict(self._n_recompensas),
                "cortes_limite": self._cortes_limite,
                "tick_ultimo_cuidado": self._tick_ultimo_cuidado, "tick_ultima_decisao": self._tick_ultima_decisao,
                "pendentes": [[t, registro_dict(r)] for t, r in self._pendentes],
                "ultima": registro_dict(self._ultima),
            },
        }
        if self._consequencia_pendente is not None:
            d["aprendizado"]["consequencia_pendente"] = registro_dict(self._consequencia_pendente[0])
        return d


def fabrica_cerebro_b(cfg_b: ConfigCerebroB | None = None, cfg_bola: ConfigBola | None = None,
                      cfg_frutas: ConfigFrutas | None = None):
    """A fabrica para a bancada: `lambda cfg=None: PoliticaCerebroB(cfg, cfg_b, cfg_bola, cfg_frutas)`."""
    return lambda cfg=None: PoliticaCerebroB(cfg, cfg_b, cfg_bola, cfg_frutas)
