/* MMO0 (docs/PLANO_V3_MMO.md, secao 12; docs/TAREFA_V3_MMO.md): a vida roteirizada que roda igual no Chrome e no Node. O mesmo codigo vai
   para o Chrome num pacote (scripts/mmo0/pagina.ts) e roda no Node direto (scripts/medir_mmo0.ts). O ovo nasce como no jogo
   (src/produto.ts: as chaves do produto, o cerebro e a ponte da luta, na versao dos ovos novos, VERSAO_PET), e o dono e um roteiro: cuida
   pela fome, pela sujeira e pela lesao, faz carinho e brinca de vez em quando, e, do Rookie em diante, luta na Arena da POC. O roteiro le o
   estado do pet, entao a vida gravada no Chrome e a do Chrome: se o corpo divergir, o roteiro pode divergir junto, e a medida pega.
   So engenharia: nenhuma run de pesquisa, nenhuma faixa de sementes (as sementes sao as dos testes, 101 em diante). */
import { IDS_CENA, Motor, PetMorto, VERSAO_PET, hashSemente, type EventoRegistro } from "../../motor/index.ts";
import { ligarProduto } from "../../src/produto.ts";

/** quantos passos de 10 ticks no maximo, e de quantos em quantos passos se guarda o marco (PROPOSTO, SEM FONTE) */
export const PASSOS_MAX = 2000, MARCO_A_CADA = 50;

/** uma luta, como o jogador a ve: o rival, a semente, se venceu, se saiu lesionado , e, em cada luta da serie, a vida que sobrou a cada lado e os passos */
export interface LutaVista { indice: number; rival: string; semente: number; venceu: boolean; lesao: boolean; vidas: number[] }
/** o marco: depois do evento indice-1 do registro, o hash da assinatura */
export interface Marco { indice: number; hash: string }
export interface Vida {
  semente: number; cerebro: "modular" | "a"; versao: number; passos: number; morreu: boolean;
  log: EventoRegistro[]; assinatura: string; hashAssinatura: string; estado: string; lutas: LutaVista[]; marcos: Marco[]; ms: number;
}

/** FNV-1a de 32 bits, em hexadecimal: so para comparar marcos sem guardar a assinatura inteira (nao e seguranca) */
export function fnv(texto: string): string {
  let h = 0x811c9dc5;
  for (let i = 0; i < texto.length; i++) { h ^= texto.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
  return h.toString(16).padStart(8, "0");
}

/** o roteiro: o dado do passo p (0..999), derivado da semente da vida (a mesma conta nos dois runtimes: so inteiros) */
const dado = (semente: number, p: number): number => hashSemente("mmo0-roteiro", semente, p) % 1000;

export function viver(semente: number, cerebro: "modular" | "a"): Vida {
  const t0 = performance.now();
  const m = ligarProduto(new Motor(semente, VERSAO_PET));
  if (cerebro === "a") m.trocarCerebro("a");   // no jogo, a escolha de Ajustes vai no "cb" do ovo; aqui, um "cb" a mais logo depois
  const lutas: LutaVista[] = [], marcos: Marco[] = [];
  let p = 0;
  for (; p < PASSOS_MAX && !m.morte; p++) {
    m.avancar(10);
    if (m.morte) break;
    const d = dado(semente, p);
    try {
      if (m.e.fome < .6) m.deixarComida("racao", Math.max(0, Math.min(1023, m.mundo!.pet[0] + 24)), m.mundo!.pet[1]);
      if (m.e.sujeira >= 2) m.observar("limpar");
      if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
      if (d < 60) m.observar("acariciar");
      else if (d < 100) m.observar("brincar");
      if (m.estagioAtual !== "bebe" && !m.morte && d >= 750) {
        const rv = m.rivaisArenaPoc(), k = lutas.length, s = hashSemente("mmo0-luta", semente, k);
        const r = m.lutarPoc(rv[d % rv.length], s, IDS_CENA[k % IDS_CENA.length]);
        lutas.push({ indice: m.log.length - 1, rival: r.rival, semente: s, venceu: r.venceu, lesao: r.lesao, vidas: r.serie.flatMap(x => [x.vidaA, x.vidaB, x.passos]) });
      }
    } catch (err) {
      if (err instanceof PetMorto) break;
      /* o motor recusou a acao (dormindo, por exemplo): o roteiro segue, como o medir_replay_lp2 */
    }
    if ((p + 1) % MARCO_A_CADA === 0) marcos.push({ indice: m.log.length, hash: fnv(m.assinatura()) });
  }
  const assinatura = m.assinatura();
  return { semente, cerebro, versao: m.versao, passos: p, morreu: !!m.morte, log: JSON.parse(JSON.stringify(m.log)) as EventoRegistro[],
    assinatura, hashAssinatura: fnv(assinatura), estado: JSON.stringify(m.e), lutas, marcos, ms: +(performance.now() - t0).toFixed(1) };
}
