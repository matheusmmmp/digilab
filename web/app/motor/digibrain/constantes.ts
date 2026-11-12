/* As constantes do DigiBrain modular no laboratorio (docs/TAREFA_V3_LAB_MODULAR.md, LM1): a ConfigDigibrainInatos e a ConfigDigibrain do
   braco REL da C4, copiadas do gabarito (test/gabaritos/digibrain_modular_constantes.json, do exportador da LM0). Nenhum numero nasce
   aqui: test/digibrain_modular_constantes.test.ts confere cada folha contra o gabarito e a CONFIG_MODULAR_MUNDO contra o motor.
   Os valores sao PROPOSTOS (os do Python); a calibracao fica para a rodada de equilibrio. */

/** a ConfigDigibrainInatos (digilab/config.py), na ordem do gabarito; as tabelas sao listas de pares, como no Python */
export const INATOS_MODULAR = {
  a_max: 4096,
  beta_e: 1024,
  beta_t: 512,
  beta_u: 512,
  c_g: 1024,
  d_max: 1024,
  e0: 512,
  e_max: 1024,
  epsilon: 128,
  escala: 1024,
  escala_cuidado: 480,
  eta_d: 256,
  eta_faceta: 16,
  eta_h: 4,
  fora_do_r: ["susto"],
  g0: 1024,
  g_max: 2048,
  g_max_incentivo: 1024,
  g_min: 512,
  ganho_r: 4,
  h_max: 512,
  janela_rec: 96,
  lambda_busca: 256,
  lambda_retomar: 256,
  lambda_sono: 256,
  n_cen: 8,
  n_desiste: 3,
  n_desiste_cheiro: 6,
  n_dur: 32,
  n_ep: 16,
  n_rec: 16,
  n_rep_central: 2,
  n_seg_max: 6,
  n_suspensa_max: 6,
  r_norm: 2,
  s_v: 1024,
  sim_min: 768,
  tau_c: 15,
  tau_e: 120,
  tau_f_desce: 480,
  tau_f_sobe: 60,
  tau_hab: 120,
  tau_v: 240,
  teto_faceta: 256,
  theta_dur: 256,
  theta_sig: 128,
  urgencia_a: 512,
  urgencia_b: 1536,
  urgencia_lambda: 512,
  w0: [["ocioso", [["vies", 128], ["u_fome", -256], ["u_higiene", -256], ["u_energia", -256], ["u_tedio", -256]]], ["dormir", [["vies", -512], ["u_fome", -1024], ["u_energia", 3072], ["noite", 512], ["dormindo", 512]]], ["comer", [["vies", -1088], ["u_fome", 3072]]], ["brincar", [["vies", -256], ["u_fome", -512], ["u_energia", -512], ["u_humor", 512], ["u_tedio", 512], ["bola_vista", 1024]]], ["chamar_atencao", [["vies", -512], ["u_higiene", 1024], ["u_solidao", 512], ["u_estresse", 256], ["sem_cuidado", 256], ["comida_vista", -1024], ["fome_sem_comida", 2048]]], ["explorar", [["vies", 128], ["u_energia", -2048], ["u_tedio", 1024], ["u_curiosidade", 1024], ["fome_sem_comida", 512], ["F", 512]]], ["emburrar", [["vies", -512], ["cuidado_humor", 2048]]]],
  w0_nov: [["brincar", 128]],
  w0_prox: [["comer", 512], ["brincar", 256]],
  w0_tipo: [["comer", [["racao", 256], ["a", 256], ["b", 256], ["c", 256], ["podre", -2048]]]],
  w0_tipo_cheiro: 256,
  w_corpo: 1,
  w_lem: 512,
  w_lugar: 2,
  w_mem: 1024,
  w_pers: 4096,
  w_vista: 1,
} as const;

/** a ConfigDigibrain do laboratorio (o braco REL da C4: o M3* com a memoria_autobio, controle_mem = "rel") */
export const CONFIG_DIGIBRAIN_LAB = {
  cheiro_inato: true,
  controle_g_apr: "nenhum",
  controle_mem: "rel",
  credito_corrida: false,
  facetas_mem: false,
  fala_unidades: false,
  g_apr_constante: 0,
  intencao_cheiro: true,
  intencao_suspensa: false,
  ligada: true,
  m_mem: true,
  memoria_autobio: true,
  modula_g_apr: false,
  p1: true,
  p2: true,
  passeio: false,
  persistencia: true,
  redecidir_evento: false,
} as const;

/** a ConfigDigibrain que o M-ADAPT recebe: a do laboratorio, com a subchave `fala_unidades` (DC3d) ligada ou nao */
/** `olhar` (GOSTO_VISUAL, P1f): a subchave do gosto visual, opcional para a config de hoje sair byte a byte (sem o campo, desligada) */
export type ConfigDigibrainModular = Omit<typeof CONFIG_DIGIBRAIN_LAB, "fala_unidades"> & { readonly fala_unidades: boolean; readonly olhar?: boolean };
/** o laboratorio com a subchave `fala_unidades` ligada (docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, 3.1 e A1.1; o braco LAB+F da DC3): so o pet de
 *  teste com a marca "fu" no registro (motor.ts) */
export const CONFIG_DIGIBRAIN_LAB_FALA: ConfigDigibrainModular = { ...CONFIG_DIGIBRAIN_LAB, fala_unidades: true };

/** As unidades de fala (digilab/config.py, CONTEUDOS_FALA e TERMO_DO_CONTEUDO; DC3, 3.1): com a `fala_unidades`, o `chamar_atencao` vira
 *  (chamar_atencao, c) com c em CONTEUDOS_FALA; o termo do receptor de cada conteudo no W0 do chamar. Conferidas contra o gabarito da DC3d
 *  (test/gabaritos/digibrain_fala_unidades.json.gz) por test/digibrain_fala_unidades.test.ts. */
export const CONTEUDOS_FALA = ["fome", "higiene", "solidao"] as const;
export type ConteudoFala = typeof CONTEUDOS_FALA[number];
export const TERMO_DO_CONTEUDO = [["fome", "fome_sem_comida"], ["higiene", "u_higiene"], ["solidao", "u_solidao"]] as const;
/** a ConfigFalaUnidades (digilab/config.py): `ganho_conteudo` = 3S/2, PROPOSTO, SEM FONTE (fixado na DC3a pela condicao da 3.1) */
export const CONFIG_FALA_UNIDADES = { ganho_conteudo: 1536 } as const;

/** O gosto visual no DigiBrain modular (GOSTO_VISUAL, P1d do Python; o porte da P1f): o comportamento `olhar` no fim da lista, so com a
 *  subchave `olhar`, e a ConfigOlhar (digilab/config.py; todos PROPOSTOS, SEM FONTE). Conferidos contra test/gabaritos/gosto_visual.json.gz
 *  por test/gosto_visual_paridade.test.ts. Desligada (todo pet de hoje), nada disto entra. */
export const COMPORTAMENTO_OLHAR = "olhar";
export interface ConfigOlhar {
  readonly escala: number; readonly largura_min: number; readonly largura_max: number;
  readonly w0_olhar: readonly (readonly [string, number])[]; readonly w0_prox: number; readonly w0_nov: number; readonly w_gosto: number;
  readonly ganho_gosto_visual: number; readonly tau_exposicao: number; readonly teto_exposicao: number; readonly agrado_no_corpo: boolean;
}
export const CONFIG_OLHAR: ConfigOlhar = {
  escala: 450000, largura_min: 112500, largura_max: 450000, w0_olhar: [["vies", -256], ["u_tedio", 512], ["u_curiosidade", 512]],
  w0_prox: 256, w0_nov: 256, w_gosto: 1024, ganho_gosto_visual: 1024, tau_exposicao: 960, teto_exposicao: 128, agrado_no_corpo: false,
};
/** o laboratorio com a subchave `olhar` (a vida do gabarito do gosto visual) */
export const CONFIG_DIGIBRAIN_LAB_OLHAR: ConfigDigibrainModular = { ...CONFIG_DIGIBRAIN_LAB, olhar: true };
/** o olhar do jogo (a v31; D-GV-CEREBRO-4): a ConfigOlhar da P1d com a subchave do agrado no corpo ligada (GV-16: "os dois, cada um atras da
    sua sub-chave"; o canal `gosto_visual` no sinal ja vem com a subchave `olhar`). Os numeros sao os da P1d, PROPOSTOS, SEM FONTE */
export const CONFIG_OLHAR_JOGO: ConfigOlhar = { ...CONFIG_OLHAR, agrado_no_corpo: true };

/** os numeros do Config e da ConfigMundo que o M-SENS le: o passo do cerebro (Config.intervalo_decisao_ticks), a noite (Config.inicio_noite_tick,
 *  fim_noite_tick) e a visao (ConfigMundo.sub, raio_visao_celulas, max_vistos). Conferidos contra o motor e contra constantes_python.json. */
export const CONFIG_MODULAR_MUNDO = {
  intervalo_decisao_ticks: 15, inicio_noite_tick: 1320, fim_noite_tick: 420, sub: 16, raio_visao_celulas: 6, max_vistos: 8,
} as const;

/** TICKS_POR_DIA (digilab/config.py) */
export const TICKS_POR_DIA = 1440;

/** RECEPTORES_DIGIBRAIN, COMPORTAMENTOS_DIGIBRAIN e CARACTERISTICAS_DIGIBRAIN (digilab/config.py), na ordem do Python */
export const RECEPTORES_DIGIBRAIN = ["fome", "higiene", "energia", "humor", "saude", "tedio", "curiosidade", "solidao", "estresse", "dor", "susto"] as const;
export const COMPORTAMENTOS_DIGIBRAIN = ["ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar"] as const;
export const CARACTERISTICAS_DIGIBRAIN = ["vies", ...RECEPTORES_DIGIBRAIN.map(r => `u_${r}`), "noite", "dormindo", "sem_cuidado", "comida_vista",
  "sem_comida", "bola_vista", "fome_sem_comida", "cuidado_humor", "F", "V", "E"] as const;


/** A ConfigDecodificador (digilab/config.py, DC1): os pesos e os limiares do `dec-v1`, PROPOSTOS, SEM FONTE. Conferida folha a folha contra
 *  test/gabaritos/decodificador_python.json por test/decodificador.test.ts. */
export const CONFIG_DECODIFICADOR = {
  limiar_valor: 512, limiar_confianca: 512, limiar_desfecho: 128, piso_sonda: 640, ganho_v: 4, ganho_sigma: 8, n_sp_teto: 8,
  fins_frustrantes: ["desistiu", "sumiu", "trocou"],
  p_fome_urgencia: 2, p_fome_fracao: 1, p_fome_intencao: 1, p_fome_pista: 1,
  p_sono_urgencia: 2, p_sono_fracao: 1, p_sono_reflexo: 1, p_sono_noite: 1,
  p_agitacao_e: 3, p_agitacao_urgencia: 2,
  p_frustracao_f: 2, p_frustracao_fim: 1, p_frustracao_n_sp: 1,
  p_determinacao_c: 2, p_determinacao_persistencia: 1,
  p_indecisao_margem: 2, p_indecisao_sondas: 1,
  p_solidao_urgencia: 2, p_solidao_fracao: 1,
  p_curiosidade_urgencia: 1, p_curiosidade_tedio: 1, p_curiosidade_g_exp: 1, p_curiosidade_fracao: 1,
} as const;
export type ConfigDecodificador = typeof CONFIG_DECODIFICADOR;

/** o alcance da memoria de lugar na ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secoes 12.14 a 12.16; a IG-6; o D_MAX_ILHA_GRANDE do
    Python): o `d_max` na proporcao do mapa de 128 x 60 celulas (2 048 subunidades = 128 celulas; o de sempre, 1 024, e a largura do mapa de
    64 x 30). So os pets do jogo na ilha grande o usam (a v25 desde o ovo; os vivos, pelo evento "ma"). DECIDIDO (Matheus, 2026-11-11:
    "Sim, para 128 celulas") */
export const D_MAX_ILHA_GRANDE = 2048;

/** o sono que segura (docs/TAREFA_V3_SONO_SEGURA.md; a ConfigSonoSegura do Python, numa config propria para o dump do modular nao mudar):
    ligado, o pet que esta dormindo segue no reflexo do sono ate a leitura da energia chegar a `lambda_acordar` (o primeiro inteiro acima de
    0,9 S), salvo a fome urgente (a urgencia da fome acima do `urgencia_lambda`) e o dono que o acorda. PROPOSTO, SEM FONTE; conferido
    contra o gabarito test/gabaritos/digibrain_modular_sono_segura.json.gz por test/digibrain_modular_sono_segura.test.ts */
export interface ConfigSonoSegura { readonly ligada: boolean; readonly lambda_acordar: number }
export const CONFIG_SONO_SEGURA: ConfigSonoSegura = { ligada: false, lambda_acordar: 922 };
export const CONFIG_SONO_SEGURA_LIGADA: ConfigSonoSegura = { ...CONFIG_SONO_SEGURA, ligada: true };
