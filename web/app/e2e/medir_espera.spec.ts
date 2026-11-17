/* CONVERSA_PET, F2 (docs/PLANO_ANALISE_V3_CONVERSA_ESPERA.md, secoes 2 e 3): a medida da espera da voz no jogo de verdade. SO RODA A MAO, e nao
   entra no `npm run e2e`: a configuracao ignora este spec sem MEDIR_ESPERA=1. Precisa do Ollama (gemma2:9b) ligado e da maquina reservada.

     npm run build
     MEDIR_ESPERA=1 MEDIR_ESPERA_BRACO=G npx playwright test            (PowerShell: $env:MEDIR_ESPERA="1"; $env:MEDIR_ESPERA_BRACO="G")

   O braco (G = voz local; H = DIGILAB_PROVEDOR_LIVRE no Claude Haiku, com o servidor iniciado assim) vem de MEDIR_ESPERA_BRACO (padrao G).
   O pet de teste modular (v16) e semeado por uma pagina da mesma origem que nao e o app (a regra do web/app/CLAUDE.md); o modo livre e a
   FALA_REDE vao pelo localStorage. 20 conversas de 6 turnos (120) com as frases dos roteiros da calibracao da DC5, na ordem, repetidas ate 20, com
   3 s de pausa depois de cada balao (PROPOSTO, SEM FONTE). Grava artifacts_v3_conversa_espera/<braco>/turnos.jsonl e meta.json.
   Nota: o jogo nao tem botao de conversa nova; a "conversa" aqui e o grupo de 6 turnos, e o historico da pagina (ate 10 trocas) segue entre elas. */
import { expect, test, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { basename, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const REPO = resolve(fileURLToPath(new URL("../../..", import.meta.url)));
const PREFIXO = "/" + basename(REPO);
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const BRACO = process.env.MEDIR_ESPERA_BRACO ?? "G";
const N_CONVERSAS = 20, N_TURNOS = 6, PAUSA_MS = 3000, TIMEOUT_TURNO_MS = 180_000;
const MODELO = process.env.MEDIR_ESPERA_MODELO ?? "gemma2:9b";
const OLLAMA = process.env.OLLAMA_HOST_URL ?? "http://127.0.0.1:11434";
const SAIDA = join(REPO, "artifacts_v3_conversa_espera", BRACO);

interface Roteiro { id: string; turnos: { papel: string; texto: string }[] }
function roteiros(): Roteiro[] {
  const r = JSON.parse(readFileSync(join(REPO, "experiments/configs/v3_conversa_dc5/roteiros_calibracao.json"), "utf8")).roteiros as Roteiro[];
  for (const x of r) if (x.turnos.length !== N_TURNOS) throw new Error(`roteiro ${x.id} sem ${N_TURNOS} turnos`);
  return r;
}
function sha256Arquivo(p: string): string { return createHash("sha256").update(readFileSync(p)).digest("hex"); }
/** o sha256 do build: o hash dos arquivos de web/dist (caminho relativo e conteudo), em ordem */
function sha256Pasta(pasta: string): string {
  const h = createHash("sha256");
  const andar = (d: string): void => {
    for (const n of readdirSync(d).sort()) {
      const p = join(d, n);
      if (statSync(p).isDirectory()) andar(p); else { h.update(p.slice(pasta.length)); h.update(readFileSync(p)); }
    }
  };
  andar(pasta);
  return h.digest("hex");
}
function comando(exe: string, args: string[]): { saida: string | null; motivo: string | null } {
  try { return { saida: execFileSync(exe, args, { encoding: "utf8", timeout: 20_000 }).trim(), motivo: null }; }
  catch (e) { return { saida: null, motivo: `${exe} indisponivel: ${e instanceof Error ? e.message : String(e)}` }; }
}

async function semear(page: Page): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");                        /* uma pagina da mesma origem que nao e o app */
  await page.evaluate(chave => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave + "-nivel", JSON.stringify({ marcos: [1, 2, 3], cartoes: [1, 2, 3] }));      /* o Conversar aberto */
    localStorage.setItem(chave + "-lab-ligado", "1");
    localStorage.setItem(chave + "-lab", JSON.stringify({ semente: 4242, log: [], versao: 16 }));            /* o pet de teste modular, sempre o mesmo save */
    localStorage.setItem(chave + "-modo-fala", "livre");                                                      /* falaLivre.ts: MODO */
    localStorage.setItem(chave + "-fala-rede", "1");                                                          /* falaLivre.ts: FALA_REDE */
  }, CHAVE);
}

test(`medir a espera da voz, braco ${BRACO}: ${N_CONVERSAS} conversas de ${N_TURNOS} turnos`, async ({ browser }) => {
  test.skip(process.env.MEDIR_ESPERA !== "1", "so a mao, com MEDIR_ESPERA=1 (precisa do Ollama)");
  test.setTimeout(3 * 3600_000);
  const ros = roteiros();
  const frases: { conversa: number; turno: number; roteiro: string; papel: string; texto: string }[] = [];
  for (let c = 0; c < N_CONVERSAS; c++) {
    const r = ros[c % ros.length];
    r.turnos.forEach((t, i) => frases.push({ conversa: c + 1, turno: i + 1, roteiro: r.id, papel: t.papel, texto: t.texto }));
  }
  expect(frases).toHaveLength(N_CONVERSAS * N_TURNOS);

  mkdirSync(SAIDA, { recursive: true });
  const ps = comando("ollama", ["ps"]);
  const gpu = comando("nvidia-smi", ["--query-gpu=name,memory.total", "--format=csv,noheader"]);
  const psInicio = ps;
  /* o frio: descarrega o modelo antes da primeira conversa (keep_alive 0, o mesmo de digilab_fala_livre/ollama.py) */
  let descarga: string | null = null;
  try {
    const r = await fetch(`${OLLAMA}/api/generate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ model: MODELO, keep_alive: 0 }) });
    if (!r.ok) throw new Error("HTTP " + r.status);
  } catch (e) { descarga = `nao descarregou o modelo: ${e instanceof Error ? e.message : String(e)}`; }

  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  await semear(page);
  await page.goto(APP + "?medir_espera=1#/config/laboratorio");           /* o pet de teste aberto fica so na memoria da pagina: nao recarregar depois */
  await page.getByRole("button", { name: "Abrir", exact: true }).click();
  await expect(page.locator(".topo-lab .lab-selo")).toBeVisible();
  expect(await page.evaluate(() => Array.isArray((window as any).__medidaEspera))).toBe(true);
  await page.evaluate(() => { location.hash = "#/conversar/chat"; });
  await expect(page.locator("#conv-msg")).toBeEnabled();

  const conversas = () => page.evaluate(() => ((window as any).__medidaEspera as any[]).filter(r => r.situacao === "conversa").length);
  const t0 = Date.now();
  for (let i = 0; i < frases.length; i++) {
    await page.locator("#conv-msg").fill(frases[i].texto);
    await page.getByRole("button", { name: "Enviar" }).click();
    await expect.poll(conversas, { timeout: 10_000 }).toBe(i + 1);
    await page.waitForFunction(n => {
      const r = ((window as any).__medidaEspera as any[]).filter(x => x.situacao === "conversa")[n];
      return r && (r.t_balao !== null || r.erro !== null);
    }, i, { timeout: TIMEOUT_TURNO_MS, polling: 100 });
    await page.waitForTimeout(PAUSA_MS);                                    /* o tempo de ler (PROPOSTO, SEM FONTE) */
  }
  /* as ultimas verificacoes ainda podem estar em curso: espera ate 60 s para o t_verif da ultima */
  await page.waitForFunction(() => {
    const c = ((window as any).__medidaEspera as any[]).filter(x => x.situacao === "conversa");
    const u = c[c.length - 1];
    return u.t_verif !== null || u.erro !== null;
  }, null, { timeout: 60_000 }).catch(() => { /* fica t_verif null */ });
  const lista: any[] = await page.evaluate(() => (window as any).__medidaEspera);
  const psFim = comando("ollama", ["ps"]);

  let k = 0;
  const linhas = lista.map(r => {
    const f = r.situacao === "conversa" ? frases[k++] : null;
    return { braco: BRACO, ...r, conversa: f ? f.conversa : null, turno: f ? f.turno : null, roteiro: f ? f.roteiro : null, papel: f ? f.papel : null, frase: f ? f.texto : null, fria: f ? f.conversa === 1 : null };
  });
  expect(k).toBe(frases.length);
  writeFileSync(join(SAIDA, "turnos.jsonl"), linhas.map(l => JSON.stringify(l)).join("\n") + "\n");

  const commit = comando("git", ["-C", REPO, "rev-parse", "HEAD"]);
  const dist = join(REPO, "web", "dist");
  writeFileSync(join(SAIDA, "meta.json"), JSON.stringify({
    braco: BRACO, commit: commit.saida, commit_motivo: commit.motivo, n_conversas: N_CONVERSAS, n_turnos_por_conversa: N_TURNOS, pausa_ms: PAUSA_MS,
    roteiros_calibracao_sha256: sha256Arquivo(join(REPO, "experiments/configs/v3_conversa_dc5/roteiros_calibracao.json")),
    build_sha256: existsSync(dist) ? sha256Pasta(dist) : null, build_motivo: existsSync(dist) ? null : "web/dist nao existe (rode npm run build)",
    servidor_sha256: sha256Arquivo(join(REPO, "servidor", "servidor_local.py")), modelo: MODELO,
    gpu: gpu.saida, gpu_motivo: gpu.motivo, ollama_ps_inicio: psInicio.saida, ollama_ps_inicio_motivo: psInicio.motivo,
    ollama_ps_fim: psFim.saida, ollama_ps_fim_motivo: psFim.motivo, descarga_do_modelo: descarga,
    duracao_s: (Date.now() - t0) / 1000, provedor_livre: process.env.DIGILAB_PROVEDOR_LIVRE ?? null,
  }, null, 2) + "\n");
  await ctx.close();
});
