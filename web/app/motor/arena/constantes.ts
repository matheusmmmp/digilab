/* Numeros da luta da POC (docs/TAREFA_V3_LUTA_POC.md, LP1): os de web/app/arena/constantes.ts do commit efb2ded, copiados do prototipo
   remaster/fonte/site/arena.html (sha256 f3be1160...91fbeb). Sao numeros do DigiLab, nao do jogo: todos PROPOSTOS ate a LP5.
   Fonte: "EQ" = remaster/arena_equilibrio.md (as duas rodadas de 2026-10-29); "PROTOTIPO" = so o arena.html, SEM FONTE de medicao.
   Sairam com o 1 contra 1 (LP1, como no #448): as trocas, a investida do jogador e os status genericos da tela. */

/** A chave da luta da POC no jogo (LP1), LIGADA na LP4 (Matheus, 2026-11-10: "Sim, abre a LP4"): a luta do pet (a v21, motor/luta_poc.ts)
    e esta simulacao, e o combate por turnos (combate_tr) saiu. Fica como constante porque o app e os testes a leem (src/lutaPoc.ts) */
export const LUTA_POC_LIGADA = true;

/** mundo logico em px de sprite (desenhado em 2x). PROPOSTO, PROTOTIPO */
export const MUNDO = { w: 480, h: 280, esc: 2 } as const;
/** elipse da arena. PROPOSTO, PROTOTIPO */
export const ELIPSE = { cx: 240, cy: 172, rx: 210, ry: 84 } as const;
/** esqueleto Spine: 1 unidade = 100 px (velocidade dos projeteis dos dados do jogo). Do jogo (levantamento da UP-ARENA, secao 4) */
export const PX_POR_UNIDADE = 100;
/** passo fixo da simulacao (ms): o da medicao do arena_equilibrio.md (passo(16)). PROPOSTO, EQ */
export const PASSO_MS = 16;
/** limite da luta (ms): "sem fim" = chegou aqui. PROPOSTO, EQ */
export const LIMITE_MS = 300_000;

/** equilibrio entre Digimon. PROPOSTO, EQ (rodada dos Digimon, 2026-10-29). kGolpe e kProj entram ja aplicados no `fr` da tabela
    (tools/gerar_tabela_arena.py); um teste confere que o gerador usa os mesmos */
export const EQ = {
  raio: 18,            // corpo de todos (px)
  alcanceCorpo: 44,    // alcance do golpe corpo a corpo (px, mais o corpo do alvo)
  investida: 58,       // px que o golpe corpo a corpo avanca na direcao do alvo durante a preparacao
  recuo: 1,            // velocidade ao andar para longe do alvo (1 = sem penalidade)
  peito: 24,           // altura (px) de onde o tiro sai e onde ele acerta
  danoCorpo: 1, danoDist: 1,
  kGolpe: 0.06, kProj: 0.05,   // dano x (instante do golpe / 0,5 s)^kGolpe x (30 / velocidade do projetil)^kProj
  variacao: 0.1,       // dano varia +-10% por golpe
} as const;

export type Dificuldade = "facil" | "normal" | "dificil";
/** a IA: chance de desviar e tempo de reacao (ms). PROPOSTO, PROTOTIPO. A LP-3 usa a "normal" para os dois lados. O erro de mira da POC
    (facil 40, normal 18, dificil 6 px) passou a ser do lutador (Stats.erro; LP2, decisao 2): ERRO_MIRA_POC guarda os da POC */
export const DIFIC: Record<Dificuldade, { desvio: number; reacao: number }> = {
  facil: { desvio: 0.15, reacao: 450 },
  normal: { desvio: 0.45, reacao: 260 },
  dificil: { desvio: 0.8, reacao: 140 },
};
/** o erro de mira (px) de cada dificuldade da POC: o "normal" e o do lutador neutro do mapeamento da LP2. PROPOSTO, PROTOTIPO */
export const ERRO_MIRA_POC: Record<Dificuldade, number> = { facil: 40, normal: 18, dificil: 6 };

/** as opcoes da luta e os padroes do prototipo (os da medicao). PROPOSTO, EQ: vantagem de atributo 1,5x, projeteis 0,15x. O ritmo (a
    vida do jogo / 6) nao e mais da simulacao: a vida chega pronta nos Stats */
export const OPCOES_PADRAO = { forca: 1.5, pvel: 0.15, dific: "normal" as Dificuldade };

/** a distancia do tiro (LUTA_POC, LP5, D-LP5-12: "Desenho agora, motor na LP5"): como quem atira mantem distancia de quem luta de perto.
    So vale quando a entrada da luta traz o `tiro` (o candidato da bancada; no jogo, a versao do pet que o ligar, na LP5-5). Sem ele, a luta
    e a de sempre, byte a byte. Os valores do TIRO_V21 sao os da POC; os do candidato sao PROPOSTOS, SEM FONTE.
    - distMin: abaixo dela (px) quem atira nao solta o tiro de projetil e recua; 0 = sem distancia minima;
    - esperaMax: quanto tempo (ms) ele espera abaixo da distMin antes de atirar mesmo assim (encurralado na borda);
    - recuaAbaixo: recua quando a distancia fica abaixo desta fracao do alcance (a POC: 0,5);
    - recuo: a velocidade do recuo de quem atira (x o movimento; a POC: o EQ.recuo, 1);
    - recuaNaPrep: a velocidade (x o movimento) com que ele se afasta na preparacao do tiro, se o alvo esta mais perto que a distMin ou que
      o recuaAbaixo; 0 = parado, como na POC */
export interface Tiro { distMin: number; esperaMax: number; recuaAbaixo: number; recuo: number; recuaNaPrep: number }
export const TIRO_V21: Readonly<Tiro> = Object.freeze({ distMin: 0, esperaMax: 0, recuaAbaixo: 0.5, recuo: EQ.recuo, recuaNaPrep: 0 });

/** movimento e tempos das acoes. PROPOSTO, PROTOTIPO */
export const ACAO = {
  entradaX: 130,             // px do centro onde cada lado entra
  entradaY: -6,
  alcanceDist: 150,          // alcance de quem atira (px)
  desvioCpu: 380, desvioCpuMs: 180,
  atordoaCurto: 220, atordoaLongo: 900,
  empurrao: 6,               // px por golpe (x0,5 no eixo y)
  eixoY: 0.7,                // o movimento em y vale 0,7 (a arena e vista de lado)
  recSkIni: 2500, recSkVar: 1500, recargaIni: 300, recargaVar: 300,
  recargaMin: 150,
} as const;
