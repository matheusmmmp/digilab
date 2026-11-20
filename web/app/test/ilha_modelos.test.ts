/* Os modelos da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, H1): a tabela de src/telas/pet/ilha/modelos.ts contra a pasta
   public/kits3d/ (H-1) e contra a lista do script que a enche (scripts/kits3d_copiar.py). Cada arquivo da tabela existe, com o .bin e as
   imagens que ele cita; a pasta tem so o que a tabela usa, mais as licencas; o total cabe nos 8 MB; nada do Kenney (H-6); a decoracao
   que entra na area andavel e baixa (regra 5). */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { ALTURA_BAIXA, MODELOS, MODELOS_BAIXOS, MODELO_ARVORE_DO_MOTOR } from "../src/telas/pet/ilha/modelos.ts";

const APP = join(__dirname, ".."), KITS = join(APP, "public", "kits3d");
const arquivosDe = (dir: string): string[] => readdirSync(dir).flatMap(n => statSync(join(dir, n)).isDirectory() ? arquivosDe(join(dir, n)) : [join(dir, n)]);
const usados = [...new Set(Object.values(MODELOS).flatMap(m => m.arquivos))];

describe("os modelos da ilha", () => {
  test("cada arquivo da tabela esta em public/kits3d, com os buffers e as imagens que cita", () => {
    for (const a of usados) {
      const f = join(KITS, a);
      expect(existsSync(f), a).toBe(true);
      const g = JSON.parse(readFileSync(f, "utf8")) as { buffers: { uri: string }[]; images?: { uri: string }[] };
      for (const u of [...g.buffers, ...(g.images ?? [])].map(b => b.uri)) expect(existsSync(join(f, "..", u)), `${a}: ${u}`).toBe(true);
    }
  });

  test("a pasta so tem o que a tabela usa e as licencas, e cabe no orcamento de 8 MB", () => {
    const citados = new Set<string>();
    for (const a of usados) {
      const f = join(KITS, a), g = JSON.parse(readFileSync(f, "utf8")) as { buffers: { uri: string }[]; images?: { uri: string }[] };
      citados.add(f);
      for (const u of [...g.buffers, ...(g.images ?? [])].map(b => b.uri)) citados.add(join(f, "..", u));
    }
    const todos = arquivosDe(KITS);
    const sobra = todos.filter(f => !citados.has(f) && !/License.*\.txt$/.test(f));
    expect(sobra).toEqual([]);
    for (const kit of ["quaternius", "kaykit"]) expect(readdirSync(join(KITS, kit)).some(n => /^License.*\.txt$/.test(n)), kit).toBe(true);
    expect(todos.reduce((s, f) => s + statSync(f).size, 0)).toBeLessThanOrEqual(8 * 1024 * 1024);
  });

  test("o script copia a mesma lista da tabela, sem o Kenney", () => {
    const py = readFileSync(join(APP, "scripts", "kits3d_copiar.py"), "utf8");
    const lista = (kit: string) => [...py.slice(py.indexOf(`"${kit}": {`)).split('"modelos": [')[1].split("]")[0].matchAll(/"([A-Za-z0-9_]+)"/g)].map(m => `${kit}/${m[1]}.gltf`);
    expect([...lista("quaternius"), ...lista("kaykit")].sort()).toEqual([...usados].sort());
    expect(usados.some(a => /kenney/i.test(a))).toBe(false);
  });

  test("so a decoracao baixa entra na area andavel; a arvore do motor e a unica alta la dentro", () => {
    for (const n of MODELOS_BAIXOS) expect(MODELOS[n].altura, n).toBeLessThanOrEqual(ALTURA_BAIXA);
    expect(MODELOS[MODELO_ARVORE_DO_MOTOR].baixo).toBe(false);
    for (const m of Object.values(MODELOS)) { expect(m.arquivos.length).toBeGreaterThan(0); expect(m.altura).toBeGreaterThan(0); }
  });
});
