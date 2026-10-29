/* O gabarito das vidas v13 de hoje (COMBATE-TR, etapa R2b; CLAUDE.md: "o gabarito das vidas de hoje e gravado num commit proprio, antes da
   mudanca, e um teste confere"). Antes de tirar do motor os ramos das versoes v1-v12 (D-9), estas vidas v13 gravam o registro e a assinatura
   do Motor a cada evento; test/vidas_v13.test.ts as refaz e confere tudo, bit a bit, depois da remocao. As vidas cobrem o que um pet v13 faz:
   o cuidado pelo laco do corpo e o mundo (alimentar, a racao no chao, limpar, brincar, carinho, tapa, tratar), as medalhas e as evolucoes,
   o treino (e o forcar), as lutas em tempo real (bots, a campanha, os lideres), as travas e os vetos, os chips e as cartas, e o ritmo
   classico. Grava test/gabaritos/vidas_v13_ts.json.
     node scripts/gerar_gabarito_vidas_v13.ts */
import { writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { Motor, NPC, PetMorto, TPD, VERSAO_PET, hashSemente, type AcaoDono, type EventoRegistro, type Exercicio } from "../motor/index.ts";

if (VERSAO_PET !== 13) throw new Error("o gabarito e das vidas v13: VERSAO_PET = " + VERSAO_PET);
const EXERCICIOS: Exercicio[] = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"];

/** o sha256 da assinatura (a assinatura inteira, com o cerebro, passa de 100 kB por evento) */
const sha = (x: string): string => createHash("sha256").update(x).digest("hex");
interface Vida { nome: string; semente: number; log: EventoRegistro[]; assinaturas: string[] }

/** o dono do jogo: cuida pelo estado, treina, luta e mexe nas regras, com a sequencia tirada da semente (deterministico) */
function viver(semente: number, dias: number, o: { classica?: boolean; lutas: string[]; perto?: boolean }, m: Motor = new Motor(semente)): Motor {
  if (o.classica) m.configurar("classica");
  const passos = Math.round(dias * TPD / 30);
  let k = 0;
  const tenta = (f: () => void) => { try { f(); } catch (err) { if (err instanceof PetMorto) throw err; /* o motor recusou: segue */ } };
  for (let p = 0; p < passos && !m.morte; p++) {
    m.avancar(30);
    const e = m.e, r = hashSemente("gab-v13", semente, p) % 100;
    if (e.fome < .6 && p % 2 === 0) tenta(() => o.perto && m.mundo ? m.deixarComida("racao", Math.min(1023, m.mundo.pet[0] + 24), m.mundo.pet[1]) : m.observar("alimentar"));
    if (e.sujeira >= 2) tenta(() => m.observar("limpar"));
    if (p % 5 === 0) tenta(() => m.observar("acariciar"));
    if (p % 7 === 3) tenta(() => m.observar("brincar"));
    if (p % 13 === 12) tenta(() => m.observar("tapa" as AcaoDono));
    if (m.lesionadoDesde !== null) tenta(() => m.observar("tratar_lesao"));
    /* as medalhas chegam com o tempo (o Tamer as ganha fora do pet) */
    const dia = Math.floor((m.e.tick - 480) / TPD);
    if (m.medalhas < Math.min(5, 1 + dia)) tenta(() => m.liberar(Math.min(5, 1 + dia)));
    if (m.estagioAtual !== "bebe" && r < 30) tenta(() => m.treinar(EXERCICIOS[k++ % EXERCICIOS.length]));
    if (m.estagioAtual !== "bebe" && r >= 30 && r < 55) {
      const rival = o.lutas[k++ % o.lutas.length];
      /* a carta de Folego nas lutas contra os NPCs, de vez em quando (o motor recusa sem o treino minimo) */
      const carta = NPC[rival] && r % 4 === 0 ? "carta_folego" : null;
      tenta(() => m.lutar(rival, hashSemente("luta", m.semente, m.log.length), carta));
    }
    if (m.gp && r === 77) tenta(() => m.intervirGambit("travar", m.gp!.ativas[0]));
    if (m.gp && r === 78 && m.gp.ativas.length > 1) tenta(() => m.intervirGambit("vetar", m.gp!.ativas[m.gp!.ativas.length - 1]));
    if (m.gp && r === 79 && m.gp.vetos.length) tenta(() => m.intervirGambit("liberar", m.gp!.vetos[0]));
    if (r === 90) tenta(() => m.equipar("chip_forca"));
  }
  return m;
}

const vidas: Vida[] = [];
function gravar(nome: string, m: Motor): void {
  /* a assinatura depois de cada evento do registro, pelo replay */
  const x = new Motor(m.semente), assinaturas: string[] = [];
  for (const ev of m.log) { x.aplicarEvento(ev); assinaturas.push(sha(x.assinatura())); }
  if (assinaturas[assinaturas.length - 1] !== sha(m.assinatura())) throw new Error(`${nome}: o replay nao confere`);
  const tipos: Record<string, number> = {};
  for (const ev of m.log) tipos[ev[1] + (ev[1] === "d" ? ":" + ev[2] : "")] = (tipos[ev[1] + (ev[1] === "d" ? ":" + ev[2] : "")] ?? 0) + 1;
  console.log(JSON.stringify(tipos));
  vidas.push({ nome, semente: m.semente, log: m.log.map(ev => [...ev] as EventoRegistro), assinaturas });
  console.log(nome, m.log.length, "eventos", m.estagioAtual, m.lutas.lutas, "lutas no estagio", m.evolucoes.length, "evolucoes", m.morte ? "morreu" : "");
}
gravar("cuidado_e_bots", viver(1301, 2.5, { lutas: ["aleatorio", "agressivo", "tartaruga"] }));
const adulto = viver(1302, 3, { lutas: ["npc_tier1_brutamontes", "aleatorio", "npc_tier2_sentinela"], perto: true });
gravar("campanha_mundo", adulto);
/* o filho do adulto com ele mesmo (o evento "o", a heranca), vivendo um dia */
gravar("filho", viver(1305, 1, { lutas: ["aleatorio"] }, Motor.cruzar(adulto, adulto, 1305, 1306, "teste")));
gravar("ritmo_classico", viver(1303, 2, { classica: true, lutas: ["aleatorio", "atirador"] }));
gravar("adultos", viver(1304, 5, { lutas: ["aleatorio", "aleatorio", "contragolpe", "duelista"] }));
writeFileSync(fileURLToPath(new URL("../test/gabaritos/vidas_v13_ts.json", import.meta.url)),
  JSON.stringify({ gerado_por: "web/app/scripts/gerar_gabarito_vidas_v13.ts", versao_pet: VERSAO_PET, vidas }) + "\n");
