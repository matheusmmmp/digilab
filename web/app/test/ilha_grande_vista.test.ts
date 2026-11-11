/* A vista da ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12, IG3): a grade (grade.ts) do layout `grande` do motor, sem three e sem DOM.
     - a ilha inteira fica dentro do mapa do motor, com o mar em volta; a terra da grade e a terra do motor, celula a celula;
     - cada arvore fechada do mapa tem uma arvore no centro da celula dela, e nada mais alto entra na area;
     - cada marco fica em cima do bloco de celulas fechadas dele, e nenhuma decoracao cai numa celula fechada;
     - os lugares, os postes, a praca e os caminhos ficam em celulas em que o pet pisa, e todo lugar se alcanca a pe a partir do ninho;
     - a luz cabe no maximo de focos, e as ilhas de antes nao mudam (os testes delas conferem). */
import { describe, expect, test } from "vitest";
import { AGUA_ILHA_GRANDE, ARVORE_FECHADA, CMU_GRANDE, CMU_MVP_AGUA, MARCO_FECHADO, PONTE, celulasSecas } from "../motor/index.ts";
import { ILHA_GRANDE, LUZ_HIERARQUIA, PLANTA_ILHA_AGUA, PLANTA_ILHA_GRANDE } from "../src/telas/pet/ilha/constantes.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { LUZ_MAX, listaDeFocos } from "../src/telas/pet/ilha/luzConta.ts";
import { pixelsDoMapa } from "../src/telas/pet/ilha/minimapa.ts";
import { MODELOS } from "../src/telas/pet/ilha/modelos.ts";
import { rotaEmTerra } from "../src/telas/pet/ilha/rotaConta.ts";

const CM = CMU_GRANDE, W = CM.celulas_x, H = CM.celulas_y, secas = celulasSecas(CM)!;
const ilha = ilhaDe(CM);
const livre = (x: number, z: number): boolean => x >= 0 && z >= 0 && x < W && z < H && secas[Math.floor(z) * W + Math.floor(x)];
const letra = (x: number, z: number): string => AGUA_ILHA_GRANDE[Math.floor(z)][Math.floor(x)];

describe("a grade da ilha grande", () => {
  test("a planta e a da ilha grande, a moldura e so mar e a terra da grade e a do motor", () => {
    expect(ilha.comAgua).toBe(true);
    expect(ilha.planta).toBe(PLANTA_ILHA_GRANDE);
    expect(ilhaDe(CMU_MVP_AGUA).planta).toBe(PLANTA_ILHA_AGUA);
    expect([ilha.larg, ilha.prof, ilha.x0, ilha.z0]).toEqual([W + 2 * ILHA_GRANDE.moldura, H + 2 * ILHA_GRANDE.moldura, -ILHA_GRANDE.moldura, -ILHA_GRANDE.moldura]);
    for (let j = 0; j < ilha.prof; j++) for (let i = 0; i < ilha.larg; i++) {
      const x = ilha.x0 + i, z = ilha.z0 + j, c = ilha.cel(x, z)!;
      const terraDoMotor = x >= 0 && z >= 0 && x < W && z < H && letra(x, z) !== "~" && letra(x, z) !== "r";
      expect(c.tipo !== "agua", `${x}, ${z}`).toBe(terraDoMotor);
    }
    expect(ilha.pontes.length).toBe(12);
    for (const [x, z] of ilha.pontes) expect(letra(x, z)).toBe(PONTE);
  });

  test("cada arvore fechada do mapa tem a arvore dela, no centro da celula; nada mais alto entra na area", () => {
    const arvores = ilha.fechadas.filter(f => f.tipo === "arvore"), doMotor = ilha.objetos.filter(o => o.doMotor !== null);
    expect(arvores.length).toBe(AGUA_ILHA_GRANDE.join("").split(ARVORE_FECHADA).length - 1);
    expect(arvores.length).toBeGreaterThanOrEqual(60);
    expect(doMotor.map(o => [o.x, o.z])).toEqual(arvores.map(f => [f.x + 0.5, f.z + 0.5]));
    for (const o of doMotor) {
      expect(letra(o.x, o.z)).toBe(ARVORE_FECHADA);
      expect(MODELOS[o.modelo].baixo).toBe(false);
      expect(o.escala).toBeGreaterThanOrEqual(0.85);
    }
    expect(new Set(doMotor.map(o => o.modelo)).size).toBe(2);
    /* nenhuma arvore fechada some da vista: o pet a contorna, entao ela tem de aparecer */
    ilha.objetos.forEach((o, i) => { if (o.doMotor !== null) expect(ilha.escondidos.has(i)).toBe(false); });
    /* o resto do que fica de pe dentro do mapa e baixo (a regra 5), e nada dele cai numa celula fechada */
    ilha.objetos.forEach((o, i) => {
      if (o.doMotor !== null || ilha.escondidos.has(i)) return;
      expect(MODELOS[o.modelo].baixo, `${o.modelo} em ${o.x}, ${o.z}`).toBe(true);
      expect(livre(o.x, o.z) || letra(o.x, o.z) === "." , `${o.modelo} em ${o.x}, ${o.z}`).toBe(true);
    });
    for (const o of ilha.extras) expect(MODELOS[o.modelo].baixo || o.modelo === "pedra", o.modelo).toBe(true);
  });

  test("cada marco fica em cima do bloco de celulas fechadas dele", () => {
    const marcos = ilha.enfeites.filter(e => e.nome !== "poste");
    expect(marcos.map(e => e.nome).sort()).toEqual(["carro", "geladeira", "lata", "trilho"]);
    const blocos = new Map<string, [number, number][]>();
    for (const f of ilha.fechadas) if (f.tipo === "marco") {
      const m = marcos.reduce((a, b) => Math.hypot(a.x - f.x - 0.5, a.z - f.z - 0.5) <= Math.hypot(b.x - f.x - 0.5, b.z - f.z - 0.5) ? a : b);
      blocos.set(m.nome, [...(blocos.get(m.nome) ?? []), [f.x, f.z]]);
    }
    expect(ilha.fechadas.filter(f => f.tipo === "marco").length).toBe(AGUA_ILHA_GRANDE.join("").split(MARCO_FECHADO).length - 1);
    for (const m of marcos) {
      const b = blocos.get(m.nome)!;
      expect(b, m.nome).toBeDefined();
      const cx = b.reduce((s, [x]) => s + x + 0.5, 0) / b.length, cz = b.reduce((s, [, z]) => s + z + 0.5, 0) / b.length;
      expect([m.x, m.z], m.nome).toEqual([cx, cz]);
      expect([m.x, m.z], m.nome).toEqual([...PLANTA_ILHA_GRANDE.marcos[m.nome as "carro"].ponto]);
    }
    expect([...blocos.values()].map(b => b.length).sort()).toEqual([1, 4, 6, 6]);
  });

  test("os lugares, os postes, a praca e os caminhos ficam onde o pet pisa, e todo lugar se alcanca a pe a partir do ninho", () => {
    const P = PLANTA_ILHA_GRANDE, ninho: [number, number] = [CM.layout.ninho[0] + 0.5, CM.layout.ninho[1] + 0.5];
    expect(ilha.lugares.map(l => l.nome)).toEqual(["portao", "barraca", "cais"]);
    for (const l of ilha.lugares) {
      if (l.nome === "cais") { expect(ilha.cel(Math.floor(l.x), Math.floor(l.z))!.nivel).toBe(-1); continue; }   /* o cais fica no mar, rente a praia */
      expect(livre(l.x, l.z), l.nome).toBe(true);
    }
    for (const e of ilha.enfeites) if (e.nome === "poste") expect(livre(e.x, e.z), `poste em ${e.x}, ${e.z}`).toBe(true);
    expect(ilha.enfeites.filter(e => e.nome === "poste").length).toBe(P.postes.length);
    /* a praca e os caminhos: nenhuma celula de caminho e fechada, e ha caminho pintado (a praca inteira, pelo menos) */
    let caminho = 0;
    for (let z = 0; z < H; z++) for (let x = 0; x < W; x++) if (ilha.cel(x, z)!.tipo === "caminho") { caminho++; expect(livre(x, z), `${x}, ${z}`).toBe(true); }
    expect(caminho).toBeGreaterThan(Math.PI * P.praca.raio ** 2);
    for (const linha of ilha.caminhos) for (let k = 1; k < linha.length; k++) for (let t = 0; t <= 20; t++) {
      const x = linha[k - 1][0] + ((linha[k][0] - linha[k - 1][0]) * t) / 20, z = linha[k - 1][1] + ((linha[k][1] - linha[k - 1][1]) * t) / 20;
      if (z < H - 9) expect(livre(x, z), `caminho em ${x}, ${z}`).toBe(true);        /* o fim do caminho do cais entra na praia e para nela */
    }
    /* do ninho a praca, ao portao e a barraca (do outro lado do rio, pela ponte) ha caminho em terra */
    for (const alvo of [[P.praca.x, P.praca.z], ...ilha.lugares.filter(l => l.nome !== "cais").map(l => [l.x, l.z])] as [number, number][]) {
      const rota = rotaEmTerra(CM, ninho, alvo);
      expect(rota, `${alvo}`).not.toBeNull();
      for (const [x, z] of rota!) expect(livre(x, z), `rota em ${x}, ${z}`).toBe(true);
    }
    const barraca = ilha.lugares.find(l => l.nome === "barraca")!, rota = rotaEmTerra(CM, ninho, [barraca.x, barraca.z])!;
    expect(rota.some(([x, z]) => letra(x, z) === PONTE)).toBe(true);
  });

  test("a luz cabe no maximo de focos, e o minimapa tem um pixel por celula", () => {
    const focos = listaDeFocos(ilha);
    expect(focos.length).toBeLessThanOrEqual(LUZ_MAX);
    expect(focos.length).toBeGreaterThan(30);
    /* na ilha de hoje os focos dos caminhos seguem no passo de sempre */
    const hoje = ilhaDe(CMU_MVP_AGUA), f = listaDeFocos(hoje);
    let n = 0;
    for (const c of hoje.caminhos) for (let k = 1; k < c.length; k++)
      n += Math.max(1, Math.round(Math.hypot(c[k][0] - c[k - 1][0], c[k][1] - c[k - 1][1]) / LUZ_HIERARQUIA.passo)) + 1;
    expect(f.filter(x => x[2] === LUZ_HIERARQUIA.raioCaminho).length).toBe(n);
    const paleta = { grama: { casa: [1], jardim: [2], campo: [3], mata: [4] }, areia: [5], caminho: [6] } as never;
    expect(pixelsDoMapa(ilha, paleta).length).toBe(ilha.larg * ilha.prof * 4);
  });
});
