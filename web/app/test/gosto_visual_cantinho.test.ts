// A etapa 2 do código do PLANO_UX_GOSTO_VISUAL (o cantinho e as reações), sem DOM (vitest em node). Cobre: o sinal da TV no lugar do balão
// de texto (o ícone de cada reação, o mínimo de 3 s, e a fila: o chamado e a fala passam na frente); a TV em três quartos na grade, nas duas
// ilhas, valendo sempre (a UX-GV-3); o toque na TV que pede o painel (a UX-GV-2), com o mesmo gesto do toque nos lugares; a ida da câmera
// ao cantinho; e, pela fonte, que o balão em 3D saiu, que o palco só ganha o sinal por último e que sem a chave a cena não tem sinal nem TV
// tocável.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { afterEach, describe, expect, test } from "vitest";
import { CMU_MVP, CMU_MVP_AGUA } from "../motor/index.ts";
import { S } from "../src/grades.ts";
import { CENA } from "../src/telas/pet/cenaEstado.ts";
import { destinoNoPonto } from "../src/telas/pet/ToqueLugar.tsx";
import { PLANTA_ILHA_AGUA, TV_TRES_QUARTOS } from "../src/telas/pet/ilha/constantes.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { CAIXA_TV, CAMERA_CANTINHO, passoDaCamera, pontosDoCantinho, suave, tvDaIlha } from "../src/telas/pet/ilha/cantinhoTvConta.ts";
import { BALAO, desligarTv, publicarTv } from "../src/gostoVisual/estadoTv.ts";
import type { Reacao } from "../src/gostoVisual/gosto.ts";
import { aoPedirPainelTv, marcarPainelTv, painelTvAberto, pedirPainelTv } from "../src/gostoVisual/painelTvEstado.ts";
import { FilaSinal, SINAL_DA_REACAO, SINAL_MIN_MS, esquecerSinalTv, marcarSentadoNaTv, ocuparSinalTv, reacaoDoSinal, sinalDaTvAgora } from "../src/gostoVisual/sinalTv.ts";
import { ligarToqueTv, tvNoPonto } from "../src/gostoVisual/ToqueTv.tsx";

const fonte = (rel: string): string => readFileSync(join(import.meta.dirname, "..", rel), "utf8");
afterEach(() => { desligarTv(); esquecerSinalTv(); marcarPainelTv(false); CENA.mundo = null; CENA.ret = null; CENA.coberto = false; CENA.petNaMao = false; });

describe("o sinal da TV: um ícone no lugar do balão de texto (UX-GV-10)", () => {
  test("cada reação tem o ícone do plano (seção 5.1), e os ícones existem nas grades do jogo", () => {
    expect(SINAL_DA_REACAO).toEqual({ adorando: "coracao", olhando: null, curioso: "pergunta", enjoou: "reticencias", nao_gosta: "x", distraido: null });
    expect(Object.keys(SINAL_DA_REACAO).sort()).toEqual(Object.keys(BALAO).sort());
    for (const k of Object.values(SINAL_DA_REACAO)) if (k) expect((S as Record<string, unknown>)[k], k).toBeDefined();
  });
  test("o sinal só muda quando a reação muda, e fica pelo menos 3 s", () => {
    expect(SINAL_MIN_MS).toBe(3000);
    const f = new FilaSinal();
    expect(f.passo("adorando", 0)).toBe("adorando");
    /* o P0 trocava a cada segundo: aqui a troca espera o mínimo */
    expect(f.passo("curioso", 1000)).toBe("adorando");
    expect(f.passo("enjoou", 2999)).toBe("adorando");
    expect(f.passo("enjoou", 3000)).toBe("enjoou");
    expect(f.passo("adorando", 4000)).toBe("enjoou");
    /* a mesma reação não reinicia o relógio */
    expect(f.passo("enjoou", 5900)).toBe("enjoou");
    expect(f.passo("adorando", 6000)).toBe("adorando");
    /* a TV desligou: esquece na hora, e a próxima reação entra sem esperar */
    expect(f.passo(null, 6100)).toBeNull();
    expect(f.passo("curioso", 6200)).toBe("curioso");
  });
  test("falha alto com entrada inválida", () => {
    expect(() => new FilaSinal(-1)).toThrow();
    expect(() => new FilaSinal().passo("adorando", NaN)).toThrow();
  });
  test("só há sinal com a TV ligada e o pet sentado na almofada", () => {
    expect(sinalDaTvAgora(0)).toBeNull();
    publicarTv({ ligada: true, origem: "jogo", reacao: "adorando" });
    expect(sinalDaTvAgora(10)).toBeNull();                       /* ainda andando até a almofada */
    marcarSentadoNaTv(true);
    expect(sinalDaTvAgora(20)).toBe("coracao");
    desligarTv();
    expect(sinalDaTvAgora(30)).toBeNull();
  });
  test("a fila: com o chamado do pet ou a fala do jogo na tela, o sinal da TV espera, e o relógio da reação segue", () => {
    publicarTv({ ligada: true, origem: "jogo", reacao: "nao_gosta" });
    marcarSentadoNaTv(true);
    expect(sinalDaTvAgora(0)).toBe("x");
    for (const quem of ["chamado", "fala"] as const) {
      ocuparSinalTv(quem, true);
      expect(sinalDaTvAgora(100)).toBeNull();
      expect(reacaoDoSinal(100)).toBe("nao_gosta");
      ocuparSinalTv(quem, false);
      expect(sinalDaTvAgora(200)).toBe("x");
    }
    /* as reações sem ícone (olhando, distraído) ficam só na pose */
    publicarTv({ reacao: "olhando" });
    expect(sinalDaTvAgora(SINAL_MIN_MS + 300)).toBeNull();
    expect(reacaoDoSinal(SINAL_MIN_MS + 300)).toBe("olhando" satisfies Reacao);
  });
  test("o balão de texto saiu do 3D, e o palco pinta o sinal por último, só se a cena o tem", () => {
    const c = fonte("src/telas/pet/ilha/cantinhoTv.ts");
    expect(c).not.toMatch(/BALAO|SpriteMaterial|fillText/);
    expect(c).toContain("marcarSentadoNaTv(q.sentado && TV.ligada)");
    const p = fonte("src/telas/pet/PalcoPet.tsx");
    expect(p).toContain("const daTv = doJogo === null ? CENA.sinalTv?.(performance.now()) ?? null : null;");
    expect(p).toContain("return doJogo ?? daTv;");
    expect(p).not.toContain("gostoVisual/");
    /* sem o protótipo montado a cena não tem sinal: o palco é o de hoje */
    expect(CENA.sinalTv).toBeNull();
    expect(fonte("src/gostoVisual/GostoVisual.tsx")).toContain("CENA.sinalTv = sinalDaTvAgora; return () => { CENA.sinalTv = null; };");
  });
});

describe("a TV em três quartos (UX-GV-3, valendo sempre)", () => {
  for (const cm of [CMU_MVP, CMU_MVP_AGUA]) test(`a frente da TV fica a 40° do sul, de onde a câmera olha (${cm.layout.nome})`, () => {
    const t = tvDaIlha(ilhaDe(cm));
    expect(TV_TRES_QUARTOS).toBe(40);
    expect(Math.abs(t.giro)).toBeCloseTo((40 * Math.PI) / 180, 12);
    /* a frente (+z do glTF girado) aponta para o sul: a tela aparece para a câmera */
    expect(Math.cos(t.giro)).toBeGreaterThan(0.7);
    /* quem assiste fica na frente e de lado: a almofada mais ao sul que a TV, e fora da linha entre a TV e a câmera */
    const p = pontosDoCantinho(ilhaDe(cm));
    expect(p.assento[1]).toBeGreaterThan(p.tv[1]);
    expect(Math.abs(p.assento[0] - p.tv[0])).toBeGreaterThan(1);
  });
  test("na ilha com água a TV vira para o lado da praça", () => {
    const t = tvDaIlha(ilhaDe(CMU_MVP_AGUA));
    expect(Math.sign(Math.sin(t.giro))).toBe(Math.sign(PLANTA_ILHA_AGUA.praca.x - t.x));
  });
  test("o giro não depende da chave: a grade não lê o protótipo", () => {
    expect(fonte("src/telas/pet/ilha/grade.ts")).not.toMatch(/gostoVisual|gosto_visual/);
  });
});

describe("o toque na TV abre o painel (UX-GV-2)", () => {
  type Ponteiro = { pointerId: number; clientX: number; clientY: number; button: number; buttons: number; pointerType: string };
  const alvo = () => Object.assign(new EventTarget(), { getBoundingClientRect: () => ({ left: 0, top: 0 }), style: { cursor: "" } });
  const ev = (tipo: string, p: Partial<Ponteiro>) => Object.assign(new Event(tipo), { pointerId: 1, clientX: 0, clientY: 0, button: 0, buttons: 0, pointerType: "mouse", ...p });
  const comTv = () => { CENA.mundo = { tvEm: (x: number, y: number) => x >= 100 && x <= 160 && y >= 100 && y <= 160, lugarEm: () => "barraca" } as unknown as typeof CENA.mundo; };

  test("um toque na TV pede o painel; um arrasto, fora da TV, sobre o pet ou com a cena coberta, não", () => {
    comTv();
    const el = alvo(); let pedidos = 0;
    const desligar = ligarToqueTv(el, () => { pedidos++; });
    el.dispatchEvent(ev("pointerdown", { clientX: 120, clientY: 120 })); el.dispatchEvent(ev("pointerup", { clientX: 121, clientY: 121 }));
    expect(pedidos).toBe(1);
    el.dispatchEvent(ev("pointerdown", { clientX: 120, clientY: 120 })); el.dispatchEvent(ev("pointermove", { clientX: 150, clientY: 120, buttons: 1 })); el.dispatchEvent(ev("pointerup", { clientX: 150, clientY: 120 }));
    expect(pedidos).toBe(1);
    el.dispatchEvent(ev("pointerdown", { clientX: 10, clientY: 10 })); el.dispatchEvent(ev("pointerup", { clientX: 10, clientY: 10 }));
    expect(pedidos).toBe(1);
    CENA.ret = { x: 110, y: 110, w: 20, h: 20 };
    expect(tvNoPonto(el, 120, 120)).toBe(false);
    CENA.ret = null; CENA.coberto = true;
    expect(tvNoPonto(el, 120, 120)).toBe(false);
    CENA.coberto = false; CENA.petNaMao = true;
    expect(tvNoPonto(el, 120, 120)).toBe(false);
    CENA.petNaMao = false;
    /* o cursor vira a mão sobre a TV e volta ao sair */
    el.dispatchEvent(ev("pointermove", { clientX: 120, clientY: 120 }));
    expect(el.style.cursor).toBe("pointer");
    el.dispatchEvent(ev("pointermove", { clientX: 10, clientY: 10 }));
    expect(el.style.cursor).toBe("");
    desligar();
    el.dispatchEvent(ev("pointerdown", { clientX: 120, clientY: 120 })); el.dispatchEvent(ev("pointerup", { clientX: 120, clientY: 120 }));
    expect(pedidos).toBe(1);
  });
  test("o toque na TV é da TV: a barraca atrás dela não abre; sem a TV na cena, a barraca abre como hoje", () => {
    const el = alvo();
    comTv();
    expect(destinoNoPonto(el, 120, 120)).toBeNull();
    expect(destinoNoPonto(el, 10, 10)).not.toBeNull();
    CENA.mundo = { lugarEm: () => "barraca" } as unknown as typeof CENA.mundo;
    expect(destinoNoPonto(el, 120, 120)).not.toBeNull();
    expect(tvNoPonto(el, 120, 120)).toBe(false);
  });
  test("a tela Pet atende o pedido; fora dela, ninguém", () => {
    expect(pedirPainelTv()).toBe(false);
    let n = 0;
    const sair = aoPedirPainelTv(() => { n++; });
    expect(pedirPainelTv()).toBe(true);
    expect(n).toBe(1);
    sair();
    expect(pedirPainelTv()).toBe(false);
  });
  test("a vista só publica a TV tocável com o cantinho, e a área de toque tem pelo menos 44 px", () => {
    expect(CAIXA_TV.minPx).toBe(44);
    expect(fonte("src/telas/pet/ilha/vista.ts")).toContain("...(vista.temCantinho ? { tvEm: (x: number, y: number) => vista.tvEm(x, y) } : {})");
  });
});

describe("a câmera vai ao cantinho com o painel da TV aberto (seção 6)", () => {
  test("a ida e a volta duram CAMERA_CANTINHO.ms, e com movimento reduzido não há ida", () => {
    let f = 0;
    for (let t = 0; t < CAMERA_CANTINHO.ms; t += 100) f = passoDaCamera(f, true, 100, false);
    expect(f).toBeCloseTo(1, 9);
    expect(passoDaCamera(1, true, 100, false)).toBe(1);
    expect(passoDaCamera(0.5, false, CAMERA_CANTINHO.ms / 4, false)).toBeCloseTo(0.25, 12);
    expect(passoDaCamera(0, false, 100, false)).toBe(0);
    expect([passoDaCamera(0.3, true, 16, true), passoDaCamera(0.7, false, 16, true)]).toEqual([1, 0]);
    expect(() => passoDaCamera(NaN, true, 16, false)).toThrow();
    expect([suave(0), suave(0.5), suave(1)]).toEqual([0, 0.5, 1]);
  });
  test("o painel aberto é um estado solto que a tela Pet marca e a ilha lê", () => {
    expect(painelTvAberto()).toBe(false);
    marcarPainelTv(true);
    expect(painelTvAberto()).toBe(true);
    const t = fonte("src/telas/pet/TelaPet.tsx");
    expect(t).toContain('useEffect(() => { marcarPainelTv(atual === "tv"); return () => marcarPainelTv(false); }, [atual]);');
    /* o cantinho fica à esquerda do painel de 900 px em diante */
    expect(CAMERA_CANTINHO.largo).toBeLessThan(0.5);
  });
  test('com "Exibir detalhes do pet" desligado, a pilha fica só com a linha "TV"', () => {
    const t = fonte("src/telas/pet/TelaPet.tsx");
    expect(t).toContain("{largo ? (!atual && (detalhesPet || temTv) && (");
    expect(t).toContain('{detalhesPet && <PainelHud id="estado"');
    expect(t).toContain("{detalhesPet && nascendo === 0 && <LinhaDigiBrain");
    expect(t).toContain("{temTv && <LinhaTv");
  });
});
