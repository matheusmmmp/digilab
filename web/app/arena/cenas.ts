/* As 8 arenas (porte do arena.html): geometria e regra de cada uma, sem desenho (o desenho fica em src/telas/lutar/arena_tr/).
   Coordenadas no mundo logico 480 x 280. Todos os numeros PROPOSTOS; a fonte e o arena_equilibrio.md (rodada das arenas, 2026-10-29):
   Coliseu fecha a partir de 30 s ate 50% em 30 s, 5%/s fora; Praia mare de 18 s, agua a 70%, 72 px; Deserto tempestade a cada 20 s por
   6 s, projeteis a 60%, mira 3x pior, areia puxa 26 px/s e deixa a 70%; Castelo runa de 1,2 s, +30% por 8 s, recarga de 12 s, pilar com
   3 golpes; Caverna lava 6%/s, erupcao a cada 7 s com 1,2 s de aviso, 10%, 28 px; Ringue empurrao 2x e 7x, 15% e 600 ms fora, medo da
   borda a partir de 80%. */
import { ELIPSE } from "./constantes.ts";
import { ativo, emCampo, evento, ferir, fugirZona, mudar, noElipse, normArena, paraCentro, ref } from "./nucleo.ts";
import type { EstadoCena, IdCena, Luta, Lutador } from "./tipos.ts";

type Vetor = [number, number];
/** a definicao de uma arena: os dados e as regras que a simulacao consulta */
export interface DefCena {
  nome: string;
  desc: string;
  obst?: [number, number, number, string, number?][];   // x, y, raio, imagem, golpes para quebrar
  zonas?: [string, number, number, number, number][];   // tipo, x, y, rx, ry
  semCerca?: boolean;
  empurrao?: number; empurraoHab?: number;
  tick?(c: EstadoCena, L: Luta, dt: number): void;
  guia?(c: EstadoCena, L: Luta, u: Lutador): Vetor;
  mov?(c: EstadoCena, u: Lutador): number;
  projVel?(c: EstadoCena): number;
  erro?(c: EstadoCena): number;
}

export const CENAS: Record<IdCena, DefCena> = {
  campo: { nome: "Campo de treino", desc: "Sem regras: só os dois lutadores e o chão." },
  coliseu: {
    nome: "Coliseu",
    desc: "A arena fecha. A partir de 30 s a área segura encolhe até 50% em 30 s. Fora dela, cada segundo custa 5% da vida máxima. Acaba com quem só foge.",
    tick(c, L, dt) {
      const t = L.relogio / 1000; c.seguro = t < 30 ? 1 : 1 - 0.5 * Math.min(1, (t - 30) / 30);
      if (t >= 30 && !c.avisou) { c.avisou = true; evento(L, { tipo: "arena_fecha" }); }
      for (const u of emCampo(L)) if (normArena(u.x, u.y) > c.seguro) ferir(L, u, 0.05 * dt / 1000, "fora da área segura");
    },
    guia(c, _L, u) { const n = normArena(u.x, u.y); return n > c.seguro * 0.85 ? paraCentro(u, 2) : [0, 0]; },
  },
  floresta: {
    nome: "Floresta Green Shade",
    desc: "Árvores e moitas. As árvores bloqueiam corpos e projéteis: mire sem tronco no caminho. Dentro de uma moita você fica escondido e a CPU erra a mira quatro vezes mais.",
    obst: [[150, 140, 12, "arvore"], [335, 136, 12, "arvore"], [240, 212, 12, "arvore"], [92, 196, 11, "arvore"], [392, 200, 11, "arvore"]],
    zonas: [["moita", 228, 136, 30, 11], ["moita", 318, 214, 30, 11], ["moita", 128, 222, 24, 9], ["moita", 400, 160, 22, 9]],
    tick(c, L) { for (const u of emCampo(L)) u.escondido = c.zonas.some(z => z.tipo === "moita" && noElipse(u.x, u.y, z)); },
  },
  praia: {
    nome: "Praia Shellfish",
    desc: "Maré. A água sobe e desce pela frente da arena a cada 18 s. Na água o movimento cai para 70%. As rochas bloqueiam corpos e projéteis.",
    obst: [[175, 146, 11, "rocha1"], [318, 168, 10, "rocha2"]],
    tick(c, L) { const f = (Math.sin(L.relogio / 18000 * Math.PI * 2 - Math.PI / 2) + 1) / 2; c.linha = ELIPSE.cy + ELIPSE.ry + 4 - f * 72; },
    mov(c, u) { return u.y > c.linha ? 0.7 : 1; },
    guia(c, _L, u) { return u.y > c.linha - 8 ? [0, -1.2] : [0, 0]; },
  },
  deserto: {
    nome: "Deserto Endless",
    desc: "Areia movediça e tempestade. O centro puxa quem entra e deixa lento. A cada 20 s vem uma tempestade de 6 s: projéteis a 60% da velocidade e a CPU mira três vezes pior.",
    zonas: [["areia", 240, 176, 46, 18]],
    tick(c, L, dt) {
      const t = L.relogio / 1000, ciclo = (t - 12) % 20;
      const antes = c.tempestade; c.tempestade = t >= 12 && ciclo < 6;
      if (c.tempestade && !antes) evento(L, { tipo: "tempestade" });
      const z = c.zonas[0];
      for (const u of emCampo(L)) if (noElipse(u.x, u.y, z)) {
        const dx = z.x - u.x, dy = z.y - u.y, d = Math.hypot(dx, dy) || 1;
        u.x += dx / d * 26 * dt / 1000; u.y += dy / d * 26 * dt / 1000 * 0.7;
      }
    },
    mov(c, u) { return noElipse(u.x, u.y, c.zonas[0]) ? 0.7 : 1; },
    guia(c, _L, u) { return fugirZona(u, c.zonas[0], 1.4, 1.5); },
    projVel(c) { return c.tempestade ? 0.6 : 1; },
    erro(c) { return c.tempestade ? 3 : 1; },
  },
  castelo: {
    nome: "Castelo Midnight",
    desc: "Pilares e runa. Os quatro pilares bloqueiam projéteis e quebram com três golpes. Fique 1,2 s na runa do centro para causar 30% a mais de dano por 8 s; ela recarrega em 12 s.",
    obst: [[168, 146, 11, "pilar", 3], [312, 146, 11, "pilar", 3], [168, 206, 11, "pilar", 3], [312, 206, 11, "pilar", 3]],
    zonas: [["runa", 240, 176, 22, 9]],
    tick(c, L, dt) {
      c.runaCd = c.runaCd - dt;
      const z = c.zonas[0];
      for (const u of emCampo(L)) {
        if (c.runaCd <= 0 && noElipse(u.x, u.y, z)) {
          u.naRuna = u.naRuna + dt;
          if (u.naRuna >= 1200) {
            u.buffAte = L.relogio + 8000; c.runaCd = 12000; u.naRuna = 0;
            evento(L, { tipo: "runa", u: ref(u), x: u.x, y: u.y });
          }
        } else u.naRuna = 0;
      }
    },
    guia(c, _L, u) {
      if (c.runaCd > 0 || u.recarga < 300) return [0, 0];
      const z = c.zonas[0], dx = z.x - u.x, dy = z.y - u.y, d = Math.hypot(dx, dy) || 1;
      return d < 170 ? [dx / d * 1.1, dy / d * 1.1] : [0, 0];
    },
  },
  caverna: {
    nome: "Caverna Blackheart",
    desc: "Lava e erupções. Pisar nas fendas de lava custa 6% da vida máxima por segundo. A cada 7 s dois pontos brilham e explodem 1,2 s depois: 10% da vida máxima para quem estiver perto.",
    zonas: [["lava", 150, 160, 30, 8], ["lava", 332, 192, 32, 9], ["lava", 252, 132, 24, 7]],
    tick(c, L, dt) {
      for (const u of emCampo(L)) if (c.zonas.some(z => noElipse(u.x, u.y, z))) ferir(L, u, 0.06 * dt / 1000, "na lava");
      c.prox = (c.prox ?? 5000) - dt;
      if (c.prox <= 0) {
        c.prox = 7000;
        for (let i = 0; i < 2; i++) {
          // uma erupcao mira perto de um lutador, a outra cai em qualquer lugar (com um so em campo, o sorteio pode nao achar ninguem)
          const alvo = i === 0 ? emCampo(L)[Math.floor(L.r.cena() * 2)] ?? null : null;
          let x = alvo ? alvo.x + (L.r.cena() - 0.5) * 40 : ELIPSE.cx + (L.r.cena() - 0.5) * ELIPSE.rx * 1.4;
          let y = alvo ? alvo.y + (L.r.cena() - 0.5) * 16 : ELIPSE.cy + (L.r.cena() - 0.5) * ELIPSE.ry * 1.4;
          if (normArena(x, y) > 0.9) { x = ELIPSE.cx + (x - ELIPSE.cx) * 0.8; y = ELIPSE.cy + (y - ELIPSE.cy) * 0.8; }
          c.erupcoes.push({ x, y, t: 0, explodiu: false });
        }
      }
      for (const e of c.erupcoes) {
        e.t += dt;
        if (e.t >= 1200 && !e.explodiu) {
          e.explodiu = true;
          for (const u of emCampo(L)) if (Math.hypot(u.x - e.x, (u.y - e.y) / 0.6) < 28) ferir(L, u, 0.10, "na erupção", true);
        }
      }
      c.erupcoes = c.erupcoes.filter(e => e.t < 1800);
    },
    guia(c, _L, u) {
      const v: Vetor = [0, 0];
      for (const z of c.zonas) { const g = fugirZona(u, z, 1.6, 1.4); v[0] += g[0]; v[1] += g[1]; }
      for (const e of c.erupcoes) if (!e.explodiu) {
        const dx = u.x - e.x, dy = u.y - e.y, d = Math.hypot(dx, dy / 0.6) || 1;
        if (d < 46) { v[0] += dx / d * 2.4; v[1] += dy / d * 2.4; }
      }
      return v;
    },
  },
  ringue: {
    nome: "Ringue D-1 Grand Prix",
    desc: "Sem cerca. Os golpes empurram o dobro e a habilidade sete vezes mais. Quem sai do ringue perde 15% da vida máxima e volta ao centro atordoado.",
    semCerca: true, empurrao: 2, empurraoHab: 7,
    tick(_c, L) {
      for (const u of [ativo(L, "a"), ativo(L, "b")].filter(x => !x.morto && x.entrada <= 0)) {
        if (u.foraAte) { if (L.relogio >= u.foraAte) { u.foraAte = 0; u.x = ELIPSE.cx + (u.lado === "a" ? -40 : 40); u.y = ELIPSE.cy; mudar(u, "stun"); u.atordoado = 500; } continue; }
        if (normArena(u.x, u.y) > 1.02) {
          u.foraAte = L.relogio + 600; u.dash = 0;
          evento(L, { tipo: "queda_ringue", u: ref(u) }); ferir(L, u, 0.15, "fora do ringue", true);
        }
      }
    },
    guia(_c, _L, u) { const n = normArena(u.x, u.y); return n > 0.8 ? paraCentro(u, 1.6 * (n - 0.8) / 0.2 + 0.4) : [0, 0]; },
  },
};
export const IDS_CENA = Object.keys(CENAS) as IdCena[];

export function iniciarCena(id: IdCena): EstadoCena {
  const c = CENAS[id];
  return {
    id, obst: (c.obst || []).map(([x, y, r, img, hp]) => ({ x, y, r, img, hp, max: hp })),
    zonas: (c.zonas || []).map(([tipo, x, y, rx, ry]) => ({ tipo, x, y, rx, ry })), seguro: 1,
    avisou: false, linha: Infinity, tempestade: false, runaCd: 0, prox: undefined, erupcoes: [],
  };
}
