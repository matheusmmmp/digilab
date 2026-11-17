/* BETA, etapa BT0 (docs/PLANO_V3_BETA.md, secoes 3 e 7; BT-3 DECIDIDA): quanto tempo de RELOGIO um jogador novo leva do ovo ao primeiro Mega,
   o marco 10 do Tamer (src/nivel.ts, ULTIMO_MARCO; MMO-13: e onde o multijogador abre).
   Duas partes:
   1) A VIDA, em tempo de jogo. Refaz no Node, pelo motor do jogo, a vida de um jogador novo: os dois ovos (DOIS_OVOS_LIGADO, o GrupoDoJogo da
      VERSAO_GRUPO, como o chocarDoisOvos da jornada.ts), o primeiro do brasao de cada especie, no ritmo "rapida" (o padrao), com o produto
      ligado e os perfis do jogador da CN0 (PERFIS do scripts/medir_cn0_save.ts: o dono, os treinos, as lutas e a TV por dia de jogo), e com
      o Tamer conferindo as medalhas no fim de cada dia de jogo (conferir* e sincronizarPet, como a CN0). Mede o tick de cada estagio (Rookie,
      Champion, Ultimate, Mega) de cada pet e o nivel do Tamer (marcosFeitos), e conta o que segura o relogio: as lutas (o tempo do palco, a
      soma dos `relogio` da serie de cada luta) e os chamados do bebe. A vida acaba no primeiro Mega ou em DIAS_MAX dias de jogo.
   2) O RELOGIO. O tempo do pet so anda com a aba aberta (D-CONTA-38; src/tempo.ts): a cada segundo aberto, `velocidade` minutos de jogo; a luta
      no palco e o Resultado dela seguram o tempo (lutaSeguraTempo); o chamado do bebe cai para 1x ate o dono atender. Entao o tempo ABERTO ate
      um estagio e
        (os minutos de jogo ate la) / (velocidade em min/s) + (o palco das lutas ate la) + (as lutas) x T_RESULTADO + (os chamados) x T_ATENDER,
      e os dias de RELOGIO sao esse tempo aberto dividido pelos minutos abertos por dia (as sessoes). As velocidades, os tempos fixos e as
      sessoes sao HIPOTESES, PROPOSTAS, SEM FONTE (nao ha medida de como as pessoas jogam), e vao para o JSON (`hipoteses`). O salto de 1 h
      real por passo (o PC dormindo com a aba aberta) entra so como cota inferior (`soSeguraRelogio`: so o que segura o relogio, como se o tempo
      de jogo fosse de graca), porque o dono simulado cuida a cada 15 min de jogo e ninguem cuida de um pet que andou 25 dias de uma vez.
   Sementes: hashSemente("bt0", ...), fora das faixas reservadas; poucas vidas, como as dos testes. So engenharia; o motor, o save e as versoes
   de pet nao mudam, e nenhuma chave de beta e implementada aqui.
     node scripts/medir_bt0_mega.ts                 # grava scripts/medicoes/bt0_mega.json
     node scripts/medir_bt0_mega.ts --rapido        # 1 vida, 2 especies, 4 dias (o teste), sem gravar */
import { writeFileSync, mkdirSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import { fileURLToPath } from "node:url";
import {
  ACOES_DONO_JOGO_V11, CD, CTR, ESPECIES, GrupoDoJogo, IDS_CENA, Motor, PetMorto, TICK_INICIAL, TPD, VERSAO_GRUPO, criarDono, criarRng,
  hashSemente, valorSentidoTela, valorSentidoTelaDesligada, type AcaoDono, type Dono, type Especie, type Estagio, type Exercicio,
  type ResultadoLutaPoc, type Rng, type VisaoDono,
} from "../motor/index.ts";
import { ligarProduto } from "../src/produto.ts";
import { VELOCIDADES } from "../src/tempo.ts";
import { ULTIMO_MARCO, marcosFeitos } from "../src/nivel.ts";
import { Tamer, conferirBits, conferirCampeao, conferirItensDasMedalhas, conferirMedalhas, conferirRecordes, conferirMarcoMega, sincronizarPet } from "../src/tamer.ts";
import { PERFIS, type Perfil } from "./medir_cn0_save.ts";

export const VERSAO_MEDIDA = 1;
/** o fim da vida simulada, se o Mega nao vier antes: 60 dias de jogo (PROPOSTO; a 10 min/s, 6 h de jogo aberto) */
export const DIAS_MAX = 60;
const EXERCICIOS = Object.keys(CTR.exercicios) as Exercicio[];
/** os estagios medidos e o nome Digimon de cada um (nomes-digimon-na-tela) */
/** os marcos do Tamer (src/nivel.ts, 3.3) em que a chave de beta poderia abrir o cais (secao 3 do plano: o 9 ou um mais cedo). Cada peca
    abre pelo PROPRIO marco, nao pela contagem: o 6 e o Champion, o 7 as tres medalhas, o 8 as seis, o 9 o titulo da Liga, o 10 o Mega */
export const MARCOS_CAIS = [6, 7, 8, 9, 10] as const;
export const ESTAGIOS: readonly [Estagio, string][] = [["crianca", "Rookie"], ["adolescente", "Champion"], ["adulto", "Ultimate"], ["mega", "Mega"]];

/* ------------------------------------------------ as hipoteses do relogio (PROPOSTAS, SEM FONTE) */
export interface Sessoes { sessoesPorDia: number; minutosPorSessao: number }
export const HIPOTESES = {
  /** a velocidade com que o jogo abre (tempo.ts: `let velocidade = 10`; a velocidade nao e guardada, CN0) e as outras da tela de Ajustes */
  velocidadePadrao: "10 min/s",
  /** segundos que o Resultado de uma luta fica aberto (o tempo segurado depois do palco). PROPOSTO, SEM FONTE */
  segundosResultado: 8,
  /** segundos ate o dono atender um chamado do bebe, com o tempo em 1x. PROPOSTO, SEM FONTE */
  segundosAtender: { dedicado: 10, casual: 60, tv_longa: 10 } as Record<string, number>,
  /** as sessoes por dia de relogio de cada perfil. PROPOSTO, SEM FONTE */
  sessoes: {
    dedicado: { sessoesPorDia: 4, minutosPorSessao: 30 },
    casual: { sessoesPorDia: 2, minutosPorSessao: 15 },
    tv_longa: { sessoesPorDia: 4, minutosPorSessao: 30 },
  } as Record<string, Sessoes>,
  /** a grade de sensibilidade: minutos abertos por dia de relogio */
  gradeMinutosPorDia: [15, 30, 60, 120, 240],
  /** os dias de relogio que o plano pergunta (o beta tem 7; a chave de beta, uns 3) */
  marcosDias: [3, 7],
  nota: "o tempo de jogo anda so com a aba aberta, na velocidade escolhida (tempo.ts); a luta no palco e o Resultado seguram o tempo; o chamado do bebe cai para 1x ate o dono atender. A TV nao muda a velocidade (os minutos de TV dos perfis da CN0 sao minutos de jogo). O treino, o cuidado e a conversa nao seguram o relogio. Tudo PROPOSTO, SEM FONTE",
};

/* ------------------------------------------------ a vida (como a CN0: o dono dos Cenarios, treino, arena e um lider por dia de jogo) */
function acoesDoDono(dono: Dono, r: Rng, m: Motor, passo: number, passos: number, orc: number, gasto: number): AcaoDono[] {
  const rest = orc - gasto, min = Math.max(0, rest - (passos - passo - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
  const v: VisaoDono = { e: m.e, acao: m.acao, passo, passos, orc, gasto, min, max, atrasado: gasto < orc * (passo + 1) / passos, chamados: m.chamadosAbertos() };
  const a = dono.decidir(v, r).filter(x => ACOES_DONO_JOGO_V11.includes(x));
  if (m.lesionadoDesde !== null && a.length) a[0] = "tratar_lesao";
  return a;
}
function mudarNiveis(n: number[], r: Rng): number[] {
  const k = r.int(7), x = [...n];
  x[k] = Math.max(0, Math.min(15, x[k] + (r.random() < 0.5 ? -1 : 1)));
  return x;
}
/** a semente do grupo cujo primeiro ovo e da especie do brasao (a jornada sorteia ate cair nela; aqui, hashSemente("bt0", ...) em ordem) */
export function sementeDoBrasao(esp: Especie, i: number): number {
  for (let k = 0; k < 10_000; k++) {
    const s = hashSemente("bt0", esp, i, k) >>> 0, g = new GrupoDoJogo(s, VERSAO_GRUPO);
    if (g.motor(g.ids[0]).especie === esp) return s;
  }
  throw new Error("sem semente do brasao " + esp);
}
/** uma luta do palco: o tempo que ela segura, em segundos (a soma do relogio de cada luta da serie, 1 ou 3 na Cidadela) */
const segundosDoPalco = (r: ResultadoLutaPoc): number => r.serie.reduce((a, x) => a + x.relogio, 0) / 1000;

export interface Marca { tick: number; minutosDeJogo: number; lutas: number; segundosPalco: number; chamadosBebe: number; dia: number }
export interface PetVida { id: string; especie: Especie; estagios: Partial<Record<Estagio, Marca>>; morreu: boolean; medalhasNoFim: number; forma: string }
export interface VidaBt0 {
  perfil: string; variante: Variante; chipsEquipados: number; brasao: Especie; i: number; semente: number; versao: number; dias: number; morreu: boolean;
  pets: PetVida[]; lutas: number; vitorias: number; lideresTentados: number; segundosPalco: number; chamadosBebe: number;
  /** o primeiro estagio que QUALQUER dos dois pets alcancou: e o que o jogador ve (o marco do Tamer e por jogador) */
  primeiro: Partial<Record<Estagio, Marca & { pet: string }>>;
  /** o nivel do Tamer (a contagem de marcosFeitos) no fim de cada dia de jogo */
  nivelPorDia: number[];
  /** o dia de jogo em que o Tamer chegou ao ULTIMO_MARCO (null: nao chegou) */
  diaNivel10: number | null;
  medalhas: number;
  /** as lutas e as vitorias contra cada NPC da campanha (os lideres das medalhas e os outros), somados os dois pets */
  porLider: Record<string, { lutas: number; vitorias: number }>;
  /** o fim do primeiro dia de jogo em que o Tamer tinha cada marco de MARCOS_CAIS (null: nao chegou) */
  marcoAlcancado: Record<number, Marca | null>;
}

/** as duas variantes do dono: o da CN0 como esta (nunca equipa) e o que equipa os chips que o Tamer ganhou, nas vagas livres, no fim de
    cada dia de jogo (o cartao do nivel 5, "A medalha trouxe um chip"). PROPOSTO, SEM FONTE; nenhuma usa as cartas de revanche */
export const VARIANTES = ["cn0", "chips"] as const;
export type Variante = (typeof VARIANTES)[number];
export function viver(perfil: Perfil, brasao: Especie, i: number, diasMax = DIAS_MAX, variante: Variante = "cn0"): VidaBt0 {
  const semente = sementeDoBrasao(brasao, i), g = new GrupoDoJogo(semente, VERSAO_GRUPO), ids = g.ids;
  for (const id of ids) g.agir(id, m => { ligarProduto(m); });
  const ms = ids.map(id => g.motor(id)), tamer = new Tamer(), versao = ms[0].versao;
  const agir = (m: Motor, f: (m: Motor) => void): void => { g.agir(ids[ms.indexOf(m)], f); };
  const donos = ms.map(() => criarDono(perfil.dono)), rs = ms.map((_, k) => criarRng(hashSemente("bt0-dono", semente, k)));
  const rTv = criarRng(hashSemente("bt0-tv", semente)), rLuta = criarRng(hashSemente("bt0-luta", semente));
  const passosDia = TPD / CD.passo, passos = passosDia * diasMax, orc = Math.round(CD.porDia * diasMax), gasto = ms.map(() => 0);
  let chipsEquipados = 0, lutas = 0, vitorias = 0, lideres = 0, palco = 0, chamados = 0, niveis = [8, 8, 8, 8, 0, 0, 0], morreu = false, dia = 0;
  const abertosAntes = ms.map(() => new Set<string>()), porLider: Record<string, { lutas: number; vitorias: number }> = {};
  const pets: PetVida[] = ms.map((m, k) => ({ id: ids[k], especie: m.especie, estagios: {}, morreu: false, medalhasNoFim: 0, forma: "" }));
  const nivelPorDia: number[] = [], porDia: (Marca & { nivel: number; marcos: number[]; medalhas: number })[] = [];
  let diaNivel10: number | null = null;
  const marcar = (): void => {
    ms.forEach((m, k) => {
      for (const ev of m.evolucoes) if (!pets[k].estagios[ev.estagio] && ESTAGIOS.some(([e]) => e === ev.estagio))
        pets[k].estagios[ev.estagio] = { tick: ev.tick, minutosDeJogo: ev.tick - TICK_INICIAL, lutas, segundosPalco: +palco.toFixed(1), chamadosBebe: chamados, dia: dia + 1 };
    });
  };
  /* os chamados do bebe que abriram (cada um novo e um momento em 1x ate o dono atender) */
  const contarChamados = (): void => {
    ms.forEach((m, k) => {
      const ab = new Set<string>(m.chamadosAbertos());
      for (const c of ab) if (!abertosAntes[k].has(c)) chamados++;
      abertosAntes[k] = ab;
    });
  };
  const tentar = (m: Motor, rival: string, s: number, mapa: (typeof IDS_CENA)[number]): boolean => {
    let r: ResultadoLutaPoc | null = null;
    try { agir(m, x => { r = x.lutarPoc(rival, s, mapa); }); } catch (err) { if (err instanceof PetMorto) return false; return false; }
    if (!r) return false;
    lutas++; palco += segundosDoPalco(r); if ((r as ResultadoLutaPoc).venceu) vitorias++;
    if (rival in m.campanha) { const c = (porLider[rival] ??= { lutas: 0, vitorias: 0 }); c.lutas++; if ((r as ResultadoLutaPoc).venceu) c.vitorias++; }
    return true;
  };
  const lutar = (m: Motor, s: number, k: number, lider: boolean): boolean => {
    if (m.estagioAtual === "bebe" || m.morte) return false;
    if (lider) {
      for (const l of Object.keys(m.campanha)) {
        if ((m.campanha[l] ?? 0) > 0) continue;
        const mapa = IDS_CENA.find(c => m.porqueNaoLutaPoc(l, c, s) === null);
        if (mapa === undefined) continue;
        if (tentar(m, l, s, mapa)) { lideres++; return true; }
      }
    }
    const rv = m.rivaisArenaPoc(), mapa = IDS_CENA[k % IDS_CENA.length];
    if (!rv.length || m.porqueNaoLutaPoc(rv[k % rv.length], mapa, s) !== null) return false;
    return tentar(m, rv[k % rv.length], s, mapa);
  };
  const inicioTv = 19 * 60, temMega = (): boolean => ms.some(m => m.estagioAtual === "mega");
  try {
    for (dia = 0; dia < diasMax && !morreu && !temMega(); dia++) {
      const treinos = ms.map(() => 0), lutasDia = ms.map(() => 0), lider = ms.map(() => false);
      for (let pd = 0; pd < passosDia && !morreu; pd++) {
        const p = dia * passosDia + pd, hora = ms[0].e.tick % TPD;
        if (g.temTv && perfil.tvMinDia > 0 && hora <= inicioTv && inicioTv < hora + CD.passo) {
          for (let t = 0; t < perfil.tvMinDia; t++) {
            for (let q = 0; q < 6; q++) if (rTv.random() < 0.6) { niveis = mudarNiveis(niveis, rTv); g.sentidoTela(valorSentidoTela("tv", niveis)); }
            g.avancar(1); contarChamados();
          }
          g.sentidoTela(valorSentidoTelaDesligada("tv"));
          g.avancar(CD.passo);
        } else {
          /* o bebe anda minuto a minuto (como o tempo.ts), para contar cada chamado que abre */
          if (ms.some(m => m.estagioAtual === "bebe")) for (let q = 0; q < CD.passo; q++) { g.avancar(1); contarChamados(); }
          else g.avancar(CD.passo);
        }
        if (ms.some(m => m.morte)) { morreu = true; break; }
        ms.forEach((m, k) => {
          for (const a of acoesDoDono(donos[k], rs[k], m, p, passos, orc, gasto[k])) { agir(m, x => x.observar(a)); gasto[k]++; }
          if (m.estagioAtual !== "bebe" && treinos[k] < perfil.treinosDia && m.treino.podeTocar(m.e.tick) && !m.treino.pedePausa) {
            try { agir(m, x => { x.treinar(EXERCICIOS[(dia * 7 + treinos[k]) % EXERCICIOS.length]); }); treinos[k]++; } catch { /* o motor recusou */ }
          }
          if (lutasDia[k] < perfil.lutasDia && pd % Math.max(1, Math.floor(passosDia / (perfil.lutasDia + 1))) === 0 && pd > 0) {
            const s = rLuta.int(0x7fffffff);
            if (lutar(m, s, lutas, !lider[k])) { lutasDia[k]++; lider[k] = true; }
            if (m.lesionadoDesde !== null) agir(m, x => x.observar("tratar_lesao"));
          }
        });
        contarChamados();
        marcar();
        if (ms.some(m => m.morte)) { morreu = true; break; }
        if (temMega()) break;
      }
      /* o fim do dia de jogo (ou o Mega): o Tamer confere o que os pets fizeram e os pets conhecem as medalhas */
      const quando = Date.UTC(2026, 10, 1, 12) + dia * 86_400_000;
      for (const m of ms) {
        if (m.morte) continue;
        conferirMedalhas(tamer, m, quando); conferirItensDasMedalhas(tamer, m, quando); conferirCampeao(tamer, m, quando); conferirRecordes(tamer, m, quando);
        conferirBits(tamer, m, quando); conferirMarcoMega(tamer, [m], quando);
        agir(m, x => { sincronizarPet(tamer, x); });
        if (variante === "chips") for (const it of tamer.itens) if (m.porqueNaoEquipa(it.id) === null) { agir(m, x => { x.equipar(it.id); }); chipsEquipados++; }
      }
      marcar();
      const marcos = marcosFeitos(ms, tamer), nivel = marcos.length;
      nivelPorDia.push(nivel);
      porDia.push({ tick: ms[0].e.tick, minutosDeJogo: ms[0].e.tick - TICK_INICIAL, lutas, segundosPalco: +palco.toFixed(1), chamadosBebe: chamados, dia: dia + 1, nivel, marcos, medalhas: tamer.medalhas.length });
      if (diaNivel10 === null && marcosFeitos(ms, tamer).includes(ULTIMO_MARCO)) diaNivel10 = dia + 1;
    }
  } catch (err) { if (!(err instanceof PetMorto)) throw err; morreu = true; }
  marcar();
  ms.forEach((m, k) => { pets[k].morreu = !!m.morte; pets[k].medalhasNoFim = m.medalhas; pets[k].forma = `${m.estagioAtual}`; });
  const primeiro: VidaBt0["primeiro"] = {};
  for (const [e] of ESTAGIOS) {
    const cs = pets.flatMap(p => p.estagios[e] ? [{ ...p.estagios[e]!, pet: p.id }] : []).sort((a, b) => a.tick - b.tick);
    if (cs.length) primeiro[e] = cs[0];
  }
  return { perfil: perfil.nome, variante, chipsEquipados, brasao, i, semente, versao, dias: nivelPorDia.length, morreu, pets, lutas, vitorias, lideresTentados: lideres,
    segundosPalco: +palco.toFixed(1), chamadosBebe: chamados, primeiro, nivelPorDia, diaNivel10, medalhas: tamer.medalhas.length, porLider,
    marcoAlcancado: Object.fromEntries(MARCOS_CAIS.map(n => [n, porDia.find(x => x.marcos.includes(n)) ?? null])) };
}

/* ------------------------------------------------ o relogio */
/** os segundos ABERTOS ate uma marca, numa velocidade (min de jogo por s); `soSegura` ignora o tempo de jogo (a cota inferior do salto) */
export function segundosAbertos(m: Marca, minPorSegundo: number, perfil: string, soSegura = false): number {
  const jogo = soSegura ? 0 : m.minutosDeJogo / minPorSegundo;
  return jogo + m.segundosPalco + m.lutas * HIPOTESES.segundosResultado + m.chamadosBebe * (HIPOTESES.segundosAtender[perfil] ?? 30);
}
/** os dias de relogio com `minutosPorDia` abertos por dia */
export const diasDeRelogio = (segundos: number, minutosPorDia: number): number => segundos / 60 / minutosPorDia;
const mediana = (xs: number[]): number => { const s = [...xs].sort((a, b) => a - b), n = s.length; return n ? (n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2) : NaN; };
const r1 = (x: number): number => +x.toFixed(1), r2 = (x: number): number => +x.toFixed(2);

export function medir(opc: { vidas: number; especies: readonly Especie[]; dias: number }) {
  const vidas: VidaBt0[] = [];
  for (const va of VARIANTES) for (const p of PERFIS) for (const esp of opc.especies) for (let i = 0; i < opc.vidas; i++) {
    const v = viver(p, esp, i, opc.dias, va);
    vidas.push(v);
    const mg = v.primeiro.mega;
    console.log(`${va} ${p.nome} ${esp} #${i}: ${v.dias} dias de jogo, ${v.lutas} lutas (${v.vitorias} vitorias), ${v.medalhas} medalhas, ${mg ? `Mega no min ${mg.minutosDeJogo}` : "sem Mega"}${v.morreu ? ", morreu" : ""}`);
  }
  const vels = VELOCIDADES.filter(([, v]) => v > 0).map(([nome, v]) => ({ nome, minPorSegundo: v }));
  /* por perfil e especie, e por perfil: o tempo de jogo de cada estagio (a mediana entre as vidas) e o tempo aberto em cada velocidade */
  const grupos = VARIANTES.flatMap(va => PERFIS.flatMap(p => [...opc.especies.map(e => ({ va, p, e: e as Especie | "todas" })), { va, p, e: "todas" as const }]));
  const tabela = grupos.map(({ va, p, e }) => {
    const vs = vidas.filter(v => v.variante === va && v.perfil === p.nome && (e === "todas" || v.brasao === e)), ses = HIPOTESES.sessoes[p.nome];
    const minPorDia = ses.sessoesPorDia * ses.minutosPorSessao;
    const estagios = Object.fromEntries(ESTAGIOS.map(([est, nome]) => {
      const ms = vs.map(v => v.primeiro[est]).filter((x): x is NonNullable<typeof x> => !!x);
      const porVel = Object.fromEntries(vels.map(({ nome: vn, minPorSegundo }) => {
        const seg = ms.map(m => segundosAbertos(m, minPorSegundo, p.nome));
        return [vn, { horasAbertasMediana: ms.length ? r2(mediana(seg) / 3600) : null,
          diasDeRelogioMediana: ms.length ? r2(diasDeRelogio(mediana(seg), minPorDia)) : null }];
      }));
      const piso = ms.map(m => segundosAbertos(m, 1, p.nome, true));
      return [nome, { chegaram: ms.length, de: vs.length,
        diasDeJogoMediana: ms.length ? r2(mediana(ms.map(m => m.minutosDeJogo)) / TPD) : null,
        lutasMediana: ms.length ? mediana(ms.map(m => m.lutas)) : null,
        palcoMinMediana: ms.length ? r1(mediana(ms.map(m => m.segundosPalco)) / 60) : null,
        porVelocidade: porVel,
        soSeguraRelogioHorasMediana: ms.length ? r2(mediana(piso) / 3600) : null }];
    }));
    /* quantas vidas chegam ao Mega em 3 e 7 dias de relogio, na velocidade padrao e nas sessoes do perfil, e na grade */
    const vPad = vels.find(v => v.nome === HIPOTESES.velocidadePadrao)!.minPorSegundo;
    const diasMega = vs.map(v => v.primeiro.mega ? diasDeRelogio(segundosAbertos(v.primeiro.mega, vPad, p.nome), minPorDia) : Infinity);
    const emDias = Object.fromEntries(HIPOTESES.marcosDias.map(d => [`ate${d}dias`, diasMega.filter(x => x <= d).length]));
    const grade = Object.fromEntries(vels.map(({ nome: vn, minPorSegundo }) => [vn, Object.fromEntries(HIPOTESES.gradeMinutosPorDia.map(mpd => {
      const ds = vs.map(v => v.primeiro.mega ? diasDeRelogio(segundosAbertos(v.primeiro.mega, minPorSegundo, p.nome), mpd) : Infinity);
      return [`${mpd}minPorDia`, Object.fromEntries(HIPOTESES.marcosDias.map(d => [`ate${d}dias`, ds.filter(x => x <= d).length]))];
    }))]));
    /* cada marco do Tamer de MARCOS_CAIS: quantos chegam, em quantos dias de relogio (velocidade padrao, sessoes do perfil), e em 3 e 7 dias */
    const marcos = Object.fromEntries(MARCOS_CAIS.map(n => {
      const ds = vs.map(v => v.marcoAlcancado[n] ? diasDeRelogio(segundosAbertos(v.marcoAlcancado[n]!, vPad, p.nome), minPorDia) : Infinity), ok = ds.filter(Number.isFinite);
      return [`marco${n}`, { chegaram: ok.length, de: vs.length, diasDeJogoMediana: ok.length ? r2(mediana(vs.flatMap(v => v.marcoAlcancado[n] ? [v.marcoAlcancado[n]!.minutosDeJogo / TPD] : []))) : null,
        diasDeRelogioMediana: ok.length ? r2(mediana(ok)) : null, ...Object.fromEntries(HIPOTESES.marcosDias.map(d => [`ate${d}dias`, ds.filter(x => x <= d).length])) }];
    }));
    return { variante: va, perfil: p.nome, marcos, brasao: e, vidas: vs.length, sessoes: ses, minutosAbertosPorDia: minPorDia, estagios,
      megaNaVelocidadePadrao: { ...emDias, de: vs.length, diasDeRelogio: diasMega.map(x => Number.isFinite(x) ? r2(x) : null) },
      gradeMega: grade,
      porLider: vs.reduce((acc, v) => { for (const [k, x] of Object.entries(v.porLider)) { const a = (acc[k] ??= { lutas: 0, vitorias: 0 }); a.lutas += x.lutas; a.vitorias += x.vitorias; } return acc; }, {} as Record<string, { lutas: number; vitorias: number }>),
      diaDeJogoNivel10: vs.map(v => v.diaNivel10), mortes: vs.filter(v => v.morreu).length };
  });
  return { vidas, tabela, velocidades: vels };
}

/* ------------------------------------------------ a linha de comando */
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const rapido = process.argv.includes("--rapido");
  const opc = rapido ? { vidas: 1, especies: ESPECIES.slice(0, 2), dias: 4 } : { vidas: 3, especies: ESPECIES, dias: DIAS_MAX };
  const t0 = performance.now(), r = medir(opc);
  const saida = {
    gerado_por: "web/app/scripts/medir_bt0_mega.ts", versao_medida: VERSAO_MEDIDA, commit: execSync("git rev-parse --short HEAD").toString().trim(),
    data: new Date().toISOString().slice(0, 10), comando: "cd web/app && node scripts/medir_bt0_mega.ts",
    maquina: { cpu: os.cpus()[0]?.model ?? "?", nucleos: os.cpus().length, plataforma: `${process.platform} ${os.release()}` }, node: process.version,
    versaoGrupo: VERSAO_GRUPO, ritmo: "rapida", vidasPorPerfilEEspecie: opc.vidas, especies: opc.especies, diasDeJogoMax: opc.dias, ultimoMarco: ULTIMO_MARCO,
    perfis: PERFIS, hipoteses: HIPOTESES, velocidades: r.velocidades,
    tabela: r.tabela,
    vidas: r.vidas,
    segundos: +((performance.now() - t0) / 1000).toFixed(1),
    nota: "PROPOSTO, SEM FONTE: os perfis do jogador (os da CN0), as sessoes por dia, os segundos do Resultado e do chamado, as velocidades. Medido: os ticks de cada estagio, as lutas e o tempo do palco (o relogio da arena) pelo motor. 'primeiro' e o primeiro dos dois pets do jogador a chegar ao estagio. 'soSeguraRelogio' e a cota inferior (o tempo de jogo de graca, como no salto de 1 h real)",
  };
  if (rapido) console.log(JSON.stringify(saida.tabela.map(x => [x.variante, x.perfil, x.brasao, x.estagios.Rookie.chegaram])));
  else {
    const DEST = fileURLToPath(new URL("./medicoes/", import.meta.url));
    mkdirSync(DEST, { recursive: true });
    writeFileSync(DEST + "bt0_mega.json", JSON.stringify(saida, null, 1) + "\n");
    console.log(`bt0_mega.json gravado (${saida.segundos} s)`);
  }
}
