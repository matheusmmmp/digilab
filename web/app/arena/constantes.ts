/* Numeros da arena em tempo real (docs/TAREFA_V2_UP_ARENA.md). Sao numeros do DigiLab, nao do jogo: todos PROPOSTOS ate o Matheus
   jogar (D5, 2026-10-29), copiados do prototipo remaster/fonte/site/arena.html (sha256 f3be1160...91fbeb).
   Fonte: "EQ" = remaster/arena_equilibrio.md (as duas rodadas de 2026-10-29); "PROTOTIPO" = so o arena.html, SEM FONTE de medicao. */

/** mundo logico em px de sprite (desenhado em 2x). PROPOSTO, PROTOTIPO */
export const MUNDO = { w: 480, h: 280, esc: 2 } as const;
/** elipse da arena. PROPOSTO, PROTOTIPO */
export const ELIPSE = { cx: 240, cy: 172, rx: 210, ry: 84 } as const;
/** esqueleto Spine: 1 unidade = 100 px (velocidade dos projeteis dos dados do jogo). Do jogo (levantamento, secao 4) */
export const PX_POR_UNIDADE = 100;
/** ms entre trocas voluntarias; ms que quem entra fica sem poder agir. PROPOSTO, PROTOTIPO */
export const TROCA_ESPERA = 3000;
export const ENTRADA = 450;
/** passo fixo da simulacao (ms): o da medicao do arena_equilibrio.md (passo(16)). PROPOSTO, EQ */
export const PASSO_MS = 16;
/** limite da luta na medicao (ms): "sem fim" = chegou aqui. PROPOSTO, EQ */
export const LIMITE_MS = 300_000;

/** equilibrio entre Digimon. PROPOSTO, EQ (rodada dos Digimon, 2026-10-29) */
export const EQ = {
  raio: 18,            // corpo de todos (px)
  alcanceCorpo: 44,    // alcance do golpe corpo a corpo (px, mais o corpo do alvo)
  investida: 58,       // px que o golpe corpo a corpo avanca na direcao do alvo durante a preparacao
  recuo: 1,            // velocidade ao andar para longe do alvo (1 = sem penalidade)
  peito: 24,           // altura (px) de onde o tiro sai e onde ele acerta
  danoCorpo: 1, danoDist: 1,
  kGolpe: 0.06, kProj: 0.05,   // dano x (instante do golpe / 0,5 s)^kGolpe x (30 / velocidade do projetil)^kProj
  pesoEstagio: 0.2,    // fracao da diferenca de status entre estagios e por nivel que vale na arena
  variacao: 0.1,       // dano varia +-10% por golpe
} as const;

export type Dificuldade = "facil" | "normal" | "dificil";
/** CPU: chance de desviar, tempo de reacao (ms), erro de mira (px), chance de trocar quando o ativo esta mal. PROPOSTO, PROTOTIPO
    (a medicao usa a "normal") */
export const DIFIC: Record<Dificuldade, { desvio: number; reacao: number; erro: number; troca: number }> = {
  facil: { desvio: 0.15, reacao: 450, erro: 40, troca: 0.1 },
  normal: { desvio: 0.45, reacao: 260, erro: 18, troca: 0.4 },
  dificil: { desvio: 0.8, reacao: 140, erro: 6, troca: 0.8 },
};

/** status genericos (Digimon sem registro no jogo, e movimento, ciclo e habilidade de todos): [chave, rotulo, min, max, passo, padrao].
    PROPOSTO, PROTOTIPO (8 s: a recarga mais comum das habilidades ativas do jogo) */
export const STATS = [
  ["hp", "Vida", 200, 4000, 50, 900],
  ["atk", "Ataque", 10, 400, 5, 100],
  ["def", "Defesa", 0, 300, 5, 50],
  ["vel", "Movimento", 20, 200, 5, 70],
  ["cad", "Ciclo ataque (ms)", 800, 4000, 50, 2000],
  ["crit", "Crítico %", 0, 50, 1, 10],
  ["hcd", "Recarga hab. (s)", 2, 30, 1, 8],
  ["hpot", "Força hab. ×", 1, 4, 0.25, 2],
] as const;
export type ChaveStat = typeof STATS[number][0];
export type StatsGenericos = Record<ChaveStat, number>;
export const STATS_PADRAO = Object.fromEntries(STATS.map(s => [s[0], s[5]])) as StatsGenericos;

/** opcoes da luta e os padroes do prototipo (os da medicao). PROPOSTO, EQ: vida do jogo / 6, vantagem de atributo 1,5x, projeteis 0,15x */
export const OPCOES_PADRAO = { ritmo: 6, forca: 1.5, pvel: 0.15, dific: "normal" as Dificuldade };
export const RITMOS = [1, 3, 6, 10] as const;
export const FORCAS = [1, 1.25, 1.5, 2] as const;

/** movimento e tempos das acoes. PROPOSTO, PROTOTIPO */
export const ACAO = {
  entradaX: 130,             // px do centro onde cada lado entra
  entradaY: -6,
  alcanceDist: 150,          // alcance de quem atira (px)
  investidaJogador: 420, investidaJogadorMs: 160, investidaRecargaMs: 1200,
  desvioCpu: 380, desvioCpuMs: 180,
  atordoaCurto: 220, atordoaLongo: 900,
  empurrao: 6,               // px por golpe (x0,5 no eixo y)
  eixoY: 0.7,                // o movimento em y vale 0,7 (a arena e vista de lado)
  recSkIni: 2500, recSkVar: 1500, recargaIni: 300, recargaVar: 300,
  recargaMin: 150, recargaTroca: 500,
} as const;
