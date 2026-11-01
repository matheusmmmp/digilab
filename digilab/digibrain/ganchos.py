"""Os ganchos que ficam vazios no prototipo: M-PERS, M-GEN e M-EXPR (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.9).

- **M-GEN:** o registro unico dos parametros inatos, `ParametrosInatos`, por modulo; no prototipo e a constante PROPOSTA
  `CONFIG_DIGIBRAIN_INATOS` (digilab/config.py). O genoma futuro escreve esse registro; o aprendido nunca entra nele (EG-5).
- **M-PERS:** `faceta(nome)` e `mudar_faceta(nome, passo, episodios)`; no prototipo nao ha faceta, a leitura devolve o neutro (0, nenhuma
  inclinacao) e a mudanca falha alto (a memoria consolidada e etapa propria; o temperamento inato fica fora do alcance dela, DM-6).
- **M-EXPR:** le so o registro da decisao, fora do cerebro, e nao decide nada; a fala e o T-MOTIVO-2 entram com o verificador da fala
  (fora da etapa 1)."""
from __future__ import annotations

from dataclasses import fields

from ..config import CONFIG_DIGIBRAIN_INATOS, ConfigDigibrainInatos
from ._comum import sem_equacao

# os campos de cada modulo (o que o genoma futuro escreveria em cada um)
CAMPOS_POR_MODULO = {
    "comum": ("escala", "a_max"),
    "sens": ("tau_hab", "escala_cuidado"),
    "afeto": ("tau_v", "tau_e", "urgencia_a", "urgencia_b", "urgencia_lambda", "ganho_r", "r_norm", "fora_do_r", "g0", "beta_e",
              "g_min", "g_max", "e0", "beta_t", "beta_u", "e_max"),
    "impulso": ("w0", "w0_prox", "w0_nov", "w0_tipo", "w0_tipo_cheiro"),
    "arb": ("epsilon", "lambda_sono"),
    "plast": ("eta_d", "eta_h", "h_max", "c_g", "s_v", "g_max_incentivo"),
    "estado": ("tau_c", "tau_f_sobe", "tau_f_desce", "w_pers", "n_desiste", "n_desiste_cheiro", "n_suspensa_max", "lambda_retomar",
               "n_seg_max"),
    "mem": ("n_ep", "lambda_busca", "d_max", "w_mem", "theta_sig", "n_rec", "n_dur", "n_cen", "janela_rec", "theta_dur", "n_rep_central", "w_lugar",
            "w_vista", "w_corpo", "sim_min", "w_lem"),
}


class Personalidade:
    """M-PERS: as facetas; o temperamento inato fica fora do alcance delas (DM-6). No prototipo, nenhuma faceta."""

    NEUTRO = 0

    def faceta(self, nome: str) -> int:
        return self.NEUTRO

    def mudar_faceta(self, nome: str, passo: int, episodios) -> None:
        raise sem_equacao("M-PERS", "mudar_faceta")


class ParametrosInatos:
    """M-GEN: o registro unico dos parametros inatos, por modulo"""

    def __init__(self, inatos: ConfigDigibrainInatos | None = None) -> None:
        self.inatos = inatos or CONFIG_DIGIBRAIN_INATOS
        todos = {f.name for f in fields(self.inatos)}
        listados = [c for cs in CAMPOS_POR_MODULO.values() for c in cs]
        if sorted(listados) != sorted(todos):
            raise RuntimeError(f"M-GEN: campos fora dos modulos {sorted(todos - set(listados))} ou repetidos")

    def do_modulo(self, modulo: str) -> dict:
        if modulo not in CAMPOS_POR_MODULO:
            raise KeyError(f"M-GEN: modulo {modulo!r}")
        return {c: getattr(self.inatos, c) for c in CAMPOS_POR_MODULO[modulo]}


class Expressao:
    """M-EXPR: le so o registro da decisao, fora do cerebro, e nao decide nada"""

    def expressar(self, registro):
        raise sem_equacao("M-EXPR", "expressar")
