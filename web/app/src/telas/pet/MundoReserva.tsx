/* A reserva do mundo (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2): sem WebGL, a cena dos pets v12 em CSS. A mesma janela de 16 x 12
   celulas da cena 3D (vistaMundo.ts) vista de cima, com uma faixa de ceu no alto: o chao de cada regiao do layout, o ninho, o comedouro, a
   racao e a bola nas posicoes do Motor.mundo, e o pet na dele, interpolado. So le o motor. Conta ao resto da tela, por CENA, onde o pet
   esta (para os extras do PalcoPet) e como passar do ponteiro ao mapa (o soltar da racao), como a cena 3D. */
import { useEffect, useRef, useState } from "react";
import { OVO, chaveSprite, corDominante, type Mundo } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { S, gradeDe, imagemGrade, paleta } from "../../grades.ts";
import { useJogo } from "../../jogo.ts";
import { CENA } from "./cenaEstado.ts";
import { Seguidor, dentroDoMapa, janelaEm, ninhoDe, type Janela } from "./vistaMundo.ts";

/** a faixa de ceu no alto da caixa (fracao da altura): so vista */
const TOPO = 0.22;
const COR_REGIAO: Readonly<Record<string, string>> = { casa: "#D6E3F4", jardim: "#CFE7C2", campo: "#E3F0D2", mata: "#B9D9A4" };

interface Geo { W: number; H: number; jan: Janela }
const paraCaixa = (g: Geo, x: number, y: number): [number, number] =>
  [((x - g.jan.x0) / g.jan.w) * g.W, g.H * TOPO + ((y - g.jan.y0) / g.jan.h) * g.H * (1 - TOPO)];

export function MundoReserva() {
  const { motor: m, nascendo } = useJogo(), a = useAtlas(), caixa = useRef<HTMLDivElement>(null);
  const seguidor = useRef(new Seguidor()), ultimo = useRef(performance.now()), [, redesenhar] = useState(0);
  const mu = m.mundo as Mundo, cm = mu.cm;
  /* um passo a cada 120 ms, como a cena 3D: a posicao desenhada anda ate a do motor */
  useEffect(() => {
    const t = setInterval(() => {
      const agora = performance.now();
      seguidor.current.seguir(mu.pet, agora - ultimo.current, cm);
      ultimo.current = agora;
      redesenhar(x => x + 1);
    }, 120);
    return () => clearInterval(t);
  }, [mu, cm]);
  const pos = seguidor.current.pos ?? seguidor.current.seguir(mu.pet, 0, cm);
  const el = caixa.current, W = el?.clientWidth ?? 0, H = el?.clientHeight ?? 0, g: Geo = { W, H, jan: janelaEm(cm, pos) };
  /* o pet: o idle do atlas (o primeiro quadro) ou a grade de reserva, na maior escala inteira que cabe em 20% da altura e 30% da largura
     (como na cena 3D do mapa) */
  const sprite = (() => {
    if (a.tipo === "ok") {
      const nome = nascendo > 0 ? OVO[m.especie] : chaveSprite(m.forma), [w, h] = dimSprite(a.dados, nome);
      return imagemAtlas(a, nome, Math.max(1, Math.min(4, Math.floor((H * 0.2) / h), Math.floor((W * 0.3) / w))), { sombria: m.sombria });
    }
    const grade = nascendo > 0 ? S.ovo : S[gradeDe(m.estagioAtual)];
    return imagemGrade(grade, Math.max(1, Math.min(8, Math.floor((H * 0.2) / grade.length), Math.floor((W * 0.3) / grade[0].length))), paleta(corDominante(m.tracos)));
  })();
  const [ppx, ppy] = paraCaixa(g, pos[0], pos[1]), ret = { x: Math.round(ppx - sprite.w / 2), y: Math.round(ppy - sprite.h), w: sprite.w, h: sprite.h };
  useEffect(() => {
    CENA.modoMundo = true;
    return () => { CENA.modoMundo = false; CENA.ret = null; CENA.mundo = null; };
  }, []);
  CENA.ret = W > 0 ? ret : null;
  CENA.mundo = {
    paraMundo: (cx, cy) => {
      const r = caixa.current?.getBoundingClientRect(), mm = m.mundo;
      if (!r || !mm || !(r.width > 0 && r.height > 0)) return null;
      const fy = (cy - r.top) / r.height;
      if (fy < TOPO) return null;
      const jan = janelaEm(mm.cm, seguidor.current.pos ?? mm.pet);
      const x = Math.round(jan.x0 + ((cx - r.left) / r.width) * jan.w), y = Math.round(jan.y0 + ((fy - TOPO) / (1 - TOPO)) * jan.h);
      return dentroDoMapa(mm.cm, x, y) ? [x, y] : null;
    },
    paraTela: (x, y) => {
      const r = caixa.current!.getBoundingClientRect(), [bx, by] = paraCaixa({ W: r.width, H: r.height, jan: janelaEm(cm, seguidor.current.pos ?? mu.pet) }, x, y);
      return [r.left + bx, r.top + by];
    },
    get pet() { return seguidor.current.pos ?? [mu.pet[0], mu.pet[1]]; },
  };
  const ponto = (x: number, y: number, cls: string, key?: string | number) => {
    const [bx, by] = paraCaixa(g, x, y);
    return <span key={key} className={cls} style={{ left: bx, top: by }} />;
  };
  return (
    <div className="cena-mundo" ref={caixa} aria-hidden="true">
      {W > 0 && <>
        {cm.layout.regioes.map(([nome, c0, c1]) => {
          const x0 = Math.max(c0 * cm.sub, g.jan.x0), x1 = Math.min((c1 + 1) * cm.sub, g.jan.x0 + g.jan.w);
          if (x1 <= x0) return null;
          return <span key={nome} className="cena-mundo-regiao" data-regiao={nome}
            style={{ left: ((x0 - g.jan.x0) / g.jan.w) * W, width: ((x1 - x0) / g.jan.w) * W, top: H * TOPO, background: COR_REGIAO[nome] ?? "#DDD" }} />;
        })}
        {ponto(...ninhoDe(cm), "cena-mundo-ninho")}
        {ponto(mu.comedouro[0], mu.comedouro[1], "cena-mundo-comedouro")}
        {[...mu.comidas.values()].map(c => {
          const sit = mu.situacao(c, m.e.tick);
          return sit === null ? null : ponto(c.x, c.y, `cena-mundo-racao${sit === "podre" ? " cena-mundo-racao--podre" : ""}`, c.id);
        })}
        {ponto(...mu.bolaEm(m.e.tick), "cena-mundo-bola")}
        <span className="cena-mundo-sombra" style={{ left: ppx, top: ppy }} />
        <img className="dl-pix cena-mundo-pet" src={sprite.url} width={sprite.w} height={sprite.h} alt="" style={{ left: ret.x, top: ret.y }} />
      </>}
    </div>
  );
}
