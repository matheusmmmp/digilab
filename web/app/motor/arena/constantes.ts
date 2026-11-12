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
/** a chave forcaAtr (N3 da investigacao do nucleo, docs/PLANO_LUTA_NUCLEO.md; D-N-3 e D-N-5): a vantagem do atributo vem na entrada da
    luta, de 1 (o triangulo sem efeito) ate este teto; sem a chave, o OPCOES_PADRAO.forca. Nenhuma versao de pet a liga. PROPOSTO, SEM FONTE */
export const FORCA_ATR_MAX = 3;

/** a distancia do tiro (LUTA_POC, LP5, D-LP5-12: "Desenho agora, motor na LP5"): como quem atira mantem distancia de quem luta de perto.
    So vale quando a entrada da luta traz o `tiro` (o candidato da bancada; no jogo, a versao do pet que o ligar, na LP5-5). Sem ele, a luta
    e a de sempre, byte a byte. Os valores do TIRO_V21 sao os da POC; os do candidato sao PROPOSTOS, SEM FONTE.
    - distMin: abaixo dela (px) quem atira nao solta o tiro de projetil e recua; 0 = sem distancia minima;
    - esperaMax: quanto tempo (ms) ele espera abaixo da distMin antes de atirar mesmo assim (encurralado na borda);
    - recuaAbaixo: recua quando a distancia fica abaixo desta fracao do alcance (a POC: 0,5);
    - recuo: a velocidade do recuo de quem atira (x o movimento; a POC: o EQ.recuo, 1);
    - recuaNaPrep: a velocidade (x o movimento) com que ele se afasta na preparacao do tiro, se o alvo esta mais perto que a distMin ou que
      o recuaAbaixo; 0 = parado, como na POC;
    - danoProj: o dano do projetil (no lugar do EQ.danoDist, 1 na POC) e velProj: a velocidade dele (x o OPCOES_PADRAO.pvel; 1 na POC).
      Tiram forca de quem atira quando ele mantem distancia (D-LP5-13, 4: "Aprovo as 4") */
export interface Tiro { distMin: number; esperaMax: number; recuaAbaixo: number; recuo: number; recuaNaPrep: number; danoProj: number; velProj: number }
export const TIRO_V21: Readonly<Tiro> = Object.freeze({ distMin: 0, esperaMax: 0, recuaAbaixo: 0.5, recuo: EQ.recuo, recuaNaPrep: 0, danoProj: EQ.danoDist, velProj: 1 });

/** a esquiva pela perspicacia e pela velocidade (LUTA_POC, LP5, D-LP5-14: o Matheus, "Vamos daí fazer com o Mira e o Caráter Atento
    juntos"). So vale quando a entrada da luta traz a `esquiva`; sem ela, a luta e a de sempre, byte a byte. Cada lutador traz nos Stats a
    perspicacia (perc: perceber o golpe e reagir antes; a bancada a tira da mira e do carater atento) e a agilidade (agil: o pulo da
    esquiva; do folego). 1 = o lutador neutro. Os numeros sao PROPOSTOS, SEM FONTE.
    - kChance: o peso da perc na chance de desviar (a chance da dificuldade x (1 + kChance x (perc - 1))), ate o chanceMax;
    - kReacao: o peso da perc no tempo de reacao (a reacao da dificuldade / (1 + kReacao x (perc - 1)));
    - kDash: o peso da agil na velocidade do pulo (ACAO.desvioCpu x (1 + kDash x (agil - 1)));
      os tres fatores sao lineares (o nucleo nao usa `**`) e ficam em pelo menos 0,1;
    - pertoChance: a chance base de ler o golpe de perto do outro (na preparacao, ao alcance) e pular para tras; 0 = so o tiro, como na POC;
    - pertoReacao: o tempo de reacao base (ms) contra o golpe de perto;
    - contraMs: depois de uma esquiva do golpe de perto, a recarga do ataque fica no maximo nisto (ms; o contra-ataque); 0 = sem */
export interface Esquiva { kChance: number; kReacao: number; kDash: number; chanceMax: number; pertoChance: number; pertoReacao: number; contraMs: number }

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

/** o golpe de apoio (LUTA_POC, LP6-1; docs/PLANO_LP6_SEGUNDO_GOLPE.md, secao 3; as decisoes 1 a 3 do Matheus, 2026-11-11: "pode seguir para
    o plano lp6"): um segundo golpe, do tipo que falta ao golpe principal, que sai pela distancia e tem recarga propria. So vale quando a
    entrada da luta traz o `apoio` (a chave; nenhuma versao de pet o liga ate a LP6-4); sem ele, a luta e a de sempre, byte a byte. Os
    numeros sao PROPOSTOS, SEM FONTE, e entram na calibracao da LP6-3.
    - dano: o dano do apoio, em fracao do dano do golpe principal (o mesmo tipo de dano e o mesmo `fr` do principal, vezes isto);
    - recarga: a recarga do apoio, em vezes o ciclo do ataque do lutador (Stats.cad), contada do comeco do apoio;
    - longeMs: quanto tempo (ms) o alvo de quem bate de perto fica alem do alcance de perto antes do tiro fraco sair.
    Quando sai: o de perto de quem atira, com o alvo abaixo da distMin do tiro (sem o `tiro`, da metade do alcance, o recuo da POC) e ao
    alcance de perto; o tiro fraco de quem bate de perto, com o alvo alem do alcance de perto por longeMs e ao alcance do tiro */
export interface Apoio {
  dano: number; recarga: number; longeMs: number;
  /** LP6-3 (D-LP6-3-7; "Apoio so no Ult/Mega (a)", Matheus, 2026-11-11): o apoio so existe quando o maior estagio dos dois lutadores e
      este ou maior (ORDEM_ESTAGIOS); sem o campo, em todos os estagios (a LP6-1) */
  desde?: (typeof ORDEM_ESTAGIOS)[number];
  /** LP6-3 (D-LP6-3-4 e D-LP6-3-7): o recuo depois do apoio de perto de quem atira, atras desta chave propria; sem ela, a regra da LP6-1 */
  recua?: boolean;
}
export const APOIO_LP6: Readonly<Apoio> = Object.freeze({ dano: 0.6, recarga: 2, longeMs: 1500 });
/** o recuo depois do apoio de perto de quem atira (LP6-3, D-LP6-3-4; "Regra e grade", Matheus, 2026-11-11): o atirador bate e recua, sem
    atacar, ate o alvo ficar na distMin do tiro, no maximo pela espera do tiro (o esperaMax). Sem o `tiro` na entrada, ate a metade do
    alcance, no maximo por este tempo (ms). PROPOSTO, SEM FONTE */
export const RECUO_APOIO_SEM_TIRO_MS = 1500;
/** o golpe de apoio na tabela das formas (formas.ts, gerada por tools/gerar_tabela_arena.py; um teste confere que o gerador usa os mesmos):
    o instante do golpe e o clipe a `ritmo` vezes os do golpe principal (o Attack_1 reaproveitado, mais rapido; secao 4 do plano) e o tiro
    fraco na velocidade `vel` (a 20 do "Guide", secao 3). PROPOSTO, SEM FONTE */
export const APOIO_TABELA = { ritmo: 0.6, vel: 20 } as const;

/** a arena do Ultimate e do Mega (LUTA_POC, LP6-1; docs/PLANO_LP6_SEGUNDO_GOLPE.md, secao 4a; a decisao 4 PROPOSTA, com a recomendacao
    aplicada): a elipse cresce pelo maior estagio dos dois lutadores, e tudo que e da cena cresce junto (as zonas, os obstaculos, a area
    segura, a linha da mare e os pontos de inicio); os corpos, o alcance e a velocidade nao mudam. So vale quando a entrada da luta traz a
    `arenaPorEstagio` (a chave); sem ela, a elipse de sempre, byte a byte. O fator de cada estagio (In-Training, Rookie e Champion: 1).
    PROPOSTO, SEM FONTE */
export interface ArenaPorEstagio { Ultimate: number; Mega: number }
export const ARENA_POR_ESTAGIO_LP6: Readonly<ArenaPorEstagio> = Object.freeze({ Ultimate: 1.15, Mega: 1.3 });
/** os numeros da LP6-3 (docs/PLANO_LP6_SEGUNDO_GOLPE.md, secao 8; o candidato lp6_3_u120 do PR #834): o apoio so na luta de Ultimate ou de
    Mega, dano 0,6, recarga 3 vezes, sem o recuo (a decisao 2 atualizada; PROPOSTO, SEM FONTE); e a elipse 1,2 no Ultimate e 1,4 no Mega (a
    decisao 4, DECIDIDA: "(a) 1,2 e 1,4 (Recommended)", Matheus, 2026-11-11). Sao os da v27 na LP6-4 */
export const APOIO_LP6_3: Readonly<Apoio> = Object.freeze({ dano: 0.6, recarga: 3, longeMs: 1500, desde: "Ultimate" });
export const ARENA_POR_ESTAGIO_LP6_3: Readonly<ArenaPorEstagio> = Object.freeze({ Ultimate: 1.2, Mega: 1.4 });
/** a ordem dos estagios da tabela das formas, do menor ao maior (o maior dos dois lutadores escolhe o fator) */
export const ORDEM_ESTAGIOS = ["In-Training", "Rookie", "Champion", "Ultimate", "Mega"] as const;
