// Uso: node docs/pranchas/ux-digibrain/dados_digibrain.mts docs/pranchas/ux-digibrain/dados.json   (Node 22.6+, tipos removidos pelo Node)
// Dados reais para a prancha do DigiBrain "scan holografico": Motor.reproduzir(semente, log, versao).digibrain(), sem tocar o motor.
// O save base e o SAVE_V11 do e2e (web/app/e2e/jogo.spec.ts, linha ~1170). Para achar os estados, reproduz prefixos do log e uma
// vida mais longa (o mesmo save seguido de avancos de 60 ticks e carinhos), e grava cada estado com o log exato que o produz.
import { writeFileSync } from "node:fs";
const raiz = new URL("../../../web/app/", import.meta.url).href;  // docs/pranchas/ux-digibrain -> web/app
const { Motor } = await import(raiz + "motor/motor.ts");

const SAVE = { semente: 4242, versao: 13, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] as any[] };

function ler(log: any[]) {
  const m = Motor.reproduzir(SAVE.semente, log, SAVE.versao);
  const db = m.digibrain();
  const hist = m.historico.filter((h: any) => h.quem === "pet").slice(-5).reverse();
  const em = (m.pol.mem as any).emocoes; const ult = em[em.length - 1];
  return { db, ultimas: hist, emocao: ult ? ult.nome : null, t: m.e?.t ?? null };
}

const saida: Record<string, any> = { fonte: "Motor.reproduzir(4242, log, 13).digibrain() — web/app/motor/motor.ts:319; save base SAVE_V11 de web/app/e2e/jogo.spec.ts", estados: {} };

// sem decisao: o recem-nascido (log vazio)
saida.estados.sem_decisao = { log: [], ...ler([]) };
// o save do e2e inteiro
const base = ler(SAVE.log);
saida.estados.save_e2e = { log: SAVE.log, ...base };

// uma vida mais longa para achar: decisao com escolha, decisao de uma opcao so, e o aprendido nao vazio
let log = [...SAVE.log]; let t = 900;
let comEscolha: any = null, umaOpcao: any = null, comAprendido: any = null, mudou: any = null;
for (let k = 0; k < 400 && (!comEscolha || !umaOpcao || !comAprendido || !mudou); k++) {
  if (k % 5 === 0) log.push([t, "d", "acariciar"]);
  log.push([t, "t", 60]); t += 60;
  const r = ler(log); const d = r.db?.decisao;
  if (!d) continue;
  if (!comEscolha && d.quem_decidiu.escolha && d.chances.length >= 3) comEscolha = { log: [...log], ...r };
  if (!umaOpcao && !d.quem_decidiu.escolha) umaOpcao = { log: [...log], ...r };
  if (!comAprendido && r.db.aprendido.length >= 2 && d.quem_decidiu.escolha) comAprendido = { log: [...log], ...r };
  if (!mudou && d.quem_decidiu.mudou) mudou = { log: [...log], ...r };
}
saida.estados.com_escolha = comEscolha;
saida.estados.uma_opcao = umaOpcao;
saida.estados.com_aprendido = comAprendido;
saida.estados.mudou = mudou;

const resumo = Object.fromEntries(Object.entries(saida.estados).map(([k, v]: any) => [k, v === null ? null : {
  eventos: v.log.length, n: v.db?.decisao?.n, regra: v.db?.decisao?.regra, acao: v.db?.decisao?.acao, chances: v.db?.decisao?.chances,
  quem: v.db?.decisao?.quem_decidiu, aprendido: v.db?.aprendido, arestas: v.db?.mapa.arestas.length,
  aprendidas: v.db?.mapa.arestas.filter((a: any) => a.aprendido !== 0).length, acesas: v.db?.mapa.acesas?.arestas.length }]));
console.log(JSON.stringify(resumo, null, 1));
writeFileSync(process.argv[2], JSON.stringify(saida, null, 1));
