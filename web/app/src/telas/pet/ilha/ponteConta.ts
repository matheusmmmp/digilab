/* A conta da ponte da ilha com agua (docs/TAREFA_V3_ILHA_AGUA.md, IA3; ponte.ts a desenha), sem three e sem DOM: de cada celula de ponte
   da grade (Ilha.pontes, as do mapa do motor), as caixas do tabuado e do corrimao, em celulas do mundo (x leste, y para cima, z sul).
   - o sentido da celula: quem atravessa anda de terra a terra; se ha agua ao norte ou ao sul dela, anda-se em x, e as tabuas correm em z;
   - o tabuado: PONTE_ILHA.tabuado.porCelula tabuas por celula, com a fresta entre elas, um pouco acima do chao, sobrando para fora da
     celula nas beiras que dao para a agua;
   - o corrimao: so nas beiras que dao para a agua, um pau ao longo da beira e um poste em cada ponta dela.
   Todos os numeros sao do desenho (PONTE_ILHA): PROPOSTO, SEM FONTE. */
import { PONTE_ILHA } from "./constantes.ts";
import type { Ilha } from "./grade.ts";

/** uma beira de celula de ponte que da para a agua: a celula e o lado (dx, dz) em que a agua esta */
export interface Beira { x: number; z: number; dx: number; dz: number }
/** uma caixa alinhada aos eixos: o canto de baixo e o de cima, e a peca (para a cor) */
export interface Caixa { peca: "tabua" | "corrimao" | "poste"; min: [number, number, number]; max: [number, number, number]; tom: number }

const LADOS: readonly (readonly [number, number])[] = [[0, -1], [1, 0], [0, 1], [-1, 0]];

/** as beiras das celulas de ponte que dao para a agua (onde vai o corrimao) */
export function celulasDoCorrimao(ilha: Pick<Ilha, "pontes" | "cel">): Beira[] {
  const out: Beira[] = [];
  for (const [x, z] of ilha.pontes) for (const [dx, dz] of LADOS) if (ilha.cel(x + dx, z + dz)?.tipo === "agua") out.push({ x, z, dx, dz });
  return out;
}

/** as caixas da ponte inteira */
export function caixasDaPonte(ilha: Pick<Ilha, "pontes" | "cel">): Caixa[] {
  const T = PONTE_ILHA.tabuado, C = PONTE_ILHA.corrimao, out: Caixa[] = [];
  const agua = (x: number, z: number) => ilha.cel(x, z)?.tipo === "agua";
  for (const [x, z] of ilha.pontes) {
    /* agua ao norte ou ao sul: anda-se em x, as tabuas correm em z (e sobram para o norte e para o sul); senao, o contrario */
    const emX = agua(x, z - 1) || agua(x, z + 1) || !(agua(x - 1, z) || agua(x + 1, z));
    const passo = 1 / T.porCelula, y0 = T.altura, y1 = T.altura + T.espessura;
    for (let k = 0; k < T.porCelula; k++) {
      /* o tom e o da tabua inteira: as celulas vizinhas ao longo dela dao o mesmo */
      const a = k * passo + T.fresta / 2, b = (k + 1) * passo - T.fresta / 2, tom = ((emX ? x * 7 : z * 13) + k * 5) % PONTE_ILHA.cor.tabua.length;
      if (emX) out.push({ peca: "tabua", tom, min: [x + a, y0, z - (agua(x, z - 1) ? T.sobra : 0)], max: [x + b, y1, z + 1 + (agua(x, z + 1) ? T.sobra : 0)] });
      else out.push({ peca: "tabua", tom, min: [x - (agua(x - 1, z) ? T.sobra : 0), y0, z + a], max: [x + 1 + (agua(x + 1, z) ? T.sobra : 0), y1, z + b] });
    }
  }
  const beiras = celulasDoCorrimao(ilha), tem = (x: number, z: number, dx: number, dz: number) => beiras.some(o => o.x === x && o.z === z && o.dx === dx && o.dz === dz);
  for (const b of beiras) {
    /* os postes da beira: um em cada ponta; onde a beira continua na celula vizinha, um so, na divisa (quem o poe e a celula de antes) */
    const ao = b.dx !== 0 ? b.z : b.x, antes = b.dx !== 0 ? tem(b.x, b.z - 1, b.dx, b.dz) : tem(b.x - 1, b.z, b.dx, b.dz);
    const depois = b.dx !== 0 ? tem(b.x, b.z + 1, b.dx, b.dz) : tem(b.x + 1, b.z, b.dx, b.dz);
    const pontas = [...(antes ? [] : [ao + C.poste / 2]), depois ? ao + 1 : ao + 1 - C.poste / 2];
    /* a linha da beira, recuada para dentro da celula */
    const fixo = b.dx !== 0 ? b.x + (b.dx > 0 ? 1 - C.recuo : C.recuo) : b.z + (b.dz > 0 ? 1 - C.recuo : C.recuo), m = C.pau / 2, p = C.poste / 2;
    const yT = PONTE_ILHA.tabuado.altura + PONTE_ILHA.tabuado.espessura;
    if (b.dx !== 0) {
      out.push({ peca: "corrimao", tom: 0, min: [fixo - m, yT + C.altura - C.pau, b.z], max: [fixo + m, yT + C.altura, b.z + 1] });
      for (const e of pontas) out.push({ peca: "poste", tom: 0, min: [fixo - p, yT, e - p], max: [fixo + p, yT + C.altura, e + p] });
    } else {
      out.push({ peca: "corrimao", tom: 0, min: [b.x, yT + C.altura - C.pau, fixo - m], max: [b.x + 1, yT + C.altura, fixo + m] });
      for (const e of pontas) out.push({ peca: "poste", tom: 0, min: [e - p, yT, fixo - p], max: [e + p, yT + C.altura, fixo + p] });
    }
  }
  return out;
}
