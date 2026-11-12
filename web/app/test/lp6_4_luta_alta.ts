/* LUTA_POC, LP6-4: a vida de um pet que chega ao Ultimate e ao Mega e luta neles (a luta que a LP6 muda: o apoio e a elipse sao so desses
   estagios). O Tamer ja tem as medalhas do Mega no nascimento (o evento "u"), e o dono cuida como na vida da LP2 (test/lp2_v21.ts); a
   partir do Champion o pet luta na Arena, um rival do estagio dele, o mapa em rodizio. O pet de um so e o primeiro do grupo (a v26, com o
   irmao no mesmo mundo, que so e cuidado). A mesma funcao serve ao gabarito (test/gabaritos/lp6_4_luta_alta_v<versao>.json), ao teste e ao
   gerador (node test/lp6_4_luta_alta.ts --gravar --versao 25). So le o motor. */
import { createHash } from "node:crypto";
import { writeFileSync } from "node:fs";
import { CMD, TPD } from "../motor/constantes.ts";
import { IDS_CENA, Motor, PetMorto, GrupoDoJogo, ehDoGrupo, hashSemente, mapaDoLugar, type EventoRegistro } from "../motor/index.ts";

export const SEMENTES_ALTA = [101, 202, 303] as const;
export const DIAS_ALTA = 4;
const PRODUTO = { chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true };
const sha = (x: string): string => createHash("sha256").update(x).digest("hex");

/** o pet que luta e o jeito de agir nele e de andar o tempo: o Motor sozinho ou o primeiro do grupo */
export interface Vida { m: Motor; agir<T>(f: (m: Motor) => T): T; avancar(n: number): void; log(): unknown; assinatura(): string; reproduzir(): string }

export function nascerAlta(semente: number, versao: number): Vida {
  if (ehDoGrupo(versao)) {
    const g = new GrupoDoJogo(semente, versao), a = g.ids[0]!;
    for (const i of g.ids) g.agir(i, m => { m.ligarProduto(PRODUTO); m.trocarCerebro("modular"); m.ligarPonteLuta(true); });
    return { m: g.motor(a), agir: f => g.agir(a, f), avancar: n => g.avancar(n), log: () => JSON.parse(JSON.stringify(g.log)),
             assinatura: () => g.assinatura(), reproduzir: () => GrupoDoJogo.reproduzir(semente, versao, g.log).assinatura() };
  }
  const m = new Motor(semente, versao);
  m.ligarProduto(PRODUTO); m.trocarCerebro("modular"); m.ligarPonteLuta(true);
  return { m, agir: f => f(m), avancar: n => m.avancar(n), log: () => JSON.parse(JSON.stringify(m.log)) as EventoRegistro[],
           assinatura: () => m.assinatura(), reproduzir: () => Motor.reproduzir(semente, m.log, versao).assinatura() };
}

export interface VidaAlta { semente: number; estagio: string; eventos: number; lutas: number; ult: number; mega: number; log_sha: string; assinatura: string; resultados: string }

export function viverAlta(semente: number, versao: number, dias = DIAS_ALTA): { v: Vida; res: string[]; ult: number; mega: number } {
  const v = nascerAlta(semente, versao), m = v.m, res: string[] = [];
  let ult = 0, mega = 0;
  v.agir(x => x.liberar(CMD.mega));
  for (let p = 0; p < Math.round(dias * TPD / 30) && !m.morte; p++) {
    v.avancar(30);
    const mu = m.mundo!, r = hashSemente("lp6-4-alta", semente, p) % 100;
    try {
      v.agir(x => {
        if (x.e.fome < .6 && p % 2 === 0) x.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
        if (x.e.sujeira >= 2 && r < 70) x.observar("limpar");
        if (p % 5 === 0 && r < 80) x.observar("acariciar");
        if (x.lesionadoDesde !== null) x.observar("tratar_lesao");
      });
      const est = m.estagioAtual;
      if (p % 4 === 2 && (est === "adolescente" || est === "adulto" || est === "mega")) {
        const s = hashSemente("lp6-4-alta-luta", semente, p);
        /* para o pet subir (a taxa de vitorias do Ultimate e do Mega): no Champion e em metade das do Ultimate, o NPC mais facil que o
           pet pode desafiar; as outras, a Arena */
        const npc = est === "adolescente" || (est === "adulto" && (p / 4 | 0) % 2 === 0);
        const R = v.agir(x => {
          if (npc) for (const l of x.lugares) for (const k of l.rivais) if (!x.porqueNaoLutaPoc(k, mapaDoLugar(l), s)) return x.lutarPoc(k, s, mapaDoLugar(l));
          const rv = x.rivaisArenaPoc(); return x.lutarPoc(rv[(p / 4 | 0) % rv.length]!, s, IDS_CENA[(p / 4 | 0) % IDS_CENA.length]!);
        });
        if (est === "adulto") ult++; else if (est === "mega") mega++;
        res.push(`${est}:${R.rival}@${R.mapa}:${R.serie.map(x => `${x.vencedor}/${x.relogio}/${x.vidaA}/${x.vidaB}/${x.passos}`).join(";")}`);
      }
    } catch (err) { if (err instanceof PetMorto) throw err; /* o motor recusou: segue */ }
  }
  return { v, res, ult, mega };
}

export function gravarAlta(semente: number, x: ReturnType<typeof viverAlta>): VidaAlta {
  const log = x.v.log() as unknown[];
  return { semente, estagio: x.v.m.estagioAtual, eventos: log.length, lutas: x.res.length, ult: x.ult, mega: x.mega,
           log_sha: sha(JSON.stringify(log)), assinatura: sha(x.v.assinatura()), resultados: sha(JSON.stringify(x.res)) };
}
export const reproduzirAlta = (x: ReturnType<typeof viverAlta>): string => sha(x.v.reproduzir());

export const gabaritoAlta = (versao: number): string => `./gabaritos/lp6_4_luta_alta_v${versao}.json`;
if (process.argv.includes("--gravar")) {
  const i = process.argv.indexOf("--versao"), versao = Number(process.argv[i + 1]);
  if (i < 0 || !Number.isInteger(versao)) throw new Error("--versao N");
  const vidas = SEMENTES_ALTA.map(s => gravarAlta(s, viverAlta(s, versao)));
  writeFileSync(new URL(gabaritoAlta(versao), import.meta.url),
    JSON.stringify({ versao: 1, pet: versao, dias: DIAS_ALTA, sementes: SEMENTES_ALTA, vidas }, null, 1) + "\n");
  console.log(`v${versao}: ${vidas.map(x => `${x.semente} ${x.estagio} ${x.lutas} lutas (${x.ult} Ult, ${x.mega} Mega)`).join("; ")}`);
}
