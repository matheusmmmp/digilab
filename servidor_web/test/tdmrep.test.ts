/* O aviso de mineração reservada (PI-6, o TDMRep do grupo do W3C,
   https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510/; D-CONTA-231 a 234): o arquivo /.well-known/tdmrep.json e o
   cabeçalho tdm-reservation: 1 na API, no Worker dos assets e no site do jogo (o build e o montar_site.sh). */
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { atender, CABECALHO_TDM as CABECALHO_WORKER, CAMINHO_TDMREP as CAMINHO_WORKER, TDM_RESERVA as RESERVA_WORKER, TDMREP_JSON,
  type Ambiente } from "../deploy/worker_assets/worker.ts";
import { criarApp } from "../src/app.ts";
import { GeradorFala } from "../src/fala.ts";
import { CABECALHO_TDM, CAMINHO_TDMREP, headersDoPages, META_TDM, TDM_RESERVA, tdmrepJson } from "../src/protecao/tdmrep.ts";

const PUBLICO = fileURLToPath(new URL("../../web/app/public/", import.meta.url));
const lerPublico = (c: string): string => readFileSync(join(PUBLICO, c), "utf8").replaceAll("\r\n", "\n");

describe("o formato (o relatório de 2024-05-10)", () => {
  it("o arquivo é uma lista de regras, com a origem toda reservada (1), sem o tdm-policy", () => {
    expect(JSON.parse(tdmrepJson())).toEqual([{ location: "/", "tdm-reservation": 1 }]);
    expect(CAMINHO_TDMREP).toBe("/.well-known/tdmrep.json");
    expect([CABECALHO_TDM, TDM_RESERVA]).toEqual(["tdm-reservation", 1]);
    expect(META_TDM).toBe('<meta name="tdm-reservation" content="1">');
    expect(tdmrepJson()).not.toContain("tdm-policy");
  });
  it("o Worker usa as mesmas regras", () => {
    expect([CAMINHO_WORKER, CABECALHO_WORKER, RESERVA_WORKER, TDMREP_JSON]).toEqual([CAMINHO_TDMREP, CABECALHO_TDM, TDM_RESERVA, tdmrepJson()]);
  });
});

describe("o build do jogo (web/app/public, node scripts/gerar_robots.ts)", () => {
  it("o .well-known/tdmrep.json e o _headers são os gerados", () => {
    expect(lerPublico(".well-known/tdmrep.json"), "rode node scripts/gerar_robots.ts").toBe(tdmrepJson());
    expect(lerPublico("_headers"), "rode node scripts/gerar_robots.ts").toBe(headersDoPages());
    /* o formato do _headers do Pages: o caminho na coluna 0, o cabeçalho indentado embaixo */
    expect(headersDoPages()).toMatch(/^\/\*\n {2}tdm-reservation: 1$/m);
  });
  it("a página do jogo leva a meta", () => {
    const html = readFileSync(fileURLToPath(new URL("../../web/app/index.html", import.meta.url)), "utf8");
    expect(html).toContain(META_TDM);
  });
});

describe("a API", () => {
  const app = () => criarApp({ gerador: new GeradorFala(null, null), motivoInicial: "" });
  it("serve o /.well-known/tdmrep.json, também no HEAD", async () => {
    const r = await app().request(CAMINHO_TDMREP);
    expect(r.status).toBe(200);
    expect(r.headers.get("content-type")).toMatch(/^application\/json/);
    expect(await r.text()).toBe(tdmrepJson());
    const h = await app().request(CAMINHO_TDMREP, { method: "HEAD" });
    expect(h.status).toBe(200);
    expect(h.headers.get(CABECALHO_TDM)).toBe("1");
  });
  it("toda resposta leva o cabeçalho: a /saude, o robots.txt, a fala, o 404 e a recusa da borda", async () => {
    for (const caminho of ["/saude", "/robots.txt", "/api/fala/status", "/nao-existe", CAMINHO_TDMREP]) {
      const r = await app().request(caminho);
      expect(r.headers.get(CABECALHO_TDM), caminho).toBe("1");
    }
    const recusa = await app().request("/saude", { headers: { "Cf-Ray": "x" } });
    expect(recusa.status).toBe(403);
    expect(recusa.headers.get(CABECALHO_TDM)).toBe("1");
  });
});

describe("o Worker dos assets", () => {
  const env: Ambiente = { ASSETS: { get: async () => null }, DIGILAB_SEGREDO_ASSETS: "s".repeat(40), DIGILAB_ORIGEM_JOGO: "https://exemplo.test" };
  const ctx = { waitUntil() {} };
  const pedir = (caminho: string, metodo = "GET") =>
    atender(new Request("https://assets.exemplo.test" + caminho, { method: metodo }), env, ctx, Date.now, null);
  it("serve o tdmrep.json sem assinatura; o cabeçalho vai também na recusa e no OPTIONS", async () => {
    const r = await pedir(CAMINHO_TDMREP);
    expect(r.status).toBe(200);
    expect(await r.text()).toBe(tdmrepJson());
    expect(r.headers.get(CABECALHO_TDM)).toBe("1");
    const h = await pedir(CAMINHO_TDMREP, "HEAD");
    expect([h.status, await h.text(), h.headers.get(CABECALHO_TDM)]).toEqual([200, "", "1"]);
    const sem = await pedir("/atlas/pecas.png");
    expect(sem.status).toBe(403);
    expect(sem.headers.get(CABECALHO_TDM)).toBe("1");
    expect((await pedir("/x.png", "OPTIONS")).headers.get(CABECALHO_TDM)).toBe("1");
  });
});

/* o montar_site.sh precisa do bash (o do Git no Windows, o do runner no CI) */
const temBash = spawnSync("bash", ["--version"]).status === 0;
describe.skipIf(!temBash)("o site do Pages (deploy/montar_site.sh)", () => {
  const script = fileURLToPath(new URL("../deploy/montar_site.sh", import.meta.url));
  const build = (arquivos: Record<string, string>): string => {
    const dir = mkdtempSync(join(tmpdir(), "digilab-build-"));
    for (const [c, t] of Object.entries(arquivos)) {
      mkdirSync(dirname(join(dir, c)), { recursive: true });
      writeFileSync(join(dir, c), t);
    }
    return dir;
  };
  const montar = (dir: string) => {
    const site = join(mkdtempSync(join(tmpdir(), "digilab-site-")), "site");
    return { site, r: spawnSync("bash", [script, dir, site], { encoding: "utf8" }) };
  };
  it("leva o robots.txt, o tdmrep.json e o _headers para a raiz; a página da raiz leva a meta", () => {
    const { site, r } = montar(build({ "index.html": "<html></html>", "robots.txt": "r", ".well-known/tdmrep.json": tdmrepJson(),
      "_headers": headersDoPages(), "assets/a.js": "x" }));
    expect(r.status, r.stderr + r.stdout).toBe(0);
    expect(readFileSync(join(site, ".well-known/tdmrep.json"), "utf8")).toBe(tdmrepJson());
    expect(readFileSync(join(site, "_headers"), "utf8")).toBe(headersDoPages());
    expect(readFileSync(join(site, "robots.txt"), "utf8")).toBe("r");
    expect(readFileSync(join(site, "index.html"), "utf8")).toContain(META_TDM);
    for (const c of ["jogo/robots.txt", "jogo/_headers", "jogo/.well-known"]) expect(existsSync(join(site, c)), c).toBe(false);
    expect(existsSync(join(site, "jogo/index.html"))).toBe(true);
  });
  it("falha alto se o build vier sem o aviso", () => {
    const { r } = montar(build({ "index.html": "<html></html>", "robots.txt": "r", "_headers": headersDoPages() }));
    expect(r.status).not.toBe(0);
    expect(r.stdout + r.stderr).toMatch(/tdmrep\.json/);
  });
});
