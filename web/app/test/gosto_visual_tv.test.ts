// O cantinho da TV na ilha (src/telas/pet/ilha/cantinhoTv.ts e cantinhoTvConta.ts; o protótipo P0 do gosto visual,
// docs/futuro/gosto_visual_pet.md, seção 14). Sem DOM (vitest em node). Cobre: com a chave desligada, o cantinho não entra na vista (a
// vista só o monta atrás da chave) nem nas listas de lugares e enfeites, e a ilha fica a de hoje; com ela ligada, o chão do cantinho é
// terra plana da área nas duas ilhas (com e sem água), só a decoração baixa sai, e o pet chega à almofada por terra; a pose de cada reação;
// a ida e a volta do pet desenhado; o estado da TV que o cartão escreve e a cena lê, fora do motor e do save.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { CMU_MVP, CMU_MVP_AGUA, celulasSecas } from "../motor/index.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { LUGARES, ORDEM_LUGARES } from "../src/telas/pet/ilha/lugares.ts";
import { ENFEITES_MODELOS, LUGARES_MODELOS } from "../src/telas/pet/ilha/modelos.ts";
import { comprimento, rotaEmTerra } from "../src/telas/pet/ilha/rotaConta.ts";
import {
  ALTURA_TV, CANTINHO_TV, INCLINA_CURIOSO, IdaAoCantinho, MODELO_TV, SENTADO_TEXELS, cantinhoNaVista, poseNoCantinho, pontosDoCantinho, prepararChao,
} from "../src/telas/pet/ilha/cantinhoTvConta.ts";
import { BALAO, TV, desligarTv, publicarTv } from "../src/gostoVisual/estadoTv.ts";

const fonte = (rel: string): string => readFileSync(join(import.meta.dirname, "..", rel), "utf8");
const tudo = (i: ReturnType<typeof ilhaDe>) => JSON.stringify([i.celulas, i.objetos, i.extras, i.enfeites, i.lugares, i.caminhos, [...i.escondidos], i.pontes]);

describe("a chave desligada: a ilha de hoje", () => {
  test("sem ?gosto_visual=1 o cantinho não entra na vista", () => {
    expect(cantinhoNaVista("")).toBe(false);
    expect(cantinhoNaVista("?gosto_visual=0")).toBe(false);
    expect(cantinhoNaVista("?luta_poc=1")).toBe(false);
    expect(cantinhoNaVista("?gosto_visual=1")).toBe(true);
  });
  test("a vista só monta o cantinho atrás da chave, e só põe o grupo dele na cena se ele existe", () => {
    const v = fonte("src/telas/pet/ilha/vista.ts");
    expect(v.match(/montarCantinho\(/g)?.length).toBe(1);
    expect(v).toMatch(/this\.cantinho = cantinhoNaVista\(\) \? montarCantinho\(/);
    expect(v).toMatch(/if \(this\.cantinho\) \{\s*this\.cenaIlha\.cena\.add\(this\.cantinho\.grupo\)/);
    /* fora daí, a vista só lê o cantinho por `this.cantinho?.` ou atrás de `this.cantinho ?` / `&& this.cantinho` */
    for (const linha of v.split("\n").filter(l => /cantinho\./.test(l) && !/this\.cantinho\?\./.test(l)))
      expect(linha, linha).toMatch(/this\.cantinho \?|&& this\.cantinho|if \(this\.cantinho\)|this\.cantinho\.(carregarModelo|grupo)/);
  });
  test("o cantinho não entra nas listas de lugares nem de enfeites, e a ilha (as células, os objetos, os escondidos) sai a mesma", () => {
    expect(ORDEM_LUGARES).toEqual(["saco", "portao", "barraca"]);
    expect(Object.keys(LUGARES)).not.toContain("tv");
    expect(Object.keys(LUGARES_MODELOS)).not.toContain("tv");
    expect(Object.keys(ENFEITES_MODELOS)).not.toContain("tv");
    for (const cm of [CMU_MVP, CMU_MVP_AGUA]) {
      const a = ilhaDe(cm), b = ilhaDe(cm);
      expect(tudo(a)).toBe(tudo(b));
      expect(a.enfeites.map(e => e.nome)).not.toContain("tv");
      expect(a.lugares.map(l => l.nome).sort()).toEqual(["barraca", "cais", "portao"]);
    }
  });
});

describe("a chave ligada: o lugar", () => {
  test("o chão do cantinho é terra plana da área nas duas ilhas; só a decoração baixa sob o tapete sai da vista", () => {
    for (const cm of [CMU_MVP, CMU_MVP_AGUA]) {
      const ilha = ilhaDe(cm), antes = new Set(ilha.escondidos);
      prepararChao(ilha);
      const novos = [...ilha.escondidos].filter(i => !antes.has(i));
      const [cx, cz] = CANTINHO_TV.centro;
      for (const i of novos) {
        const o = ilha.objetos[i]!;
        expect(o.doMotor).toBeNull();
        expect(Math.hypot(o.x - cx, o.z - cz)).toBeLessThan(CANTINHO_TV.clareira);
      }
      /* as células, os lugares e os enfeites não mudam */
      const outra = ilhaDe(cm);
      expect(JSON.stringify([ilha.celulas, ilha.objetos, ilha.enfeites, ilha.lugares])).toBe(JSON.stringify([outra.celulas, outra.objetos, outra.enfeites, outra.lugares]));
    }
  });
  test("o cantinho fica longe do ninho, do saco, dos lugares e dos enfeites", () => {
    const ilha = ilhaDe(CMU_MVP_AGUA), [cx, cz] = CANTINHO_TV.centro, R = CANTINHO_TV.clareira;
    for (const e of ilha.enfeites) expect(Math.hypot(e.x - cx, e.z - cz), e.nome).toBeGreaterThan(R + 1);
    for (const l of ilha.lugares) expect(Math.hypot(l.x - cx, l.z - cz), l.nome).toBeGreaterThan(R + 1);
    expect(Math.hypot(22 - cx, 9 - cz)).toBeGreaterThan(R + 1);                 // o saco (PLANTA_ILHA.lugares.saco)
  });
  test("a almofada fica em terra, e o pet chega a ela por terra do ninho na ilha com água", () => {
    const { assento, tv } = pontosDoCantinho(), secas = celulasSecas(CMU_MVP_AGUA)!, W = CMU_MVP_AGUA.celulas_x;
    for (const p of [assento, tv]) expect(secas[Math.floor(p[1]) * W + Math.floor(p[0])]).toBe(true);
    const rota = rotaEmTerra(CMU_MVP_AGUA, [4.5, 15.5], assento);
    expect(rota[rota.length - 1]).toEqual(assento);
    expect(comprimento(rota)).toBeLessThan(20);
  });
  test("o modelo da TV do Matheus: o caminho e a altura esperados", () => {
    expect(MODELO_TV).toBe("enfeites/tv/tv.gltf");
    expect(ALTURA_TV).toBeGreaterThan(1);
  });
});

describe("a chave ligada: o pet", () => {
  test("a pose de cada reação: senta, olha para a TV, inclina no curioso, pula no adorando, vira no não curti e no enjoou", () => {
    expect(SENTADO_TEXELS).toBeGreaterThan(0);
    expect(poseNoCantinho(null, 0, false)).toEqual({ altura: SENTADO_TEXELS, angulo: 0, olhar: "tv" });
    expect(poseNoCantinho("olhando", 0, false).olhar).toBe("tv");
    expect(poseNoCantinho("curioso", 0, false)).toEqual({ altura: SENTADO_TEXELS, angulo: INCLINA_CURIOSO, olhar: "tv" });
    expect(poseNoCantinho("nao_gosta", 0, false).olhar).toBe("fora");
    expect(poseNoCantinho("enjoou", 0, false).olhar).toBe("fora");
    expect(poseNoCantinho("distraido", 0, false).olhar).toBeNull();
    const pulos = [0, 100, 200, 300, 400].map(t => poseNoCantinho("adorando", t, false).altura);
    expect(Math.max(...pulos)).toBeGreaterThan(SENTADO_TEXELS);
    /* com "reduzir movimento", sem o pulinho */
    expect([0, 100, 200, 300].map(t => poseNoCantinho("adorando", t, true).altura)).toEqual([SENTADO_TEXELS, SENTADO_TEXELS, SENTADO_TEXELS, SENTADO_TEXELS]);
  });
  test("a ida: com a TV ligada o pet anda até a almofada e senta; desligada, volta para onde o motor diz e o cantinho solta", () => {
    const { assento } = pontosDoCantinho(), ida = new IdaAoCantinho(assento, () => null), motor: [number, number] = [4.5, 15.5];
    expect(ida.passo(0, motor, motor, false, false)).toEqual({ cel: motor, andando: false, sentado: false, ativo: false });
    const meio = ida.passo(0, motor, motor, true, false);
    expect(meio.ativo && meio.andando && !meio.sentado).toBe(true);
    const chegou = ida.passo(60_000, motor, motor, true, false);
    expect(chegou).toEqual({ cel: assento, andando: false, sentado: true, ativo: true });
    const volta = ida.passo(60_001, assento, motor, false, false);
    expect(volta.ativo && volta.andando).toBe(true);
    expect(ida.passo(120_000, assento, motor, false, false)).toEqual({ cel: motor, andando: false, sentado: false, ativo: false });
    /* com "reduzir movimento", chega na hora */
    expect(new IdaAoCantinho(assento, () => null).passo(0, motor, motor, true, true).sentado).toBe(true);
  });
});

describe("o estado da TV (o cartão escreve, a cena lê)", () => {
  test("ligar, sentir e desligar; nada do motor, do log nem do save", () => {
    desligarTv();
    const v0 = TV.versao;
    publicarTv({ ligada: true, origem: "jogo" });
    publicarTv({ programa: "planilha", reacao: "curioso" });
    expect([TV.ligada, TV.origem, TV.programa, TV.reacao, TV.versao]).toEqual([true, "jogo", "planilha", "curioso", v0 + 2]);
    expect(BALAO[TV.reacao!]).toBe("? o que é isso");
    desligarTv();
    expect([TV.ligada, TV.origem, TV.programa, TV.reacao, TV.sentido, TV.video]).toEqual([false, null, null, null, null, null]);
    for (const f of ["src/gostoVisual/estadoTv.ts", "src/telas/pet/ilha/cantinhoTv.ts", "src/telas/pet/ilha/cantinhoTvConta.ts"])
      expect(fonte(f), f).not.toMatch(/mudarMotor|aplicarEvento|trocarMotor|save\.ts|localStorage/);
  });
});
