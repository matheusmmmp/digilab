/* O cenario do lugar lembrado (a Fase 1 da auditoria da cadeia orgao-cerebro-mundo, PR-A; D1 aprovada pelo Matheus em 2026-11-11; nota no
   vault, 20 Temas/Auditoria — cadeia órgão-cérebro-mundo (Wobbledogs).md, secao 6). So um teste: nenhum codigo do jogo muda.
   O roteiro, pelo log, num pet de hoje (VERSAO_PET): dois dias em que o dono poe a racao sempre no mesmo lugar P quando a fome cai abaixo de 0,6;
   depois, ninguem poe mais nada e o tempo anda ate 50 h de jogo com a fome caindo e nenhuma comida a vista. O mesmo log roda com o DigiBrain
   modular (o padrao dos ovos novos, src/cerebro.ts) e com o cerebro A (a linha de base).
     T1, o modular: com fome e sem comida a vista, ele escolhe ir ao lugar lembrado perto de P, a sonda sem_memoria mostra que foi a memoria que
         decidiu (sem ela, outra escolha), e ele chega perto de P;
     T2, o A: com o mesmo log, ele nao chega perto de P sem comida a vista (o A nao ve o mundo nem lembra lugar: chama o dono). Em 4 das 5
         sementes o A nem comeu a racao do treino, que pode ficar no chao: por isso nele so conta o tempo sem comida a vista;
     T3, a visita vazia: chegando em P sem comida, o modular grava o episodio "nao_havia" na memoria;
     T4, o replay: o log refaz a mesma vida (a assinatura), nos dois cerebros.
   ACHADO desta etapa (registro, D-CADEIA-2): o lugar vazio nao perde valor nesta janela; depois de 11 visitas "nao_havia" o pet segue escolhendo
   o lugar. O teste nao trava isso: so registra que a visita vazia e gravada. */
import { describe, expect, test } from "vitest";
import { Motor } from "../motor/motor.ts";
import { TPD } from "../motor/constantes.ts";

/** o lugar da racao (as coordenadas do e2e de comer) e o raio de "chegou perto", nas unidades do mundo. PROPOSTOS, SEM FONTE */
const P: readonly [number, number] = [168, 248];
const PERTO = 16;
const SEMENTES = [101, 102, 103, 104, 105];
const PASSOS_FOME = 200;           // passos de 15 min: 50 h de jogo sem comida

function treinar(s: number, cerebro: "modular" | "a"): Motor {
  /* a v23 de forma explicita: o cenario foi medido no mundo de 64 x 30, com a racao em P = (168, 248), que na ilha grande (a v24, ILHA_AGUA,
     IG4) e mar. Na ilha grande, com a racao no comedouro de la, o modular faz o mesmo (medido na juncao: 26 e 25 escolhas do lugar
     lembrado nas sementes 101 e 105), mas o ponto lembrado cai a 16,5 unidades do comedouro, fora do raio PERTO de 16 deste teste */
  const m = new Motor(s, 23);
  m.trocarCerebro(cerebro);
  for (let p = 0; p < Math.round(2 * TPD / 30); p++) {
    m.avancar(30);
    if (m.e.fome < .6 && m.mundo!.comidas.size === 0) m.deixarComida("racao", P[0], P[1]);
    if (m.e.sujeira >= 2) m.observar("limpar");
  }
  return m;
}
const dist = (m: Motor): number => Math.hypot(m.mundo!.pet[0] - P[0], m.mundo!.pet[1] - P[1]);

interface Fome { memoriaDecidiu: boolean; escolhaPerto: boolean; chegou: boolean; vazias: number; m: Motor }
function semComida(m: Motor, exigirVazio: boolean): Fome {
  let memoriaDecidiu = false, escolhaPerto = false, chegou = false;
  const vazias0 = m.lab?.mem.episodios.filter(e => e.classe === "nao_havia").length ?? 0;
  for (let i = 0; i < PASSOS_FOME; i++) {
    m.avancar(15);
    const vazio = m.mundo!.comidas.size === 0;
    if (exigirVazio) expect(vazio, "o cenario e sem comida a vista").toBe(true);
    if (vazio && dist(m) <= PERTO) chegou = true;
    const l = m.leituraLab();
    if (!l || l.escolha[1] !== "ponto") continue;
    const ponto = l.escolha[2] as readonly [number, number];
    if (Math.hypot(ponto[0] - P[0], ponto[1] - P[1]) <= PERTO) escolhaPerto = true;
    if (l.alvo?.do_mem && l.sondas.find(x => x.nome === "sem_memoria")?.mudaria === true) memoriaDecidiu = true;
  }
  const vazias = (m.lab?.mem.episodios.filter(e => e.classe === "nao_havia").length ?? 0) - vazias0;
  return { memoriaDecidiu, escolhaPerto, chegou, vazias, m };
}

describe("o lugar lembrado: a fome sem comida vira procura no modular, e nao no A", () => {
  for (const s of SEMENTES) {
    test(`semente ${s}`, () => {
      const mod = treinar(s, "modular"), a = treinar(s, "a");
      expect(mod.mundo!.consumos.length, "o modular comeu no treino").toBeGreaterThan(0);
      expect(mod.lab, "o modular decide").not.toBeNull();
      expect(a.lab, "o A nao tem o DigiBrain modular").toBeNull();
      /* o A pode nao ter comido a racao do treino (ele so come com a fome entre 0,25 e 0,45: achado 3 da auditoria); entao, nele, "chegou perto"
         so conta enquanto nao ha comida a vista */
      const fm = semComida(mod, true), fa = semComida(a, false);
      /* T1 */
      expect(fm.escolhaPerto, "T1: escolheu o lugar lembrado perto de P").toBe(true);
      expect(fm.memoriaDecidiu, "T1: a memoria decidiu (a sonda sem_memoria muda a escolha)").toBe(true);
      expect(fm.chegou, "T1: chegou perto de P").toBe(true);
      /* T2 */
      expect(fa.chegou, "T2: o A nao vai a P sem ver a comida").toBe(false);
      /* T3 */
      expect(fm.vazias, "T3: a visita sem comida vira o episodio nao_havia").toBeGreaterThan(0);
      /* T4 */
      for (const m of [fm.m, fa.m]) expect(Motor.reproduzir(m.semente, m.log, m.versao).assinatura()).toBe(m.assinatura());
    });
  }
});
