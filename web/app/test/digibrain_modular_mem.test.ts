/* G-PAR do M-MEM (LM3): as chamadas de `mem.*` do gabarito da LM0 (relogio, consolidar, lembrar, termo_lembranca, recuperar, codificar,
   codificar_autobio) e o `episodio_autobio` (que o gabarito grava como `adapt.episodio_autobio`), refeitos em ordem numa Memoria nova por vida.
   O gabarito guarda a assinatura do estado ao fim de cada decisao, nao por chamada: ela e conferida ali, e a saida de cada chamada e conferida
   na hora. As sondas `sem_lembranca` e `lembranca_decidiu`: o `impulso.unidades` e o `arb.escolher` sao refeitos com o termo da lembranca e o
   `casa` OFICIAIS do mem.ts (no lugar do `casa` refeito no teste do impulso), com o M-PLAST de mentira da LM1 e a rng de politica da LM2, e o
   que sai (unidades, pesos, sondas) e conferido contra o Python nas 3 072 decisoes. */
import { describe, expect, test } from "vitest";
import { Arbitragem } from "../motor/digibrain/arb.ts";
import { CONFIG_DIGIBRAIN_LAB, CONFIG_MODULAR_MUNDO, INATOS_MODULAR } from "../motor/digibrain/constantes.ts";
import { Impulso, type PlastImpulso } from "../motor/digibrain/impulso.ts";
import { Memoria, episodioAutobio } from "../motor/digibrain/mem.ts";
import { RandomPy } from "../motor/mundo.ts";
import { assinar, conferir, entrada, leiturasPlast, vidasModular } from "./digibrain_modular_gabarito.ts";

/** a chave da persistencia no Python (`str` da tupla) em JSON */
const chaveDoPython = (t: string): string => JSON.stringify(JSON.parse(t.replace(/'/g, '"').replace(/None/g, "null").replace(/\(/g, "[").replace(/\)/g, "]")));
const novaMemoria = (): Memoria => new Memoria({ sub: CONFIG_MODULAR_MUNDO.sub }, null, CONFIG_DIGIBRAIN_LAB);

describe("G-PAR mem", () => {
  test("as chamadas do M-MEM, o episodio e as sondas da lembranca iguais ao Python nas oito vidas", () => {
    const lp = leiturasPlast();
    const impulso = new Impulso(null, CONFIG_DIGIBRAIN_LAB);
    const n: Record<string, number> = {
      "mem.relogio": 0, "mem.consolidar": 0, "mem.lembrar": 0, "mem.termo_lembranca": 0, "mem.recuperar": 0, "mem.codificar": 0,
      "mem.codificar_autobio": 0, "adapt.episodio_autobio": 0,
    };
    let consolidou = 0, lembrou = 0, comTermo = 0, recuperou = 0, episodios = 0, semEpisodio = 0, lembrancaDecidiu = 0, comUnidadeCasada = 0, decisoes = 0, sondasSem = 0;
    const origens = new Set<string>(), memorias = new Set<string>();
    vidasModular().forEach((v, iv) => {
      const mem = novaMemoria();
      const arb = new Arbitragem(null, CONFIG_DIGIBRAIN_LAB.memoria_autobio, CONFIG_DIGIBRAIN_LAB.facetas_mem);
      const rng = new RandomPy(v.semente + 1_000_003);
      let anterior: (typeof v.decisoes)[number] | null = null;
      for (const d of v.decisoes) {
        const lv = lp[iv]!.decisoes[d.k]!;
        const fila = [...lv.chamadas];
        let termo: ReturnType<Memoria["termoLembranca"]> = null;
        let memoriaRec: ReturnType<Memoria["recuperar"]> | null = null;
        let unidadesTS: any = null;
        // o gravador atribui o `adapt.episodio_autobio` do fechamento da decisao k-1 a ela (o gancho `adapt.*` conta k-1); o `afeto.consequencia` a que ele se
        // refere esta na lista da decisao k, onde o fechamento roda. O episodio e puro: refeito aqui, com os `$ref` resolvidos na decisao de agora.
        let episodioTS: ReturnType<typeof episodioAutobio> = null;
        const ce = anterior?.chamadas.find(x => x.m === "adapt.episodio_autobio");
        if (ce) {
          const a = (i: number) => entrada(d, ce, i);
          episodioTS = episodioAutobio(a(0), a(1), a(2), a(3), a(4), a(5), a(6), a(7), a(8), a(9), a(10), a(11), INATOS_MODULAR);
          conferir(`${v.lugar}/${v.dono}/${v.semente} k=${anterior!.k} adapt.episodio_autobio`, episodioTS, ce.s);
          if (episodioTS === null) semEpisodio++; else { episodios++; origens.add(episodioTS.origem); }
        }
        for (const c of d.chamadas) {
          const onde = `${v.lugar}/${v.dono}/${v.semente} k=${d.k} ${c.m}`;
          if (c.m === "mem.relogio") {
            conferir(onde, mem.relogio(c.e[0] as number), c.s);
          } else if (c.m === "mem.consolidar") {
            const r = mem.consolidar(c.e[0] as number);
            conferir(onde, r, c.s);
            if (r !== null) consolidou++;
          } else if (c.m === "mem.lembrar") {
            const r = mem.lembrar(entrada(d, c, 0));
            conferir(onde, r, c.s);
            if (r.recuperado !== null) { lembrou++; memorias.add(r.memoria!); }
          } else if (c.m === "mem.termo_lembranca") {
            termo = mem.termoLembranca(entrada(d, c, 0));
            conferir(onde, termo, c.s);
            if (termo !== null) comTermo++;
          } else if (c.m === "mem.recuperar") {
            memoriaRec = mem.recuperar(entrada(d, c, 0), entrada(d, c, 1));
            conferir(onde, memoriaRec, c.s);
            if (memoriaRec.recuperado !== null) recuperou++;
          } else if (c.m === "mem.codificar") {
            conferir(onde, mem.codificar(c.e[0] as any), c.s);
          } else if (c.m === "mem.codificar_autobio") {
            if (episodioTS === null) throw new Error(`${onde}: codificar_autobio sem episodio`);
            conferir(`${onde} (entrada)`, entrada(anterior!, c, 0), episodioTS);
            conferir(onde, mem.codificarAutobio(episodioTS), c.s);
          } else if (c.m === "impulso.unidades") {
            // o impulso pergunta ao M-PLAST (as leituras da LM1) e recebe o termo e o `casa` do mem.ts
            const proxima = (m: string) => {
              const x = fila.shift();
              if (!x || x.m !== m) throw new Error(`${onde}: esperava ${m}, veio ${x?.m}`);
              return x;
            };
            const plast: PlastImpulso = {
              habito(b, z) { const x = proxima("plast.habito"); conferir(`${onde} ${x.m}.entrada`, [b, [...z]], x.e); return x.s as number; },
              incentivo(pc, classe, drives) { const x = proxima("plast.incentivo"); conferir(`${onde} ${x.m}.entrada`, [pc, classe, [...drives]], x.e); return x.s as number; },
            };
            const ctx = entrada(d, c, 2);
            const persistencia = Object.fromEntries(Object.entries(ctx.persistencia as Record<string, number>).map(([k, h]) => [chaveDoPython(k), h]));
            const lembranca = termo === null ? null : ([termo, mem.casa] as const);
            const [unidades, z] = impulso.unidades(entrada(d, c, 0), entrada(d, c, 1), { ...ctx, persistencia }, plast, memoriaRec, c.e[5] as string[], lembranca, c.e[7]);
            conferir(onde, [unidades, z], c.s);
            unidadesTS = unidades;
            if (termo !== null && unidades.some(u => u.termos["lembranca"] !== 0)) comUnidadeCasada++;
            continue;
          } else if (c.m === "arb.reflexo") {
            arb.reflexo(entrada(d, c, 0));
            continue;
          } else if (c.m === "arb.escolher") {
            const s = arb.escolher(unidadesTS, entrada(d, c, 1), entrada(d, c, 2), rng, entrada(d, c, 4), entrada(d, c, 5));
            conferir(onde, s, c.s);
            if (typeof s.sondas["sem_lembranca"] !== "undefined") sondasSem++;
            if (s.sondas["lembranca_decidiu"]) lembrancaDecidiu++;
            decisoes++;
            continue;
          } else {
            continue;                                    // as outras chamadas sao dos outros modulos
          }
          n[c.m]!++;
        }
        conferir(`${v.lugar}/${v.dono}/${v.semente} k=${d.k} assinatura do mem`, assinar(mem.estadoInterno()), d.assinatura["mem"]);
        anterior = d;
      }
    });
    n["adapt.episodio_autobio"] = episodios + semEpisodio;
    const total = Object.values(n).reduce((a, b) => a + b, 0);
    console.log(`G-PAR mem: ${total} chamadas conferidas (${Object.entries(n).map(([k, x]) => `${k} ${x}`).join(", ")}); episodios ${episodios} (sem episodio ${semEpisodio}, `
      + `origens ${[...origens].sort().join("/")}), consolidacoes ${consolidou}, lembrancas ${lembrou} (memorias ${[...memorias].sort().join("/")}), com termo ${comTermo}, `
      + `recuperacoes ${recuperou}; sondas: sem_lembranca em ${sondasSem} de ${decisoes} decisoes, lembranca_decidiu ${lembrancaDecidiu}, decisoes com unidade casada ${comUnidadeCasada}`);
    for (const [m, x] of Object.entries(n)) expect(x, m).toBeGreaterThan(0);
    expect(decisoes).toBe(8 * 384);
    expect(sondasSem).toBe(8 * 384);
    for (const x of [consolidou, lembrou, comTermo, recuperou, episodios, semEpisodio, lembrancaDecidiu, comUnidadeCasada]) expect(x).toBeGreaterThan(0);
  });

  test("facetas_mem e os bracos de pesquisa do controle_mem ficam fora do laboratorio", () => {
    const base = CONFIG_DIGIBRAIN_LAB;
    expect(() => new Memoria({ sub: 16 }, null, { ...base, facetas_mem: true })).toThrow(/facetas_mem/);
    for (const c of ["sem", "rec", "emb", "rel_sem_neg"]) expect(() => new Memoria({ sub: 16 }, null, { ...base, controle_mem: c })).toThrow(/controle_mem/);
    const m = novaMemoria();
    expect(() => m.evidenciaFaceta("cautela_comida")).toThrow(/facetas_mem/);
    expect(() => m.classesComPositivo()).toThrow(/facetas_mem/);
  });
});
