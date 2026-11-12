/* LUTA_POC, LP4 (docs/TAREFA_V3_LUTA_POC.md, 5.1): a chave ligada para todos e a limpeza do combate por turnos.
     - a chave: LUTA_POC_LIGADA, os ovos novos v21, so a v21 (e o pet de teste) abrem, o app sempre com a luta da POC;
     - pela fonte: o combate_tr, o combate.ts, o gambits_pet, o palco 1D (palcoTR/), o src/luta.ts e as telas do combate de antes nao existem,
       e ninguem os importa;
     - os itens: so o chip de stat faz efeito; os chips de regra e as cartas ficam no catalogo para o registro do Tamer, sem efeito, e o Tamer
       nao ganha mais nenhum deles;
     - a Fabrica: so a v21. */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import {
  ITENS, ITEM_DA_MEDALHA, LUTA_POC_LIGADA, MEDALHAS, Motor, VERSAO_FABRICA_ATUAL, VERSAO_PET, VERSAO_PET_LAB, VERSOES_FABRICA, VERSOES_PET,
  chipServe, itemDe, temEfeito,
} from "../motor/index.ts";
import { lutaPocLigada, versaoDoOvo, versoesQueAbrem } from "../src/lutaPoc.ts";
import { Tamer, conferirItensDasMedalhas } from "../src/tamer.ts";

const APP = join(__dirname, "..");
const arquivos = (d: string): string[] => readdirSync(d).flatMap(n => statSync(join(d, n)).isDirectory() ? arquivos(join(d, n)) : /\.(ts|tsx|mjs)$/.test(n) ? [join(d, n)] : []);

describe("a chave ligada (LP4)", () => {
  test("LUTA_POC_LIGADA, a v21 nos ovos novos e so a v21 (e o pet de teste) abrindo", () => {
    expect(LUTA_POC_LIGADA).toBe(true);
    expect(VERSAO_PET).toBe(27);
    expect(VERSOES_PET).toEqual([21, 22, 23, 24, 25, 26, 27]);   // a v26: os dois pets (CO4c)
    expect(lutaPocLigada()).toBe(true);
    expect(versaoDoOvo()).toBe(27);
    expect(versoesQueAbrem()).toEqual([21, 22, 23, 24, 25, 26, 27]);
    expect(new Motor(1, 21).versao).toBe(21);
    expect(new Motor(1, VERSAO_PET_LAB).versao).toBe(16);
    for (const v of [1, 6, 12, 13, 14, 15, 17, 18, 19, 20]) expect(() => new Motor(1, v), `v${v}`).toThrow(/versão de pet desconhecida/);
  });
});

describe("o combate por turnos saiu (pela fonte)", () => {
  test("os arquivos dele nao existem", () => {
    for (const f of ["motor/combate_tr", "motor/combate.ts", "motor/gambits_pet.ts", "src/luta.ts", "src/aprendizadoLuta.ts", "src/telas/lutar/palcoTR",
      "src/telas/lutar/TelaLuta.tsx", "src/telas/lutar/TelaArena.tsx", "src/telas/lutar/TelaCampanha.tsx", "src/telas/lutar/ModalResultado.tsx",
      "src/telas/lutar/EditorRegras.tsx", "src/telas/lutar/PainelAprendizado.tsx", "src/componentes/EscolhaCarta.tsx", "scripts/equilibrio_tr"])
      expect(existsSync(join(APP, f)), f).toBe(false);
  });
  test("ninguem no motor, no app ou nos testes os importa", () => {
    const quem: string[] = [];
    for (const d of ["motor", "src", "test", "scripts", "e2e", "e2e_capturas"]) for (const f of arquivos(join(APP, d))) {
      if (f.endsWith("luta_poc_lp4.test.ts")) continue;
      const txt = readFileSync(f, "utf8");
      /* o luta.ts de motor/arena/ (o nucleo da POC) fica: so o src/luta.ts saiu */
      if (/from\s+"[^"]*(combate_tr\/|\/combate\.ts|gambits_pet\.ts|aprendizadoLuta|palcoTR\/|EditorRegras|PainelAprendizado|ModalResultado|EscolhaCarta|TelaLuta\.tsx)"/.test(txt)
          || /from\s+"(\.\.\/)+(src\/)?luta\.ts"/.test(txt) || (f.includes(join(APP, "src")) && /from\s+"\.\/luta\.ts"/.test(txt)))
        quem.push(f.slice(APP.length + 1));
    }
    expect(quem).toEqual([]);
  });
});

describe("os itens (LP-5)", () => {
  test("so o chip de stat faz efeito; os chips de regra e as cartas ficam, sem efeito e sem servir em estagio nenhum", () => {
    expect(ITENS.filter(temEfeito).map(x => x.id)).toEqual(["chip_forca", "chip_guarda"]);
    for (const it of ITENS.filter(x => !temEfeito(x))) {
      expect(it.efeito, it.id).toMatch(/sem efeito/);
      if (it.tipo === "chip_regra") for (const e of ["crianca", "adolescente", "adulto", "mega"] as const) expect(chipServe(it, e)).toBe(false);
    }
    const m = new Motor(5, 21);
    m.liberar(1);
    while (m.estagioAtual === "bebe") m.avancar(60);
    expect(m.porqueNaoEquipa("chip_recuo")).toMatch(/chip de regra/);
    expect(() => m.equipar("chip_recuo")).toThrow(/chip de regra/);
    expect(m.porqueNaoEquipa("chip_forca")).toBeNull();
  });
  test("as medalhas so dao os chips de stat ao Tamer; os chips de regra que ele ja tem ficam no registro", () => {
    const t = new Tamer(), m = new Motor(5, 21);
    for (const md of MEDALHAS) t.ganhar(md.id, m, 1);
    const novos = conferirItensDasMedalhas(t, m, 2).map(x => x.id);
    expect(novos).toEqual(MEDALHAS.map(md => ITEM_DA_MEDALHA[md.id]).filter(id => temEfeito(itemDe(id))));
    expect(conferirItensDasMedalhas(t, m, 3)).toEqual([]);
    /* um Tamer de antes, com o chip de regra no registro, ainda abre */
    const antigo = Tamer.reproduzir([...t.log.slice(0, 2), ["item", { id: "chip_recuo", n: 1, quando: 1, origem: "medalha", lider: "npc_tier2_carcereiro", pet: 5, forma: "x", est: "adolescente", tick: 900 }]]);
    expect(antigo.temChip("chip_recuo")).toBe(true);
  });
});

describe("a Fabrica (LP2b e LP4)", () => {
  test("so a v21", () => {
    expect(VERSOES_FABRICA).toEqual([21]);
    expect(VERSAO_FABRICA_ATUAL).toBe(21);
  });
});
