/* A página do WORLD-POC-01a (etapas E3 e E4): a sala em Three.js (vista.ts) sobre o mundo inteiro do POC, em tempo real.
   - O mundo anda TICKS_POR_SEGUNDO ticks por segundo; a vista desenha a cada quadro, interpolando o pet e a bola entre o tick anterior e
     o atual. A interpolação é só desenho: o motor nunca lê a vista.
   - O sprite: o atlas do Digimon UP, só no modo dev e só se ele existir na máquina (W-6: fica fora do repositório); senão, ou com
     ?sprite=reserva, o sprite de reserva.
   - A M3: o contador de quadros na tela e o botão "Medir 10 s", que mostra a medida em JSON para copiar (no celular, a página em http
     não tem a área de transferência; o texto fica selecionável).
   - `window.__poc`: os ganchos que o e2e (e2e_poc/) usa para a M1, a M2, a M3 e a M5. */
import { Simulacao } from "./simulacao.ts";
import { PALETA_RESERVA, SPRITE_RESERVA } from "./sprite_reserva.ts";
import { type FonteSprite, type Pose, Vista } from "./vista.ts";

const TICKS_POR_SEGUNDO = 10;
/* o POC-02 (docs/TAREFA_V2_WORLD_POC_02.md, etapa E3): a página roda com o corpo químico do jogo; ?corpo=0 volta ao POC-01a */
const COM_CORPO = new URLSearchParams(location.search).get("corpo") !== "0";
const novaSimulacao = (semente: number) => new Simulacao(semente, undefined, { corpo: COM_CORPO });

/** os receptores no painel, na ordem e com os nomes da tela; a leitura vai de 0 a 1024 (nos drives de hoje, 1024 é satisfeito; nos
 *  novos, 1024 é a falta toda) */
const RECEPTORES_PAINEL: [string, string][] = [
  ["fome", "fome"], ["higiene", "higiene"], ["energia", "energia"], ["humor", "humor"], ["saude", "saúde"],
  ["tedio", "tédio"], ["solidao", "solidão"], ["estresse", "estresse"], ["dor", "dor"], ["susto", "susto"],
];

/** o painel do corpo: só desenho, a leitura dos receptores do estado (o motor nunca lê a tela) */
function desenharPainel(receptores: Readonly<Record<string, number>> | null): void {
  const painel = el("corpo");
  painel.hidden = receptores === null;
  if (receptores === null) return;
  if (!painel.childElementCount) {
    for (const [chave, nome] of RECEPTORES_PAINEL) {
      const linha = document.createElement("div");
      linha.className = "receptor";
      linha.dataset.receptor = chave;
      linha.innerHTML = `<span class="nome"></span><span class="nivel"><span></span></span><span class="valor"></span>`;
      (linha.querySelector(".nome") as HTMLElement).textContent = nome;
      painel.appendChild(linha);
    }
  }
  for (const linha of painel.querySelectorAll<HTMLElement>(".receptor")) {
    const v = receptores[linha.dataset.receptor!];
    if (!Number.isInteger(v)) throw new Error(`o painel sem o receptor ${linha.dataset.receptor}`);
    (linha.querySelector(".valor") as HTMLElement).textContent = String(v);
    (linha.querySelector(".nivel > span") as HTMLElement).style.width = `${(v / 1024) * 100}%`;
  }
}
const SPRITE_ATLAS = "brasa_crianca_sereno";   // um pet de exemplo do atlas, quadro 0
const MEDIR_MS = 10_000;

const el = <T extends HTMLElement>(id: string): T => {
  const e = document.getElementById(id);
  if (!e) throw new Error(`#${id} nao existe na pagina`);
  return e as T;
};

async function fonteDoSprite(): Promise<{ fonte: FonteSprite; nome: string }> {
  const reserva: FonteSprite = { tipo: "pixels", linhas: SPRITE_RESERVA, paleta: PALETA_RESERVA, subPorTexel: 1 };
  if (new URLSearchParams(location.search).get("sprite") === "reserva") return { fonte: reserva, nome: "reserva" };
  try {
    const r = await fetch("./Assets/digilab_atlas_up.json");
    if (!r.ok) return { fonte: reserva, nome: "reserva" };
    const atlas = await r.json() as { atlas: string; sprites: Record<string, { quadros: number[][] }> };
    const q = atlas.sprites[SPRITE_ATLAS]?.quadros[0];
    if (!q) return { fonte: reserva, nome: "reserva" };
    const img = new Image();
    img.src = "./Assets/digilab_atlas_up.png";
    await img.decode();
    return { fonte: { tipo: "imagem", imagem: img, x: q[0], y: q[1], w: q[2], h: q[3], subPorTexel: 0.5 }, nome: `atlas:${SPRITE_ATLAS}` };
  } catch {
    return { fonte: reserva, nome: "reserva" };   // sem o atlas na máquina: o de reserva, como manda a W-6
  }
}

/** o aparelho parece um celular ou tablet? (o userAgent, e o iPadOS, que se apresenta como Mac, pelo toque) */
const ehCelular = (): boolean =>
  /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || (/Macintosh/.test(navigator.userAgent) && navigator.maxTouchPoints > 1);

const mediana = (v: number[]) => { const s = [...v].sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : 0; };
const p95 = (v: number[]) => { const s = [...v].sort((a, b) => a - b); return s.length ? s[Math.min(s.length - 1, Math.floor(s.length * 0.95))] : 0; };

async function iniciar(): Promise<void> {
  el("titulo").textContent = COM_CORPO ? "WORLD-POC-02 (com o corpo)" : "WORLD-POC-01a";
  const { fonte, nome } = await fonteDoSprite();
  let sim = novaSimulacao(Number(el<HTMLInputElement>("semente").value));
  const canvas = el<HTMLCanvasElement>("tela");
  let vista = new Vista(canvas, sim.mundo, fonte);
  const ajustar = () => {
    const caixa = el("palco");
    vista.ajustar(caixa.clientWidth, caixa.clientHeight, devicePixelRatio || 1);
  };
  ajustar();
  addEventListener("resize", ajustar);

  let rodando = true, acumulado = 0, ultimo = performance.now();
  let anterior: Pose = poseDe(sim), atual: Pose = poseDe(sim);
  let poseFixa: Pose | null = null;
  const quadros: number[] = [];
  let medindo: { inicio: number; deltas: number[]; fim: (d: number[]) => void } | null = null;

  const laco = (agora: number) => {
    const dt = agora - ultimo;
    ultimo = agora;
    quadros.push(dt);
    if (quadros.length > 120) quadros.shift();
    if (medindo) {
      medindo.deltas.push(dt);
      if (agora - medindo.inicio >= MEDIR_MS) { const m = medindo; medindo = null; m.fim(m.deltas); }
    }
    if (rodando && poseFixa === null) {
      acumulado += dt;
      const passo = 1000 / TICKS_POR_SEGUNDO;
      while (acumulado >= passo) { anterior = atual; sim.avancar(1); atual = poseDe(sim); acumulado -= passo; }
      const a = Math.min(1, acumulado / passo);
      vista.desenhar(interpolar(anterior, atual, a));
    } else vista.desenhar(poseFixa ?? atual);
    const ms = mediana(quadros);
    el("fps").textContent = ms > 0 ? `${(1000 / ms).toFixed(0)} quadros/s · tick ${sim.mundo.tick} · sprite ${nome}` : "";
    desenharPainel(sim.corpo === null ? null : sim.corpo.receptores());
    requestAnimationFrame(laco);
  };
  requestAnimationFrame(laco);

  el<HTMLButtonElement>("pausar").addEventListener("click", () => {
    rodando = !rodando;
    el("pausar").textContent = rodando ? "Pausar" : "Continuar";
  });
  el<HTMLButtonElement>("reiniciar").addEventListener("click", () => {
    sim = novaSimulacao(Number(el<HTMLInputElement>("semente").value));
    vista.renderer.dispose();
    vista = new Vista(canvas, sim.mundo, fonte);
    ajustar();
    anterior = atual = poseDe(sim);
  });

  const medirFps = (): Promise<Record<string, unknown>> => new Promise(resolve => {
    medindo = {
      inicio: performance.now(), deltas: [], fim: deltas => {
        const t = vista.tamanho, total = deltas.reduce((a, b) => a + b, 0);
        resolve({
          medida: "M3", data: new Date().toISOString(), aparelho: ehCelular() ? "celular" : "desktop", userAgent: navigator.userAgent,
          devicePixelRatio,
          tela_css: [innerWidth, innerHeight], canvas_px: [t.largura, t.altura], px_por_sub: t.pxPorSub, sprite: nome,
          duracao_s: +(total / 1000).toFixed(3), quadros: deltas.length, fps_media: +((deltas.length * 1000) / total).toFixed(2),
          quadro_mediana_ms: +mediana(deltas).toFixed(2), quadro_p95_ms: +p95(deltas).toFixed(2),
        });
      },
    };
  });
  el<HTMLButtonElement>("medir").addEventListener("click", async () => {
    el("medir").textContent = "Medindo 10 s…";
    const m = await medirFps();
    el<HTMLTextAreaElement>("medida").value = JSON.stringify(m, null, 1);
    el("medir").textContent = "Medir 10 s";
    try { await navigator.clipboard.writeText(JSON.stringify(m)); el("copiado").textContent = "copiado"; }
    catch { el("copiado").textContent = "selecione o texto e copie à mão"; }
    if (!ehCelular()) el("copiado").textContent += " (atenção: medida de desktop, não é a M3 do celular)";
  });
  el<HTMLButtonElement>("baixar").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify({ semente: sim.semente, log: sim.log, registros: sim.registros }, null, 1)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `world_poc_01_${sim.semente}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  });

  /* os ganchos do e2e: param o tempo, põem o pet num lugar, desenham e leem os pixels */
  Object.assign(window, {
    __poc: {
      sprite: nome,
      webgl: vista.renderer.getContext() !== null,
      pausar: () => { rodando = false; },
      colocarPet: (x: number, y: number) => {
        rodando = false;
        sim.mundo.pet.x = x; sim.mundo.pet.y = y;
        poseFixa = { pet: [x, y], bola: [sim.mundo.bola.x, sim.mundo.bola.y] };
        return vista.desenhar(poseFixa);
      },
      conferirM2: () => {
        vista.desenhar(poseFixa ?? atual);
        return { ...vista.conferirPixels(), retangulo: vista.retangulo, ...vista.tamanho, cobrindo: vista.cobrindo };
      },
      pixelsDiferentesDoFundo: () => {
        vista.desenhar(poseFixa ?? atual);
        const gl = vista.renderer.getContext(), t = vista.tamanho, buf = new Uint8Array(t.largura * t.altura * 4);
        gl.readPixels(0, 0, t.largura, t.altura, gl.RGBA, gl.UNSIGNED_BYTE, buf);
        let n = 0;
        for (let k = 0; k < buf.length; k += 4) if (buf[k] !== 0xf4 || buf[k + 1] !== 0xf1 || buf[k + 2] !== 0xea) n++;
        return { diferentes: n, total: t.largura * t.altura };
      },
      medirFps,
      hashDe: (semente: number, ticks: number, corpo = false) => {
        const s = new Simulacao(semente, undefined, { corpo });
        s.avancar(ticks);
        return s.hash();
      },
      tamanho: () => vista.tamanho,
      comCorpo: COM_CORPO,
      receptores: () => (sim.corpo === null ? null : sim.corpo.receptores()),
      painel: () => Object.fromEntries([...document.querySelectorAll<HTMLElement>("#corpo .receptor")].map(l =>
        [l.dataset.receptor!, Number((l.querySelector(".valor") as HTMLElement).textContent)])),
    },
  });
  if (!ehCelular()) el("aviso").textContent = "Este aparelho não parece um celular: a medida sai marcada como desktop, e não vale como a M3 do celular.";
  el("estado").textContent = "pronto";
}

function poseDe(s: Simulacao): Pose {
  return { pet: [s.mundo.pet.x, s.mundo.pet.y], bola: [s.mundo.bola.x, s.mundo.bola.y] };
}

function interpolar(a: Pose, b: Pose, t: number): Pose {
  const l = (x: number, y: number) => x + (y - x) * t;
  return { pet: [l(a.pet[0], b.pet[0]), l(a.pet[1], b.pet[1])], bola: [l(a.bola[0], b.bola[0]), l(a.bola[1], b.bola[1])] };
}

iniciar().catch(err => { el("estado").textContent = `erro: ${String(err)}`; throw err; });
