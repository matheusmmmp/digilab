/* As posturas como efeito na luta em tempo real (LUTA_EFEITOS, etapa E4; docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 3.5). So apresentacao e
   puro (sem DOM): tudo sai do estado da luta (a acao, o preparo e a pele de cada lado), dos eventos `dano` e do `passo`, nunca do relogio do
   navegador; a mesma luta desenha as mesmas posturas. Nada aqui toca o motor, o log, o replay nem o ResultadoLutaTR, e nada empurra
   (D-EMP-9/11: o empurrao e so do motor). O desenho em canvas fica em desenhoTR.ts.
   - O escudo no `defender`: um arco de pixels na frente do corpo (do lado do rival), que acende quando um golpe bate nele.
   - A imagem fantasma na `esquiva`: copias apagadas do sprite, para tras, que se abrem no comeco da esquiva.
   - A aura no `carregar`: faiscas na cor do elemento que sobem dos dois lados do corpo. A elipse tracejada no chao continua a da E3
     (chaoTR.ts, telegrafiaDoPasso): a aura nao desenha nada no chao, para nao repetir o anel.
   - O clarao no `contra_golpe`: em guarda, um brilho pequeno na frente; no golpe que ele devolve, uma cruz de luz na frente do corpo.
   - O brilho na `pele_dura`: enquanto a pele dura vale (S.passo < peleAte, que passa do fim da acao), o sprite fica com a cor do metal e
     uma faixa de luz que corre por ele.
   - A etiqueta de texto de antes vira um icone pequeno em grade de pixel (7 x 7) sobre a cabeca; o nome vai no title e no leitor de tela
     (PalcoTR.tsx). */
import type { EventoTR, LadoTR, LutaTR } from "../../../../motor/index.ts";
import { ELEMENTO, type ElementoTR } from "./elementosTR.ts";
import type { PixelTR } from "./projeteisTR.ts";

/** As posturas da E4. PROPOSTO, SEM FONTE: ajustar nas capturas.
    - escudoAlto: a altura do arco do escudo (fracao da altura do sprite); escudoFrente: onde ele fica (fracao da meia-largura, na frente);
      acende: os passos em que o escudo (e o contra-golpe) ficam acesos depois de um golpe.
    - fantasmas: as copias da esquiva (opacidade de cada); fantasmaPx: o passo entre elas em pixels do sprite; abre: os passos em que elas
      se abrem do corpo ate o passo cheio; fantasmaTinta: quanto da cor do elemento cobre a copia.
    - aura: as faiscas de cada lado do corpo; auraCiclo: os passos em que uma faisca sobe do pe ao topo; auraMeia: a distancia do centro
      (fracao da largura do sprite).
    - claraoContra: os passos da cruz de luz do contra-golpe; brilhoGuarda: o ciclo (passos) do brilho pequeno em guarda.
    - peleAlfa: a opacidade da cor do metal sobre o sprite; peleFaixa: a largura da faixa de luz (pixels do sprite); peleCiclo: os passos
      em que a faixa atravessa o sprite.
    - icone: o lado da grade do icone (pixels de icone); iconePx: quantos pixels do sprite tem cada pixel do icone; iconeAcima: o vao entre
      o icone e o topo do sprite (px de CSS); pixelMinCss: o pixel do icone e dos efeitos tem pelo menos isto em px de CSS (arredondado
      para cima em pixels do sprite: a grade continua a do sprite). */
export const POSTURA = {
  escudoAlto: .62, escudoFrente: .62, acende: 8,
  fantasmas: [.55, .3], fantasmaPx: 9, abre: 6, fantasmaTinta: .55,
  aura: 4, auraCiclo: 20, auraMeia: .3,
  claraoContra: 9, brilhoGuarda: 8,
  peleAlfa: .45, peleFaixa: 5, peleCiclo: 36,
  icone: 7, iconePx: 1, iconeAcima: 8, pixelMinCss: 2,
} as const;

/** a postura que o icone mostra: a acao em curso (as posturas) ou o pesado preparado, a espera do golpe */
export type PosturaTR = "defender" | "esquivar" | "carregar" | "contra_golpe" | "preparar_pesado" | "pesado_pronto" | "marcar" | "pele_dura";
export const POSTURAS_TR: readonly PosturaTR[] = ["defender", "esquivar", "carregar", "contra_golpe", "preparar_pesado", "pesado_pronto", "marcar", "pele_dura"];
/** o nome na tela (o title e o leitor de tela): o de NOME_V2, e o pesado pronto */
export const NOME_POSTURA: Record<PosturaTR, string> = {
  defender: "defender", esquivar: "esquivar", carregar: "carregar", contra_golpe: "contra-golpe", preparar_pesado: "preparar pesado",
  pesado_pronto: "pesado pronto", marcar: "marcar", pele_dura: "pele dura",
};
const ACOES_POSTURA: readonly string[] = ["defender", "esquivar", "carregar", "contra_golpe", "preparar_pesado", "marcar", "pele_dura"];

/** a postura do icone neste passo (a mesma regra da etiqueta de antes: o preparo pronto, senao a acao de postura); null sem postura ou no nocaute */
export function posturaDoLado(l: LadoTR): PosturaTR | null {
  if (l.hp <= 0) return null;
  if (l.prep) return "pesado_pronto";
  const n = l.acao?.nome;
  return n && ACOES_POSTURA.includes(n) ? n as PosturaTR : null;
}

/** um golpe que bateu numa postura: o escudo do defender ou o contra-golpe que devolveu (o lado e o de quem esta na postura) */
export interface BatidaTR { tipo: "escudo" | "contra"; lado: number; t0: number }

/** as batidas de um passo, dos eventos `dano`: o dano em quem defende (ou contra-golpeia) acende o escudo; o dano em quem atacou, enquanto o
    outro contra-golpeia, e o golpe devolvido. Chamado a cada passo pelo aplicarEventosTR */
export function seguirPosturasTR(v: { batidas: BatidaTR[] }, sim: LutaTR, ev: readonly EventoTR[]): void {
  const S = sim.S;
  for (const e of ev) {
    if (e.tipo !== "dano") continue;
    const eu = S.L[e.lado].acao?.nome, outro = S.L[1 - e.lado].acao?.nome;
    if (eu === "defender" || eu === "contra_golpe") v.batidas.push({ tipo: "escudo", lado: e.lado, t0: e.t });
    if (outro === "contra_golpe" && !v.batidas.some(b => b.tipo === "contra" && b.lado === 1 - e.lado && b.t0 === e.t)) v.batidas.push({ tipo: "contra", lado: 1 - e.lado, t0: e.t });
  }
  v.batidas = v.batidas.filter(b => S.passo - b.t0 < Math.max(POSTURA.acende, POSTURA.claraoContra));
}
const acesa = (bs: readonly BatidaTR[], tipo: BatidaTR["tipo"], lado: number, passo: number, dur: number): number => {
  let f = 0;
  for (const b of bs) if (b.tipo === tipo && b.lado === lado && passo >= b.t0 && passo - b.t0 < dur) f = Math.max(f, 1 - (passo - b.t0) / dur);
  return f;
};

/** os efeitos de postura de um lado neste passo (o que o desenho pinta), so do estado e das batidas */
export interface EfeitoPosturaTR {
  escudo: { aceso: number } | null;
  /** a esquiva: as copias (deslocamento para tras em pixels do sprite e a opacidade) */
  fantasmas: { dx: number; alfa: number }[];
  aura: boolean; contra: { guarda: boolean; clarao: number } | null;
  /** a pele dura: onde a faixa de luz esta (0 a 1 da largura), ou null com o movimento reduzido (so a cor do metal) */
  pele: { faixa: number | null } | null;
}
export function efeitoDaPostura(l: LadoTR, lado: number, passo: number, batidas: readonly BatidaTR[], reduzido: boolean): EfeitoPosturaTR {
  const sem: EfeitoPosturaTR = { escudo: null, fantasmas: [], aura: false, contra: null, pele: null };
  if (l.hp <= 0) return sem;
  const a = l.acao, n = a?.nome, idade = a ? passo - a.inicio : 0;
  if (n === "defender") sem.escudo = { aceso: reduzido ? 0 : acesa(batidas, "escudo", lado, passo, POSTURA.acende) };
  if (n === "esquivar") {
    /* abrem do corpo ate o passo cheio; com o movimento reduzido, ja abertas e paradas */
    const f = reduzido ? 1 : Math.min(1, (idade + 1) / POSTURA.abre);
    sem.fantasmas = POSTURA.fantasmas.map((alfa, k) => ({ dx: Math.max(1, Math.round((k + 1) * POSTURA.fantasmaPx * f)), alfa }));
  }
  if (n === "carregar") sem.aura = true;
  /* o clarao do golpe devolvido sai mesmo que o contra-golpe tenha acabado no mesmo passo */
  const cl = reduzido ? 0 : acesa(batidas, "contra", lado, passo, POSTURA.claraoContra);
  if (n === "contra_golpe" || cl > 0) sem.contra = { guarda: n === "contra_golpe", clarao: cl };
  if (passo < l.peleAte) sem.pele = { faixa: reduzido ? null : (passo % POSTURA.peleCiclo) / POSTURA.peleCiclo };
  return sem;
}

/** os pixels do escudo, virado para a direita (o desenho espelha), relativos ao centro da frente, para uma altura de `alto` pixels do sprite:
    um arco (parentese) com a borda saturada, o meio claro e o brilho somado por tras; aceso (0 a 1), o meio fica branco e o brilho dobra */
export function pixelsDoEscudo(alto: number, aceso: number): PixelTR[] {
  const out: PixelTR[] = [], r = Math.max(3, Math.round(alto / 2)), curva = Math.max(1, Math.round(r / 3));
  for (let dy = -r; dy <= r; dy++) {
    /* a curva: o arco se adianta no meio e recua nas pontas */
    const dx = Math.round(curva * (1 - (dy * dy) / (r * r)));
    out.push({ dx: dx - 1, dy, cor: "#8fdcff", alfa: .35 + .4 * aceso, tam: 4, luz: true });
    out.push({ dx: dx + 2, dy, cor: "#2c73e0", alfa: 1, tam: 1, luz: false });
    out.push({ dx, dy, cor: aceso > .5 ? "#ffffff" : "#bfeaff", alfa: 1, tam: 2, luz: false });
  }
  return out;
}

/** as faiscas da aura do carregar, relativas aos pes no centro, para uma meia-largura `meia` e uma altura `alto` (pixels do sprite): de cada
    lado, POSTURA.aura faiscas que sobem do pe ao topo e se apagam, na cor do elemento, com luz. Sem acaso: o mesmo passo da a mesma aura.
    Com o movimento reduzido, as faiscas param (o mesmo desenho em todo passo) */
export function pixelsDaAura(el: ElementoTR, meia: number, alto: number, passo: number, reduzido: boolean): PixelTR[] {
  const c = ELEMENTO[el], out: PixelTR[] = [], p = reduzido ? 0 : passo;
  for (const s of [1, -1]) for (let k = 0; k < POSTURA.aura; k++) {
    const fase = (p + k * Math.round(POSTURA.auraCiclo / POSTURA.aura) + (s > 0 ? 0 : Math.round(POSTURA.auraCiclo / (2 * POSTURA.aura)))) % POSTURA.auraCiclo;
    const f = fase / POSTURA.auraCiclo, dy = -7 - Math.round(f * alto), dx = s * (meia + (k % 2) - Math.round(f * 2));
    out.push({ dx: dx - 2, dy: dy - 2, cor: c.halo, alfa: .45 * (1 - f), tam: 5, luz: true });
    /* a faisca: 2 x 2 na cor do meio (a borda, saturada, no fim), com o risco de 2 pixels abaixo (o rastro da subida) */
    /* a faisca 2 x 2 com o contorno na cor saturada (a borda) e o miolo claro; o risco de 2 pixels abaixo e o rastro da subida */
    const alfa = 1 - f * .5;
    out.push({ dx: dx - 1, dy: dy - 1, cor: c.borda, alfa, tam: 4, luz: false });
    out.push({ dx, dy, cor: f < .55 ? c.nucleo : c.meio, alfa: 1, tam: 2, luz: false });
    out.push({ dx, dy: dy + 3, cor: c.borda, alfa: alfa * .8, tam: 2, luz: false });
    out.push({ dx, dy: dy + 5, cor: c.borda, alfa: alfa * .45, tam: 1, luz: false });
  }
  return out;
}

/** os pixels do contra-golpe, relativos a frente do corpo (virado para a direita): em guarda, um brilho pequeno em cruz (pisca no ciclo
    POSTURA.brilhoGuarda, e fica parado com o movimento reduzido); no golpe devolvido (clarao de 1 a 0), uma cruz de luz grande que encolhe */
export function pixelsDoContra(guarda: boolean, clarao: number, passo: number, reduzido: boolean): PixelTR[] {
  const out: PixelTR[] = [];
  if (guarda) {
    const r = reduzido || Math.floor(passo / (POSTURA.brilhoGuarda / 2)) % 2 === 0 ? 2 : 1;
    out.push({ dx: 0, dy: 0, cor: "#ffffff", alfa: 1, tam: 1, luz: false });
    for (let k = 1; k <= r; k++) for (const [a, b] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) out.push({ dx: a * k, dy: b * k, cor: k === r ? "#ff8a8a" : "#ffe0e0", alfa: 1, tam: 1, luz: false });
  }
  if (clarao > 0) {
    const r = Math.round(3 + 6 * clarao);
    /* a cruz de 2 pixels de grossura: o miolo amarelo e as pontas vermelhas, sobre um contorno escuro (o alvo esta branco do clarao da E1
       no mesmo passo); primeiro o contorno inteiro, depois a cor */
    for (let dy = -4; dy <= 4; dy++) for (let dx = -4; dx <= 4; dx++) if (dx * dx + dy * dy <= 16) out.push({ dx, dy, cor: "#ff6a3a", alfa: .5 * clarao, tam: 1, luz: true });
    for (let k = -r; k <= r; k++) for (const [x, y] of [[k, 0], [0, k]]) out.push({ dx: x - 1, dy: y - 1, cor: "#3a0a0a", alfa: .85, tam: 4, luz: false });
    for (let k = -r; k <= r; k++) {
      const cor = Math.abs(k) > r - 3 ? "#e0242a" : Math.abs(k) <= 1 ? "#ffffff" : "#ffd23f";
      for (const [x, y] of [[k, 0], [0, k]]) out.push({ dx: x, dy: y, cor, alfa: 1, tam: 2, luz: false });
    }
  }
  return out;
}

/** a cor do metal da pele dura e a da faixa de luz */
export const COR_PELE = { metal: "#c9d6e3", faixa: "#ffffff" } as const;

/** os icones 7 x 7 (1: a cor da postura; 2: o detalhe claro), virados para a direita (o lado de la espelha a esquiva) */
const ICONES: Record<PosturaTR, readonly string[]> = {
  defender: ["1111111", "1222221", "1222221", "1222221", ".12221.", "..121..", "...1..."],
  esquivar: [".......", "1..1...", ".1..1..", "..2..2.", ".1..1..", "1..1...", "......."],
  carregar: ["....11.", "...11..", "..12...", ".11111.", "...21..", "..11...", ".11...."],
  contra_golpe: ["1.....1", ".1...1.", "..1.1..", "...2...", "..1.1..", "22...22", "2.....2"],
  preparar_pesado: ["..111..", "..111..", "..111..", "..111..", "...1...", ".......", "..111.."],
  pesado_pronto: [".11.11.", ".11.11.", ".11.11.", ".11.11.", ".11.11.", ".......", ".11.11."],
  marcar: ["...1...", ".11111.", ".1...1.", "111.111", ".1...1.", ".11111.", "...1..."],
  pele_dura: ["...1...", "..121..", ".12221.", "1222221", ".12221.", "..121..", "...1..."],
};
/** a cor de cada icone (o carregar e o preparo do pesado ganham a do elemento). PROPOSTO, SEM FONTE */
const COR_ICONE: Record<PosturaTR, string | null> = {
  defender: "#5cc4f2", esquivar: "#bfeaff", carregar: null, contra_golpe: "#ff5d5d", preparar_pesado: null, pesado_pronto: "#ffd23f",
  marcar: "#ff8a2b", pele_dura: "#c9d6e3",
};
/** os pixels do icone da postura, na grade do icone (0..icone-1, com a placa escura de 1 pixel em volta, -1..icone), para quem esta do
    lado `lado` (o 1 espelha a esquiva, que aponta para tras). Sem acaso e sem passo: o icone nao pisca */
export function pixelsDoIcone(p: PosturaTR, el: ElementoTR, lado: number): PixelTR[] {
  const g = ICONES[p], n = POSTURA.icone, cor = COR_ICONE[p] ?? ELEMENTO[el].meio, out: PixelTR[] = [];
  for (let y = -1; y <= n; y++) for (let x = -1; x <= n; x++) {
    const borda = x === -1 || y === -1 || x === n || y === n;
    out.push({ dx: x, dy: y, cor: borda ? cor : "#10151f", alfa: borda ? .9 : .82, tam: 1, luz: false });
  }
  g.forEach((lin, y) => { for (let x = 0; x < n; x++) {
    const ch = lin[p === "esquivar" && lado === 0 ? n - 1 - x : x];
    if (ch === "1") out.push({ dx: x, dy: y, cor, alfa: 1, tam: 1, luz: false });
    else if (ch === "2") out.push({ dx: x, dy: y, cor: "#ffffff", alfa: 1, tam: 1, luz: false });
  } });
  return out;
}
