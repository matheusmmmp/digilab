// A linha do agora e o chip de causa da tela Pet (P1 da UX_TELA_PET; docs/PROPOSTAS_V3_UX_TELA_PET.md, "P1"). Sem DOM (vitest em node):
// renderToStaticMarkup. Cobre: os cinco estados da linha (texto, a malha so no "aprendido", o "?" sem decisao, o modular sem marca), o nome
// acessivel de cada um, o texto sem botao com os detalhes do pet desligados (P1-5), os tres casos do chip e a leitura sem montar o mapa.
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, test } from "vitest";
import { Motor, type LeituraDecisao, type MotivoVida } from "../motor/index.ts";
import { ChipCausa, LinhaAgoraVista, decisaoAgora, rotuloAgora, vistaAgora } from "../src/telas/pet/LinhaAgora.tsx";

/* so os campos que a linha le: a regra, a escolha e o que o instinto faria */
const decisao = (regra: string, escolha: boolean, mudou: boolean, instinto = "ocioso"): LeituraDecisao =>
  ({ regra, quem_decidiu: { escolha, mudou, acao_instinto: instinto } }) as unknown as LeituraDecisao;
const pet = (acao: string, lab: object | null = null): Motor => ({ acao, lab }) as unknown as Motor;

const linha = (v: ReturnType<typeof vistaAgora>, abrir = true): string =>
  renderToStaticMarkup(h(LinhaAgoraVista, { v, aoAbrir: abrir ? () => {} : undefined }));
const rotulo = (s: string): string => s.match(/aria-label="([^"]*)"/)![1]!;

describe("a linha do agora: os cinco estados", () => {
  test("o aprendido mudou a escolha: a malha, 'aprendido' e o que o instinto faria; so esse caso tem malha", () => {
    const v = vistaAgora(pet("brincar"), decisao("tempo_livre", true, true, "ocioso")), s = linha(v);
    expect(v.caso).toBe("aprendido");
    expect(s).toContain("dl-malha");
    expect(s).toContain("aprendido");
    expect(s).toContain("sem ele: à toa");
    expect(rotulo(s)).toBe("Agora: brincando. Aprendido: sem ele, à toa. Abrir o porquê no DigiBrain.");
  });
  test("o instinto bastava: a regra e 'o instinto faria o mesmo', sem malha", () => {
    const v = vistaAgora(pet("explorar"), decisao("tempo_livre", true, false)), s = linha(v);
    expect(v.caso).toBe("instinto");
    expect(s).toContain("Tempo livre · o instinto faria o mesmo");
    expect(s).toContain(">instinto<");   /* a forma curta, a 390 */
    expect(s).not.toContain("dl-malha");
    expect(rotulo(s)).toBe("Agora: explorando. Tempo livre: o instinto faria o mesmo. Abrir o porquê no DigiBrain.");
  });
  test("uma opcao so: 'só havia uma opção', sem malha", () => {
    const v = vistaAgora(pet("dormir"), decisao("sono_exaustao", false, false)), s = linha(v);
    expect(v.caso).toBe("uma");
    expect(s).toContain("Exausto · só havia uma opção");
    expect(s).toContain(">uma opção<");
    expect(s).not.toContain("dl-malha");
    expect(rotulo(s)).toBe("Agora: dormindo. Exausto: só havia uma opção. Abrir o porquê no DigiBrain.");
  });
  test("antes da primeira decisao: o '?' tracejado e 'sem motivo registrado'", () => {
    const v = vistaAgora(pet("ocioso"), null), s = linha(v);
    expect(v.caso).toBe("sem");
    expect(s).toContain("chip-causa--sem");
    expect(s).toContain("sem motivo registrado");
    expect(s).not.toContain("dl-malha");
    expect(rotulo(s)).toBe("Agora: à toa. Sem motivo registrado. Abrir o porquê no DigiBrain.");
  });
  test("o modular decide: 'cérebro modular', sem marca, e a decisao do A (que parou) nao conta", () => {
    const v = vistaAgora(pet("brincar", {}), decisao("tempo_livre", true, true)), s = linha(v);
    expect(v.caso).toBe("modular");
    expect(s).toContain("cérebro modular");
    expect(s).not.toContain("chip-causa");
    expect(s).not.toContain("dl-malha");
    expect(rotulo(s)).toBe("Agora: brincando. Cérebro modular. Abrir o porquê no DigiBrain.");
  });
});

describe("a linha do agora: o botao", () => {
  test("com os detalhes do pet, um botao que abre o DigiBrain (aria-controls e aria-pressed)", () => {
    const s = linha(vistaAgora(pet("brincar"), decisao("tempo_livre", true, false)));
    expect(s).toMatch(/^<button type="button"/);
    expect(s).toContain('aria-controls="pet-painel"');
    expect(s).toContain('aria-pressed="false"');
  });
  test("sem os detalhes do pet (P1-5): texto sem botao, com nome acessivel e sem o convite a abrir", () => {
    const s = linha(vistaAgora(pet("brincar"), decisao("tempo_livre", true, true)), false);
    expect(s).not.toContain("<button");
    expect(s).toContain('role="group"');
    expect(rotulo(s)).toBe("Agora: brincando. Aprendido: sem ele, à toa.");
    expect(rotuloAgora(vistaAgora(pet("ocioso"), null), false)).toBe("Agora: à toa. Sem motivo registrado.");
  });
});

describe("a leitura da decisao", () => {
  test("sem montar o mapa, ela e a mesma de Motor.digibrain().decisao", () => {
    const m = new Motor(101); m.avancar(300);
    const db = m.digibrain();
    expect(db).not.toBeNull();
    expect(decisaoAgora(m)).toEqual(db!.decisao);
    expect(vistaAgora(m).acao).toBeTruthy();
  });
  test("pet novo, sem decisao: caso 'sem'", () => {
    expect(decisaoAgora(new Motor(101))).toBeNull();
    expect(vistaAgora(new Motor(101)).caso).toBe("sem");
  });
});

describe("o chip do balao", () => {
  const mot = (extra: Partial<MotivoVida>): MotivoVida => ({ origem: "vida", tick: 0, acao: "treinar_cansado", fatores: [], refsOrd: [], intensidade: 0, exploracao: false, humor: 0, valorDecidiu: false, ...extra });
  const texto = (m: MotivoVida): string => renderToStaticMarkup(h(ChipCausa, { mot: m }));
  test("fadiga_treino: a caixa solida de necessidade, 'vem do corpo · treino puxado'", () => {
    const s = texto(mot({ fatores: ["fadiga_treino"] }));
    expect(s).toContain("chip-causa--corpo");
    expect(s.replace(/<[^>]+>/g, "")).toBe("vem do corpo · treino puxado");
  });
  test("outro fator: so o marcador, neutro (nunca vazio)", () => {
    const s = texto(mot({ fatores: ["teimosia"] }));
    expect(s).toContain("chip-causa--neutro");
    expect(s.replace(/<[^>]+>/g, "")).toBe("teimoso");
  });
  test("sem fator ou exploracao: '? sem motivo registrado', tracejado; o '?' fica fora do nome acessivel", () => {
    for (const m of [mot({}), mot({ fatores: ["fadiga_treino"], exploracao: true })]) {
      const s = texto(m);
      expect(s).toContain("chip-causa--sem");
      expect(s).toContain('aria-hidden="true">?<');
      expect(s.replace(/<b[^>]*>\?<\/b>/, "").replace(/<[^>]+>/g, "")).toBe("sem motivo registrado");
    }
  });
});
