/* Sobe o servidor local (CN1).
     npm run dev                                   # http://127.0.0.1:8766, provedor auto (Claude se houver chave, senao so template)
     npm run dev -- --porta 8765                   # na porta do servidor Python: o proxy do Vite (web/app) cai aqui
     npm run dev -- --provedor nenhum              # so template
     npm run dev -- --modelo claude-haiku-4-5 --limite-usd 2
   A chave so no ambiente (ANTHROPIC_API_KEY). O teto e TOTAL e acumulado no mesmo arquivo do servidor Python (servidor/gasto_fala.json,
   fora do git), para os dois servidores somarem um teto so; DIGILAB_GASTO_FALA troca o arquivo. So escuta em 127.0.0.1. */
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";
import { serve } from "@hono/node-server";
import { criarApp } from "./app.ts";
import { CATALOGO } from "./catalogo.ts";
import { criarClienteClaude, GeradorFala, ProvedorClaude } from "./fala.ts";
import { ControleGasto } from "./gasto.ts";

export const PORTA_PADRAO = 8766;
export const ARQUIVO_GASTO_PADRAO = fileURLToPath(new URL("../../servidor/gasto_fala.json", import.meta.url));

const { values: a } = parseArgs({
  options: {
    porta: { type: "string", default: String(PORTA_PADRAO) },
    provedor: { type: "string", default: "auto" },
    modelo: { type: "string" },
    "limite-usd": { type: "string", default: String(CATALOGO.limite_usd_padrao) },
  },
  strict: true,
});

const porta = Number(a.porta), limite = Number(a["limite-usd"]);
if (!Number.isInteger(porta) || porta <= 0 || porta > 65535) throw new Error(`--porta invalida: ${a.porta}`);
if (!Number.isFinite(limite) || limite < 0) throw new Error(`--limite-usd invalido: ${a["limite-usd"]}`);
if (!["auto", "claude", "nenhum"].includes(a.provedor)) throw new Error(`--provedor desconhecido: ${a.provedor} (auto, claude ou nenhum)`);

let gerador: GeradorFala, motivo = "", estado: string;
const cliente = a.provedor === "nenhum" ? null : criarClienteClaude();
if (a.provedor === "nenhum") {
  motivo = "desligado por --provedor nenhum";
} else if (cliente === null) {
  motivo = "sem credencial da API do Claude (ANTHROPIC_API_KEY)";
}
if (cliente === null) {
  gerador = new GeradorFala(null, null);
  estado = `sem LLM: so template (${motivo})`;
} else {
  const arquivo = process.env.DIGILAB_GASTO_FALA || ARQUIVO_GASTO_PADRAO;
  const gasto = new ControleGasto(limite, arquivo, (nivel, g) =>
    console.log(`  ALERTA de gasto: ${Math.round(nivel * 100)}% do teto (US$ ${g.gasto_usd.toFixed(4)} de US$ ${g.limite_usd.toFixed(2)})`));
  /* modelo sem preco levanta aqui: o servidor nao sobe */
  gerador = new GeradorFala(new ProvedorClaude(cliente, a.modelo ?? CATALOGO.modelo_padrao), gasto);
  estado = `LLM: Claude ${gerador.modelo}; gasto US$ ${gasto.gasto.toFixed(4)} de US$ ${gasto.limite.toFixed(2)} (${arquivo})`;
}

serve({ fetch: criarApp({ gerador, motivoInicial: motivo }).fetch, hostname: "127.0.0.1", port: porta }, info =>
  console.log(`Digilab servidor_web em http://127.0.0.1:${info.port}  (/saude, /api/fala/status, POST /api/fala)  [${estado}]`));
