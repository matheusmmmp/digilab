/* A Fabrica e o Salao da Fronteira de Batalha no app (docs/DESIGN_FRONTEIRA.md, secoes 3 e 4; medalhas parte 4c; motor/fabrica.ts e
   motor/salao.ts). Tudo passa pelas portas de sempre: o Tamer muda so por jogo.mudarTamer, o pet ativo so por jogo.mudarMotor e os guardados
   so por pets.atualizarGuardado.
   - Fabrica: nenhum pet luta; o alugado, as lutas e as trocas vao para o registro do Tamer.
   - Salao: um pet de cada estagio, entre o ativo e os guardados (so v6). Um guardado que luta recebe no registro dele, na hora parada em
     que esta, o que o ativo receberia (o "u" das medalhas e o "f" da Fronteira, tamer.sincronizarPet) e a luta; ele continua guardado. A
     tentativa e jogada antes em copias (o resultado do motor e deterministico) e so entao gravada: nos registros dos pets, na ordem, e
     por fim no Tamer. Se a gravacao der outro resultado que a copia, falha alto. */
import { ESTAGIOS_SALAO, LUTAS_SERIE_FABRICA, Motor, NOME_EST, RIVAL_SALAO, chaveSprite, formaRivalSalao, nomeForma, type Estagio, type Forma, type LutaFabrica,
  VERSAO_FABRICA_ATUAL } from "../motor/index.ts";
import { jogoAtual, mudarMotor, mudarTamer, tamerAtual } from "./jogo.ts";
import { abrirGuardado, atualizarGuardado, ehGrupoGuardado, lerGuardados } from "./pets.ts";
import { sincronizarPet, type LutaSalao, type Tamer, type TentativaSalao } from "./tamer.ts";
import { assistirPoc, fimDoPet, ladoDesenho, lutasDoResultado, type LutaNaTela } from "./lutaPocTela.ts";
import { MAPA_FABRICA, type ResultadoLutaPoc } from "../motor/index.ts";

/* ------------------------------------------------ Fabrica */
/** comeca a tentativa nova da Fabrica com o alugado i (0 a 2) */
/* a tentativa nova grava as regras da luta da POC (v: 21; LP2b), as unicas desde a LP4 */
export const alugarFabrica = (i: number): void => { mudarTamer(t => t.alugarFabrica(i, Date.now(), VERSAO_FABRICA_ATUAL)); };
/** a proxima luta da tentativa em andamento (so no registro do Tamer), e depois ela no palco da luta da POC (LP3) */
export const lutarFabrica = (): void => {
  let luta: LutaFabrica | null = null;
  mudarTamer(t => { luta = t.lutarFabrica(); });
  const x = luta as LutaFabrica | null;
  if (!x) throw new Error("a luta da Fábrica não voltou do registro do Tamer");
  const serieF = Math.floor(x.k / LUTAS_SERIE_FABRICA) + 1, naSerieF = x.k % LUTAS_SERIE_FABRICA + 1;
  /* a Fabrica da luta da POC (v21, LP2b) no palco novo (LP3): a mesma entrada que a TentativaFabrica usou (o alugado leva a vida dentro da
     serie, menos logo depois de uma troca; cada rival entra inteiro). O palco confere o fim com o do registro */
  const tent = tamerAtual().fabrica[tamerAtual().fabrica.length - 1], ant = tent.lutas[tent.lutas.length - 2];
  if (!tent || tent.lutas[tent.lutas.length - 1].k !== x.k) throw new Error("a tentativa da Fábrica não bate com a luta que voltou");
  const v0 = naSerieF > 1 && ant && !ant.trocou ? ant.poc.vidaA : undefined, ka = chaveSprite(x.alugado), kr = chaveSprite(x.rival);
  const lt: LutaNaTela = {
    entrada: { cena: MAPA_FABRICA, semente: x.s, a: { forma: ka, stats: tent.statsPoc(x.alugado), ...(v0 !== undefined ? { vida0: v0 } : {}) }, b: { forma: kr, stats: tent.statsPoc(x.rival) } },
    esperado: { vencedor: x.poc.vencedor, relogio: x.poc.relogio, passos: x.poc.passos, ko: x.poc.vidaA <= 0 || x.poc.vidaB <= 0 },
    A: ladoDesenho(ka), B: ladoDesenho(kr), rotulo: `série ${serieF}, luta ${naSerieF} de ${LUTAS_SERIE_FABRICA}`,
  };
  assistirPoc([lt], "Fronteira · Fábrica", L => fimDoPet(L, lt.A, lt.B, x.venceu ? "O alugado segue na tentativa." : "A tentativa acabou."));
};
/** troca o alugado pelo rival que ele acabou de derrotar */
export const trocarFabrica = (): void => { mudarTamer(t => t.trocarFabrica()); };

/* ------------------------------------------------ Salao */
/** de onde vem o pet: o ativo ou o guardado i */
export type OrigemPet = "ativo" | number;
/** um pet que o Salao ve: ele como lutaria agora (o ativo; ou a copia sincronizada com o Tamer do guardado, nada gravado; so leitura), o
    estagio e, se nao pode lutar, o porque */
export interface CandidatoSalao { origem: OrigemPet; semente: number; m: Motor; nome: string; est: Estagio; erro: string | null }

/** a copia do pet como ele lutaria no Salao agora: reproduzido do registro e com o que o Tamer daria a ele (so na copia) */
function copiaSincronizada(t: Tamer, semente: number, log: Motor["log"], versao: number): Motor {
  const m = Motor.reproduzir(semente, log, versao);
  sincronizarPet(t, m);
  return m;
}
/** os pets do jogador (o ativo e os guardados) que o Salao ve, com o estagio de cada um. O ativo e o proprio (o app ja o sincroniza a cada
    mudanca; so leitura); os guardados, copias sincronizadas. Os guardados que nao abrem falham alto */
export function candidatosSalao(t: Tamer = tamerAtual()): CandidatoSalao[] {
  const out: CandidatoSalao[] = [], a = jogoAtual().motor;
  const junta = (origem: OrigemPet, m: Motor) => out.push({ origem, semente: m.semente, m, nome: nomeForma(m.forma), est: m.estagioAtual, erro: m.porqueNaoSalao() });
  junta("ativo", a);
  lerGuardados().forEach((g, i) => { if (!ehGrupoGuardado(g)) junta(i, copiaSincronizada(t, g.semente, g.log, g.versao)); });   // o par dos dois pets fica fora (CO4d)
  return out;
}
/** os estagios do Salao sem nenhum pet que possa lutar */
export const estagiosQueFaltam = (c: readonly CandidatoSalao[]): Estagio[] => ESTAGIOS_SALAO.filter(e => !c.some(x => x.est === e && !x.erro));

/** uma luta de uma tentativa do Salao, para a tela: o nivel, o pet, o rival (sorteado da semente e do estagio) e o resultado */
export interface LutaSalaoTela { est: Estagio; nome: string; rival: Forma; venceu: boolean; segundos: number }
/** a tentativa: as lutas (ate a primeira que nao foi vitoria) e o evento do Tamer */
export interface ResultadoSalao { tentativa: TentativaSalao; lutas: LutaSalaoTela[];
  /** as lutas no palco da luta da POC (LP3), uma por nivel */
  poc: LutaNaTela[] }
const nivel = (e: Estagio): string => NOME_EST[e];

/** uma tentativa do Salao com os pets escolhidos (um por estagio, na ordem de ESTAGIOS_SALAO) */
export function tentarSalao(escolha: readonly OrigemPet[]): ResultadoSalao {
  const t = tamerAtual();
  if (!t.titulo) throw new Error("o Salão abre depois do título da Liga dos Líderes");
  if (escolha.length !== ESTAGIOS_SALAO.length) throw new Error(`o Salão pede um pet de cada nível (${ESTAGIOS_SALAO.length})`);
  if (new Set(escolha).size !== escolha.length) throw new Error("o mesmo pet em dois níveis do Salão");
  const cands = candidatosSalao(t);
  /* 1. a tentativa nas copias: quem luta, com que semente, e quem venceu (para na primeira que nao for vitoria) */
  const plano: { c: CandidatoSalao; luta: LutaSalao; poc: ResultadoLutaPoc }[] = [];
  for (const [i, est] of ESTAGIOS_SALAO.entries()) {
    const c = cands.find(x => x.origem === escolha[i]);
    if (!c) throw new Error(`o pet escolhido para o nível ${nivel(est)} não está mais aqui`);
    if (c.erro) throw new Error(`${c.nome}: ${c.erro}`);
    if (c.est !== est) throw new Error(`${c.nome} é ${nivel(c.est)}, não ${nivel(est)}`);
    const m = copiaSincronizada(t, c.m.semente, c.m.log, c.m.versao), k = m.salao.tentativas + 1, s = m.sementeSalao();
    /* o Salao da luta da POC (LP2b): Motor.lutarPoc, e o palco novo (LP3) */
    const rp = m.lutarPoc(RIVAL_SALAO, s, null);
    plano.push({ c, poc: rp, luta: { est, pet: c.semente, forma: c.nome, k, s, tick: m.e.tick, venceu: rp.venceu } });
    if (!rp.venceu) break;
  }
  /* 2. a gravacao: a luta de cada um no registro dele (o ativo pela porta de sempre; o guardado continua guardado) */
  for (const { c, luta } of plano) {
    let venceu: boolean;
    if (c.origem === "ativo") {
      venceu = false;
      mudarMotor(m => {
        if (m.semente !== c.semente) throw new Error("o pet ativo mudou antes da luta do Salão");
        venceu = m.lutarPoc(RIVAL_SALAO, luta.s, null).venceu;
      });
    } else {
      const g = lerGuardados()[c.origem];
      if (!g || g.semente !== c.semente) throw new Error(`o pet guardado ${c.nome} mudou antes da luta do Salão`);
      const m = abrirGuardado(g);
      sincronizarPet(tamerAtual(), m);
      venceu = m.lutarPoc(RIVAL_SALAO, luta.s, null).venceu;
      atualizarGuardado(c.origem, m);
    }
    if (venceu !== luta.venceu) throw new Error(`a luta de ${c.nome} no Salão deu outro resultado ao gravar`);
  }
  /* 3. a tentativa no registro do Tamer (o recorde sai dela) */
  const tentativa = mudarTamer(tm => tm.registrarSalao(plano.map(p => p.luta)));
  const poc = plano.map((p, i) => ({ ...lutasDoResultado(p.poc)[0], rotulo: `nível ${nivel(p.luta.est)} (${i + 1} de ${ESTAGIOS_SALAO.length})` }));
  return { tentativa, poc,
    lutas: plano.map(p => ({ est: p.luta.est, nome: p.c.nome, rival: formaRivalSalao(p.luta.s, p.luta.est), venceu: p.luta.venceu,
      segundos: Math.round(p.poc.serie[0].relogio / 1000) })) };
}
/** a tentativa do Salao no palco da luta da POC (LP3): as lutas, um pet de cada nivel, ate a primeira que nao foi vitoria */
export function mostrarSalao(r: ResultadoSalao): void {
  const n = ESTAGIOS_SALAO.length, v = r.lutas.filter(x => x.venceu).length, lutas = r.poc;
  assistirPoc(lutas, "Fronteira · Salão", L => fimDoPet(L, lutas[lutas.length - 1].A, lutas[lutas.length - 1].B, v === n ? `Venceu os ${n} níveis!` : `Venceu ${v} de ${n} níveis seguidos.`));
}
