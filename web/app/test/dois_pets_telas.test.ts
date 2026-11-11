/* As telas dos dois pets, pelo lado do app (docs/TAREFA_V3_COOPERACAO.md, etapa CO4d):
   - o irmao do pet em foco e os pets vivos (o topo e o relogio leem por aqui);
   - o relogio freia pelo chamado de qualquer um dos dois;
   - o que copia, exporta e confere o save conhece o grupo (Ajustes e o Registro);
   - o par vai inteiro para a espera e volta inteiro (Meus pets); o Salao nao o ve;
   - a heranca nao aceita um pet do par nesta etapa, e o arquivo do par ainda nao se importa (D-CO4d-5). */
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { ESPECIES, GrupoDoJogo, TPD, VERSAO_V25 } from "../motor/index.ts";
import { CHAVE, type Armazenamento } from "../src/save.ts";
import { focar, iniciarJogo, irmaoEmFoco, jogoAtual, mudarMotor, petsVivos, replayDaTelaConfere, textoDaTela, textoDoSaveAtual, trocarGrupo } from "../src/jogo.ts";
import { chocarDoisOvos, especieDaSemente } from "../src/jornada.ts";
import { CHAVE_GUARDADOS, abrirGuardado, ativarGuardado, ehGrupoGuardado, lerGuardados } from "../src/pets.ts";
import { podeSerPai } from "../src/heranca.ts";
import { lerArquivo } from "../src/importar.ts";
import { ajustarVelocidadeChamado, escolherVelocidade, freadoPorChamado } from "../src/tempo.ts";

const ESP = ESPECIES[1];
const SEMENTE = (() => { for (let s = 7; ; s++) if (especieDaSemente(s) === ESP) return s; })();
let dados: Record<string, string> = {};
beforeEach(() => {
  dados = {};
  vi.stubGlobal("localStorage", { getItem: (k: string) => (k in dados ? dados[k]! : null), setItem: (k: string, v: string) => { dados[k] = v; }, removeItem: (k: string) => { delete dados[k]; } });
  const a: Armazenamento = { getItem: k => (k in dados ? dados[k]! : null), setItem(k, v) { dados[k] = v; } };
  iniciarJogo(a);
  trocarGrupo(chocarDoisOvos(ESP, "rapida", SEMENTE), "novo");
});
afterEach(() => { vi.unstubAllGlobals(); });

describe("o foco, o irmao e o relogio", () => {
  test("o irmao do pet em foco e os pets vivos", () => {
    const g = jogoAtual().grupo!;
    expect(irmaoEmFoco()!.ident).toBe("B");
    expect(petsVivos()).toEqual([g.motor("A"), g.motor("B")]);
    focar("B");
    expect(irmaoEmFoco()!.ident).toBe("A");
  });

  test("o relogio freia pelo chamado de qualquer um dos dois", () => {
    /* os dois bebes chamam juntos (o chamado sai do relogio): atendido o do pet em foco, o do irmao segue freando o tempo */
    const g = jogoAtual().grupo!, ATENDE = { fome: "alimentar", higiene: "limpar", carinho: "acariciar" } as const;
    escolherVelocidade(60);
    let k = 0;
    while (g.motor("A").chamadosAbertos().length === 0 && k++ < TPD) mudarMotor(m => m.avancar(1), "adiado");
    expect(ajustarVelocidadeChamado() || freadoPorChamado()).toBe(true);
    for (const c of g.motor("A").chamadosAbertos()) mudarMotor(m => m.observar(ATENDE[c]));
    expect(g.motor("A").chamadosAbertos()).toEqual([]);
    expect(g.motor("B").chamadosAbertos().length).toBeGreaterThan(0);
    ajustarVelocidadeChamado();
    expect(freadoPorChamado()).toBe(true);             // o irmao ainda chama
    for (const c of g.motor("B").chamadosAbertos()) { focar("B"); mudarMotor(m => m.observar(ATENDE[c])); }
    ajustarVelocidadeChamado();
    expect(freadoPorChamado()).toBe(false);            // atendidos os dois, o tempo volta
    escolherVelocidade(10);
  });
});

describe("o save nas telas", () => {
  test("copiar, exportar e conferir: o registro do grupo inteiro", () => {
    mudarMotor(m => m.avancar(60), "agora");
    mudarMotor(m => m.observar("acariciar"));
    const d = JSON.parse(textoDaTela()) as { grupo: boolean; foco: string };
    expect(d).toMatchObject({ grupo: true, foco: "A" });
    expect(textoDoSaveAtual()).toBe(textoDaTela());
    const r = replayDaTelaConfere();
    expect(r.ok).toBe(true);
    expect(r.eventos).toBe(jogoAtual().grupo!.log.length);
    expect(dados[CHAVE]).toBe(textoDaTela());
  });

  test("o par vai inteiro para a espera e volta inteiro; o Salao nao o ve", () => {
    const g = jogoAtual().grupo!;
    mudarMotor(m => m.avancar(120), "agora");
    const assin = g.assinatura();
    /* um pet de um so guardado, e o par troca de lugar com ele */
    dados[CHAVE_GUARDADOS] = JSON.stringify([JSON.parse(JSON.stringify({ semente: 20260924, log: [], versao: 23 }))]);
    ativarGuardado(0);
    expect(jogoAtual().grupo).toBeNull();
    const guardado = lerGuardados()[0];
    expect(ehGrupoGuardado(guardado)).toBe(true);
    expect(abrirGuardado(guardado).noGrupo).toBe(true);
    ativarGuardado(0);
    expect(jogoAtual().grupo!.assinatura()).toBe(assin);
    expect(ehGrupoGuardado(lerGuardados()[0])).toBe(false);
  });

  test("a heranca nao aceita um pet do par, e o arquivo do par ainda nao se importa", () => {
    const g = jogoAtual().grupo!;
    expect(podeSerPai(g.motor("A"))).toBe(false);
    expect(() => lerArquivo(textoDaTela(), "par.digilab")).toThrow(/dois pets/);
    expect(GrupoDoJogo.reproduzir(g.semente, VERSAO_V25, g.log).assinatura()).toBe(g.assinatura());
  });
});
