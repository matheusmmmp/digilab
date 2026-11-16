/* EVIDENCIA A2: a ablacao do aprendizado no jogo (docs/PLANO_ANALISE_V3_ABLACAO_APRENDIZADO.md, registrado antes de qualquer vida). Uma vida =
   (semente, dono, braco): o ovo do jogo de hoje (VERSAO_PET, montado como o jogo e o scripts/equilibrio_cuidado/e0.ts montam), com um dono
   sintetico do motor (motor/donos.ts, no laco do test/evolucao_canonica.test.ts, sem luta), por 3 dias. O braco A e o pet como o jogo o choca;
   o braco B e o mesmo pet com um involucro na instancia, de fora, no `m.lab.impulso.unidades`: antes de cada leitura, o H, o desfecho e o andar
   do M-PLAST vao a 0 no lugar (secao 2.2 do plano). Nenhum arquivo do motor muda. So le o motor.

     node scripts/ablacao_aprendizado.ts --primeira S --k K [--dias 3] [--teste] --saida arquivo.json

   As sementes S...S+K-1 saem da faixa 98101...98505 (a run), ou das de teste 101...505 com --teste. Cada vida roda duas vezes (o sha da
   sequencia das decisoes tem de sair igual), e a do braco A e refeita pelo replay do jogo (Motor.reproduzir). Falha alto em toda conferencia. */
import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import {
  ACOES_DONO_JOGO_V11, CD, Motor, PetMorto, TPD, VERSAO_PET, criarDono, criarRng, hashSemente, type AcaoDono, type EventoRegistro, type TipoDono, type VisaoDono,
} from "../motor/index.ts";
import { COMPORTAMENTOS_DIGIBRAIN } from "../motor/digibrain/constantes.ts";

export const DONOS: readonly TipoDono[] = ["atencioso", "relapso", "incoerente"];
export const BRACOS = ["A", "B"] as const;
export type Braco = typeof BRACOS[number];
export const FAIXA = [98101, 98505] as const;
export const FAIXA_TESTE = [101, 505] as const;
export const DIAS = 3;
/** os grupos do motivo (secao 3 do plano): o tipo_escolha agrupado; um tipo fora deles falha alto */
export const CLASSES_COMIDA = ["racao", "a", "b", "c", "podre"] as const;
export const GRUPOS_TIPO = ["comida", "cheiro", "bola", "vagar", "ponto", "sem_objeto"] as const;
const PRODUTO = { chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true };
/** AB-2b (Matheus, 2026-11-16, "Mapear para acariciar/tapa"): o retorno do dono sintetico vira o gesto do jogo, a correspondencia da tela
 *  (Elogiar = acariciar, Repreender = tapa; docs/registro, elogiar e repreender). Sem isso, o incoerente sai igual ao atencioso */
export const GESTO_DO_JOGO: Readonly<Record<string, AcaoDono>> = { elogiar: "acariciar", repreender: "tapa" };
export const paraOJogo = (a: AcaoDono): AcaoDono => GESTO_DO_JOGO[a] ?? a;

const sha = (x: string): string => createHash("sha256").update(x).digest("hex");
type Dict = Record<string, unknown>;

export function grupoDoTipo(tipo: unknown): typeof GRUPOS_TIPO[number] {
  if (tipo === null) return "sem_objeto";
  if ((CLASSES_COMIDA as readonly unknown[]).includes(tipo)) return "comida";
  if (tipo === "cheiro" || tipo === "bola" || tipo === "vagar" || tipo === "ponto") return tipo;
  throw new Error(`tipo_escolha desconhecido: ${JSON.stringify(tipo)}`);
}

/** o ovo como o jogo choca hoje */
export function nascer(semente: number): Motor {
  const m = new Motor(semente, VERSAO_PET);
  m.ligarProduto(PRODUTO);
  m.trocarCerebro("modular");
  m.ligarPonteLuta(true);
  if (m.cerebroAtual !== "modular" || m.lab === null) throw new Error("o pet nao decide com o modular");
  const cd = m.lab.cd as { p1?: unknown; p2?: unknown };
  if (cd.p1 !== true || cd.p2 !== true) throw new Error(`o M-PLAST sem o P1 e o P2 ligados: ${JSON.stringify({ p1: cd.p1, p2: cd.p2 })}`);
  return m;
}

/** o braco B (secao 2.2): o involucro na instancia, que zera no lugar o estado aprendido antes de cada leitura do impulso */
export function zerarAntesDeCadaDecisao(m: Motor): { leituras: () => number } {
  const lab = m.lab;
  if (lab === null) throw new Error("sem o modular");
  const imp = lab.impulso as unknown as { unidades: (...a: unknown[]) => unknown };
  const original = imp.unidades.bind(imp);
  const p = lab.plast;
  let n = 0;
  imp.unidades = (...a: unknown[]) => {
    for (const k of Object.keys(p.H)) p.H[k]!.fill(0);
    if (p.desfecho !== null) for (const k of Object.keys(p.desfecho)) p.desfecho[k]!.fill(0);
    p.andar = 0;
    n += 1;
    return original(...a);
  };
  return { leituras: () => n };
}

export interface RegistroVida {
  semente: number; dono: TipoDono; braco: Braco; dias: number; decisoes: number; morte: string | null; recusas: number;
  acoes: Record<string, number>; tipos: Record<string, number>; reflexo: number; nada_a_fazer: number;
  escolhida: { incentivo: number; habito: number; fora_da_lista: number }; unidades_com_aprendido: number; leituras_zeradas: number | null;
  log_sha256: string; decisoes_sha256: string;
}

/** a vida, uma execucao: o motor e o registro */
function executar(semente: number, dono: TipoDono, braco: Braco, dias: number): { m: Motor; log: EventoRegistro[]; reg: RegistroVida } {
  const m = nascer(semente);
  const z = braco === "B" ? zerarAntesDeCadaDecisao(m) : null;
  const d = criarDono(dono), r = criarRng(hashSemente("dono", semente, dono));
  const passos = Math.round(dias * TPD / CD.passo), orc = Math.round(16 * dias);
  let gasto = 0, recusas = 0;
  for (let p = 0; p < passos && !m.morte; p++) {
    m.avancar(CD.passo);
    if (m.morte) break;
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v: VisaoDono = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos,
      chamados: m.chamadosAbertos() };
    for (const a of d.decidir(v, r).map(paraOJogo).filter(x => ACOES_DONO_JOGO_V11.includes(x))) {
      try { m.observar(a); } catch (err) { if (err instanceof PetMorto) throw err; recusas += 1; }   // o motor recusou (como no dc3d): conta
      gasto += 1;
    }
  }
  const motivos = m.lab!.motivos as Dict[];
  const acoes = Object.fromEntries(COMPORTAMENTOS_DIGIBRAIN.map(b => [b, 0])) as Record<string, number>;
  const tipos = Object.fromEntries(GRUPOS_TIPO.map(g => [g, 0])) as Record<string, number>;
  let reflexo = 0, nada = 0, inc = 0, hab = 0, comAprendido = 0, fora = 0;
  for (const mo of motivos) {
    const a = mo["acao"] as string;
    if (!(a in acoes)) throw new Error(`acao fora dos COMPORTAMENTOS_DIGIBRAIN: ${JSON.stringify(a)}`);
    acoes[a]! += 1;
    tipos[grupoDoTipo(mo["tipo_escolha"])]! += 1;
    if (mo["reflexo"] === true) reflexo += 1; else if (mo["reflexo"] !== false) throw new Error("reflexo sem bool");
    if (mo["nada_a_fazer"] === true) nada += 1; else if (mo["nada_a_fazer"] !== false) throw new Error("nada_a_fazer sem bool");
    const us = mo["unidades"] as { chave: unknown; termos: Record<string, number> }[];
    for (const u of us) if ((u.termos["incentivo"] ?? 0) !== 0 || (u.termos["habito"] ?? 0) !== 0) comAprendido += 1;
    const ce = JSON.stringify(mo["escolha"]), esc = us.find(u => JSON.stringify(u.chave) === ce);   // as chaves sao listas
    if (esc === undefined) { fora += 1; continue; }        // a escolha fora da lista (o reflexo ou a intencao que segue): sem termos
    inc += esc.termos["incentivo"] ?? 0;
    hab += esc.termos["habito"] ?? 0;
  }
  if (braco === "B" && comAprendido !== 0) throw new Error(`o braco B com ${comAprendido} unidades com incentivo ou habito diferente de 0`);
  const log = JSON.parse(JSON.stringify(m.log)) as EventoRegistro[];
  const reg: RegistroVida = {
    semente, dono, braco, dias, decisoes: motivos.length, morte: m.morte ? String(m.morte.causa) : null, recusas, acoes, tipos, reflexo,
    nada_a_fazer: nada, escolhida: { incentivo: inc, habito: hab, fora_da_lista: fora }, unidades_com_aprendido: comAprendido,
    leituras_zeradas: z === null ? null : z.leituras(), log_sha256: sha(JSON.stringify(log)),
    decisoes_sha256: sha(JSON.stringify(motivos.map(mo => [mo["acao"], mo["tipo_escolha"], mo["escolha"]]))),
  };
  return { m, log, reg };
}

/** a vida conferida (secao 4): duas execucoes iguais e, no braco A, o replay do jogo com as mesmas decisoes */
export function vida(semente: number, dono: TipoDono, braco: Braco, dias = DIAS): RegistroVida {
  if (!DONOS.includes(dono)) throw new Error(`dono desconhecido: ${JSON.stringify(dono)}`);
  if (!(BRACOS as readonly string[]).includes(braco)) throw new Error(`braco desconhecido: ${JSON.stringify(braco)}`);
  if (!Number.isInteger(dias) || dias < 1) throw new Error(`dias precisa ser inteiro >= 1: ${dias}`);
  const um = executar(semente, dono, braco, dias), dois = executar(semente, dono, braco, dias);
  if (um.reg.decisoes_sha256 !== dois.reg.decisoes_sha256 || um.reg.log_sha256 !== dois.reg.log_sha256)
    throw new Error(`a vida (${semente}, ${dono}, ${braco}) nao sai igual em duas execucoes`);
  if (braco === "A") {
    const rep = Motor.reproduzir(semente, um.log, VERSAO_PET);
    const a0 = JSON.stringify((um.m.lab!.motivos as Dict[]).map(mo => mo["acao"]));
    const a1 = JSON.stringify(((rep.lab?.motivos ?? []) as Dict[]).map(mo => mo["acao"]));
    if (a0 !== a1) throw new Error(`o replay da vida (${semente}, ${dono}, A) muda as decisoes`);
  }
  return um.reg;
}

export function sementesDe(primeira: number, k: number, teste: boolean): number[] {
  if (!Number.isInteger(primeira) || !Number.isInteger(k) || k < 1) throw new Error(`--primeira e --k inteiros, k >= 1: ${primeira}, ${k}`);
  const [lo, hi] = teste ? FAIXA_TESTE : FAIXA;
  if (primeira < lo || primeira + k - 1 > hi) throw new Error(`as sementes ${primeira}...${primeira + k - 1} fora da faixa ${lo}...${hi}`);
  return Array.from({ length: k }, (_, i) => primeira + i);
}

/** todas as vidas, na ordem (semente, dono, braco) */
export function todas(sementes: readonly number[], dias = DIAS): RegistroVida[] {
  const out: RegistroVida[] = [];
  for (const s of sementes) for (const d of DONOS) for (const b of BRACOS) out.push(vida(s, d, b, dias));
  if (!out.some(r => r.braco === "A" && r.unidades_com_aprendido > 0)) throw new Error("o braco A sem nenhuma unidade com o aprendido: a manipulacao nao manipula");
  return out;
}

function argumentos(argv: readonly string[]): { primeira: number; k: number; dias: number; teste: boolean; saida: string } {
  const o: Record<string, string | boolean> = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]!;
    if (a === "--teste") { o["teste"] = true; continue; }
    if (!["--primeira", "--k", "--dias", "--saida"].includes(a) || argv[i + 1] === undefined) throw new Error(`argumento desconhecido: ${a}`);
    o[a.slice(2)] = argv[++i]!;
  }
  if (typeof o["primeira"] !== "string" || typeof o["k"] !== "string" || typeof o["saida"] !== "string") throw new Error("faltam --primeira, --k ou --saida");
  return { primeira: Number(o["primeira"]), k: Number(o["k"]), dias: o["dias"] === undefined ? DIAS : Number(o["dias"]), teste: o["teste"] === true,
    saida: o["saida"] as string };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const a = argumentos(process.argv.slice(2));
  const vidas = todas(sementesDe(a.primeira, a.k, a.teste), a.dias);
  mkdirSync(dirname(a.saida), { recursive: true });
  writeFileSync(a.saida, JSON.stringify({ harness: fileURLToPath(import.meta.url).replace(/\\/g, "/").split("/web/app/")[1] ?? null,
    node: process.version, versao_pet: VERSAO_PET, donos: DONOS, bracos: BRACOS, dias: a.dias, sementes: [a.primeira, a.k], teste: a.teste,
    vidas }, null, 1) + "\n");
}
