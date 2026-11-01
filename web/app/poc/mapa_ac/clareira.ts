/* A clareira da Floresta Nativa (mapa_ac.html?mapa=clareira): outro mapa na mesma grade do mapa_ac, só dados, sem three e sem DOM.
   O desenho segue o mapeamento 2.5D (docs/MAPEAMENTO_2_5D.md, na pasta acima da worktree): uma clareira redonda no meio de uma floresta
   fechada, o platô ao norte com a cachoeira caindo numa lagoa dentro da clareira, o riacho que sai dela para o mar e a trilha de terra
   que desce da rampa do platô até a praia. No centro, a laje de pedra onde fica o ovo (ovo.ts). Reaproveita a vista, o andar e a
   colisão do Mapa; só troca as células, os objetos e o ponto de início. Todos os números são do desenho: PROPOSTO, SEM FONTE. */
import { ALTURA_NIVEL, FUNDO_AGUA, LARG, Mapa, NIVEL_AGUA, PROF, type Objeto, type Tipo, rng } from "./mapa.ts";

export const CENTRO: readonly [number, number] = [28, 25];
const RAIO_CLAREIRA = 7.2;
const RIO_ALTO: readonly (readonly [number, number])[] = [[37, 0], [36.5, 5], [35, 10], [34.2, 15], [33.6, 19.5]];
const RIO_BAIXO: readonly (readonly [number, number])[] = [[34.5, 21], [37, 26], [38.5, 32], [37.5, 38], [37, 46]];
const LAGOA = { x: 33.2, z: 20.6, rx: 2.7, rz: 1.9 };
const TRILHA: readonly (readonly [number, number])[] = [[20.5, 16], [21.5, 19], [23.5, 21.5]];
const TRILHA_SUL: readonly (readonly [number, number])[] = [[27.5, 31.5], [27, 35], [25.5, 38.5], [25, 42]];
const RAMPA = { x: 20, largura: 2 };

function ruido1(semente: number, n: number): (t: number) => number {
  const r = rng(semente), v = Array.from({ length: n + 2 }, () => r());
  return (t: number) => {
    const i = Math.floor(t), f = t - i, s = f * f * (3 - 2 * f);
    const a = v[((i % n) + n) % n], b = v[(((i + 1) % n) + n) % n];
    return a + (b - a) * s;
  };
}
const dist2Seg = (px: number, pz: number, ax: number, az: number, bx: number, bz: number) => {
  const dx = bx - ax, dz = bz - az, l = dx * dx + dz * dz;
  const t = l === 0 ? 0 : Math.max(0, Math.min(1, ((px - ax) * dx + (pz - az) * dz) / l));
  const qx = ax + t * dx - px, qz = az + t * dz - pz;
  return qx * qx + qz * qz;
};
const perto = (x: number, z: number, pts: readonly (readonly [number, number])[], r: number) =>
  pts.slice(1).some((p, i) => dist2Seg(x, z, pts[i][0], pts[i][1], p[0], p[1]) <= r * r);

export class MapaClareira extends Mapa {
  override readonly inicio: [number, number] = [CENTRO[0], CENTRO[1] + 3.6];

  constructor() {
    super();
    this.celulas.length = 0;
    this.objetos.length = 0;
    const bordaPlato = ruido1(41, 13), bordaMorro = ruido1(43, 7), bordaPraia = ruido1(47, 11);
    for (let z = 0; z < PROF; z++) for (let x = 0; x < LARG; x++) {
      const cx = x + 0.5, cz = z + 0.5;
      const limitePlato = 11 + bordaPlato(cx / 4.5) * 3;
      let nivel = cz < limitePlato ? 1 : 0;
      if (cz < 4.5 + bordaMorro(cx / 3.5) * 2.5 && (cx < 17 || cx > 45)) nivel = 2;
      const limitePraia = 40 + bordaPraia(cx / 5) * 1.6;
      let tipo: Tipo = "grama";
      if (cz > limitePraia) tipo = "areia";
      if (cz > limitePraia + 2.6) { tipo = "agua"; nivel = -1; }
      const lagoa = ((cx - LAGOA.x) / LAGOA.rx) ** 2 + ((cz - LAGOA.z) / LAGOA.rz) ** 2 <= 1;
      if (perto(cx, cz, RIO_ALTO, 1.1) || perto(cx, cz, RIO_BAIXO, 1.0) || (nivel === 0 && lagoa)) tipo = "agua";
      else if (tipo === "grama" && (perto(cx, cz, TRILHA, 0.8) || perto(cx, cz, TRILHA_SUL, 0.8))) tipo = "caminho";
      const h = nivel < 0 ? FUNDO_AGUA - 0.5 : tipo === "agua" ? Math.max(nivel, 0) * ALTURA_NIVEL + FUNDO_AGUA : nivel * ALTURA_NIVEL;
      this.celulas.push({ tipo, nivel, cantos: [h, h, h, h] });
    }
    this.cavarRampa();
    this.porObjetosClareira();
  }

  /* a rampa do platô, a oeste da clareira: as duas células ao sul da borda viram ladeira (o mesmo corte do Mapa) */
  private cavarRampa(): void {
    let borda = -1;
    for (let z = 0; z < PROF - 1; z++) if (this.cel(RAMPA.x, z)!.nivel === 1 && this.cel(RAMPA.x, z + 1)!.nivel === 0) { borda = z; break; }
    if (borda < 0) throw new Error(`rampa em x=${RAMPA.x} sem borda de platô`);
    for (let dx = 0; dx < RAMPA.largura; dx++) for (let k = 0; k < 2; k++) {
      const c = this.cel(RAMPA.x + dx, borda + 1 + k)!;
      const alto = ALTURA_NIVEL * (1 - k / 2), baixo = ALTURA_NIVEL * (1 - (k + 1) / 2);
      c.tipo = "caminho"; c.nivel = 0;
      c.cantos = [alto, alto, baixo, baixo];
    }
    /* a trilha continua no platô, para o norte da rampa */
    for (let z = borda - 3; z <= borda; z++) for (let dx = 0; dx < RAMPA.largura; dx++) {
      const c = this.cel(RAMPA.x + dx, z);
      if (c && c.tipo === "grama") c.tipo = "caminho";
    }
  }

  private porObjetosClareira(): void {
    const r = rng(1999);
    const dCentro = (x: number, z: number) => Math.hypot(x - CENTRO[0], z - CENTRO[1]);
    const plano = (x: number, z: number, folga: number) => {
      const base = this.cel(Math.floor(x), Math.floor(z));
      if (!base) return false;
      for (let dz = -folga; dz <= folga; dz++) for (let dx = -folga; dx <= folga; dx++) {
        const c = this.cel(Math.floor(x) + dx, Math.floor(z) + dz);
        if (!c || c.tipo !== "grama" || c.cantos.some(h => h !== c.cantos[0]) || c.nivel !== base.nivel) return false;
      }
      return true;
    };
    const longe = (x: number, z: number, d: number) => !this.objetos.some(o => o.raio > 0 && (o.x - x) ** 2 + (o.z - z) ** 2 < d * d);
    const empurrar = (o: Objeto) => this.objetos.push(o);
    /** sorteia `n` objetos onde `onde` aceita; `dist` é a folga até os que bloqueiam */
    const por = (modelo: string, n: number, onde: (x: number, z: number) => boolean, folga: number, dist: number, esc: [number, number], raio: number) => {
      for (let i = 0, t = 0; i < n && t < n * 60; t++) {
        const x = 1 + r() * (LARG - 2), z = 1 + r() * (PROF - 2);
        if (!onde(x, z) || !plano(x, z, folga) || !longe(x, z, dist)) continue;
        empurrar({ modelo, x, z, giro: r() * Math.PI * 2, escala: esc[0] + r() * (esc[1] - esc[0]), raio });
        i++;
      }
    };
    /* ao sul da clareira (entre ela e a câmera) as árvores altas ficam de fora numa faixa, para não tampar a vista; só sub-bosque */
    const frente = (x: number, z: number) => z > CENTRO[1] + 2 && dCentro(x, z) < RAIO_CLAREIRA + 6;
    const anel = (x: number, z: number) => { const d = dCentro(x, z); return d > RAIO_CLAREIRA && d < RAIO_CLAREIRA + 3 && !frente(x, z); };
    const mata = (x: number, z: number) => dCentro(x, z) > RAIO_CLAREIRA + 1.5 && !frente(x, z);
    const dentro = (x: number, z: number) => dCentro(x, z) < RAIO_CLAREIRA - 0.6;
    const longeDoOvo = (x: number, z: number) => dCentro(x, z) > 2.2;

    /* o centro: a laje com o ovo (o ovo é desenhado à parte) e um anel de pedrinhas */
    empurrar({ modelo: "laje", x: CENTRO[0], z: CENTRO[1], giro: 0.3, escala: 1, raio: 0.55 });     // o raio é o do ovo em cima dela
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2 + r() * 0.2;
      empurrar({ modelo: "pedrinha", x: CENTRO[0] + Math.cos(a) * 1.75, z: CENTRO[1] + Math.sin(a) * 1.75, giro: r() * 6.3, escala: 0.8 + r() * 0.5, raio: 0 });
    }
    /* a moldura da clareira: copas redondas grandes no anel, depois a mata fechada */
    por("arvore_redonda", 26, anel, 0, 2.3, [1.1, 1.35], 0.45);
    por("arvore_torta", 10, anel, 0, 2.6, [1.0, 1.2], 0.45);
    por("pinheiro", 95, mata, 0, 2.1, [0.9, 1.3], 0.4);
    por("arvore_redonda", 70, mata, 0, 2.2, [0.9, 1.2], 0.45);
    por("arvore_torta", 22, mata, 0, 2.4, [0.9, 1.15], 0.45);
    por("arvore_morta", 6, mata, 0, 2.4, [0.9, 1.1], 0.35);
    por("pedra_grande", 9, mata, 0, 1.8, [0.8, 1.3], 0.5);
    /* dentro da clareira: os tocos e o tronco para sentar, as pedras soltas */
    por("toco", 4, (x, z) => dentro(x, z) && longeDoOvo(x, z) && dCentro(x, z) > 4, 0, 2.5, [1.0, 1.25], 0.3);
    empurrar({ modelo: "tronco", x: CENTRO[0] - 3.6, z: CENTRO[1] + 2.4, giro: 0.5, escala: 1.1, raio: 0.45 });
    por("pedra", 4, (x, z) => dentro(x, z) && dCentro(x, z) > 4.5, 0, 2, [0.6, 0.9], 0.35);
    /* o sub-bosque: samambaias e arbustos no anel e na mata; cogumelos perto dos troncos e no chão da mata */
    por("samambaia", 160, (x, z) => dCentro(x, z) > RAIO_CLAREIRA - 1, 0, 0, [0.8, 1.3], 0);
    por("arbusto", 40, (x, z) => dCentro(x, z) > RAIO_CLAREIRA - 0.5, 0, 1.4, [0.9, 1.2], 0.4);
    por("cogumelo", 45, (x, z) => dCentro(x, z) > RAIO_CLAREIRA - 2, 0, 0, [0.8, 1.4], 0);
    for (const o of this.objetos.filter(o => o.modelo === "toco" || o.modelo === "arvore_morta")) {
      empurrar({ modelo: "orelha_pau", x: o.x + 0.25, z: o.z + 0.3, giro: r() * 6.3, escala: 1, raio: 0 });
      empurrar({ modelo: "cogumelo", x: o.x - 0.35, z: o.z + 0.35, giro: r() * 6.3, escala: 0.9, raio: 0 });
    }
    /* o chão da clareira: flores, trevos e grama; na mata, só grama rala */
    por("flor", 60, (x, z) => dentro(x, z) && longeDoOvo(x, z), 0, 0, [0.8, 1.2], 0);
    por("trevo", 35, (x, z) => dentro(x, z) && longeDoOvo(x, z), 0, 0, [0.8, 1.2], 0);
    por("grama", 35, dentro, 0, 0, [0.7, 1.3], 0);
    por("grama", 160, mata, 0, 0, [0.7, 1.2], 0);
    /* os lírios na lagoa, na superfície da água */
    for (let i = 0; i < 7; i++) {
      const a = r() * Math.PI * 2, k = Math.sqrt(r()) * 0.75;
      empurrar({ modelo: "lirio", x: LAGOA.x + Math.cos(a) * LAGOA.rx * k, z: LAGOA.z + Math.sin(a) * LAGOA.rz * k, giro: r() * 6.3,
        escala: 0.7 + r() * 0.5, raio: 0, y: NIVEL_AGUA + 0.03 });
    }
  }
}
