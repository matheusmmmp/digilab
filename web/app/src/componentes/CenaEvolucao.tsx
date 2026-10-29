/* A cena oficial de digievolucao antes do cartao da Revelacao (docs/TAREFA_V2_UP_EVOLUCAO.md; chave CENA_EVOLUCAO_UP em
   src/evolucaoUp.ts). Baixa os quadros da cena, toca no canvas 2D (o fundo, o pet do app no osso, a frente: o aditivo somado com
   "lighter", o normal por cima) e chama aoFim no fim, no "Pular" ou com o erro (a Revelacao mostra o aviso e segue no cartao), dizendo se
   a cena ja tocou o efeito da evolucao (senao o cartao toca, como hoje).
   A reserva sem cena e o clipe Evol do atlas; sem Evol, aoFim na hora. */
import { useEffect, useRef, useState } from "react";
import { atlasAtual, quadroSombrio, type AtlasOk } from "../atlas.ts";
import {
  baixarQuadros, carregarMapaEvolucao, centroDoCorpo, escolherCena, lugarDigimon, quadroDigimon, sequencia, EVOLUCAO_URL,
  type MapaEvolucao, type PassoCena,
} from "../evolucaoUp.ts";
import { SOM } from "../som.ts";

/** quantos quadros a frente ficam decodificados (PROPOSTO, SEM FONTE: o tocador da etapa 0 usou 20) */
const JANELA = 20;
/** a escala do pet na reserva Evol: a da revelacao (UI_GUIDELINES, secao 5) */
const ESCALA_RESERVA = 4;

function desenharPet(g: CanvasRenderingContext2D, a: AtlasOk, chave: string, clipe: "Idle" | "Evol", ms: number, x: number, y: number, escala: number, sombria: boolean): void {
  const { quadro: q, img } = quadroDigimon(a, chave, clipe, ms);
  if (q[2] === 0) return;
  g.imageSmoothingEnabled = false;
  if (sombria) g.drawImage(quadroSombrio(img, q), x + (q[4] - 1) * escala, y + (q[5] - 1) * escala, (q[2] + 2) * escala, (q[3] + 2) * escala);
  else g.drawImage(img, q[0], q[1], q[2], q[3], x + q[4] * escala, y + q[5] * escala, q[2] * escala, q[3] * escala);
}

export function CenaEvolucao({ antes, depois, sombria, aoFim }: { antes: string; depois: string; sombria: boolean; aoFim: (aviso: string | undefined, tocouSom: boolean) => void }) {
  const ref = useRef<HTMLCanvasElement>(null), fimRef = useRef(aoFim), revelouRef = useRef(false), [progresso, setProgresso] = useState<number | null>(0);
  fimRef.current = aoFim;
  useEffect(() => {
    let vivo = true, raf = 0;
    const acabar = (aviso?: string): void => { if (!vivo) return; vivo = false; cancelAnimationFrame(raf); fimRef.current(aviso, revelouRef.current); };
    const canvas = (): [HTMLCanvasElement, CanvasRenderingContext2D] => {
      const cv = ref.current; if (!cv) throw new Error("canvas da cena ausente");
      const r = cv.getBoundingClientRect(), d = devicePixelRatio || 1;
      cv.width = Math.max(1, Math.round(r.width * d)); cv.height = Math.max(1, Math.round(r.height * d));
      const g = cv.getContext("2d"); if (!g) throw new Error("canvas 2d indisponível");
      return [cv, g];
    };
    const reservaEvol = (a: AtlasOk): void => {
      const s = a.dados.sprites[depois], evol = s?.clipes?.Evol;
      if (!s || !evol) throw new Error("reserva Evol sem o clipe: " + depois);
      const total = evol.ms.reduce((x, y) => x + y, 0), [cv, g] = canvas(), d = devicePixelRatio || 1, e = ESCALA_RESERVA * Math.max(1, Math.round(d));
      const x = (cv.width - s.caixa[0] * e) / 2, y = (cv.height - s.caixa[1] * e) / 2, t0 = performance.now();
      setProgresso(null); void SOM.tocarEvolucao(0); revelouRef.current = true;
      const quadro = (agora: number): void => {
        if (!vivo) return;
        const ms = agora - t0;
        if (ms >= total) return acabar();
        g.clearRect(0, 0, cv.width, cv.height);
        desenharPet(g, a, depois, "Evol", ms, Math.round(x), Math.round(y), e, sombria);
        raf = requestAnimationFrame(quadro);
      };
      raf = requestAnimationFrame(quadro);
    };
    const tocar = (a: AtlasOk, mapa: MapaEvolucao, seq: PassoCena[], blobs: Map<string, Blob>, bgm: string, revela: number): void => {
      const [cv, g] = canvas(), k = cv.width / mapa.w, centros = { antes: centroDoCorpo(a, antes), depois: centroDoCorpo(a, depois) };
      const prontos = new Map<number, Promise<ImageBitmap[]>>(), feitos = new Map<number, ImageBitmap[]>();
      const pedir = (i: number): void => {
        if (i >= seq.length || prontos.has(i)) return;
        const p = Promise.all(seq[i].camadas.map(c => createImageBitmap(blobs.get(`${seq[i].arquivo}_${c}.webp`)!)));
        prontos.set(i, p);
        p.then(v => { if (vivo) feitos.set(i, v); else v.forEach(b => b.close()); }, (e: unknown) => acabar(`quadro ${seq[i].arquivo} não decodificou: ${String(e)}`));
      };
      setProgresso(null); void SOM.tocarMusica(bgm); void SOM.tocarEvolucao(revela); revelouRef.current = true;
      /* o relogio so anda com o quadro pronto: se a decodificacao atrasar, a cena segura em vez de pular */
      let t = 0, antes0 = performance.now(), mostrado = -1;
      const quadro = (agora: number): void => {
        if (!vivo) return;
        const i = Math.floor(t * mapa.fps / 1000);
        if (i >= seq.length) return acabar();
        for (let j = i; j < i + JANELA; j++) pedir(j);
        for (const [j, v] of feitos) if (j < i) { v.forEach(b => b.close()); feitos.delete(j); prontos.delete(j); }
        const v = feitos.get(i);
        if (v) {
          if (i !== mostrado) {
            const p = seq[i];
            g.globalCompositeOperation = "source-over"; g.imageSmoothingEnabled = true;
            g.drawImage(v[0], 0, 0, cv.width, cv.height);
            if (p.digimon && p.clipe !== null && p.clipe_ms !== null) {
              const chave = p.digimon === "antes" ? antes : depois, l = lugarDigimon(mapa, p.osso, centros[p.digimon]);
              desenharPet(g, a, chave, p.clipe, p.clipe_ms, l.x * k, l.y * k, l.escala * k, sombria && p.digimon === "depois");
            }
            for (let c = 1; c < p.camadas.length; c++) {
              g.globalCompositeOperation = p.camadas[c].endsWith("a") ? "lighter" : "source-over"; g.imageSmoothingEnabled = true;
              g.drawImage(v[c], 0, 0, cv.width, cv.height);
            }
            g.globalCompositeOperation = "source-over"; mostrado = i;
          }
          t += agora - antes0;
        }
        antes0 = agora;
        raf = requestAnimationFrame(quadro);
      };
      raf = requestAnimationFrame(quadro);
    };
    (async () => {
      const a = atlasAtual();
      if (a.tipo !== "ok") throw new Error(a.tipo === "erro" ? "atlas: " + a.erro : "atlas ainda carregando");
      const mapa = await carregarMapaEvolucao(), esc = escolherCena(mapa, depois, !!a.dados.sprites[depois]?.clipes?.Evol);
      if (!vivo) return;
      if (esc.tipo === "hoje") return acabar();
      if (esc.tipo === "evol") return reservaEvol(a);
      const seq = sequencia(mapa, esc.cena), blobs = await baixarQuadros(seq, p => { if (vivo) setProgresso(p); }, EVOLUCAO_URL);
      if (vivo) tocar(a, mapa, seq, blobs, esc.bgm, mapa.cenas[esc.cena].revela_s);
    })().catch((e: unknown) => { console.error("cena da evolucao", e); acabar(e instanceof Error ? e.message : String(e)); });
    return () => { vivo = false; cancelAnimationFrame(raf); };
  }, [antes, depois, sombria]);
  return (
    <div className="evm-cenaup" data-testid="cena-evolucao">
      <canvas ref={ref} className="evm-cenaup-tela" aria-hidden="true" />
      {progresso !== null && <span className="evm-cenaup-carga" role="status">carregando a cena… {Math.round(progresso * 100)}%</span>}
      <button type="button" className="dl-btn evm-cenaup-pular" data-autofocus onClick={() => fimRef.current(undefined, revelouRef.current)}>Pular</button>
    </div>
  );
}
