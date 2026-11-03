/* A bola no golpe e a bola do dono (docs/TAREFA_V3_HABITAT_OBJETOS.md): o pet v15 (o v14 com a chave bolaNoGolpe do Mundo, a
   ConfigBolaNoGolpe do Python) e o evento "db" (o dono poe a bola parada num lugar, em qualquer pet com o mundo).
     - direcaoDoGolpe: os mesmos casos do tests/test_bola_no_golpe.py do Python;
     - desligada (o padrao do Mundo e os pets v13 e v14), a bola de sempre: os gabaritos do mundo seguem byte a byte (mundo.test.ts,
       mvp_mundo.test.ts); aqui, o Mundo com a chave desligada explicita e igual ao sem ela;
     - ligada, cada rolagem sai na direcao em que o pet vinha, com a distancia do sorteio de sempre;
     - o "db": vai ao registro, refaz no replay bit a bit e falha alto se invalido. */
import { describe, expect, test } from "vitest";
import { CMU_MVP, DIR16, Motor, Mundo, TPD, direcaoDoGolpe, type EventoRegistro } from "../motor/index.ts";

/** o dono que poe a bola perto do pet todo passo: o pet que quer brincar anda ate ela e bate */
function viver(m: Motor, dias: number): void {
  const passos = Math.round(dias * TPD / 30), d = [[24, 0], [-24, 0], [0, 24], [0, -24]];
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const [x, y] = m.mundo!.pet, [dx, dy] = d[p % 4];
    m.deixarBola(Math.min(1023, Math.max(0, x + dx)), Math.min(479, Math.max(0, y + dy)));
    if (m.e.fome < .6 && p % 2 === 0) m.observar("alimentar");
    if (m.e.sujeira >= 2) m.observar("limpar");
  }
}

/** onde o pet estava antes de cada batida na bola: o x, y da decisao anterior (so a decisao o move), e o ninho na primeira */
function antesDasBatidas(mu: Mundo): [number, number][] {
  const ninho: [number, number] = [mu.cm.layout.ninho[0] * mu.cm.sub + mu.cm.sub / 2, mu.cm.layout.ninho[1] * mu.cm.sub + mu.cm.sub / 2];
  let antes = ninho;
  const fora: [number, number][] = [];
  for (const d of mu.decisoes as { x: number; y: number; brincou_com_bola: boolean }[]) {
    if (d.brincou_com_bola) fora.push(antes);
    antes = [d.x, d.y];
  }
  return fora;
}

describe("a bola no golpe (pets v15)", () => {
  test("direcaoDoGolpe: a das 16 mais alinhada; em cima da bola, null (os casos do Python)", () => {
    expect(direcaoDoGolpe(0, 0, 0, 0)).toBeNull();
    expect(direcaoDoGolpe(0, 0, 10, 0)).toBe(0);
    expect(direcaoDoGolpe(0, 0, 0, -10)).toBe(4);
    expect(direcaoDoGolpe(0, 0, -10, 0)).toBe(8);
    expect(direcaoDoGolpe(0, 0, 0, 10)).toBe(12);
    expect(direcaoDoGolpe(5, 5, 15, -5)).toBe(2);
    DIR16.forEach(([cx, cy], k) => expect(direcaoDoGolpe(100, 100, 100 + cx, 100 + cy)).toBe(k));
  });

  test("desligada explicita, o Mundo e o de sempre", () => {
    const a = new Mundo({ semente: 101, cfg: CMU_MVP }), b = new Mundo({ semente: 101, cfg: CMU_MVP, bolaNoGolpe: false });
    expect(a.bolaNoGolpe).toBe(false);
    expect(JSON.stringify(b.resumo())).toBe(JSON.stringify(a.resumo()));
  });

  test("so o v15 liga a chave; o v14 e o v13 seguem com a bola de antes", () => {
    expect(new Motor(101).mundo!.bolaNoGolpe).toBe(true);
    expect(new Motor(101, 14).mundo!.bolaNoGolpe).toBe(false);
    expect(new Motor(101, 13).mundo!.bolaNoGolpe).toBe(false);
  });

  test("ligada, a bola sai na direcao em que o pet vinha, com a distancia de sempre na primeira batida", () => {
    let golpes = 0;
    for (const semente of [101, 202, 303]) {
      const v15 = new Motor(semente), v14 = new Motor(semente, 14);
      viver(v15, 4); viver(v14, 4);
      const r15 = v15.mundo!.rolagens as { tick: number; de: [number, number]; direcao: number; celulas: number }[];
      const r14 = v14.mundo!.rolagens as typeof r15;
      expect(r15.length).toBeGreaterThan(0);
      /* ate a primeira batida a vida e a mesma; a distancia dela sai do mesmo sorteio */
      expect([r15[0].tick, r15[0].celulas]).toEqual([r14[0].tick, r14[0].celulas]);
      const antes = antesDasBatidas(v15.mundo!);
      expect(antes.length).toBe(r15.length);
      r15.forEach((r, i) => {
        const g = direcaoDoGolpe(antes[i][0], antes[i][1], r.de[0], r.de[1]);
        if (g !== null) { expect(r.direcao).toBe(g); golpes++; }
      });
    }
    expect(golpes).toBeGreaterThan(0);
  });
});

describe("a bola do dono (o evento db)", () => {
  test("vai ao registro e refaz no replay bit a bit, no v15 e no v14", () => {
    for (const versao of [15, 14]) {
      const m = new Motor(4242, versao);
      viver(m, 2);
      const log = m.log, dbs = log.filter(ev => ev[1] === "db");
      expect(dbs.length).toBeGreaterThan(0);
      const r = Motor.reproduzir(4242, log, versao);
      expect(r.assinatura()).toBe(m.assinatura());
      expect(JSON.stringify(r.mundo!.resumo())).toBe(JSON.stringify(m.mundo!.resumo()));
    }
  });

  test("a bola fica onde o dono a pos, parada", () => {
    const m = new Motor(7);
    m.avancar(5);
    m.deixarBola(300, 200);
    expect(m.mundo!.bolaEm(m.e.tick)).toEqual([300, 200]);
    expect(m.log.at(-1)).toEqual([m.e.tick, "db", { x: 300, y: 200 }]);
  });

  test("o db invalido falha alto, antes do registro e no replay", () => {
    const m = new Motor(7), n = m.log.length;
    expect(() => m.deixarBola(1024, 10)).toThrow(/fora do mapa/);
    expect(() => m.deixarBola(10.5, 10)).toThrow();
    expect(m.log.length).toBe(n);
    for (const ruim of [{ x: 1, y: 2, z: 3 }, { x: 1 }, null, { x: 2000, y: 1 }] as unknown[])
      expect(() => Motor.reproduzir(7, [[480, "db", ruim] as unknown as EventoRegistro])).toThrow();
  });
});
