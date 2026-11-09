/* LUTA_POC, LP2b: os torneios de um pet v21 (a Liga, a Torre de Batalha e o Salao) e a Fabrica da luta da POC (no registro do Tamer). A mesma
   funcao serve ao gabarito (test/gabaritos/lp2b_torneios_v21.json), ao teste e ao gerador (node test/lp2b_torneios.ts --gravar). So le o
   motor. */
import { createHash } from "node:crypto";
import { writeFileSync } from "node:fs";
import { MEDALHAS_LIGA, Motor, RIVAL_LIGA, RIVAL_SALAO, TentativaFabrica, VERSAO_FABRICA_POC, VERSAO_V21, sementeFabrica, type EventoRegistro } from "../motor/index.ts";

export const SEMENTES_LP2B = [101, 202, 303, 404, 505] as const;
const PRODUTO = { chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true };
const sha = (x: string): string => createHash("sha256").update(x).digest("hex");

/** um pet v21 que ja e Rookie, com as 6 medalhas e o titulo da Liga conhecidos (eventos "u" e "f"): pode entrar nos torneios */
export function petDosTorneios(semente: number): Motor {
  const m = new Motor(semente, VERSAO_V21);
  m.ligarProduto(PRODUTO); m.trocarCerebro("modular"); m.ligarPonteLuta(true);
  for (let p = 0; m.estagioAtual === "bebe" && p < 2000; p++) {
    m.avancar(30);
    if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, m.mundo!.pet[0] + 24)), m.mundo!.pet[1]);
    if (m.e.sujeira >= 2) m.observar("limpar");
  }
  if (m.estagioAtual === "bebe") throw new Error("o pet nao chegou a Rookie");
  m.liberar(MEDALHAS_LIGA);
  m.abrirFronteira();
  return m;
}

const resumo = (R: ReturnType<Motor["lutarPoc"]>): string =>
  `${R.rival}:${R.serie.map(x => `${x.contra}@${x.mapa}/${x.vencedor}/${x.relogio}/${x.vida0}/${x.vidaA}/${x.vidaB}`).join(";")}`;

export interface VidaTorneios { semente: number; eventos: number; lutas: number; liga: number; torre: number; salao: number; log_sha: string; assinatura: string; resultados: string }

const EXERCICIOS = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"] as const;
/** treina o pet `sessoes` vezes (um exercicio a cada 30 ticks, com o cuidado de sempre): o treino sobe os stats e a luta (LP-3) */
export function treinarMuito(m: Motor, sessoes: number): void {
  for (let p = 0; p < sessoes && !m.morte; p++) {
    m.avancar(30);
    try {
      if (m.e.fome < .6) m.deixarComida("racao", Math.max(0, Math.min(1023, m.mundo!.pet[0] + 24)), m.mundo!.pet[1]);
      if (m.e.sujeira >= 2) m.observar("limpar");
      m.treinar(EXERCICIOS[p % EXERCICIOS.length]);
    } catch { /* o motor recusou (dormindo, por exemplo): segue */ }
  }
}
export const SESSOES_LP2B = 1500;

/** a Liga, a Torre e o Salao, nessa ordem, num pet muito treinado (para as series passarem da primeira luta), tratando a lesao entre eles */
export function viverTorneios(semente: number): { m: Motor; log: EventoRegistro[]; res: string[] } {
  const m = petDosTorneios(semente), res: string[] = [];
  treinarMuito(m, SESSOES_LP2B);
  const tratar = () => { if (m.lesionadoDesde !== null) m.observar("tratar_lesao"); };
  res.push(resumo(m.lutarPoc(RIVAL_LIGA, 7001 + semente, null))); tratar(); m.avancar(30);
  res.push(resumo(m.lutarPoc("torre_batalha", m.sementeInstalacao("torre_batalha"), null))); tratar(); m.avancar(30);
  res.push(resumo(m.lutarPoc(RIVAL_SALAO, m.sementeSalao(), null)));
  return { m, log: JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], res };
}
export function gravarTorneios(semente: number, m: Motor, log: readonly EventoRegistro[], res: readonly string[]): VidaTorneios {
  /* as lutas jogadas nos tres torneios (as contagens do pet zeram a cada evolucao, e o treino o faz evoluir) */
  return { semente, eventos: log.length, lutas: res.reduce((a, r) => a + r.split(";").length, 0), liga: m.liga.tentativas, torre: m.instalacoes.torre_batalha.tentativas, salao: m.salao.tentativas,
    log_sha: sha(JSON.stringify(log)), assinatura: sha(m.assinatura()), resultados: sha(JSON.stringify(res)) };
}

/** a tentativa n da Fabrica da luta da POC, jogada ate acabar: troca o alugado pelo derrotado nas vitorias de numero par */
export function tentativaFabrica(n: number, escolha = 0): { t: TentativaFabrica; resumo: string } {
  const t = new TentativaFabrica(n, escolha, VERSAO_FABRICA_POC);
  for (let i = 0; i < 60 && !t.acabou; i++) {
    const l = t.lutar(t.proxima()!.s);
    if (l.venceu && t.vitorias % 2 === 0 && !t.porqueNaoTroca()) t.trocar();
  }
  return { t, resumo: t.lutas.map(l => `${l.k}/${l.venceu ? 1 : 0}/${l.poc!.relogio}/${l.poc!.vidaA}/${l.trocou ? "T" : ""}`).join(";") };
}

if (process.argv.includes("--gravar")) {
  const vidas = SEMENTES_LP2B.map(s => { const { m, log, res } = viverTorneios(s); return gravarTorneios(s, m, log, res); });
  const fabrica = [1, 2, 3, 4, 5].map(n => { const { t, resumo } = tentativaFabrica(n, n % 3); return { n, s: sementeFabrica(n), series: t.series, lutas: t.lutas.length, resumo: sha(resumo) }; });
  writeFileSync(new URL("./gabaritos/lp2b_torneios_v21.json", import.meta.url), JSON.stringify({ versao: 1, sementes: SEMENTES_LP2B, vidas, fabrica }, null, 1) + "\n");
  console.log(`gravado: ${vidas.length} vidas (${vidas.reduce((a, v) => a + v.lutas, 0)} lutas), ${fabrica.length} tentativas da Fábrica`);
}
