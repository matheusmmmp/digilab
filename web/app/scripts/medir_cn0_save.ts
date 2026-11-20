/* CONTA, etapa CN0 (docs/PLANO_V3_CONTA.md, secao 10; docs/ROADMAP_V3_CONTA.md, F0): o tamanho do save do jogo web por dia de jogo, para a
   sincronizacao por eventos da CN3. Grava vidas tipicas no Node, pelo mesmo motor e as mesmas funcoes do Tamer que o jogo usa, e mede, ao fim
   de cada dia de jogo (TPD ticks):
     - o save do pet de um so ({semente, log, versao}, o textoSave do save.ts) e o do grupo dos dois pets ({..., grupo: true, foco}, o
       textoSaveGrupo; VERSAO_GRUPO), em bytes UTF-8, cru, gzip (nivel 9) e brotli (qualidade 11);
     - o numero de eventos no registro e os eventos novos do dia (o que a sincronizacao mandaria);
     - o registro do Tamer (CHAVE-tamer, o textoTamer: medalhas, itens, titulo, recordes, Bits), pelas funcoes conferir* do tamer.ts;
   e, no fim, os guardados (CHAVE-guardados: os pets das outras vidas do mesmo perfil, como Guardado) e Gerações (CHAVE-geracoes: o
   primeiro pet aposentado, como Aposentado), e a soma do que iria para a nuvem.
   Os perfis sao PROPOSTO, SEM FONTE (nao ha medida de como o jogador joga): o dedicado (o dono atencioso dos Cenarios a cada passo, treino e
   lutas todo dia, a TV 30 min por dia), o casual (o dono relapso, 3 visitas por dia, uma luta por dia, sem TV) e o da TV longa (o dedicado com
   a TV 2 h por dia: o pior caso do registro, porque a TV do jogo grava um "st" a cada mudanca da media de 10 s). Na TV, o tempo anda a 1x
   (6 trechos de 10 s por minuto de jogo), e cada trecho muda um dos 7 niveis com probabilidade P_MUDA_TV (o maximo que o ResumoTela grava).
   Sementes: hashSemente("cn0", ...), fora das faixas reservadas. So engenharia, nenhuma run de pesquisa; o motor e o save nao mudam.
   Tambem confere (a parte 3 da CN0) o que o tempo faz entre fechar e abrir: o save nao tem relogio de parede, e reabrir num aparelho
   novo devolve o pet no mesmo tick (ver a secao `tempo` da saida e o teste test/medir_cn0_save.test.ts, que roda o laco do tempo.ts).
     node scripts/medir_cn0_save.ts                 # grava scripts/medicoes/cn0_save.json
     node scripts/medir_cn0_save.ts --rapido        # 1 vida por perfil e 4 dias (o teste), sem gravar */
import { writeFileSync, mkdirSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { brotliCompressSync, constants as zc, gzipSync } from "node:zlib";
import {
  ACOES_DONO_JOGO_V11, CD, CTR, GrupoDoJogo, IDS_CENA, Motor, PetMorto, TPD, VERSAO_GRUPO, VERSAO_PET, criarDono, criarRng, hashSemente,
  valorSentidoTela, valorSentidoTelaDesligada, type AcaoDono, type Dono, type Exercicio, type Rng, type TipoDono, type VisaoDono,
} from "../motor/index.ts";
import { ligarProduto } from "../src/produto.ts";
import { lerSave, textoSave, textoSaveGrupo, type Armazenamento } from "../src/save.ts";
import { VELOCIDADES, velocidadeAtual } from "../src/tempo.ts";
import { Tamer, conferirBits, conferirCampeao, conferirItensDasMedalhas, conferirMedalhas, conferirRecordes, sincronizarPet, textoTamer } from "../src/tamer.ts";

export const VERSAO_MEDIDA = 1;
/** a chance de um trecho de 10 s da TV mudar a media (e gravar um "st"). PROPOSTO, SEM FONTE: o pior caso razoavel de um video que muda */
export const P_MUDA_TV = 0.6;
const EXERCICIOS = Object.keys(CTR.exercicios) as Exercicio[];

export interface Perfil { nome: string; dono: TipoDono; treinosDia: number; lutasDia: number; tvMinDia: number; nota: string }
export const PERFIS: readonly Perfil[] = [
  { nome: "dedicado", dono: "atencioso", treinosDia: 3, lutasDia: 4, tvMinDia: 30, nota: "o dono atencioso a cada passo (15 min), 3 treinos e 4 lutas por dia, a TV 30 min" },
  { nome: "casual", dono: "relapso", treinosDia: 1, lutasDia: 1, tvMinDia: 0, nota: "o dono relapso (3 visitas por dia), 1 treino e 1 luta por dia, sem TV" },
  { nome: "tv_longa", dono: "atencioso", treinosDia: 3, lutasDia: 4, tvMinDia: 120, nota: "o dedicado com a TV 2 h por dia: o pior caso do registro" },
];

export interface Bytes { cru: number; gzip: number; brotli: number }
export function bytes(texto: string): Bytes {
  const b = Buffer.from(texto, "utf8");
  return {
    cru: b.length,
    gzip: gzipSync(b, { level: 9 }).length,
    brotli: brotliCompressSync(b, { params: { [zc.BROTLI_PARAM_QUALITY]: 11, [zc.BROTLI_PARAM_SIZE_HINT]: b.length } }).length,
  };
}
export interface Dia { dia: number; tick: number; estagio: string; eventos: number; eventosNovos: number; save: Bytes; novos: Bytes; tamer: Bytes; eventosTamer: number }
export interface PorTipo { [tipo: string]: { eventos: number; bytesCru: number } }
export interface Vida { perfil: string; grupo: boolean; semente: number; versao: number; dias: Dia[]; morreu: boolean; lutas: number; st: number; porTipo: PorTipo; tamerPorTipo: PorTipo; textoFinal: string; tamerFinal: string }
/** quantos eventos de cada tipo e quantos bytes (o JSON de cada evento, sem a virgula) eles somam; `chave` diz onde esta o tipo */
export function porTipo(log: readonly unknown[], chave: (e: unknown[]) => string): PorTipo {
  const r: PorTipo = {};
  for (const e of log as unknown[][]) { const k = chave(e), x = (r[k] ??= { eventos: 0, bytesCru: 0 }); x.eventos++; x.bytesCru += Buffer.byteLength(JSON.stringify(e)); }
  return r;
}

/** o que o dono "faz" num passo, como nos Cenarios e na bancada (equilibrio_poc/leitura_vida.ts), com as acoes do dono dos v11 em diante */
function acoesDoDono(dono: Dono, r: Rng, m: Motor, passo: number, passos: number, orc: number, gasto: number): AcaoDono[] {
  const rest = orc - gasto, min = Math.max(0, rest - (passos - passo - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
  const v: VisaoDono = { e: m.e, acao: m.acao, passo, passos, orc, gasto, min, max, atrasado: gasto < orc * (passo + 1) / passos, chamados: m.chamadosAbertos() };
  const a = dono.decidir(v, r).filter(x => ACOES_DONO_JOGO_V11.includes(x));
  if (m.lesionadoDesde !== null && a.length) a[0] = "tratar_lesao";
  return a;
}
/** os niveis da TV (7 inteiros em 0..15) andam um passo num canal sorteado */
function mudarNiveis(n: number[], r: Rng): number[] {
  const k = r.int(7), x = [...n];
  x[k] = Math.max(0, Math.min(15, x[k] + (r.random() < 0.5 ? -1 : 1)));
  return x;
}

/** um lado da vida: o pet de um so (Motor) ou o grupo (os dois pets, com o mesmo dono para os dois) */
interface Lado {
  motores(): Motor[];
  avancar(n: number): void;
  agir(m: Motor, f: (m: Motor) => void): void;
  st(valor: string): void;
  temTv: boolean;
  texto(): string;
  eventos(): number;
  log(): unknown[];
}
function ladoPet(semente: number): Lado {
  const m = ligarProduto(new Motor(semente, VERSAO_PET));
  return {
    motores: () => [m], avancar: n => m.avancar(n), agir: (x, f) => f(x), st: v => m.sentidoTela(v), temTv: m.temTv,
    texto: () => textoSave(m), eventos: () => m.log.length, log: () => m.log,
  };
}
function ladoGrupo(semente: number): Lado {
  const g = new GrupoDoJogo(semente, VERSAO_GRUPO), ids = g.ids;
  for (const i of ids) g.agir(i, m => { ligarProduto(m); });
  return {
    motores: () => ids.map(i => g.motor(i)), avancar: n => g.avancar(n),
    agir: (x, f) => { const i = ids.find(k => g.motor(k) === x)!; g.agir(i, f); }, st: v => g.sentidoTela(v), temTv: g.temTv,
    texto: () => textoSaveGrupo(g, ids[0]), eventos: () => g.log.length, log: () => g.log,
  };
}

/** tenta uma luta (arena do estagio ou, uma vez por dia, um lider da campanha aberto); o motor recusa (dormindo, morto): segue */
function lutar(lado: Lado, m: Motor, s: number, k: number, lider: boolean): boolean {
  if (m.estagioAtual === "bebe" || m.morte) return false;
  if (lider) {
    for (const l of Object.keys(m.campanha)) {
      if ((m.campanha[l] ?? 0) > 0) continue;
      const mapa = IDS_CENA.find(c => m.porqueNaoLutaPoc(l, c, s) === null);
      if (mapa === undefined) continue;
      try { lado.agir(m, x => { x.lutarPoc(l, s, mapa); }); return true; } catch (err) { if (err instanceof PetMorto) return false; }
    }
  }
  const rv = m.rivaisArenaPoc(), mapa = IDS_CENA[k % IDS_CENA.length];
  if (!rv.length || m.porqueNaoLutaPoc(rv[k % rv.length], mapa, s) !== null) return false;
  try { lado.agir(m, x => { x.lutarPoc(rv[k % rv.length], s, mapa); }); return true; } catch { return false; }
}

const QUANDO0 = Date.UTC(2026, 10, 1, 12);   // a hora de parede dos eventos do Tamer: fixa, para a medida sair igual
export function viver(perfil: Perfil, grupo: boolean, i: number, dias: number): Vida {
  const semente = hashSemente("cn0", perfil.nome, grupo ? "grupo" : "pet", i) >>> 0;
  const lado = grupo ? ladoGrupo(semente) : ladoPet(semente), tamer = new Tamer();
  const ms = lado.motores(), versao = ms[0].versao;
  const donos = ms.map(() => criarDono(perfil.dono)), rs = ms.map((_, k) => criarRng(hashSemente("cn0-dono", semente, k)));
  const rTv = criarRng(hashSemente("cn0-tv", semente)), rLuta = criarRng(hashSemente("cn0-luta", semente));
  const passosDia = TPD / CD.passo, passos = passosDia * dias, orc = Math.round(CD.porDia * dias), gasto = ms.map(() => 0);
  const out: Dia[] = [];
  let antes = lado.eventos(), textoAntes = lado.texto(), lutas = 0, st = 0, niveis = [8, 8, 8, 8, 0, 0, 0], morreu = false;
  /* a TV: um bloco de tvMinDia minutos que comeca as 19h de cada dia (o tick do dia; a hora de jogo, PROPOSTO) */
  const inicioTv = 19 * 60;
  try {
    for (let d = 0; d < dias && !morreu; d++) {
      const treinos = ms.map(() => 0), lutasDia = ms.map(() => 0), lider = ms.map(() => false);
      for (let pd = 0; pd < passosDia && !morreu; pd++) {
        const p = d * passosDia + pd, hora = (ms[0].e.tick % TPD);
        if (lado.temTv && perfil.tvMinDia > 0 && hora <= inicioTv && inicioTv < hora + CD.passo) {
          /* a TV: a 1x, 6 trechos de 10 s por minuto; cada um muda a media com P_MUDA_TV; ao fim, a TV desligada */
          for (let t = 0; t < perfil.tvMinDia; t++) {
            for (let q = 0; q < 6; q++) if (rTv.random() < P_MUDA_TV) { niveis = mudarNiveis(niveis, rTv); lado.st(valorSentidoTela("tv", niveis)); st++; }
            lado.avancar(1);
          }
          lado.st(valorSentidoTelaDesligada("tv")); st++;
          lado.avancar(CD.passo);
        } else lado.avancar(CD.passo);
        if (ms.some(m => m.morte)) { morreu = true; break; }
        ms.forEach((m, k) => {
          for (const a of acoesDoDono(donos[k], rs[k], m, p, passos, orc, gasto[k])) { lado.agir(m, x => x.observar(a)); gasto[k]++; }
          const est = m.estagioAtual;
          if (est !== "bebe" && treinos[k] < perfil.treinosDia && m.treino.podeTocar(m.e.tick) && !m.treino.pedePausa) {
            try { lado.agir(m, x => { x.treinar(EXERCICIOS[(d * 7 + treinos[k]) % EXERCICIOS.length]); }); treinos[k]++; } catch { /* o motor recusou */ }
          }
          if (lutasDia[k] < perfil.lutasDia && pd % Math.max(1, Math.floor(passosDia / (perfil.lutasDia + 1))) === 0 && pd > 0) {
            const s = rLuta.int(0x7fffffff);
            if (lutar(lado, m, s, lutas, !lider[k])) { lutas++; lutasDia[k]++; lider[k] = true; }
            if (m.lesionadoDesde !== null) lado.agir(m, x => x.observar("tratar_lesao"));
          }
        });
        if (ms.some(m => m.morte)) { morreu = true; break; }
      }
      /* o fim do dia: o Tamer confere o que o pet fez (como o jogo faz a cada mudanca) e o pet conhece as medalhas */
      const quando = QUANDO0 + d * 86_400_000;
      for (const m of ms) {
        if (m.morte) continue;
        conferirMedalhas(tamer, m, quando); conferirItensDasMedalhas(tamer, m, quando); conferirCampeao(tamer, m, quando); conferirRecordes(tamer, m, quando);
        conferirBits(tamer, m, quando);
        lado.agir(m, x => { sincronizarPet(tamer, x); });
      }
      const texto = lado.texto(), n = lado.eventos(), novos = JSON.stringify(lado.log().slice(antes)), t = textoTamer(tamer);
      out.push({ dia: d + 1, tick: ms[0].e.tick, estagio: ms.map(m => m.estagioAtual).join("+"), eventos: n, eventosNovos: n - antes,
        save: bytes(texto), novos: bytes(novos), tamer: bytes(t), eventosTamer: tamer.log.length });
      antes = n; textoAntes = texto;
    }
  } catch (err) { if (!(err instanceof PetMorto)) throw err; morreu = true; }
  return { perfil: perfil.nome, grupo, semente, versao, dias: out, morreu, lutas, st,
    porTipo: porTipo(lado.log(), e => String(e[1])), tamerPorTipo: porTipo(tamer.log, e => e[0] === "bits" ? `bits:${(e[1] as { origem: string }).origem}` : String(e[0])),
    textoFinal: lado.texto() || textoAntes, tamerFinal: textoTamer(tamer) };
}

/** o save abre de novo (o replay refaz o mesmo pet): a medida so vale se o registro gravado e o do jogo */
export function conferirReplay(texto: string): boolean {
  const a: Armazenamento = { getItem: () => texto, setItem: () => { /* so le */ } };
  return lerSave(a).tipo === "ok";
}

/** o tempo entre fechar e abrir (CN0, parte 3): o save nao guarda hora de parede; reabrir o mesmo texto noutro "aparelho" (outro
    armazenamento), qualquer tempo depois, devolve o pet no mesmo tick. O laco do tempo.ts (o salto maximo de 1 h real por passo) so anda com
    a aba aberta: o teste test/medir_cn0_save.test.ts roda o laco com o relogio falso */
export function tempoFechado(texto: string): { tickAoFechar: number; tickAoAbrir: number; campos: string[]; temHoraDeParede: boolean } {
  const d = JSON.parse(texto) as Record<string, unknown>;
  const a: Armazenamento = { getItem: () => texto, setItem: () => { /* so le */ } };
  const r = lerSave(a);
  if (r.tipo !== "ok") throw new Error("o save nao abriu");
  const m = Motor.reproduzir(d.semente as number, d.log as never, d.versao as number);
  return { tickAoFechar: m.e.tick, tickAoAbrir: r.motor.e.tick, campos: Object.keys(d), temHoraDeParede: Object.keys(d).some(k => /hora|quando|data|ts|relogio/i.test(k)) };
}

const pct = (xs: number[], q: number): number => { const s = [...xs].sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(q * (s.length - 1) + 0.5))]; };
const media = (xs: number[]): number => xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0;

export function medir(opc: { vidas: number; dias: number }) {
  const vidas: Vida[] = [];
  for (const p of PERFIS) for (const grupo of [false, true]) for (let i = 0; i < opc.vidas; i++) {
    const v = viver(p, grupo, i, opc.dias);
    if (!conferirReplay(v.textoFinal)) throw new Error(`o save de ${p.nome} ${grupo ? "grupo" : "pet"} ${i} nao reabre`);
    vidas.push(v);
    console.log(`${p.nome} ${grupo ? "grupo" : "pet  "} #${i}: ${v.dias.length} dias, ${v.dias.at(-1)?.eventos ?? 0} eventos, ${v.dias.at(-1)?.save.cru ?? 0} B cru, ${v.dias.at(-1)?.save.brotli ?? 0} B brotli, ${v.lutas} lutas, ${v.st} st${v.morreu ? ", morreu" : ""}`);
  }
  /* o resumo por perfil e tipo: por dia, a media e o maior entre as vidas */
  const resumo = PERFIS.flatMap(p => [false, true].map(grupo => {
    const vs = vidas.filter(v => v.perfil === p.nome && v.grupo === grupo), nd = Math.max(...vs.map(v => v.dias.length));
    const porDia = Array.from({ length: nd }, (_, d) => {
      const ds = vs.map(v => v.dias[d]).filter(Boolean);
      return { dia: d + 1, vidas: ds.length, eventos: Math.round(media(ds.map(x => x.eventos))), eventosNovos: Math.round(media(ds.map(x => x.eventosNovos))),
        saveCru: Math.round(media(ds.map(x => x.save.cru))), saveGzip: Math.round(media(ds.map(x => x.save.gzip))), saveBrotli: Math.round(media(ds.map(x => x.save.brotli))),
        novosCru: Math.round(media(ds.map(x => x.novos.cru))), novosGzip: Math.round(media(ds.map(x => x.novos.gzip))), novosBrotli: Math.round(media(ds.map(x => x.novos.brotli))),
        tamerCru: Math.round(media(ds.map(x => x.tamer.cru))), saveCruMax: Math.max(...ds.map(x => x.save.cru)) };
    });
    const novosDia = vs.flatMap(v => v.dias.map(x => x.eventosNovos)), bytesDia = vs.flatMap(v => v.dias.map(x => x.novos.cru));
    return { perfil: p.nome, grupo, nota: p.nota, vidas: vs.length, porDia,
      eventosNovosPorDia: { media: Math.round(media(novosDia)), p90: pct(novosDia, 0.9), max: Math.max(...novosDia) },
      bytesNovosPorDiaCru: { media: Math.round(media(bytesDia)), p90: pct(bytesDia, 0.9), max: Math.max(...bytesDia) },
      bytesPorEventoCru: +(media(vs.map(v => v.dias.at(-1)!.save.cru / v.dias.at(-1)!.eventos))).toFixed(1),
      razaoBrotli: +(media(vs.map(v => v.dias.at(-1)!.save.brotli / v.dias.at(-1)!.save.cru))).toFixed(3),
      razaoGzip: +(media(vs.map(v => v.dias.at(-1)!.save.gzip / v.dias.at(-1)!.save.cru))).toFixed(3) };
  }));
  /* o pacote da nuvem de um jogador de cada perfil: o ativo (a vida 0 de um so), os guardados (as outras vidas, de um so e o grupo, como
     Guardado), Gerações (a vida 0 aposentada, como Aposentado) e o Tamer da vida 0 */
  const pacotes = PERFIS.map(p => {
    const vs = vidas.filter(v => v.perfil === p.nome), ativo = vs.find(v => !v.grupo)!, outros = vs.filter(v => v !== ativo);
    const guardados = JSON.stringify(outros.map(v => v.grupo ? { ...JSON.parse(v.textoFinal) } : JSON.parse(v.textoFinal)));
    const geracoes = JSON.stringify([{ ...JSON.parse(ativo.textoFinal), ger: 1, filho: 1, quando: QUANDO0 }]);
    const partes = { save: bytes(ativo.textoFinal), guardados: bytes(guardados), geracoes: bytes(geracoes), tamer: bytes(ativo.tamerFinal) };
    /* as quatro chaves num pacote so (o objeto, nao os textos escapados): o que a sincronizacao inicial (a tela 3) mandaria de uma vez */
    const tudo = bytes(JSON.stringify({ save: JSON.parse(ativo.textoFinal), guardados: JSON.parse(guardados), geracoes: JSON.parse(geracoes), tamer: JSON.parse(ativo.tamerFinal) }));
    return { perfil: p.nome, guardados: outros.length, geracoes: 1, partes, tudo };
  });
  /* o salto maximo de um passo do laco (tempo.ts: dt = min(3600 s, o tempo real desde o passo anterior)) em cada velocidade: com a aba
     aberta e o PC dormindo, o primeiro passo depois anda isso, e nada mais; com a aba fechada, nada (o laco nao roda e o save nao tem hora) */
  const saltoPorPasso = VELOCIDADES.filter(([, v]) => v > 0).map(([nome, v]) => ({ velocidade: nome, minDeJogoPorSegundo: +v.toFixed(4),
    saltoMaxTicks: Math.floor(3600 * v), saltoMaxDiasDeJogo: +(3600 * v / TPD).toFixed(3) }));
  const tempo = { ...tempoFechado(vidas[0].textoFinal), velocidadeAoAbrir: velocidadeAtual(), saltoPorPasso,
    leitura: "o tempo.ts so anda com a aba aberta (setInterval de 100 ms, dt pelo performance.now); o save {semente, log, versao} nao tem hora de parede e nada no app recupera o tempo fechado. Fechar num aparelho e abrir noutro devolve o pet no tick em que fechou: o pet NAO envelhece pelo tempo fechado. A velocidade nao e guardada: toda abertura comeca em 10 min/s. O bebe anda minuto a minuto e para no primeiro chamado (acima de 1x)" };
  return { vidas, resumo, pacotes, tempo };
}

/* ------------------------------------------------ a linha de comando */
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const rapido = process.argv.includes("--rapido");
  const opc = rapido ? { vidas: 1, dias: 4 } : { vidas: 3, dias: 21 };
  const t0 = performance.now(), r = medir(opc);
  const saida = {
    gerado_por: "web/app/scripts/medir_cn0_save.ts", versao_medida: VERSAO_MEDIDA, commit: execSync("git rev-parse --short HEAD").toString().trim(),
    data: new Date().toISOString().slice(0, 10), comando: "cd web/app && node scripts/medir_cn0_save.ts",
    maquina: { cpu: os.cpus()[0]?.model ?? "?", nucleos: os.cpus().length, plataforma: `${process.platform} ${os.release()}` }, node: process.version,
    versaoPet: VERSAO_PET, versaoGrupo: VERSAO_GRUPO, vidasPorPerfil: opc.vidas, diasDeJogo: opc.dias, pMudaTv: P_MUDA_TV,
    compressao: "gzip nivel 9 e brotli qualidade 11 (node:zlib), sobre o texto UTF-8 do save como o jogo grava no localStorage",
    perfis: PERFIS, resumo: r.resumo, pacotes: r.pacotes, tempo: r.tempo,
    vidas: r.vidas.map(({ textoFinal: _t, tamerFinal: _m, ...v }) => v),
    segundos: +((performance.now() - t0) / 1000).toFixed(1),
    nota: "PROPOSTO, SEM FONTE: os perfis do jogador; a medida e de engenharia (o tamanho), nenhuma meta. 'novos' e o trecho do registro do dia (o que a CN3 mandaria), sozinho; comprimido junto do resto ele sai menor",
  };
  if (rapido) console.log(JSON.stringify(saida.resumo.map(x => [x.perfil, x.grupo, x.eventosNovosPorDia, x.bytesNovosPorDiaCru])));
  else {
    const DEST = fileURLToPath(new URL("./medicoes/", import.meta.url));
    mkdirSync(DEST, { recursive: true });
    writeFileSync(DEST + "cn0_save.json", JSON.stringify(saida, null, 1) + "\n");
    console.log(`cn0_save.json gravado (${saida.segundos} s)`);
  }
}
