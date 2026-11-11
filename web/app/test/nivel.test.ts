/* O nivel do Tamer (src/nivel.ts; docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.3 a 5): os marcos de cada save de exemplo, a ordem, o piso 4 dos saves de antes, o nunca-desce, a chave
   (so o texto: o armazenamento e do nivelTela.ts) e as pecas. Sem DOM: a funcao e pura. */
import { beforeAll, describe, expect, test } from "vitest";
import { Motor } from "../motor/index.ts";
import { ESCADA, petDaReceita } from "../src/pets.ts";
import { ehPetDoJogador } from "../src/nivelTela.ts";
import { petExemplo } from "../src/save.ts";
import { Tamer, type EventoTamer } from "../src/tamer.ts";
import {
  CARTOES, PECAS, PISO_NIVEL, anuncioDeAbertura, assinaturaIntocada, cartaoDe, cartoesPendentes, ehPetIntocado, jaConheco, lerEstado, marcarCartao, marcosDoPet, marcosDoTamer, marcosFeitos, nivelDe,
  pecaAberta, pecaDaAba, pecaDoDestino, reverTutorial, sincronizar, textoEstado, type EstadoNivel,
} from "../src/nivel.ts";

const IDS = ["campina", "torre", "floresta", "cidadela", "lago", "espiral"];
const medalhas = (n: number): EventoTamer[] => IDS.slice(0, n).map((id, i) => ["medalha", { id, n: i + 1, quando: i, pet: 1, forma: "Agumon", tick: 500 + i }] as EventoTamer);
const tamer = (n: number, titulo = false): Tamer =>
  Tamer.reproduzir([...medalhas(n), ...(titulo ? ([["campeao", { n: 1, quando: 9, pet: 1, forma: "WarGreymon", tick: 900 }]] as EventoTamer[]) : [])]);

/* os pets de exemplo da escada (pets.ts): um In-Training, um Rookie treinado e um Champion treinado */
let bebe: Motor, rookie: Motor, champion: Motor;
/* as receitas da escada de exemplo (que deixou de ser semeada na LUTA_POC), com o dono tratando a lesao do sparring da luta da POC */
beforeAll(() => { bebe = petDaReceita(ESCADA[0], true); rookie = petDaReceita(ESCADA[2], true); champion = petDaReceita(ESCADA[3], true); }, 120_000);

describe("os marcos do pet", () => {
  test("o pet de exemplo intocado nao e do jogador, mesmo com o tempo passando; um evento a mais o faz do jogador (R1)", () => {
    const sem = new Set([assinaturaIntocada(petExemplo())]);
    expect(ehPetIntocado(petExemplo(), sem)).toBe(true);
    const comTempo = petExemplo(); comTempo.avancar(300);
    expect(ehPetIntocado(comTempo, sem)).toBe(true);
    expect(ehPetDoJogador(comTempo)).toBe(false);
    const cuidado = petExemplo(); cuidado.observar("acariciar");
    expect(ehPetIntocado(cuidado, sem)).toBe(false);
    expect(ehPetDoJogador(cuidado)).toBe(true);
    expect(ehPetDoJogador(new Motor(7))).toBe(true);
  });
  test("o aviso de leitor de tela do que abriu", () => {
    expect(anuncioDeAbertura([2])).toBe("Diário aberto");
    expect(anuncioDeAbertura([3])).toBe("Crescer e Conversar abertos");
    expect(anuncioDeAbertura([1, 7, 9])).toBe("");
    expect(anuncioDeAbertura([4, 5])).toBe("Lutar e Itens abertos");
  });
  test("um ovo recem-chocado so tem o marco 1", () => {
    expect(marcosDoPet(new Motor(7))).toEqual([1]);
  });
  test("3 chamados atendidos abrem o marco 2", () => {
    const m = new Motor(7);
    m.chamados.atendidos = 2;
    expect(marcosDoPet(m)).toEqual([1]);
    m.chamados.atendidos = 3;
    expect(marcosDoPet(m)).toEqual([1, 2]);
  });
  test("sem as chaves de produto, 1 h de vida vale o marco 2; com as chaves, so o pet fora do In-Training", () => {
    const livre = new Motor(7);
    livre.avancar(59);
    expect(marcosDoPet(livre)).toEqual([1]);
    livre.avancar(1);
    expect(marcosDoPet(livre)).toEqual([1, 2]);
    const comChaves = new Motor(8);
    comChaves.produto = { chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: false };
    comChaves.avancar(90);
    expect(comChaves.estagioAtual).toBe("bebe");
    expect(marcosDoPet(comChaves)).toEqual([1]);
  });
  test("o Rookie treinado tem 1 a 4 (e ainda nao o 6); o Champion treinado tem o 6", () => {
    expect(bebe.estagioAtual).toBe("bebe");
    expect(marcosDoPet(bebe)).not.toContain(3);
    expect(rookie.estagioAtual).toBe("crianca");
    expect(marcosDoPet(rookie)).toEqual([1, 2, 3, 4]);
    expect(champion.estagioAtual).toBe("adolescente");
    expect(marcosDoPet(champion)).toEqual([1, 2, 3, 4, 6]);
  });
});

describe("os marcos do Tamer e a uniao", () => {
  test("as medalhas e o titulo", () => {
    expect(marcosDoTamer(tamer(0))).toEqual([]);
    expect(marcosDoTamer(tamer(1))).toEqual([5]);
    expect(marcosDoTamer(tamer(2))).toEqual([5]);
    expect(marcosDoTamer(tamer(3))).toEqual([5, 7]);
    expect(marcosDoTamer(tamer(6))).toEqual([5, 7, 8]);
    expect(marcosDoTamer(tamer(6, true))).toEqual([5, 7, 8, 9]);
  });
  test("a uniao dos pets e do Tamer vem em ordem, sem repetir", () => {
    expect(marcosFeitos([], tamer(0))).toEqual([]);
    expect(marcosFeitos([rookie, champion], tamer(3))).toEqual([1, 2, 3, 4, 5, 6, 7]);
  });
  test("o nivel e a CONTAGEM dos marcos, e cada peca abre pelo proprio marco, nao pelo numero", () => {
    /* o Champion treinado sem medalha: chocou, chamados, Rookie, treino e Champion = Nv 5; as Regras (marco 6) abrem e os Itens (marco 5) nao */
    const e = sincronizar({ marcos: [], cartoes: [] }, marcosFeitos([champion], tamer(0)), true).estado;
    expect(nivelDe(e)).toBe(5);
    expect(pecaAberta(e, "forcar")).toBe(true);
    expect(pecaAberta(e, "forcar")).toBe(true);
    expect(pecaAberta(e, "itens")).toBe(false);
    expect(pecaAberta(e, "fronteira")).toBe(false);
  });
});

describe("as pecas", () => {
  test("cada peca abre pelo marco da tabela do plano (3.3)", () => {
    const abre = (marcos: number[], p: Parameters<typeof pecaAberta>[1]) => pecaAberta({ marcos, cartoes: [] }, p);
    expect(PECAS.diario.marco).toBe(2); expect(abre([2], "diario")).toBe(true); expect(abre([1], "diario")).toBe(false);
    expect(PECAS.crescer.marco).toBe(3); expect(PECAS.conversar.marco).toBe(3);
    expect(PECAS.lutar.marco).toBe(4);
    expect(PECAS.itens.marco).toBe(5);
    expect("regras" in PECAS).toBe(false); expect(PECAS.forcar.marco).toBe(6);
    expect(PECAS.fronteira.marco).toBe(8);
  });
  test("o menu e a aba de cada peca; Pet e as outras abas nao tem trava", () => {
    expect(pecaDoDestino("diario")).toBe("diario");
    expect(pecaDoDestino("crescer")).toBe("crescer");
    expect(pecaDoDestino("lutar")).toBe("lutar");
    expect(pecaDoDestino("conversar")).toBe("conversar");
    expect(pecaDoDestino("pet")).toBeNull();
    expect(pecaDaAba("itens")).toBe("itens");
    expect(pecaDaAba("fronteira")).toBe("fronteira");
    expect(pecaDaAba("treinar")).toBeNull();
  });
  test("o motivo diz o marco, em palavras", () => {
    expect(PECAS.crescer.motivo).toBe("Abre quando ele virar Rookie");
    expect(PECAS.fronteira.motivo).toBe("Abre com 6 medalhas");
    for (const p of Object.values(PECAS)) expect(p.motivo.startsWith("Abre ")).toBe(true);
  });
});

describe("a ordem dos niveis e os cartoes", () => {
  test("do Nv 1 ao 9, um marco cada, na ordem do plano", () => {
    expect(CARTOES.map(c => c.n)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
    expect(CARTOES.map(c => c.titulo)).toEqual(["Cuide dele", "Diário", "Crescer", "Lutar", "Itens", "Forçar o treino", "3 medalhas", "Fronteira", "Campeão"]);
  });
  test("os textos cabem no plano (4.2): titulo de ate 3 palavras e frase de ate 8", () => {
    for (const c of CARTOES) {
      expect(c.titulo.split(/\s+/).length, c.titulo).toBeLessThanOrEqual(3);
      expect(c.frase.split(/\s+/).length, c.frase).toBeLessThanOrEqual(8);
    }
  });
  test("o Ir leva a rota do lugar; o marco das 3 medalhas nao tem para onde ir", () => {
    expect(cartaoDe(3)?.rota).toEqual({ destino: "crescer", aba: "treinar" });
    expect(cartaoDe(8)?.rota).toEqual({ destino: "lutar", aba: "fronteira" });
    expect(cartaoDe(7)?.rota).toBeUndefined();
  });
});

describe("a primeira visita, o piso 4 e o nunca-desce", () => {
  test("primeira visita, sem pet e sem Tamer: Nv 0 e nada aberto; depois de chocar, Nv 1 com o cartao do Cuide", () => {
    const zero = sincronizar(null, marcosFeitos([], tamer(0)), false);
    expect(zero.estado).toEqual({ marcos: [], cartoes: [] });
    expect(nivelDe(zero.estado)).toBe(0);
    expect(zero.novos).toEqual([]);
    for (const p of ["diario", "crescer", "lutar", "conversar", "itens", "forcar", "fronteira"] as const) expect(pecaAberta(zero.estado, p), p).toBe(false);
    const choca = sincronizar(zero.estado, marcosFeitos([new Motor(7)], tamer(0)), true);
    expect(nivelDe(choca.estado)).toBe(1);
    expect(choca.novos).toEqual([1]);
    expect(cartoesPendentes(choca.estado)).toEqual([1]);
    expect(pecaAberta(choca.estado, "diario")).toBe(false);
  });
  test("quem ja tem pet e nao tem a chave entra com o piso 4: Diario, Crescer, Lutar e Conversar abertos e os cartoes vistos em silencio", () => {
    const r = sincronizar(null, marcosFeitos([bebe], tamer(0)), true);
    expect(PISO_NIVEL).toBe(4);
    expect(r.estado.marcos).toEqual([1, 2, 3, 4]);
    expect(r.estado.cartoes).toEqual([1, 2, 3, 4]);
    expect(r.novos).toEqual([]);
    expect(cartoesPendentes(r.estado)).toEqual([]);
    for (const p of ["diario", "crescer", "lutar", "conversar"] as const) expect(pecaAberta(r.estado, p), p).toBe(true);
    expect(pecaAberta(r.estado, "itens")).toBe(false);
    expect(pecaAberta(r.estado, "forcar")).toBe(false);
    expect(pecaAberta(r.estado, "fronteira")).toBe(false);
  });
  test("so o Tamer nao vazio (sem pet) tambem entra pelo piso, com as medalhas que tem", () => {
    const r = sincronizar(null, marcosFeitos([], tamer(3)), true);
    expect(r.estado.marcos).toEqual([1, 2, 3, 4, 5, 7]);
    expect(nivelDe(r.estado)).toBe(6);
    expect(r.estado.cartoes).toEqual(r.estado.marcos);
  });
  test("um save de hoje no piso abre tudo o que abria antes, com os marcos que ele tem (Champion, 3 medalhas, Liga)", () => {
    const champ = sincronizar(null, marcosFeitos([champion], tamer(0)), true).estado;
    expect(champ.marcos).toEqual([1, 2, 3, 4, 6]);
    for (const p of ["diario", "crescer", "lutar", "conversar", "forcar"] as const) expect(pecaAberta(champ, p), p).toBe(true);
    const liga = sincronizar(null, marcosFeitos([champion], tamer(6, true)), true).estado;
    expect(liga.marcos).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
    for (const p of Object.keys(PECAS) as (keyof typeof PECAS)[]) expect(pecaAberta(liga, p), p).toBe(true);
  });
  test("com a chave, um marco novo vira 'novo' (o cartao e o brilho) e o resto fica", () => {
    const antes: EstadoNivel = { marcos: [1], cartoes: [1] };
    const r = sincronizar(antes, [1, 2], true);
    expect(r.novos).toEqual([2]);
    expect(r.estado).toEqual({ marcos: [1, 2], cartoes: [1] });
    expect(cartoesPendentes(r.estado)).toEqual([2]);
    expect(sincronizar(r.estado, [1, 2], true).estado).toBe(r.estado);       // nada mudou: o mesmo objeto
    expect(sincronizar(r.estado, [1, 2], true).novos).toEqual([]);
  });
  test("o nivel nunca desce: o pet guardado que sai nao tira o marco", () => {
    const e = sincronizar(null, marcosFeitos([champion], tamer(3)), true).estado;
    expect(nivelDe(e)).toBe(7);
    const depois = sincronizar(e, marcosFeitos([bebe], tamer(0)), true);
    expect(depois.estado).toBe(e);
    expect(nivelDe(depois.estado)).toBe(7);
    expect(depois.novos).toEqual([]);
    const sem = sincronizar(e, [], false);       // nem pet nem Tamer
    expect(nivelDe(sem.estado)).toBe(7);
  });
});

describe("a chave -nivel (o texto) e as acoes", () => {
  test("ida e volta do texto; sem a chave e null", () => {
    expect(lerEstado(null)).toBeNull();
    const e: EstadoNivel = { marcos: [1, 2, 3, 4], cartoes: [1, 2] };
    expect(lerEstado(textoEstado(e))).toEqual(e);
  });
  test("o texto que nao e o estado falha alto", () => {
    expect(() => lerEstado("{}")).toThrow(/marcos e cartoes/);
    expect(() => lerEstado('{"marcos":[0],"cartoes":[]}')).toThrow();
    expect(() => lerEstado('{"marcos":[1],"cartoes":"x"}')).toThrow();
    expect(() => lerEstado("nao json")).toThrow();
  });
  test("o estado lido ordena e tira repetidos", () => {
    expect(lerEstado('{"marcos":[3,1,1,2],"cartoes":[2,2]}')).toEqual({ marcos: [1, 2, 3], cartoes: [2] });
  });
  test("o cartao visto sai dos pendentes e nao volta", () => {
    let e: EstadoNivel = { marcos: [1, 2, 3], cartoes: [] };
    expect(cartoesPendentes(e)).toEqual([1, 2, 3]);
    e = marcarCartao(e, 2);
    expect(cartoesPendentes(e)).toEqual([1, 3]);
    expect(marcarCartao(e, 2)).toBe(e);
  });
  test("Ja conheco o jogo: abre 1 a 4 e pula os cartoes deles; os outros seguem os marcos", () => {
    const e = jaConheco({ marcos: [], cartoes: [] });
    expect(e).toEqual({ marcos: [1, 2, 3, 4], cartoes: [1, 2, 3, 4] });
    expect(pecaAberta(e, "crescer")).toBe(true);
    expect(pecaAberta(e, "itens")).toBe(false);
    const depois = sincronizar(e, [1, 2, 3, 4, 5], true);
    expect(depois.novos).toEqual([5]);
    expect(cartoesPendentes(depois.estado)).toEqual([5]);
  });
  test("Rever o tutorial: os cartoes voltam e os marcos ficam (nada tranca de novo)", () => {
    const e = reverTutorial({ marcos: [1, 2, 3, 4], cartoes: [1, 2, 3, 4] });
    expect(e.marcos).toEqual([1, 2, 3, 4]);
    expect(e.cartoes).toEqual([]);
    expect(cartoesPendentes(e)).toEqual([1, 2, 3, 4]);
  });
});
