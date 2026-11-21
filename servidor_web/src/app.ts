/* As rotas do servidor (CN1; a conta da CN2 em src/conta/rotas.ts). O contrato da fala e o mesmo do servidor/servidor_local.py, que o jogo usa hoje
   (web/app/src/fala.ts):
     GET  /saude             {"ok": true, "servico": "digilab-servidor-web"}
     GET  /api/fala/status   {"ativo", "provedor", "modelo", "sem_custo", "motivo", "gasto", "estatisticas"}
     POST /api/fala          {"motivo": {...}, "estagio": "...", "humor": 0.5} -> {"texto", "fonte": "llm"|"template", "detalhe", "gasto"}
   Pedido vindo por tunel ou proxy (cabecalhos da Cloudflare e o X-Forwarded-For) leva 403, como no servidor local sem --remoto: o acesso
   de fora vem pela borda da CN5 (abaixo). Com a conta, a fala usa a cota por conta e por dia (CN4, src/protecao/cota.ts): a resposta leva a `cota` ({limite,
   usadas, restam, dia} com a sessão; null sem ela), e, fora do local, a fala sem a sessão é só o template.
   A borda (CN5, docs/infra/DEPLOY_CN5.md): no local (o padrao), pedido vindo por tunel ou proxy (cabecalhos da Cloudflare e o
   X-Forwarded-For) leva 403, como no servidor local sem --remoto. Na borda "cloudflare" (a VPS, D-CONTA-197), o servidor continua so em
   127.0.0.1 e o pedido so chega pelo Cloudflare Tunnel: o que vem sem o Cf-Ray e o Cf-Connecting-Ip leva 403, e a conta tem de ser a de
   fora (https, sem o provedor falso). */
import { Hono, type Context } from "hono";
import { motivoDeDict, PedidoInvalido } from "./catalogo.ts";
import type { ConfigConta } from "./conta/config.ts";
import { montarRotasConta, type GuardasConta } from "./conta/rotas.ts";
import { montarRotasDesafio } from "./desafio/desafio.ts";
import { ConferidorEmWorker, type Conferidor } from "./envio/conferidor.ts";
import { montarRotasEnvio } from "./envio/rotas.ts";
import { montarRotasSemana } from "./envio/semanas.ts";
import { montarRotasSemente } from "./envio/sementes.ts";
import type { GeradorFala } from "./fala.ts";
import { montarRotasPremios } from "./premios/premios.ts";
import { montarRotasRankings } from "./premios/rankings.ts";
import { montarRotasNuvem } from "./nuvem/nuvem.ts";
import { CotaDaConta, SEM_CONTA, type CotaFala, type EstadoCota } from "./protecao/cota.ts";
import { montarRobots, montarRotasProtecao } from "./protecao/rotas.ts";

export const LIMITE_CORPO = 16 * 1024;
const CABECALHOS_DE_FORA = ["cf-ray", "cf-connecting-ip", "x-forwarded-for"];
/** os cabecalhos que o Cloudflare Tunnel sempre poe no pedido que passou pela borda */
const CABECALHOS_DA_BORDA = ["cf-ray", "cf-connecting-ip"];

/** "local": so a maquina (o padrao, a regra do servidor_web/CLAUDE.md); "cloudflare": so pelo Cloudflare Tunnel, na VPS (CN5) */
export type Borda = "local" | "cloudflare";
export const BORDAS: readonly Borda[] = ["local", "cloudflare"];

/** `conta`: a conta (CN2, src/conta/rotas.ts) e o envio dos logs (MMO3, src/envio/rotas.ts); sem ela, o servidor é o da CN1 (a /saude e a fala) */
/** `conferidor`: quem confere os envios (src/envio/conferidor.ts); por padrão, um worker só deste app */
/** `borda`: de onde o pedido pode vir (Borda); por padrão, "local" */
export interface Opcoes { gerador: GeradorFala; motivoInicial: string; conta?: ConfigConta; conferidor?: Conferidor; borda?: Borda }

export function criarApp({ gerador, motivoInicial, conta, conferidor, borda = "local" }: Opcoes): Hono {
  if (!BORDAS.includes(borda)) throw new Error(`borda desconhecida: ${borda} (${BORDAS.join(" ou ")})`);
  /* o provedor falso e a /dev/conta só existem na conta local: pela borda, ficariam abertos para fora */
  if (borda === "cloudflare" && conta?.local) throw new Error("a borda cloudflare pede a conta de fora (DIGILAB_URL_API em https://)");
  const app = new Hono();
  const json = (c: { json: (d: unknown, s?: number, h?: Record<string, string>) => Response }, codigo: number, dados: unknown) =>
    c.json(dados, codigo, { "Cache-Control": "no-store" });

  app.use("*", async (c, next) => {
    if (borda === "local" && CABECALHOS_DE_FORA.some(h => c.req.header(h))) return json(c, 403, { erro: "acesso externo so com --remoto" });
    if (borda === "cloudflare" && !CABECALHOS_DA_BORDA.every(h => c.req.header(h))) return json(c, 403, { erro: "so pela borda" });
    await next();
  });

  /* a conta antes da fala: o CORS da conta vale também para a /api/fala, e a fala com a sessão usa a cota (CN4) */
  let guardas: GuardasConta | null = null;
  if (conta) {
    guardas = montarRotasConta(app, conta);
    const g = guardas;
    montarRotasEnvio(app, conta, g, conferidor ?? new ConferidorEmWorker().conferir);
    montarRotasSemente(app, conta, g);
    montarRotasSemana(app, conta, g);
    montarRotasDesafio(app, conta, g);
    montarRotasPremios(app, conta, g);
    montarRotasRankings(app, conta, g);
    montarRotasNuvem(app, conta, g);
    montarRotasProtecao(app, conta, g);
    app.use("/api/fala", g.cors);
    app.use("/api/fala/*", g.cors);
  }

  /** a cota da fala deste pedido (CN4): a da conta com a sessão; sem a sessão, nenhuma (CN1) ou a que nunca deixa (fora do local) */
  const cotaDoPedido = (c: Context): { cota?: CotaFala; estado: () => EstadoCota | null } => {
    if (!conta || !guardas) return { estado: () => null };
    const s = guardas.sessaoDe(c);
    if (s) {
      const cota = new CotaDaConta(conta.banco, s.conta_id, conta.protecao.cotaFalaDia, conta.agora());
      return { cota, estado: () => cota.estado() };
    }
    return { cota: conta.protecao.falaSoComConta ? SEM_CONTA : undefined, estado: () => null };
  };
  const origemDaFala = (c: Context): boolean => {
    const o = c.req.header("origin");
    return !conta || o === undefined || o === conta.origemJogo || o === new URL(conta.urlApi).origin;
  };

  montarRobots(app);
  app.get("/saude", c => json(c, 200, { ok: true, servico: "digilab-servidor-web" }));

  app.get("/api/fala/status", c => {
    const p = gerador.provedor;
    const [ativo, motivo] = p === null ? [false, motivoInicial] : p.disponivel();
    return json(c, 200, { ativo, provedor: p?.nome ?? null, modelo: gerador.modelo, sem_custo: p !== null && !p.temCusto, motivo,
      gasto: gerador.gasto?.paraDict() ?? null, estatisticas: gerador.estatisticas,
      ...(conta ? { cota: cotaDoPedido(c).estado(), so_com_conta: conta.protecao.falaSoComConta } : {}) });
  });

  app.post("/api/fala", async c => {
    if (!origemDaFala(c)) return json(c, 403, { erro: "origem desconhecida" });
    const pedidoCota = cotaDoPedido(c);
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
      resultado = await gerador.gerar(motivo, d.estagio, humor, pedidoCota.cota);
    } catch (err) {
      if (err instanceof PedidoInvalido) return json(c, 400, { erro: `pedido invalido: ${err.message}` });
      throw err;
    }
    return json(c, 200, { ...resultado, gasto: gerador.gasto?.paraDict() ?? null, ...(conta ? { cota: pedidoCota.estado() } : {}) });
  });

  app.notFound(c => json(c, 404, { erro: "rota desconhecida" }));
  return app;
}
