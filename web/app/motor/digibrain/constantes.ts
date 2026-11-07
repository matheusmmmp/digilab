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
