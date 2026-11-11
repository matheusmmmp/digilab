/* A troca de ilha (docs/TAREFA_V3_ILHA_AGUA.md, IA4; a IA-4 do Matheus: os pets vivos passam para a ilha nova): o evento `mudar_ilha`
   leva o mundo do pet, no meio da vida, do layout de hoje (sem agua) para o mesmo layout com agua. O espelho do tests/test_mudar_ilha.py.
     - o formato do evento (eventoMudarIlha, lerMudarIlha): os mesmos casos do Python;
     - a troca no Mundo: a comida, a bola e o pet na agua vao para a terra mais perto; o contrato passa a ser o do destino; uma vez so;
     - o G-PAR do laco: o TS refaz o gabarito do Python (test/gabaritos/mudar_ilha_python.json, experiments/exportar_gabarito_mudar_ilha.py)
       decisao a decisao e bit a bit no Node: a vida comeca no mundo dos pets v21 (CMU_MVP, sem o contrato) e troca num tick com o pet
       acordado (uma vida) e dormindo (a outra). */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { CMU_MVP, CMU_MVP_AGUA } from "../motor/constantes.ts";
import { CONFIG_CONTRATO, CONFIG_CONTRATO_AGUA, bloqueioEm } from "../motor/contrato.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { estadoNascimentoPy } from "../motor/motor_corpo.ts";
import { ILHAS_DE_TROCA, Mundo, eventoMudarIlha, lerMudarIlha, solidosDaAgua } from "../motor/mundo.ts";
import { LacoGravado, cerebroDa, json, ler, type Rec, type Vida } from "./laco_gravado.ts";

const { texto, g: G } = ler("./gabaritos/mudar_ilha_python.json");
const SHA = "aaafcb2b10e4028859ebd3eb27b19316ea13950d9ddfc170849f086a2b0757b5";
type VidaTroca = Vida & { troca: { tick: number; dormindo: boolean; tirados: { comidas: number; bola: boolean; pet: boolean } };
                          conferido: { cruzou_pela_ponte: number } };
const VIDAS = G.vidas as VidaTroca[];
const CFG = G.config as unknown as { mundo_antes: Rec; mundo_depois: Rec; contrato_depois: Rec };

describe("o formato do log da troca de ilha (os casos do Python)", () => {
  test("o evento guarda o nome do layout e so aceita a forma canonica", () => {
    expect(eventoMudarIlha(9, "mvp_agua")).toEqual({ tick: 9, tipo: "mudar_ilha", valor: "mvp_agua" });
    expect(lerMudarIlha(eventoMudarIlha(9, "mvp_agua"))).toBe("mvp_agua");
    for (const ruim of ["", "Mvp_agua", "mvp agua", "mvp-agua", "a".repeat(33), "água", 5, null, "mvp|agua"]) {
      expect(() => eventoMudarIlha(9, ruim), String(ruim)).toThrow(/mudar_ilha/);
      expect(() => lerMudarIlha({ tipo: "mudar_ilha", valor: ruim }), String(ruim)).toThrow();
    }
    expect(() => lerMudarIlha({ tipo: "levar_pet", valor: "mvp_agua" })).toThrow(/nao e mudar_ilha/);
  });

  test("o destino e o layout de antes com a agua e o controlador", () => {
    expect(Object.keys(ILHAS_DE_TROCA)).toEqual(["mvp_agua"]);
    const { layout, contrato } = ILHAS_DE_TROCA.mvp_agua;
    expect(layout).toBe(CMU_MVP_AGUA.layout);
    expect(json({ ...layout, nome: "mvp" })).toEqual(json(CMU_MVP.layout));
    expect(contrato).toBe(CONFIG_CONTRATO_AGUA);
  });
});

describe("a troca no Mundo", () => {
  test("a comida, a bola e o pet na agua vao para a terra; o contrato passa a ser o do destino; nenhum acaso anda", () => {
    const com = new Mundo({ semente: 202, cfg: CMU_MVP }), sem = new Mundo({ semente: 202, cfg: CMU_MVP }), ref = new Mundo({ semente: 1, cfg: CMU_MVP_AGUA, contrato: CONFIG_CONTRATO_AGUA });
    for (const w of [com, sem]) {
      w.deixarComida(60, "racao", 670, 250);                    // sera o rio
      w.deixarComida(60, "racao", 300, 240);                    // terra
      w.deixarBola(60, 5, 5);                                   // sera o mar
      w.levarPet(60, 670, 250);
    }
    expect(json(com.resumo())).toEqual(json(sem.resumo()));
    const reg = com.mudarIlha(60, "mvp_agua");
    expect(com.cm).toEqual(CMU_MVP_AGUA);
    expect(com.cct).toEqual(CONFIG_CONTRATO_AGUA);
    expect(sem.cct).toEqual(CONFIG_CONTRATO);
    const [a, b] = [...com.comidas.values()];
    expect([a.x, a.y]).toEqual(ref.emTerra(670, 250));
    expect([b.x, b.y]).toEqual([300, 240]);
    expect(reg).toEqual({ tick: 60, de: "mvp", para: "mvp_agua", comidas: [{ id: a.id, de: [670, 250], para: [a.x, a.y] }],
                          bola: { de: [5, 5], para: ref.emTerra(5, 5) }, pet: { de: [670, 250], para: com.pet } });
    expect(com.bolaEm(999)).toEqual(ref.emTerra(5, 5));
    expect(bloqueioEm(com.pet[0], com.pet[1], CONFIG_CONTRATO_AGUA.r_pet, solidosDaAgua(CMU_MVP_AGUA))).toBeNull();
    expect(com.pet).not.toEqual([670, 250]);
    expect((com.resumo() as { pendente: unknown }).pendente).toBeNull();
    /* nenhum fluxo de acaso andou */
    for (const f of ["rngArvores", "rngBola", "rngSujeira", "rngAlvo"] as const) expect(com[f].random()).toBe(sem[f].random());
    expect("troca_ilha" in com.resumo()).toBe(true);
    expect("troca_ilha" in sem.resumo()).toBe(false);
  });

  test("vale uma vez, so para um destino conhecido, e sem o contrato ligado antes", () => {
    const w = new Mundo({ semente: 101, cfg: CMU_MVP });
    expect(() => w.mudarIlha(10, "ilha_que_nao_existe")).toThrow(/desconhecida/);
    expect(() => w.mudarIlha(10, "Mvp")).toThrow(/invalido/);
    expect(w.secas).toBeNull();
    w.mudarIlha(10, "mvp_agua");
    expect(() => w.mudarIlha(10, "mvp_agua")).toThrow();
    expect(() => new Mundo({ semente: 101, cfg: CMU_MVP, contrato: { ...CONFIG_CONTRATO, sensores: true } }).mudarIlha(10, "mvp_agua")).toThrow(/sem o contrato ligado/);
    expect(() => new Mundo({ semente: 101, cfg: CMU_MVP_AGUA, contrato: CONFIG_CONTRATO_AGUA }).mudarIlha(10, "mvp_agua")).toThrow(/sem o contrato ligado/);
  });
});

describe("G-PAR da troca de ilha: o laco do TS = o Python, decisao a decisao", () => {
  test("o gabarito: duas sementes, uma troca com o pet acordado e outra com ele dormindo", () => {
    expect(createHash("sha256").update(texto).digest("hex")).toBe(SHA);
    expect(json(CMU_MVP)).toEqual(CFG.mundo_antes);
    expect(json(CMU_MVP_AGUA)).toEqual(CFG.mundo_depois);
    expect(json(CONFIG_CONTRATO_AGUA)).toEqual(CFG.contrato_depois);
    expect(VIDAS.map(v => [v.semente, v.troca.dormindo])).toEqual([[202, false], [505, true]]);
    expect(VIDAS.some(v => v.troca.tirados.comidas > 0) && VIDAS.some(v => v.troca.tirados.pet)).toBe(true);
    for (const v of VIDAS) expect(v.conferido.cruzou_pela_ponte).toBeGreaterThan(0);
  });

  for (const vida of VIDAS) {
    test(`${vida.nome}: cada decisao, o log, o mundo e o corpo no fim; nada na agua depois da troca`, () => {
      const c = cerebroDa(vida);
      const m = new LacoGravado(c.politica, vida.semente, CCO_CORPO_V11, estadoNascimentoPy(0),
                                { regra: c.regra, paridade: true, cfgMundo: CMU_MVP, decidirNaComida: true, bolaNoGolpe: true });
      let trocou = false;
      for (const e of vida.log) {
        if (e.tipo === "mudar_ilha") {
          expect([e.tick, m.estado.dormindo, m.mundo.secas]).toEqual([vida.troca.tick, vida.troca.dormindo, null]);
          trocou = true;
        }
        m.aplicarEvento(e);
      }
      expect(trocou).toBe(true);
      expect(m.traco.length).toBe(vida.traco.length);
      for (let i = 0; i < vida.traco.length; i++) {
        const esperado = vida.traco[i] as Rec, obtido = m.traco[i];
        if (JSON.stringify(obtido) === JSON.stringify(esperado)) continue;
        for (const k of Object.keys(esperado)) expect(obtido[k], `traco[${i}] (${esperado.op} no tick ${esperado.tick}): ${k}`).toEqual(esperado[k]);
      }
      expect(m.log).toEqual(vida.log);
      expect(json(m.mundo.resumo())).toEqual(vida.resumo);
      expect({ q: { ...m.corpo.q }, receptores: m.corpo.receptores() }).toEqual(vida.corpo_fim);
      const e = m.estado;
      expect({ fome: e.fome, energia: e.energia, humor: e.humor, sujeira: e.sujeira, tick: e.tick }).toEqual(vida.estado_fim);
      /* do lado do TS: depois da troca o mundo e o da agua, e o pet nunca entra nela */
      const w = m.mundo, r = CONFIG_CONTRATO_AGUA.r_pet, solidos = solidosDaAgua(CMU_MVP_AGUA);
      expect(w.cm.layout.nome).toBe("mvp_agua");
      expect(w.trocaIlha!.tick).toBe(vida.troca.tick);
      for (const cm of w.comidas.values()) expect(w.seca(cm.x, cm.y)).toBe(true);
      expect(w.contratoDecisoes.length).toBeGreaterThan(0);
      for (const d of w.contratoDecisoes) {
        expect(d.tick).toBeGreaterThanOrEqual(vida.troca.tick);
        for (const [x, y] of d.trajetoria ?? []) if (bloqueioEm(x, y, r, solidos) !== null) throw new Error(`o pet na agua: (${x}, ${y})`);
      }
    });
  }
});
