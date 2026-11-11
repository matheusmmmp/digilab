// O cantinho da TV na ilha (src/telas/pet/ilha/cantinhoTv.ts e cantinhoTvConta.ts; o protótipo P0 do gosto visual,
// docs/futuro/gosto_visual_pet.md, seção 14), em volta da TV de tubo do #814 (o enfeite "tv"). Sem DOM (vitest em node). Cobre: com a chave
// desligada, o cantinho não entra na vista (a vista só o monta atrás da chave) nem nas listas de lugares e enfeites, e a ilha fica a do #814
// (a TV como o marco dela, uma só); com ela ligada, o cantinho fica na frente da TV, em terra plana da área nas duas ilhas (com e sem água),
// sem criar outra TV, só a decoração baixa sai, e o pet chega à almofada por terra; a pose de cada reação; a ida e a volta do pet desenhado;
// o estado da TV que o cartão escreve e a cena lê, fora do motor e do save.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { CMU_MVP, CMU_MVP_AGUA, celulasSecas } from "../motor/index.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { LUGARES, ORDEM_LUGARES } from "../src/telas/pet/ilha/lugares.ts";
import { ENFEITES_MODELOS, LUGARES_MODELOS } from "../src/telas/pet/ilha/modelos.ts";
import { comprimento, rotaEmTerra } from "../src/telas/pet/ilha/rotaConta.ts";
import {
  CANTINHO_TV, INCLINA_CURIOSO, IdaAoCantinho, SENTADO_TEXELS, TELA_DO_MODELO, cantinhoNaVista, poseNoCantinho, pontosDoCantinho, prepararChao, tvDaIlha,
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
      expect(linha, linha).toMatch(/this\.cantinho \?|&& this\.cantinho|if \(this\.cantinho\)|this\.cantinho\.(carregarTela|grupo|quadro)/);
  });
  test("o cantinho não entra nas listas de lugares nem de enfeites, e a ilha (as células, os objetos, a TV do #814, os escondidos) sai a mesma", () => {
    expect(ORDEM_LUGARES).toEqual(["saco", "portao", "barraca"]);
    expect(Object.keys(LUGARES)).not.toContain("tv");
    expect(Object.keys(LUGARES_MODELOS)).not.toContain("tv");
    /* a TV é o enfeite do #814 (o mesmo modelo), uma só em cada ilha; nada do cantinho vira enfeite */
    expect(ENFEITES_MODELOS.tv.arquivos).toEqual(["tv/tv.gltf"]);
    for (const cm of [CMU_MVP, CMU_MVP_AGUA]) {
      const a = ilhaDe(cm), b = ilhaDe(cm);
      expect(tudo(a)).toBe(tudo(b));
      expect(a.enfeites.filter(e => e.nome === "tv")).toHaveLength(1);
      expect(a.enfeites.map(e => e.nome).sort()).toEqual(Object.keys(ENFEITES_MODELOS).filter(n => n !== "poste").concat(Array(a.enfeites.filter(e => e.nome === "poste").length).fill("poste")).sort());
      expect(a.lugares.map(l => l.nome).sort()).toEqual(["barraca", "cais", "portao"]);
    }
    /* o cantinho não desenha TV própria: nenhuma geometria de caixa nem glTF de TV novo, só o plano da tela sobre a do #814 */
    const c = fonte("src/telas/pet/ilha/cantinhoTv.ts");
    expect(c).not.toMatch(/RoundedBoxGeometry|BoxGeometry/);
    expect(c).toMatch(/ENFEITES_MODELOS\.tv/);
  });
});

describe("a chave ligada: o lugar", () => {
  for (const cm of [CMU_MVP, CMU_MVP_AGUA]) test(`na frente da TV do #814, em terra plana da área, e só a decoração baixa sob o tapete sai da vista (${cm.layout.nome})`, () => {
    const ilha = ilhaDe(cm), antes = new Set(ilha.escondidos), t = tvDaIlha(ilha), p = pontosDoCantinho(ilha);
    expect([p.tv, p.giro]).toEqual([[t.x, t.z], t.giro]);
    /* a almofada fica na frente da tela (+z do glTF girado), a pelo menos a distância pedida */
    const f = [Math.sin(t.giro), Math.cos(t.giro)], frente = (p.assento[0] - t.x) * f[0]! + (p.assento[1] - t.z) * f[1]!;
    expect(frente).toBeGreaterThanOrEqual(CANTINHO_TV.assento.frente - 1e-9);
    for (const q of [p.assento, p.dono, p.tapete]) {
      const c = ilha.cel(Math.floor(q[0]), Math.floor(q[1]))!;
      expect([c.tipo !== "agua", c.nivel, ilha.naArea(q[0], q[1])]).toEqual([true, 0, true]);
    }
    prepararChao(ilha, p);
    for (const i of [...ilha.escondidos].filter(i => !antes.has(i))) expect(ilha.objetos[i]!.doMotor).toBeNull();
    /* as células, os objetos, os lugares e os enfeites (a TV inclusive) não mudam */
    const outra = ilhaDe(cm);
    expect(JSON.stringify([ilha.celulas, ilha.objetos, ilha.enfeites, ilha.lugares])).toBe(JSON.stringify([outra.celulas, outra.objetos, outra.enfeites, outra.lugares]));
  });
  test("a almofada fica em terra, e o pet chega a ela por terra do ninho na ilha com água", () => {
    const ilha = ilhaDe(CMU_MVP_AGUA), { assento } = pontosDoCantinho(ilha), secas = celulasSecas(CMU_MVP_AGUA)!, W = CMU_MVP_AGUA.celulas_x;
    expect(secas[Math.floor(assento[1]) * W + Math.floor(assento[0])]).toBe(true);
    const rota = rotaEmTerra(CMU_MVP_AGUA, [4.5, 15.5], assento);
    expect(rota[rota.length - 1]).toEqual(assento);
    expect(comprimento(rota)).toBeLessThan(80);
  });
  test("a tela no modelo: dentro da caixa do glTF da TV, na frente", () => {
    const g = JSON.parse(fonte("public/enfeites/tv/tv.gltf")) as { accessors: { min?: number[]; max?: number[] }[] };
    const cx = g.accessors.find(a => a.min?.length === 3)!, S = TELA_DO_MODELO;
    expect(S.x - S.rx).toBeGreaterThan(cx.min![0]!); expect(S.x + S.rx).toBeLessThan(cx.max![0]!);
    expect(S.y - S.ry).toBeGreaterThan(cx.min![1]!); expect(S.y + S.ry).toBeLessThan(cx.max![1]!);
    expect(S.z).toBeGreaterThan(0); expect(S.z).toBeLessThan(cx.max![2]!);
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
    const { assento } = pontosDoCantinho(ilhaDe(CMU_MVP_AGUA)), ida = new IdaAoCantinho(assento, () => null), motor: [number, number] = [4.5, 15.5];
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
