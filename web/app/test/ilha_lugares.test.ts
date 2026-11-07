/* Onde ficam os lugares na ilha (docs/TAREFA_V3_LUGARES_3D.md, secao 12; grade.ts, porLugares). LG-G1: um de cada, fora da area andavel.
   LG-G2: o portao e a barraca em grama plana ao norte, a distancia combinada da area, longe dos enfeites e um do outro, com a frente para a
   area. LG-G3: o cais na ultima linha de areia antes do mar, de frente para o norte. LG-G4: a clareira so esconde a decoracao (nunca uma
   arvore do motor) e so dentro do raio; os objetos em si nao mudam (o E-G0 de test/ilha_enfeites.test.ts confere contra o gabarito).
   LG-G5: a paleta da Ilha (docs/lugares3d/estilo_ilha.py) e a da textura publicada. */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { LUGARES_GRADE } from "../src/telas/pet/ilha/constantes.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { LUGARES_MODELOS, type NomeLugar } from "../src/telas/pet/ilha/modelos.ts";

describe("onde ficam os lugares (LG-G1 a LG-G4)", () => {
  for (const cm of [CMU_MVP, CMU]) test(`layout ${cm.layout.nome}`, () => {
    const ilha = ilhaDe(cm), nomes = Object.keys(LUGARES_MODELOS) as NomeLugar[];
    expect(ilha.lugares.map(l => l.nome).sort()).toEqual([...nomes].sort());
    for (const l of ilha.lugares) {
      expect(ilha.naArea(Math.floor(l.x), Math.floor(l.z)), l.nome).toBe(false);
      if (l.nome === "cais") {
        const c = ilha.cel(Math.floor(l.x), Math.floor(l.z) - 1)!, agua = ilha.cel(Math.floor(l.x), Math.floor(l.z))!;
        expect(c.tipo).toBe("areia"); expect(agua.tipo).toBe("agua"); expect(l.giro).toBeCloseTo(Math.PI);
        continue;
      }
      const G = LUGARES_GRADE[l.nome], d = ilha.distanciaDaArea(l.x, l.z), c = ilha.cel(Math.floor(l.x), Math.floor(l.z))!;
      expect(c.tipo).toBe("grama"); expect(c.cantos.every(h => h === c.cantos[0])).toBe(true);
      expect(l.z).toBeLessThan(0); expect(d).toBeGreaterThanOrEqual(G.perto - 1e-9); expect(d).toBeLessThanOrEqual(G.longe + 1e-9);
      expect(l.y).toBe(ilha.altura(l.x, l.z));
      for (const e of ilha.enfeites) expect(Math.hypot(e.x - l.x, e.z - l.z), `${l.nome} e ${e.nome}`).toBeGreaterThanOrEqual(G.deEnfeite);
      /* a frente (+z do glTF girado) aponta para o ponto mais perto da area */
      const ax = Math.min(Math.max(l.x, 0), ilha.area.w), az = Math.min(Math.max(l.z, 0), ilha.area.h);
      const dir = [Math.sin(l.giro), Math.cos(l.giro)], para = [ax - l.x, az - l.z], n = Math.hypot(para[0], para[1]);
      expect(dir[0] * para[0] / n + dir[1] * para[1] / n).toBeCloseTo(1);
    }
    const [a, b] = ilha.lugares.filter(l => l.nome !== "cais");
    expect(Math.hypot(a.x - b.x, a.z - b.z)).toBeGreaterThanOrEqual(LUGARES_GRADE.portao.deEnfeite + LUGARES_GRADE.portao.clareira);
    for (const i of ilha.escondidos) {
      const o = ilha.objetos[i];
      expect(o.doMotor).toBeNull();
      expect(ilha.lugares.some(l => Math.hypot(o.x - l.x, o.z - l.z) < LUGARES_GRADE[l.nome].clareira)).toBe(true);
    }
    ilha.objetos.forEach((o, i) => {
      if (o.doMotor !== null || ilha.escondidos.has(i)) return;
      for (const l of ilha.lugares) expect(Math.hypot(o.x - l.x, o.z - l.z)).toBeGreaterThanOrEqual(LUGARES_GRADE[l.nome].clareira);
    });
  });
});

describe("a paleta da Ilha (LG-G5)", () => {
  const DOCS = join(__dirname, "..", "..", "..", "docs", "lugares3d");
  for (const n of Object.keys(LUGARES_MODELOS) as NomeLugar[]) test(n, () => {
    const p = JSON.parse(readFileSync(join(DOCS, n, "paleta.json"), "utf8")) as { paleta: number[][]; paleta_ilha: number[][] };
    expect(p.paleta_ilha.length).toBe(p.paleta.length);
    /* o PNG de paleta publicado: as cores do PLTE estao todas na paleta da Ilha */
    const b = readFileSync(join(__dirname, "..", "public", "lugares", n, `${n}_cor.png`));
    expect(b[25]).toBe(3);    // tipo de cor 3: paleta
    const i = b.indexOf("PLTE"), len = b.readUInt32BE(i - 4), ilha = p.paleta_ilha.map(c => c.join(","));
    for (let k = 0; k < len; k += 3) expect(ilha, n).toContain([b[i + 4 + k], b[i + 5 + k], b[i + 6 + k]].join(","));
  });
});
