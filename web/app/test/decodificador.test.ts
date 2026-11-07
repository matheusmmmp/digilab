/* O decodificador de conceitos `dec-v1` (DC1, docs/research/ESPEC_DECODIFICADOR_FALA.md) em TS contra o Python: a config folha a folha, a saida bit a bit
   nos mesmos motivos das vidas curtas do braco REL (gabaritos/decodificador_python.json.gz, de experiments/exportar_decodificador.py), o formato fixo
   da espec, a fidelidade minima (lembranca e determinacao contra as sondas) e que o decodificador so le. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CATALOGO_CONCEITOS, CLASSES_EPISODIO_DEC, DESFECHOS, decodificar, decodificarV2, desfechoDoEpisodio, episodioDec, VERSAO_DECODIFICADOR, VERSAO_DECODIFICADOR_V2, type ConceitosDec } from "../motor/index.ts";
import { CONFIG_DECODIFICADOR } from "../motor/digibrain/constantes.ts";
import { conferir, vidasModular } from "./digibrain_modular_gabarito.ts";

type Dict = Record<string, any>;
const lerGz = (rel: string): any => JSON.parse(gunzipSync(readFileSync(new URL(`./gabaritos/${rel}`, import.meta.url))).toString("utf8"));
const gab = lerGz("decodificador_python.json.gz") as { catalogo: string[]; config: Dict; vidas: { origem: string; dono: string; lugar: string; semente: number; decisoes: ConceitosDec[]; episodios: (Dict | null)[]; decisoes_v2: ConceitosDec[] }[] };
const S = 1024;

/** os motivos de cada vida do gabarito, lidos dos gabaritos do modular (as mesmas vidas que o exportador decodificou) */
function motivosDe(v: { origem: string; dono: string; lugar: string; semente: number }): Dict[] {
  if (v.origem.endsWith("fins.json.gz")) {
    const f = lerGz(v.origem).vidas.find((x: Dict) => x.dono === v.dono && x.lugar === v.lugar && x.semente === v.semente);
    return f.decisoes.map((d: Dict) => d.motivo);
  }
  const m = vidasModular().find(x => x.dono === v.dono && x.lugar === v.lugar && x.semente === v.semente);
  if (!m) throw new Error("vida sem gabarito do modular: " + JSON.stringify(v));
  return m.decisoes.map(d => d.motivo as Dict);
}
const todos = gab.vidas.map(v => ({ v, motivos: motivosDe(v) }));
const clone = <T>(x: T): T => JSON.parse(JSON.stringify(x)) as T;

describe("decodificador dec-v1: paridade com o Python", () => {
  test("a config e igual ao gabarito, folha a folha", () => {
    expect(clone(CONFIG_DECODIFICADOR)).toEqual(gab.config);
  });
  test("o catalogo e a versao", () => {
    expect([...CATALOGO_CONCEITOS]).toEqual(gab.catalogo);
    expect(VERSAO_DECODIFICADOR).toBe("dec-v1");
  });
  test("a saida de cada decisao de todas as vidas e igual bit a bit", () => {
    let n = 0;
    for (const { v, motivos } of todos) {
      expect(motivos.length).toBe(v.decisoes.length);
      motivos.forEach((m, i) => { conferir(`${v.origem} ${v.dono}/${v.lugar}/${v.semente} k=${i}`, decodificar(m, S), v.decisoes[i]); n++; });
    }
    expect(n).toBeGreaterThan(3000);
  });
});

describe("decodificador dec-v1: o formato fixo da espec", () => {
  test("12 conceitos do catalogo, valor e confianca inteiros em [0, S], alvo so de texto, intencao no catalogo", () => {
    for (const { motivos } of todos) for (const m of motivos) {
      const r = decodificar(m, S);
      expect(r.versao).toBe("dec-v1");
      expect(r.k).toBe(m["k"]);
      expect(r.conceitos.map(c => c.nome)).toEqual([...CATALOGO_CONCEITOS]);
      expect(CATALOGO_CONCEITOS).toContain(r.intencao);
      for (const c of r.conceitos) {
        expect(Number.isInteger(c.valor) && c.valor >= 0 && c.valor <= S).toBe(true);
        expect(Number.isInteger(c.confianca) && c.confianca >= 0 && c.confianca <= S).toBe(true);
        if (c.alvo !== undefined) expect(typeof c.alvo).toBe("string");
      }
    }
  });
});

describe("decodificador dec-v1: fidelidade minima as sondas", () => {
  test("a lembranca so e a intencao quando a sonda sem_lembranca decidiu (e entao passa o limiar)", () => {
    let decidiu = 0, outras = 0;
    for (const { motivos } of todos) for (const m of motivos) {
      const r = decodificar(m, S), l = r.conceitos.find(c => c.nome === "lembranca")!;
      if (m["sondas"]["lembranca_decidiu"]) {
        decidiu++;
        expect(r.intencao).toBe("lembranca");
        expect(l.valor).toBeGreaterThanOrEqual(CONFIG_DECODIFICADOR.limiar_valor);
      } else {
        outras++;
        expect(r.intencao).not.toBe("lembranca");
      }
    }
    expect(decidiu).toBeGreaterThan(0);
    expect(outras).toBeGreaterThan(0);
  });
  test("a determinacao passa o limiar quando a sonda da persistencia decidiu, e sem intencao em curso nao decidindo e zero", () => {
    let decidiu = 0, semI = 0;
    for (const { motivos } of todos) for (const m of motivos) {
      const d = decodificar(m, S).conceitos.find(c => c.nome === "determinacao")!;
      if (m["sondas"]["persistencia_decidiu"]) { decidiu++; expect(d.valor).toBeGreaterThanOrEqual(CONFIG_DECODIFICADOR.limiar_valor); }
      else if (m["estado"]["I"] === null) { semI++; expect(d.valor).toBe(0); }
    }
    expect(decidiu).toBeGreaterThan(0);
    expect(semI).toBeGreaterThan(0);
  });
  test("a determinacao media e maior quando a sonda da persistencia decidiu", () => {
    const com: number[] = [], sem: number[] = [];
    for (const { motivos } of todos) for (const m of motivos) {
      if (m["estado"]["I"] === null && !m["sondas"]["persistencia_decidiu"]) continue;
      (m["sondas"]["persistencia_decidiu"] ? com : sem).push(decodificar(m, S).conceitos.find(c => c.nome === "determinacao")!.valor);
    }
    const mean = (a: number[]): number => a.reduce((s, x) => s + x, 0) / a.length;
    expect(mean(com)).toBeGreaterThan(mean(sem));
  });
});

describe("decodificador dec-v1: so le", () => {
  test("nao muda o motivo e nao depende do consequencia (que so chega na decisao seguinte)", () => {
    for (const { motivos } of todos.slice(0, 4)) for (const m of motivos) {
      const antes = clone(m), r = decodificar(m, S);
      expect(m).toEqual(antes);
      const sem = clone(m); delete sem["consequencia"];
      expect(decodificar(sem, S)).toEqual(r);
    }
  });
  test("falha alto em receptor, comportamento e sonda desconhecidos", () => {
    const base = clone(todos[0]!.motivos[40]!);
    const a = clone(base); a["afeto"]["urgencias"]["ciume"] = 1;
    expect(() => decodificar(a, S)).toThrow(/receptor desconhecido/);
    const b = clone(base); b["unidades"][0]["chave"][0] = "voar";
    expect(() => decodificar(b, S)).toThrow(/comportamento desconhecido/);
    const c = clone(base); c["sondas"]["magia_decidiu"] = true;
    expect(() => decodificar(c, S)).toThrow(/sonda desconhecida/);
    const d = clone(base); delete d["sondas"]["habito_decidiu"];
    expect(() => decodificar(d, S)).toThrow(/nao tem a sonda/);
  });
});

describe("decodificador dec-v2 (DC2b): o episodio da lembranca, paridade com o Python", () => {
  test("a versao e os catalogos", () => {
    expect(VERSAO_DECODIFICADOR_V2).toBe("dec-v2");
    expect([...CLASSES_EPISODIO_DEC]).toEqual(["racao", "a", "b", "c", "podre", "nao_havia", "bola", "sem_alvo"]);
    expect([...DESFECHOS]).toEqual(["bom", "ruim", "neutro"]);
  });
  test("a saida de cada decisao de todas as vidas, com o episodio gravado, e igual bit a bit", () => {
    let n = 0, comEpisodio = 0;
    for (const { v, motivos } of todos) {
      expect(v.episodios.length).toBe(motivos.length);
      motivos.forEach((m, i) => {
        const r = decodificarV2(m, S, v.episodios[i] ?? null);
        conferir(`${v.origem} ${v.dono}/${v.lugar}/${v.semente} k=${i} v2`, r, v.decisoes_v2[i]);
        if (r.conceitos.some(c => c.episodio !== undefined)) comEpisodio++;
        n++;
      });
    }
    expect(n).toBeGreaterThan(3000);
    expect(comEpisodio).toBeGreaterThan(3000);
  });
  test("o v2 e o v1 mais o campo episodio (so na lembranca); o v1 nao ganha o campo", () => {
    for (const { v, motivos } of todos.slice(0, 4)) motivos.forEach((m, i) => {
      const v1 = decodificar(m, S), v2 = decodificarV2(m, S, v.episodios[i] ?? null);
      expect(v1.versao).toBe("dec-v1");
      expect(v1.conceitos.every(c => c.episodio === undefined)).toBe(true);
      expect(clone({ ...v2, versao: "dec-v1", conceitos: v2.conceitos.map(c => { const { episodio: _e, ...resto } = c; return resto; }) })).toEqual(clone(v1));
      expect(v2.conceitos.filter(c => c.episodio !== undefined).every(c => c.nome === "lembranca")).toBe(true);
    });
  });
  test("o desfecho e o sinal do sigma com a margem; luta fica fora; fora do catalogo falha alto", () => {
    const m = CONFIG_DECODIFICADOR.limiar_desfecho, base = { acao: ["comer", "racao", null], classe: "racao", origem: "consumo" };
    expect(desfechoDoEpisodio({ ...base, sigma: m })).toBe("bom");
    expect(desfechoDoEpisodio({ ...base, sigma: m - 1 })).toBe("neutro");
    expect(desfechoDoEpisodio({ ...base, sigma: -(m - 1) })).toBe("neutro");
    expect(desfechoDoEpisodio({ ...base, sigma: -m })).toBe("ruim");
    expect(episodioDec({ origem: "luta", acao: ["lutar", "muralha"], classe: "muralha", sigma: -400 })).toBeNull();
    expect(() => episodioDec({ ...base, acao: ["voar", null, null], sigma: 1 })).toThrow(/comportamento desconhecido/);
    expect(() => episodioDec({ ...base, classe: "ovni", sigma: 1 })).toThrow(/classe desconhecida/);
  });
  test("o episodio tem de ser o recuperado na decisao", () => {
    const { v, motivos } = todos[0]!;
    const i = v.episodios.findIndex(e => e !== null);
    const outro = v.episodios.find(e => e !== null && e["id"] !== v.episodios[i]!["id"])!;
    expect(() => decodificarV2(motivos[i]!, S, outro)).toThrow(/nao e o recuperado/);
  });
});
