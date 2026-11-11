/* Save do jogo: so o registro {semente, log, versao}, na MESMA chave do digilab_sprites.html. O estado nunca
   e salvo: abrir e reprocessar o registro (Motor.reproduzir). Um save de hoje abre igual no app novo.
   Chaves: CHAVE (o save), CHAVE-aba ("destino/aba"), CHAVE-fala-llm, CHAVE-anterior, CHAVE-boas-vindas.
   Os dois pets (v24; docs/TAREFA_V3_COOPERACAO.md, CO4c): o save do grupo e {semente, log, versao, grupo: true, foco}, com o registro do grupo
   ([tick, tipo, valor, pet]; motor/grupo_jogo.ts) e o pet em foco na tela. Abrir e reprocessar o registro do grupo (GrupoDoJogo.reproduzir). */
import { GrupoDoJogo, Motor, type EventoGrupoJogo, type EventoRegistro } from "../motor/index.ts";
import { ligarProduto } from "./produto.ts";
import { versaoDoOvo } from "./lutaPoc.ts";

export const CHAVE = "digilab-web-v21-sprites";
export const CHAVE_ABA = CHAVE + "-aba";

/** o armazenamento que o save usa (localStorage no navegador; um Map nos testes) */
export interface Armazenamento { getItem(k: string): string | null; setItem(k: string, v: string): void }

export type LeituraSave =
  | { tipo: "vazio" }
  | { tipo: "ok"; motor: Motor; grupo: GrupoDoJogo | null }
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
  const s = d as { semente?: unknown; log?: unknown; versao?: unknown; grupo?: unknown; foco?: unknown };
  if (!Number.isInteger(s.semente) || !Array.isArray(s.log)) return { tipo: "erro", erro: "o save não tem semente inteira e registro", bruto };
  if (s.grupo !== undefined && s.grupo !== true) return { tipo: "erro", erro: "o save tem um grupo malformado", bruto };
  try {
    if (s.grupo === true) {
      const g = GrupoDoJogo.reproduzir(s.semente as number, s.versao as number, s.log as EventoGrupoJogo[]);
      if (typeof s.foco !== "string" || !g.ids.includes(s.foco)) return { tipo: "erro", erro: `o save do grupo tem um pet em foco desconhecido: ${String(s.foco)}`, bruto };
      return { tipo: "ok", motor: g.motor(s.foco), grupo: g };
    }
    return { tipo: "ok", motor: Motor.reproduzir(s.semente as number, s.log as EventoRegistro[], (s.versao ?? 1) as number), grupo: null };
  } catch (err) {
    return { tipo: "erro", erro: "o registro não reproduz: " + msg(err), bruto };
  }
}
/** grava o registro (mesmo formato e mesma ordem de campos do HTML) */
export function gravarSave(armaz: Armazenamento, m: Motor): void {
  armaz.setItem(CHAVE, textoSave(m));
}
export function textoSave(m: Motor): string {
  if (m.noGrupo) throw new Error("o pet do grupo e gravado com o grupo (textoSaveGrupo)");
  return JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao });
}
/** o save dos dois pets: o registro do grupo e o pet em foco */
export function textoSaveGrupo(g: GrupoDoJogo, foco: string): string {
  if (!g.ids.includes(foco)) throw new Error(`pet em foco fora do grupo: ${foco}`);
  return JSON.stringify({ semente: g.semente, log: g.log, versao: g.versao, grupo: true, foco });
}

/** primeiro acesso: o mesmo pet de exemplo do HTML (meio dia de vida e alguns cuidados), na versao dos ovos novos. Os pets v11 em diante
    nao tem elogio: o roteiro troca os dois elogios do HTML por carinho (os mesmos tempos e o mesmo numero de cuidados) */
export const SEMENTE_EXEMPLO = 20260924;
export function petExemplo(versao: number = versaoDoOvo()): Motor {
  const m = ligarProduto(new Motor(SEMENTE_EXEMPLO, versao)), elogio = "acariciar";
  const roteiro: [number, "alimentar" | "brincar" | "limpar" | "acariciar"][] =
    [[45, "alimentar"], [60, "brincar"], [30, elogio], [120, "limpar"], [90, "acariciar"], [60, "alimentar"], [45, elogio]];
  for (const [t, a] of roteiro) { m.avancar(t); m.observar(a); }
  m.avancar(30);
  return m;
}

const msg = (err: unknown): string => err instanceof Error ? err.message : String(err);
