/* GOSTO_VISUAL, a TV no jogo (as decisoes A a E da captura ligada ao cerebro; "Sim a tudo", Matheus, 2026-11-12; docs/registro/2026-11.md,
   D-GV-TVJOGO): a v33 (o ovo novo de um pet so: a v32 com a TV desligada, o ir ate a TV e o enjoo da imagem) e a v34 (o ovo do brasao: a v29
   com a TV no cerebro e no jogo). Confere, no motor do jogo:
     - as versoes e as chaves de cada uma; os pets de antes (v27, v29, v32) seguem sem nada novo (o gabarito tv_jogo_etapa0_ts confere os
       saves deles, byte a byte);
     - o G2 da v33: sem nenhum "st", a vida e a da v32 (as decisoes, o estado, a posicao e o registro);
     - A: a TV desligada nao e vista nem olhada, so na v33 e na v34; parar a TV do P0 grava a TV desligada;
     - D: o pet da v33 vai ate a TV sozinho, longe dela, e depois a olha;
     - E: o enjoo ligado no jogo: uma imagem parada cansa o pet da v33 (o enjoo lido sobe a cada olhar), e a v32 segue sem o enjoo;
     - B: o grupo v34 ve a mesma TV, pelo "st" do grupo, e o replay e o save refazem tudo; o pet do grupo nao grava o "st" sozinho. */
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import {
  CELULA_PERTO_DA_TV_JOGO, CONFIG_TVJOGO_LIGADA, GrupoDoJogo, Motor, ResumoTela, VERSAO_GRUPO, VERSAO_PET, centroDaCelula, distancia,
  nasceComTv, nasceComTvJogo, valorSentidoTela, type EventoRegistro, type MotorCorpoMundo,
} from "../motor/index.ts";
import { CMU_GRANDE } from "../motor/constantes.ts";
import { CONFIG_ENJOO_TELA_LIGADA } from "../motor/enjoo_tela.ts";
import { ligarProduto } from "../src/produto.ts";
import { CHAVE, lerSave, textoSave } from "../src/save.ts";
import { iniciarJogo, jogoAtual } from "../src/jogo.ts";
import { comecarNoCerebro, leituraDoCerebro, pararNoCerebro, sentirNoCerebro } from "../src/gostoVisual/cerebroTv.ts";

type Dict = Record<string, any>;
const laco = (m: Motor): MotorCorpoMundo => m.v11!.laco as MotorCorpoMundo;
const ovo = (semente: number, versao: number): Motor => ligarProduto(new Motor(semente, versao));
function cuidar(m: Motor, horas: number, cada?: (m: Motor, h: number) => void): void {
  for (let h = 1; h <= horas; h++) {
    m.avancar(60);
    if (h % 3 === 0) m.observar("alimentar");
    if (h % 5 === 0 && !m.e.dormindo) m.observar("acariciar");
    if (h % 8 === 0) m.observar("limpar");
    cada?.(m, h);
  }
}
const amostra = (h: number, s: number): number[] => [0, 1, 2, 3, 4, 5, 6].map(k => ((h * 7 + k * 3 + (s % 5)) % 11) / 10);
const perto = (): [number, number] => centroDaCelula(CELULA_PERTO_DA_TV_JOGO, CMU_GRANDE);
const motivos = (m: Motor): Dict[] => m.lab!.motivos as Dict[];
const dTv = (m: Motor): number => { const l = laco(m), tv = l.tv!; return distancia(tv.x - l.mundo.pet[0], tv.y - l.mundo.pet[1]); };

describe("as versoes: a v33 e a v34", () => {
  test("o ovo novo de um pet so nasce v33 e o do brasao v34; as chaves da TV no jogo so nelas", () => {
    expect([VERSAO_PET, VERSAO_GRUPO]).toEqual([33, 34]);
    expect([27, 29, 32, 33, 34].map(nasceComTv)).toEqual([false, false, true, true, true]);
    expect([27, 29, 32, 33, 34].map(nasceComTvJogo)).toEqual([false, false, false, true, true]);
    const m = new Motor(1);
    expect(laco(m).tvJogo).toEqual(CONFIG_TVJOGO_LIGADA);
    expect(laco(m).corpo.enjooCfg).toEqual(CONFIG_ENJOO_TELA_LIGADA);
    expect(laco(new Motor(1, 32)).tvJogo.desligar).toBe(false);
    const g = new GrupoDoJogo(101, VERSAO_GRUPO);
    expect(g.temTv).toBe(true);
    expect(laco(g.motor("A")).tv).toBe(laco(g.motor("B")).tv);                 // uma TV so, do mundo comum
    expect(laco(g.motor("A")).tv).toBe(g.grupo.comum.tv);
    expect(new GrupoDoJogo(101, 29).temTv).toBe(false);
  });

  test("G2: sem nenhum \"st\", a vida da v33 e a da v32 (o registro, as decisoes, o estado e a posicao), sementes 101 e 202, 2 dias", () => {
    for (const s of [101, 202]) {
      const a = ovo(s, 32), b = ovo(s, 33);
      cuidar(a, 48); cuidar(b, 48);
      expect(b.log).toEqual(a.log);
      expect(motivos(b).map(x => x["escolha"])).toEqual(motivos(a).map(x => x["escolha"]));
      expect(motivos(b).map(x => x["u"])).toEqual(motivos(a).map(x => x["u"]));
      expect(b.e).toEqual(a.e);
      expect(laco(b).mundo.pet).toEqual(laco(a).mundo.pet);
      expect(motivos(b).every(x => x["acao"] !== "ir_tv")).toBe(true);
    }
  });
});

describe("A: a TV desligada", () => {
  test("a TV desligada nao e vista nem olhada; o proximo \"st\" religa; o replay e o save refazem", () => {
    const m = ovo(202, 33);
    cuidar(m, 2);
    if (!m.e.dormindo) m.levarPet(...perto());
    m.sentidoTela(valorSentidoTela("tv", [9, 9, 9, 9, 3, 3, 3]));
    expect(laco(m).tv!.em(laco(m).mundo.tm(m.e.tick))).not.toBeNull();
    m.sentidoTela("tv|desligada");
    expect(m.ultimoSentidoTela).toBe("tv|desligada");
    expect(laco(m).tv!.em(laco(m).mundo.tm(m.e.tick))).toBeNull();
    const k0 = motivos(m).length;
    for (let h = 0; h < 6; h++) { if (!m.e.dormindo) m.levarPet(...perto()); m.avancar(60); }
    const depois = motivos(m).slice(k0);
    expect(depois.length).toBeGreaterThan(10);
    expect(depois.every(x => x["olhar"]["telas"].length === 0 && x["olhar"]["olha"] === null && x["acao"] !== "ir_tv")).toBe(true);
    expect(m.tvNoCerebro()!.olhando).toBe(false);
    m.sentidoTela(valorSentidoTela("tv", [9, 9, 9, 9, 3, 3, 3]));
    expect(laco(m).tv!.em(laco(m).mundo.tm(m.e.tick))).not.toBeNull();
    const r = Motor.reproduzir(202, JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], 33);
    expect(r.assinatura()).toBe(m.assinatura());
    const mapa = new Map<string, string>(), arm = { getItem: (k: string) => mapa.get(k) ?? null, setItem: (k: string, v: string) => { mapa.set(k, v); } };
    arm.setItem(CHAVE, textoSave(m));
    const l = lerSave(arm);
    if (l.tipo !== "ok") throw new Error("o save nao abriu");
    expect(l.motor.assinatura()).toBe(m.assinatura());
  });

  test("so a v33 e a v34 desligam a TV: a v32 recusa, e a forma canonica falha alto antes do registro", () => {
    const v32 = ovo(101, 32), n = v32.log.length;
    expect(() => v32.sentidoTela("tv|desligada")).toThrow(/v33/);
    expect(v32.log.length).toBe(n);
    const m = ovo(101, 33), k = m.log.length;
    expect(() => m.sentidoTela("tv|desligado")).toThrow(/malformado/);
    expect(() => m.sentidoTela("radio|desligada")).toThrow(/malformado/);
    expect(m.log.length).toBe(k);
  });
});

describe("D: o pet vai ate a TV sozinho", () => {
  test("longe da TV (fora do raio da visao), o pet da v33 vai ate ela pelo ir_tv do modular e depois a olha; o replay confere", () => {
    for (const s of [101, 202, 303]) {
      const m = ovo(s, 33);
      cuidar(m, 1);
      const [x, y] = perto();
      m.levarPet(x + 10 * CMU_GRANDE.sub, y);                 // 12 celulas da TV: fora do raio (6)
      const d0 = dTv(m);
      expect(d0).toBeGreaterThan(laco(m).mundo.raioDaVisao);
      const k0 = motivos(m).length;
      let r = new ResumoTela("tv"), foi = false, olhou = false, dMin = d0;
      for (let h = 0; h < 30 && !(foi && olhou); h++) {
        for (let k = 0; k < 30; k++) { const v = r.amostra(amostra(h, s + k)); if (v !== null) m.sentidoTela(v); }
        m.avancar(60);
        if (h % 3 === 2) m.observar("alimentar");
        dMin = Math.min(dMin, dTv(m));
        const novos = motivos(m).slice(k0);
        foi ||= novos.some(x => x["acao"] === "ir_tv");
        olhou ||= novos.some(x => x["olhar"]["olha"] === 1);
      }
      expect([s, foi, olhou]).toEqual([s, true, true]);
      expect(dMin).toBeLessThanOrEqual(laco(m).mundo.raioDaVisao);
      const ida = motivos(m).slice(k0).find(x => x["acao"] === "ir_tv")!;
      expect(ida["escolha"][0]).toBe("olhar");
      expect(ida["olhar"]["olha"]).toBeNull();
      expect(laco(m).mundo.decisoes.some(d => d["acao"] === "ir_tv" && d["alvo"] === "tv")).toBe(true);
      expect(Motor.reproduzir(s, JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], 33).assinatura()).toBe(m.assinatura());
    }
  });

  test("o painel le o ir ate a TV: \"No cerebro: indo ate a TV.\"", () => {
    const m = ovo(101, 33);
    const k = (m.lab!.motivos as Dict[]);
    cuidar(m, 1);
    m.levarPet(perto()[0] + 10 * CMU_GRANDE.sub, perto()[1]);
    m.sentidoTela(valorSentidoTela("tv", [9, 9, 9, 9, 3, 3, 3]));
    let achou = false;
    for (let t = 0; t < 40 * 60 && !achou; t++) {
      m.avancar(1);
      if (k.length && k[k.length - 1]!["acao"] === "ir_tv" && !m.e.dormindo) {
        expect(leituraDoCerebro(m)!.frase).toBe("No cérebro: indo até a TV.");
        expect(leituraDoCerebro(m)!.indo).toBe(true);
        achou = true;
      }
    }
    expect(achou).toBe(true);
  });
});

describe("E: o enjoo ligado no jogo", () => {
  /** o pet perto da TV a cada 2 h, com uma imagem parada (os mesmos sete niveis) */
  function parada(s: number, versao: number, horas: number): Motor {
    const m = ovo(s, versao);
    cuidar(m, horas, (mm, h) => { if (h % 2 === 0 && !mm.e.dormindo) mm.levarPet(...perto()); if (h === 1) mm.sentidoTela(valorSentidoTela("tv", [10, 6, 2, 8, 5, 5, 5])); });
    return m;
  }
  test("uma imagem parada cansa o pet da v33: o enjoo lido em cada olhar sobe; a v32 nao tem o enjoo", () => {
    let comEnjoo = 0;
    for (const s of [101, 202, 303]) {
      const m = parada(s, 33, 72);
      /* o enjoo lido no corpo depois de cada olhar (a consequencia da opcao de olhar, D-GV-ENJOO-CER-4) */
      const lidos = motivos(m).map(x => x["consequencia"]?.["olhar"]?.["enjoo"] as number | null | undefined).filter((e): e is number => typeof e === "number");
      expect(lidos.length).toBeGreaterThan(2);
      expect(Math.max(...lidos)).toBeGreaterThan(lidos[0]!);
      if (Math.max(...lidos) >= 512) comEnjoo++;
      expect("memoria" in (laco(m).corpo.paraDict()["tela"] as Dict)).toBe(true);     // a memoria do enjoo no corpo (D-GV-ENJOO-CER-3)
      const v32 = parada(s, 32, 24);
      expect(motivos(v32).every(x => !("enjoo" in x["olhar"]) && !(x["consequencia"]?.["olhar"] && "enjoo" in x["consequencia"]["olhar"]))).toBe(true);
    }
    expect(comEnjoo).toBeGreaterThan(0);
  });
});

describe("B: a TV no grupo v34", () => {
  test("o \"st\" do grupo e da TV do mundo comum: os dois pets veem a mesma TV; o replay e o save refazem; o pet nao grava o \"st\" sozinho", () => {
    const g = new GrupoDoJogo(303, 34);
    for (const i of g.ids) g.agir(i, m => ligarProduto(m));
    let r = new ResumoTela("tv");
    for (let h = 1; h <= 30; h++) {
      g.avancar(60);
      for (const i of g.ids) g.agir(i, m => { if (h % 3 === 0) m.observar("alimentar"); if (h % 4 === 0 && !m.e.dormindo) m.levarPet(...perto()); });
      if (h === 20) { g.sentidoTela("tv|desligada"); r = new ResumoTela("tv"); continue; }
      for (let k = 0; k < 20; k++) { const v = r.amostra(amostra(Math.floor(h / 3), 3 + k)); if (v !== null) g.sentidoTela(v); }
    }
    const st = g.log.filter(e => e[1] === "st");
    expect(st.length).toBeGreaterThan(3);
    expect(st.every(e => e[3] === null)).toBe(true);
    expect(g.ultimoSentidoTela).not.toBeNull();
    for (const i of g.ids) {
      expect(g.motor(i).log.some(e => e[1] === "st")).toBe(false);        // a TV nao entra no registro de nenhum pet
      expect(motivos(g.motor(i)).some(x => x["olhar"]["telas"].length > 0)).toBe(true);
    }
    expect(g.ids.some(i => motivos(g.motor(i)).some(x => x["olhar"]["olha"] === 1))).toBe(true);
    const rr = GrupoDoJogo.reproduzir(303, 34, JSON.parse(JSON.stringify(g.log)));
    expect(rr.assinatura()).toBe(g.assinatura());
    expect(() => g.agir("A", m => m.sentidoTela(valorSentidoTela("tv", [1, 1, 1, 1, 1, 1, 1])))).toThrow(/mundo comum/);
    expect(() => new GrupoDoJogo(101, 29).sentidoTela(valorSentidoTela("tv", [1, 1, 1, 1, 1, 1, 1]))).toThrow(/v34/);
  });
});

describe("a ligacao do P0 ao cerebro na v33 e na v34 (cerebroTv.ts)", () => {
  const dados: Record<string, string> = {};
  beforeEach(() => {
    for (const k of Object.keys(dados)) delete dados[k];
    vi.stubGlobal("localStorage", { getItem: (k: string) => (k in dados ? dados[k]! : null), setItem: (k: string, v: string) => { dados[k] = v; }, removeItem: (k: string) => { delete dados[k]; } });
  });
  afterEach(() => { vi.unstubAllGlobals(); });
  const armaz = (d: Record<string, string>) => ({ d, getItem: (k: string) => (k in d ? d[k]! : null), setItem(k: string, v: string) { d[k] = v; } });
  const sentido = (x: number) => ({ visao: { cor: x, brilho: x, movimento: x / 2, complexidade: x }, som: { volume: x / 3, variacao: x, timbre: x } });

  test("na v33, parar a TV grava a TV desligada (uma vez)", () => {
    const pet = ovo(101, 33); cuidar(pet, 2);
    iniciarJogo(armaz({ [CHAVE]: textoSave(pet) }));
    comecarNoCerebro("jogo");
    for (let k = 0; k < 10; k++) sentirNoCerebro(sentido(0.6));
    pararNoCerebro();
    pararNoCerebro();
    const st = jogoAtual().motor.log.filter(e => e[1] === "st").map(e => e[2]);
    expect(st).toEqual(["tv|9|9|4|9|3|9|9", "tv|desligada"]);
  });

  test("no grupo v34, o \"st\" vai ao grupo (sem pet), com qualquer um dos dois em foco; parar grava a TV desligada", async () => {
    const g = new GrupoDoJogo(202, 34);
    for (const i of g.ids) g.agir(i, m => ligarProduto(m));
    g.avancar(60);
    const { textoSaveGrupo } = await import("../src/save.ts") as unknown as { textoSaveGrupo?: (g: GrupoDoJogo, foco: string) => string };
    if (textoSaveGrupo === undefined) {
      /* sem o texto do save do grupo exportado, o teste usa o jogo de hoje com o grupo trocado */
      const { trocarGrupo } = await import("../src/jogo.ts");
      iniciarJogo(armaz({}));
      trocarGrupo(g, "save");
    } else iniciarJogo(armaz({ [CHAVE]: textoSaveGrupo(g, "A") }));
    const j = jogoAtual();
    expect(j.grupo).not.toBeNull();
    comecarNoCerebro("tela");
    for (let k = 0; k < 10; k++) sentirNoCerebro(sentido(0.3));
    pararNoCerebro();
    const st = j.grupo!.log.filter(e => e[1] === "st");
    expect(st.map(e => [e[2], e[3]])).toEqual([["tela|4|4|2|4|1|4|4", null], ["tela|desligada", null]]);
    for (const i of j.grupo!.ids) expect(j.grupo!.motor(i).log.some(e => e[1] === "st")).toBe(false);
  });
});
