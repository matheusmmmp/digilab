/* Os gates do PR 1 do WORLD-POC-01a (docs/TAREFA_V2_WORLD_POC_01.md, seção 4, etapas E0 a E2): o mundo do POC sem a vista.
     G-FRONTEIRA  só a vista importa o three; o POC não importa o jogo nem o motor do jogo, e o contrário também não
     G-COLISAO    o círculo não atravessa parede nem canto, desliza, e a bola rápida não atravessa
     G-BOLA       o empurrão, o atrito e a reflexão
     G-NAVEGA     o pet chega ao alvo em todos os cenários com os dois obstáculos (a M4)
     G-SENSOR     o obstáculo alto tapa e o baixo não; nada fora do cone; nenhuma posição absoluta na Observação
     G-CONTRATO   o cérebro de teste só importa o contrato
     G-DET        a mesma semente e o mesmo log dão o mesmo estado, e o replay refaz a vida (a primeira metade da M5) */
import { describe, expect, test } from "vitest";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { ATRITO_BOLA, IMPULSO_BOLA, R_PET, SUB } from "../poc/mundo3d/config.ts";
import { Controlador, caminho, grade } from "../poc/mundo3d/controlador.ts";
import { bloqueioEm, mover, passoBola, type Solido } from "../poc/mundo3d/fisica.ts";
import { Rng, distancia } from "../poc/mundo3d/inteiros.ts";
import { Mundo, centroDaCelula } from "../poc/mundo3d/mundo.ts";
import { ler, type AlvoMundo } from "../poc/mundo3d/sensores.ts";
import { Simulacao, reproduzir } from "../poc/mundo3d/simulacao.ts";
import { conferirSprite } from "../poc/mundo3d/sprite_reserva.ts";

const APP = fileURLToPath(new URL("..", import.meta.url));
const POC = join(APP, "poc", "mundo3d");

function arquivos(dir: string, ext: RegExp): string[] {
  const out: string[] = [];
  for (const n of readdirSync(dir)) {
    const c = join(dir, n);
    if (statSync(c).isDirectory()) out.push(...arquivos(c, ext));
    else if (ext.test(n)) out.push(c);
  }
  return out;
}
const semComentarios = (f: string) => readFileSync(f, "utf8").replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, "");
const importacoes = (f: string) => [...semComentarios(f).matchAll(/(?:from|import)\s*\(?\s*["']([^"']+)["']/g)].map(m => m[1]);

describe("G-FRONTEIRA: o POC fica de fora do jogo, e só a vista conhece a engine", () => {
  test("nenhum arquivo do POC, tirando a vista, importa o three", () => {
    for (const f of arquivos(POC, /\.ts$/)) {
      if (f.endsWith("vista.ts")) continue;
      expect(importacoes(f).filter(i => i === "three" || i.startsWith("three/")), f).toEqual([]);
    }
  });

  test("o POC só importa a si mesmo e, do motor, o corpo.ts e o que ele importa (CP-6, POC-02); o motor e as telas não importam o POC", () => {
    /* o fecho do corpo.ts no motor: os arquivos que ele importa, e os que esses importam */
    const fecho = new Set<string>();
    const visitar = (arq: string) => {
      if (fecho.has(arq)) return;
      fecho.add(arq);
      for (const i of importacoes(join(APP, "motor", arq))) if (i.startsWith("./")) visitar(i.slice(2));
    };
    visitar("corpo.ts");
    for (const f of arquivos(POC, /\.ts$/)) {
      for (const i of importacoes(f)) {
        const doMotor = i.startsWith("../../motor/") && fecho.has(i.slice("../../motor/".length));
        expect(i === "three" || i.startsWith("./") || doMotor, `${f}: ${i}`).toBe(true);
      }
    }
    for (const dir of ["motor", "src"]) for (const f of arquivos(join(APP, dir), /\.tsx?$/)) {
      expect(importacoes(f).some(i => i.includes("poc/")), f).toBe(false);
    }
  });

  test("o build do app não vê o POC, e o three tem versão exata", () => {
    expect(readFileSync(join(APP, "vite.config.ts"), "utf8")).not.toMatch(/poc/);
    expect(readFileSync(join(APP, "index.html"), "utf8")).not.toMatch(/poc/);
    const pkg = JSON.parse(readFileSync(join(APP, "package.json"), "utf8"));
    expect(pkg.dependencies.three).toMatch(/^\d+\.\d+\.\d+$/);
  });

  test("o mundo do POC não usa o DOM (só a página e a vista)", () => {
    for (const f of arquivos(POC, /\.ts$/)) {
      if (f.endsWith("pagina.ts") || f.endsWith("vista.ts")) continue;
      expect(semComentarios(f), f).not.toMatch(/\b(document|window|HTMLElement|requestAnimationFrame)\b/);
    }
  });

  test("o sprite de reserva é 16 x 16 e só usa a paleta", () => {
    expect(() => conferirSprite()).not.toThrow();
    expect(() => conferirSprite(["x".repeat(16)])).toThrow();
  });
});

const mundoNovo = () => new Mundo(new Rng(1));
const algumSolido = (x: number, y: number, r: number, s: readonly Solido[]) => bloqueioEm(x, y, r, s, []) !== null;

describe("G-COLISAO: o círculo contra a parede", () => {
  test("andando para a parede, o pet para encostado e nunca a invade", () => {
    const m = mundoNovo();
    const c = { x: 40, y: 100, r: R_PET };
    for (let t = 0; t < 30; t++) {
      const mv = mover(c, -4, 0, m.solidos, []);
      c.x = mv.x; c.y = mv.y;
      expect(algumSolido(c.x, c.y, c.r, m.solidos)).toBe(false);
    }
    expect([c.x, c.y]).toEqual([R_PET, 100]);
  });

  test("no canto, para encostado nas duas paredes", () => {
    const m = mundoNovo();
    const c = { x: 40, y: 40, r: R_PET };
    for (let t = 0; t < 30; t++) {
      const mv = mover(c, -4, -4, m.solidos, []);
      c.x = mv.x; c.y = mv.y;
      expect(algumSolido(c.x, c.y, c.r, m.solidos)).toBe(false);
    }
    expect([c.x, c.y]).toEqual([R_PET, R_PET]);
  });

  test("em diagonal contra a parede, desliza pelo outro eixo", () => {
    const m = mundoNovo();
    const c = { x: R_PET, y: 100, r: R_PET };
    const mv = mover(c, -4, 3, m.solidos, []);
    expect([mv.x, mv.y]).toEqual([R_PET, 103]);
    expect(mv.bloqueioX).not.toBeNull();
    expect(mv.bloqueioY).toBeNull();
  });

  test("a bola rápida não atravessa uma parede fina", () => {
    const fina: Solido[] = [{ ret: { x0: 100, y0: 0, x1: 102, y1: 200 }, categoria: "parede", alto: true }];
    const b = { x: 60, y: 50, r: 4, vx: 40, vy: 0 };
    for (let t = 0; t < 20; t++) {
      passoBola(b, fina, []);
      expect(b.x).toBeLessThan(100);
      expect(algumSolido(b.x, b.y, b.r, fina)).toBe(false);
    }
  });
});

describe("G-BOLA: o empurrão, o atrito e a reflexão", () => {
  test("o pet que anda contra a bola a empurra na direção do contato, com o impulso", () => {
    const m = mundoNovo();
    m.bola.x = 100; m.bola.y = 160; m.pet.x = 100 - R_PET - m.bola.r; m.pet.y = 160;   // num lugar livre da sala
    m.passo(4, 0, null);
    expect(m.empurroes).toBe(1);
    expect(m.bola.vy).toBe(0);
    expect(m.bola.vx).toBe(IMPULSO_BOLA - ATRITO_BOLA);    // o impulso, depois do atrito do tick
    expect(m.bola.x).toBeGreaterThan(100);
  });

  test("solta, a bola anda 10 + 9 + ... + 1 = 55 subunidades e para", () => {
    const b = { x: 40, y: 100, r: 4, vx: 10, vy: 0 };
    for (let t = 0; t < 30; t++) passoBola(b, [], []);
    expect([b.x, b.vx, b.vy]).toEqual([95, 0, 0]);
  });

  test("contra a parede, reflete com a restituição e perde velocidade", () => {
    const m = mundoNovo();
    const b = { x: 256 - 4 - 3, y: 100, r: 4, vx: 8, vy: 0 };
    passoBola(b, m.solidos, []);
    expect(b.vx).toBeLessThan(0);
    expect(Math.abs(b.vx)).toBeLessThan(8);
    for (let t = 0; t < 40; t++) { passoBola(b, m.solidos, []); expect(algumSolido(b.x, b.y, b.r, m.solidos)).toBe(false); }
    expect(b.vx).toBe(0);
  });
});

/** roda o controlador até ele parar (ou estourar), com o mundo andando */
function executar(m: Mundo, ctl: Controlador, maximo = 400): number {
  let t = 0;
  while (ctl.status === null && t < maximo) {
    const c = ctl.passo(m);
    m.passo(c.vx, c.vy, c.podeComer);
    t++;
  }
  return t;
}

describe("G-NAVEGA (M4): o pet chega à comida contornando os obstáculos", () => {
  const cenarios: [string, [number, number], [number, number]][] = [
    ["atrás do obstáculo alto", [3, 5], [8, 5]],
    ["do outro lado do alto, pelo alto", [6, 1], [6, 8]],
    ["atrás do obstáculo baixo", [9, 7], [13, 7]],
    ["de canto a canto", [1, 1], [14, 10]],
    ["do fundo para a frente", [13, 1], [2, 10]],
    ["colado na parede", [0, 6], [15, 6]],
  ];
  for (const [nome, de, para] of cenarios) {
    test(nome, () => {
      const m = mundoNovo();
      [m.pet.x, m.pet.y] = centroDaCelula(...de);
      m.comidas = [];
      m.deixarComida(...centroDaCelula(...para));
      const id = m.comidas[0].id;
      const refs = new Map<number, AlvoMundo>([[1, { tipo: "comida", id }]]);
      const ctl = new Controlador({ tipo: "consumir", ref: 1 }, refs, m);
      const t = executar(m, ctl);
      expect(ctl.status, `${nome}: parou em ${t} ticks`).toBe("chegou");
      m.passo(0, 0, null);
      expect(m.comeu).toBe(1);
      expect(m.comidas[0].ativa).toBe(false);
    });
  }

  test("o A* contorna e não corta canto; sem caminho, devolve null", () => {
    const m = mundoNovo();
    const g = grade(m);
    const cam = caminho(g, [3, 5], [8, 5])!;
    expect(cam[0]).toEqual([3, 5]);
    expect(cam[cam.length - 1]).toEqual([8, 5]);
    for (const [cx, cy] of cam) expect(g[cy * 16 + cx]).toBe(true);
    expect(caminho(g, [3, 5], [5, 4])).toBeNull();   // a célula dentro do obstáculo alto
  });
});

describe("G-SENSOR: o que o pet sente", () => {
  function comPet(cel: [number, number], orientacao: number, comida: [number, number]): Mundo {
    const m = mundoNovo();
    [m.pet.x, m.pet.y] = centroDaCelula(...cel);
    m.pet.orientacao = orientacao;
    m.comidas = [];
    m.deixarComida(...centroDaCelula(...comida));
    m.bola.x = 250; m.bola.y = 5;   // a bola longe
    return m;
  }
  const comidaVista = (m: Mundo) => ler(m, null).obs.vistos.some(v => v.categoria === "comida");

  test("o obstáculo alto tapa a comida atrás dele; o baixo não", () => {
    expect(comidaVista(comPet([3, 5], 0, [8, 5]))).toBe(false);
    expect(comidaVista(comPet([3, 5], 0, [4, 9]))).toBe(false);    // fora do cone, de lado
    expect(comidaVista(comPet([9, 7], 0, [13, 7]))).toBe(true);    // o baixo no meio
  });

  test("nada fora do cone: a comida atrás do pet não aparece, e de frente aparece", () => {
    expect(comidaVista(comPet([8, 9], 8, [12, 9]))).toBe(false);   // olhando para oeste, a comida a leste
    expect(comidaVista(comPet([8, 9], 0, [12, 9]))).toBe(true);
  });

  test("a Observação não traz posição absoluta; a distância e o setor são relativos", () => {
    const m = comPet([9, 7], 0, [13, 7]);
    const { obs } = ler(m, null);
    const chaves = (o: unknown): string[] => o && typeof o === "object"
      ? Object.entries(o).flatMap(([k, v]) => [k, ...chaves(v)]) : [];
    expect(chaves(obs).filter(k => ["x", "y", "pos", "posicao", "id"].includes(k))).toEqual([]);
    const v = obs.vistos.find(k => k.categoria === "comida")!;
    expect(v.distancia).toBe(4 * SUB);
    expect(v.setor).toBe(0);
  });

  test("os bigodes: encostado na parede oeste e olhando para ela, o bigode da frente é 0 e o de trás é o raio", () => {
    const m = mundoNovo();
    m.pet.x = R_PET; m.pet.y = 100; m.pet.orientacao = 8;
    const { obs } = ler(m, null);
    expect(obs.obstaculos[0]).toBe(0);
    expect(obs.obstaculos[4]).toBe(2 * SUB);
  });

  test("o contato: andar contra a parede deixa o contato na frente, e a leitura o consome", () => {
    const m = mundoNovo();
    m.pet.x = R_PET + 1; m.pet.y = 100;
    m.passo(-4, 0, null);
    const { obs } = ler(m, null);
    expect(obs.contato).toEqual([{ categoria: "parede", setor: 0 }]);
    expect(ler(m, null).obs.contato).toEqual([]);
  });
});

describe("G-CONTRATO: o cérebro só conhece o contrato", () => {
  test("o cerebro.ts só importa ./tipos.ts", () => {
    expect(importacoes(join(POC, "cerebro.ts"))).toEqual(["./tipos.ts"]);
  });

  test("o tipos.ts não importa nada", () => {
    expect(importacoes(join(POC, "tipos.ts"))).toEqual([]);
  });
});

describe("G-DET: o determinismo e o replay", () => {
  const vida = (semente: number) => {
    const s = new Simulacao(semente);
    s.avancar(700);
    s.aplicarEvento({ tipo: "deixar_comida", x: 40, y: 40 });
    s.avancar(800);
    return s;
  };

  test("a mesma semente dá o mesmo estado e os mesmos registros, duas vezes", () => {
    const a = vida(101), b = vida(101);
    expect(a.hash()).toBe(b.hash());
    expect(JSON.stringify(a.estado())).toBe(JSON.stringify(b.estado()));
    expect(JSON.stringify(a.registros)).toBe(JSON.stringify(b.registros));
  });

  test("o replay pelo log refaz a vida", () => {
    const a = vida(202);
    const r = reproduzir(202, a.log);
    expect(r.hash()).toBe(a.hash());
    expect(JSON.stringify(r.registros)).toBe(JSON.stringify(a.registros));
  });

  test("controle negativo: outra semente dá outra vida", () => {
    expect(vida(101).hash()).not.toBe(vida(303).hash());
  });

  test("um evento desconhecido falha alto", () => {
    const s = new Simulacao(101);
    expect(() => s.aplicarEvento({ tipo: "voar" } as never)).toThrow(/desconhecido/);
  });
});

describe("a física produz resultados observáveis, no laço inteiro com o cérebro de teste", () => {
  test("em 1.500 ticks o pet come, empurra a bola, e o registro mostra quanto a bola andou", () => {
    const s = vida101();
    const r = s.registros;
    expect(r.length).toBe(99);    // 100 decisões abertas; a última ainda está em curso no tick 1.500
    const comeu = r.filter(x => x.intencao.tipo === "consumir" && x.fisico.comeu > 0);
    const empurrou = r.filter(x => x.intencao.tipo === "empurrar" && x.fisico.empurroes > 0);
    expect(comeu.length).toBeGreaterThan(0);
    expect(empurrou.length).toBeGreaterThan(0);
    const andou = empurrou.map(x => distancia(x.fisico.bola_para[0] - x.fisico.bola_de[0], x.fisico.bola_para[1] - x.fisico.bola_de[1]));
    expect(Math.max(...andou)).toBeGreaterThan(0);
    /* o resultado percebido chega na Observação seguinte */
    for (let i = 1; i < r.length; i++) expect(r[i].observacao.resultado).toEqual(r[i - 1].percebido);
  });
});

function vida101(): Simulacao {
  const s = new Simulacao(101);
  s.avancar(1500);
  return s;
}
