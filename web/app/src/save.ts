/* Save do jogo: so o registro {semente, log, versao}, na MESMA chave do digilab_sprites.html. O estado nunca
   e salvo: abrir e reprocessar o registro (Motor.reproduzir). Um save de hoje abre igual no app novo.
   Chaves: CHAVE (o save), CHAVE-aba ("destino/aba"), CHAVE-fala-llm, CHAVE-anterior, CHAVE-boas-vindas. */
import { Motor, type EventoRegistro } from "../motor/index.ts";

export const CHAVE = "digilab-web-v21-sprites";
export const CHAVE_ABA = CHAVE + "-aba";

/** o armazenamento que o save usa (localStorage no navegador; um Map nos testes) */
export interface Armazenamento { getItem(k: string): string | null; setItem(k: string, v: string): void }

export type LeituraSave =
  | { tipo: "vazio" }
  | { tipo: "ok"; motor: Motor }
  | { tipo: "erro"; erro: string; bruto: string };

/** le e reproduz o save. Save sem versao = pet de antes do porte (v1): segue igual (como no HTML).
    Save que existe mas nao abre: erro visivel (o HTML caia no pet de exemplo e gravava por cima). */
export function lerSave(armaz: Armazenamento): LeituraSave {
  let bruto: string | null;
  try { bruto = armaz.getItem(CHAVE); } catch (err) { return { tipo: "erro", erro: "armazenamento do navegador indisponível: " + msg(err), bruto: "" }; }
  if (bruto === null) return { tipo: "vazio" };
  let d: unknown;
  try { d = JSON.parse(bruto); } catch (err) { return { tipo: "erro", erro: "o save não é JSON: " + msg(err), bruto }; }
  if (d === null) return { tipo: "vazio" };
  const s = d as { semente?: unknown; log?: unknown; versao?: unknown };
  if (!Number.isInteger(s.semente) || !Array.isArray(s.log)) return { tipo: "erro", erro: "o save não tem semente inteira e registro", bruto };
  try {
    return { tipo: "ok", motor: Motor.reproduzir(s.semente as number, s.log as EventoRegistro[], (s.versao ?? 1) as number) };
  } catch (err) {
    return { tipo: "erro", erro: "o registro não reproduz: " + msg(err), bruto };
  }
}
/** grava o registro (mesmo formato e mesma ordem de campos do HTML) */
export function gravarSave(armaz: Armazenamento, m: Motor): void {
  armaz.setItem(CHAVE, textoSave(m));
}
export function textoSave(m: Motor): string {
  return JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao });
}

/** primeiro acesso: o mesmo pet de exemplo do HTML (meio dia de vida e alguns cuidados), na versao dos ovos novos. Nos pets v11 nao ha
    elogio: o roteiro troca os dois elogios do HTML por carinho (os mesmos tempos e o mesmo numero de cuidados) */
export function petExemplo(): Motor {
  const m = new Motor(20260924), elogio = m.versao >= 11 ? "acariciar" : "elogiar";
  const roteiro: [number, "alimentar" | "brincar" | "elogiar" | "limpar" | "acariciar"][] =
    [[45, "alimentar"], [60, "brincar"], [30, elogio], [120, "limpar"], [90, "acariciar"], [60, "alimentar"], [45, elogio]];
  for (const [t, a] of roteiro) { m.avancar(t); m.observar(a); }
  m.avancar(30);
  return m;
}

const msg = (err: unknown): string => err instanceof Error ? err.message : String(err);
