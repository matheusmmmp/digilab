/* LUTA_POC, LP2: a vida de um pet v21 (a luta da POC), com cuidado e lutas pela Arena (uma forma do estagio, mapa em rodizio) e pela
   Campanha (o primeiro NPC, no mapa do lugar). A mesma funcao serve ao gabarito da vida nova (test/gabaritos/lp2_vidas_v21.json), ao teste e
   ao gerador (node test/lp2_v21.ts --gravar). So le o motor. */
import { createHash } from "node:crypto";
import { writeFileSync } from "node:fs";
import { TPD } from "../motor/constantes.ts";
import { IDS_CENA, Motor, PetMorto, VERSAO_V21, hashSemente, mapaDoLugar, type EventoRegistro } from "../motor/index.ts";

export type VarianteV21 = "v21_modular" | "v21_a";
export const VARIANTES_V21: readonly VarianteV21[] = ["v21_modular", "v21_a"];
export const SEMENTES_V21 = [101, 202, 303, 404, 505] as const;
export const DIAS_V21 = 5;
const PRODUTO = { chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true };

/** o ovo v21 como o app o choca com a chave ligada (src/produto.ts): as chaves do produto, o cerebro e a ponte da luta */
export function nascerV21(v: VarianteV21, semente: number, ponte = true, versao: number = VERSAO_V21): Motor {
  const m = new Motor(semente, versao);
  m.ligarProduto(PRODUTO);
  m.trocarCerebro(v === "v21_a" ? "a" : "modular");
  if (ponte) m.ligarPonteLuta(true);
  return m;
}

const sha = (x: string): string => createHash("sha256").update(x).digest("hex");

export interface VidaV21 {
  variante: VarianteV21; semente: number; estagio: string; eventos: number; lutas: number; vitorias: number; lesoes: number;
  log_sha: string; assinatura: string; resultados: string;
}

/** a vida de cuidado com lutas da POC; devolve o motor, o registro e o resultado de cada luta */
export function viverV21(v: VarianteV21, semente: number, dias = DIAS_V21, ponte = true, versao: number = VERSAO_V21): { m: Motor; log: EventoRegistro[]; res: string[] } {
  const m = nascerV21(v, semente, ponte, versao), res: string[] = [];
  for (let p = 0; p < Math.round(dias * TPD / 30) && !m.morte; p++) {
    m.avancar(30);
    const mu = m.mundo!, r = hashSemente("lp2-v21", semente, p) % 100;
    try {
      if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
      if (m.e.sujeira >= 2 && r < 70) m.observar("limpar");
      if (p % 5 === 0 && r < 80) m.observar("acariciar");
      if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
      if (p % 12 === 6 && m.estagioAtual !== "bebe") {
        const s = hashSemente("lp2-v21-luta", semente, p);
        const R = p % 36 === 30
          ? m.lutarPoc(m.lugares[0].rivais[0], s, mapaDoLugar(m.lugares[0]))
          : (() => { const rv = m.rivaisArenaPoc(); return m.lutarPoc(rv[(p / 12 | 0) % rv.length], s, IDS_CENA[(p / 12 | 0) % IDS_CENA.length]); })();
        res.push(`${R.rival}@${R.mapa}:${R.serie.map(x => `${x.vencedor}/${x.relogio}/${x.vidaA}/${x.vidaB}`).join(";")}`);
      }
    } catch (err) { if (err instanceof PetMorto) throw err; /* o motor recusou: segue */ }
  }
  return { m, log: JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], res };
}

export function gravarV21(v: VarianteV21, semente: number, m: Motor, log: readonly EventoRegistro[], res: readonly string[]): VidaV21 {
  return {
    variante: v, semente, estagio: m.estagioAtual, eventos: log.length, lutas: m.lutas.lutas, vitorias: m.lutas.vitorias, lesoes: m.lutas.lesoes,
    log_sha: sha(JSON.stringify(log)), assinatura: sha(m.assinatura()), resultados: sha(JSON.stringify(res)),
  };
}

/** o arquivo do gabarito de cada versao: o da v21 (LP2) e o da v22 (o da LP5-5, gravado antes da v23 entrar) */
export const gabaritoVidas = (versao: number): string => `./gabaritos/lp2_vidas_v${versao}.json`;
if (process.argv.includes("--gravar")) {
  /* --versao 22: o gabarito da v22 (LP5-5); sem ele, o da v21 */
  const i = process.argv.indexOf("--versao"), versao = i >= 0 ? Number(process.argv[i + 1]) : VERSAO_V21;
  const vidas = VARIANTES_V21.flatMap(v => SEMENTES_V21.map(s => { const { m, log, res } = viverV21(v, s, DIAS_V21, true, versao); return gravarV21(v, s, m, log, res); }));
  writeFileSync(new URL(gabaritoVidas(versao), import.meta.url),
    JSON.stringify({ versao: 1, dias: DIAS_V21, sementes: SEMENTES_V21, variantes: VARIANTES_V21, vidas }, null, 1) + "\n");
  console.log(`gravado: ${vidas.length} vidas, ${vidas.reduce((s, x) => s + x.lutas, 0)} lutas`);
}
