/* As rotas do servidor (CN1, sem conta ainda). O contrato da fala e o mesmo do servidor/servidor_local.py, que o jogo usa hoje
   (web/app/src/fala.ts):
     GET  /saude             {"ok": true, "servico": "digilab-servidor-web"}
     GET  /api/fala/status   {"ativo", "provedor", "modelo", "sem_custo", "motivo", "gasto", "estatisticas"}
     POST /api/fala          {"motivo": {...}, "estagio": "...", "humor": 0.5} -> {"texto", "fonte": "llm"|"template", "detalhe", "gasto"}
   Pedido vindo por tunel ou proxy (cabecalhos da Cloudflare e o X-Forwarded-For) leva 403, como no servidor local sem --remoto: o acesso
   de fora e da CN5 (a borda, a conta e a cota). */
import { Hono } from "hono";
import { motivoDeDict, PedidoInvalido } from "./catalogo.ts";
import type { GeradorFala } from "./fala.ts";

export const LIMITE_CORPO = 16 * 1024;
const CABECALHOS_DE_FORA = ["cf-ray", "cf-connecting-ip", "x-forwarded-for"];

export interface Opcoes { gerador: GeradorFala; motivoInicial: string }

export function criarApp({ gerador, motivoInicial }: Opcoes): Hono {
  const app = new Hono();
  const json = (c: { json: (d: unknown, s?: number, h?: Record<string, string>) => Response }, codigo: number, dados: unknown) =>
    c.json(dados, codigo, { "Cache-Control": "no-store" });

  app.use("*", async (c, next) => {
    if (CABECALHOS_DE_FORA.some(h => c.req.header(h))) return json(c, 403, { erro: "acesso externo so com --remoto" });
    await next();
  });

  app.get("/saude", c => json(c, 200, { ok: true, servico: "digilab-servidor-web" }));

  app.get("/api/fala/status", c => {
    const p = gerador.provedor;
    const [ativo, motivo] = p === null ? [false, motivoInicial] : p.disponivel();
    return json(c, 200, { ativo, provedor: p?.nome ?? null, modelo: gerador.modelo, sem_custo: p !== null && !p.temCusto, motivo,
      gasto: gerador.gasto?.paraDict() ?? null, estatisticas: gerador.estatisticas });
  });

  app.post("/api/fala", async c => {
    const tamanho = Number(c.req.header("content-length") ?? "0");
    if (!(tamanho > 0 && tamanho <= LIMITE_CORPO)) return json(c, 400, { erro: "corpo ausente ou grande demais" });
    const corpo = await c.req.text();
    if (Buffer.byteLength(corpo, "utf8") > LIMITE_CORPO) return json(c, 400, { erro: "corpo ausente ou grande demais" });
    let resultado;
    try {
      let dados: unknown;
      try { dados = JSON.parse(corpo); } catch (err) { throw new PedidoInvalido((err as Error).message); }
      if (typeof dados !== "object" || dados === null || Array.isArray(dados)) throw new PedidoInvalido("o pedido precisa ser um objeto");
      const d = dados as Record<string, unknown>;
      if (!("motivo" in d)) throw new PedidoInvalido("'motivo'");
      const motivo = motivoDeDict(d.motivo);
      if (!("estagio" in d)) throw new PedidoInvalido("'estagio'");
      const humor = d.humor ?? null;
      if (humor !== null && (typeof humor !== "number" || !Number.isFinite(humor))) throw new PedidoInvalido(`humor invalido: ${JSON.stringify(humor)}`);
      if (typeof d.estagio !== "string") throw new PedidoInvalido(`estagio desconhecido: ${JSON.stringify(d.estagio)}`);
      resultado = await gerador.gerar(motivo, d.estagio, humor);
    } catch (err) {
      if (err instanceof PedidoInvalido) return json(c, 400, { erro: `pedido invalido: ${err.message}` });
      throw err;
    }
    return json(c, 200, { ...resultado, gasto: gerador.gasto?.paraDict() ?? null });
  });

  app.notFound(c => json(c, 404, { erro: "rota desconhecida" }));
  return app;
}
