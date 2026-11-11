/* Os objetos que falam (direcao A da ilha interativa; prancha docs/pranchas/ux-ilha-a/, aprovada pelo Matheus em 2026-11-07 com "Aprovar e codar";
   decisoes I1-1 e I1-4 a I1-9 do PERGUNTAS.md). So vista: nada aqui muda o motor, a rng, o registro ou o save.
   - desde 2026-11-08 (o Matheus: "eu quero que eles só fiquem aparentes se o jogador passar o mouse por cima [...] E daí fique bem translúcido"), as
     etiquetas e os selos so aparecem com o mouse sobre o objeto, translucidos (objetos_ilha.css); o alvo atual do pet nao mostra mais a etiqueta;
   - os selos dos lugares, com o mouse sobre eles (I1-7, I1-5): o saco com os treinos de hoje e o visto (ou a hora da proxima vez); a barraca com o ponto de
     diario novo. Com o mouse sobre eles, o selo ganha o nome do menu. O lugar trancado fica com o cadeado (CadeadosDaIlha.tsx), sem selo;
   - a etiqueta curta (I1-4): no hover (so com o mouse) da tigela, da bola e dos lugares; o alvo atual do pet (objetosIlha.ts, alvoAtual) so ganha o destaque;
   - o cartao do toque (I1-4, I1-8, I1-9): tocar na tigela ou na bola abre o cartao, com o numero, a linha do que o pet aprendeu e o gesto, pelo mesmo
     caminho da barra (acoes.ts, agir("alimentar"); o "Por perto" da bola e o porBolaEm do BarraBola). A barra de baixo continua igual. Fecha no x, no Esc,
     num toque fora ou depois de FECHA_MS sem mexer;
   - o balao do pet tem prioridade (I1-6): o selo que cai sob o aviso da necessidade (.mm-aviso, o celular) some enquanto se sobrepoe;
   - o pet continua como na PEGAR_PET (I1-1): clicar no sprite e o carinho (ToquePet.tsx) e segurar o pega (PegarPet.tsx); o toque aqui ignora o sprite.
   A posicao de cada coisa vem da vista (CENA.aoObjetos, no fim de cada quadro, como o CadeadosDaIlha): a tigela e a bola pelo paraTela do motor e os
   lugares pelo pe e pela altura. O estilo e escrito direto (sem setState por quadro). Sem a ilha 3D (a reserva) nada aparece. As medidas sao de layout:
   PROPOSTO, SEM FONTE. */
import { useEffect, useLayoutEffect, useMemo, useRef, useSyncExternalStore, type RefObject } from "react";
import { BookOpen, Check, CircleDot, Clock, Dumbbell, Minus, Soup, Swords, TrendingDown, TrendingUp, X, type LucideIcon } from "lucide-react";
import { agir, podeAgir } from "../acoes.ts";
import { jogoAtual, useJogo } from "../jogo.ts";
import { PECAS, PECA_DO_LUGAR, pecaAberta } from "../nivel.ts";
import { useNivel } from "../nivelTela.ts";
import type { Lugar } from "../viagem.ts";
import { CENA } from "../telas/pet/cenaEstado.ts";
import { hhmm } from "../telas/pet/TelaPet.tsx";
import { TOQUE, noSprite } from "../telas/pet/ToquePet.tsx";
import { porBolaEm } from "../telas/pet/PorBola.tsx";
import { lugaresNomeados } from "../telas/pet/vistaMundo.ts";
import { alvoAtual, diarioNovo, lerDiarioVisto, linhaAprendeu, racoesNaTigela, seloDoSaco, ultimaNovidade } from "../telas/pet/objetosIlha.ts";
import "../estilo/objetos_ilha.css";

export type Objeto = "tigela" | "bola" | Lugar;
const LUGARES: readonly Lugar[] = ["saco", "portao", "barraca"];
const OBJETOS: readonly Objeto[] = ["tigela", "bola", ...LUGARES];
const ICONE_LUGAR: Readonly<Record<Lugar, LucideIcon>> = { saco: Dumbbell, portao: Swords, barraca: BookOpen };
/** o cartao fecha sozinho depois deste tempo sem mexer (ms; I1-4). PROPOSTO, SEM FONTE */
export const FECHA_MS = 6000;
/** a tigela e a bola na tela, em celulas (multiplicadas pelos px por celula da vista): o topo, o centro e o raio do toque. PROPOSTO, SEM FONTE */
const FORMA = { tigela: { topo: 0.4, centro: 0.15, raio: 0.6 }, bola: { topo: 0.85, centro: 0.4, raio: 0.55 } } as const;
/** a ponta entre a etiqueta e o objeto (px). PROPOSTO, SEM FONTE */
const PONTA = 10;
/** o topo do lugar para o selo e a etiqueta (fracao da altura que a vista publica, a partir do pe; a altura e a do modelo inteiro, com folga). PROPOSTO, SEM FONTE */
const ALTURA_LUGAR = 0.8;

/* ------------------------------------------------ o estado do toque (so a tela): o objeto sob o mouse e o cartao aberto */
const TOQUE_OBJ: { sobre: Objeto | null; aberto: "tigela" | "bola" | null; mexeu: number; foco: boolean } = { sobre: null, aberto: null, mexeu: 0, foco: false };
const ouvintes = new Set<() => void>();
let versao = 0;
const mudar = (f: () => void) => { f(); versao++; for (const o of ouvintes) o(); };
function useToqueObj(): typeof TOQUE_OBJ {
  useSyncExternalStore(o => { ouvintes.add(o); return () => { ouvintes.delete(o); }; }, () => versao);
  return TOQUE_OBJ;
}
/** o objeto sob o mouse agora (null fora deles): o CadeadosDaIlha so mostra o cadeado do lugar sob o mouse */
export function useObjetoSobre(): Objeto | null { return useToqueObj().sobre; }
/** fecha o cartao (o x, o Esc, o toque fora, o tempo) */
export const fecharCartao = (): void => { if (TOQUE_OBJ.aberto) mudar(() => { TOQUE_OBJ.aberto = null; TOQUE_OBJ.foco = false; }); };
/** o dono mexeu no cartao (o ponteiro, o teclado): o tempo de fechar recomeca */
const mexeu = (): void => mudar(() => { TOQUE_OBJ.mexeu = performance.now(); });

/* ------------------------------------------------ onde cada objeto estava no ultimo quadro (px do cliente): o toque le daqui */
interface NaTela { x: number; topo: number; pe: number; cx: number; cy: number; raio: number; dentro: boolean }
const POS: Partial<Record<Objeto, NaTela>> = {};

/** guarda onde cada objeto caiu na tela neste quadro (a vista chama, pelo CENA.aoObjetos): a tigela e a bola pelo paraTela do motor e a escala `ppc`
    (px por celula), os lugares pelo pe e pela altura que a vista publica. `W` e `H`: o tamanho da janela */
export function atualizarPosicoes(p: Readonly<Record<Lugar, readonly [number, number, number]>>, ppc: number, tigela: readonly [number, number],
  bola: readonly [number, number], W: number, H: number): void {
  const dentro = (x: number, y: number) => x > 0 && x < W && y > 0 && y < H;
  for (const [o, [x, y]] of [["tigela", tigela], ["bola", bola]] as const) {
    const f = FORMA[o];
    POS[o] = { x, pe: y, topo: y - f.topo * ppc, cx: x, cy: y - f.centro * ppc, raio: Math.max(22, f.raio * ppc), dentro: dentro(x, y) };
  }
  for (const l of LUGARES) {
    const [x, y, h] = p[l];
    POS[l] = { x, pe: y, topo: y - h * ALTURA_LUGAR, cx: x, cy: y - h / 2, raio: Math.max(22, h * 0.35), dentro: dentro(x, y - h / 2) };
  }
}
/** o estado do toque, para os testes (so leitura) */
export const estadoToqueObjetos = (): Readonly<typeof TOQUE_OBJ> => TOQUE_OBJ;

/** o objeto sob o ponto do cliente (px), ou null: o sprite do pet e do pet; o lugar trancado nao conta (tem o cadeado) */
export function objetoNoPonto(el: { getBoundingClientRect(): { left: number; top: number } }, cx: number, cy: number): Objeto | null {
  if (CENA.coberto || CENA.bolaNaMao || CENA.petNaMao || !CENA.mundo) return null;
  if (noSprite(cx, cy, el.getBoundingClientRect(), CENA.ret)) return null;
  for (const o of ["bola", "tigela"] as const) {
    const p = POS[o];
    if (p?.dentro && Math.hypot(cx - p.cx, cy - p.cy) <= p.raio) return o;
  }
  if (CENA.mundo.tvEm?.(cx, cy)) return null;   /* a TV do cantinho (so com `?gosto_visual=1`) nao e a barraca */
  const l = CENA.mundo.lugarEm?.(cx, cy) ?? null;
  if (l === "portao" || l === "barraca") return l;
  const s = POS.saco;
  if (s?.dentro && Math.abs(cx - s.x) <= s.raio && cy <= s.pe && cy >= s.topo) return "saco";
  return null;
}

/** liga o toque e o hover dos objetos na cena do habitat (`el`); devolve a funcao que desliga. O toque no lugar continua do ToqueLugar (abre o menu) */
export function ligarToqueObjetos(el: EventTarget & { getBoundingClientRect(): { left: number; top: number } }): () => void {
  type P = Event & { pointerId: number; clientX: number; clientY: number; button: number; buttons: number; pointerType: string };
  let mao: { id: number; x: number; y: number; t: number; o: Objeto | null } | null = null;
  const baixo = (ev: Event) => {
    const e = ev as P;
    if (e.pointerType === "mouse" && e.button !== 0) return;
    mao = { id: e.pointerId, x: e.clientX, y: e.clientY, t: performance.now(), o: objetoNoPonto(el, e.clientX, e.clientY) };
  };
  const move = (ev: Event) => {
    const e = ev as P;
    if (mao && mao.id === e.pointerId && Math.hypot(e.clientX - mao.x, e.clientY - mao.y) > TOQUE.andaMax) mao = null;
    if (e.pointerType === "mouse" && e.buttons === 0) {
      const o = objetoNoPonto(el, e.clientX, e.clientY);
      if (o !== TOQUE_OBJ.sobre) mudar(() => { TOQUE_OBJ.sobre = o; });
    }
  };
  const cima = (ev: Event) => {
    const e = ev as P, m = mao; mao = null;
    if (!m || m.id !== e.pointerId) return;
    if (performance.now() - m.t > TOQUE.duraMax || Math.hypot(e.clientX - m.x, e.clientY - m.y) > TOQUE.andaMax) return;
    if (CENA.petNaMao || CENA.bolaNaMao) return;
    const o = m.o === "tigela" || m.o === "bola" ? m.o : null;
    /* tocar na tigela ou na bola abre o cartao dela (de novo, fecha); tocar fora fecha; o lugar e do ToqueLugar */
    mudar(() => { TOQUE_OBJ.aberto = o && TOQUE_OBJ.aberto !== o ? o : null; TOQUE_OBJ.mexeu = performance.now(); });
  };
  const sai = () => { if (TOQUE_OBJ.sobre) mudar(() => { TOQUE_OBJ.sobre = null; }); };
  const solta = () => { mao = null; };
  el.addEventListener("pointerdown", baixo); el.addEventListener("pointermove", move); el.addEventListener("pointerup", cima);
  el.addEventListener("pointercancel", solta); el.addEventListener("pointerleave", sai);
  return () => {
    el.removeEventListener("pointerdown", baixo); el.removeEventListener("pointermove", move); el.removeEventListener("pointerup", cima);
    el.removeEventListener("pointercancel", solta); el.removeEventListener("pointerleave", sai);
  };
}
/** escuta o ponteiro na cena do habitat (`alvo`), como o ToqueLugar */
export function ToqueObjetos({ alvo }: { alvo: RefObject<HTMLElement | null> }) {
  useEffect(() => {
    const el = alvo.current;
    return el ? ligarToqueObjetos(el) : undefined;
  }, [alvo]);
  return null;
}

/* ------------------------------------------------ o desenho */
const sobrepoe = (a: DOMRect, x0: number, y0: number, x1: number, y1: number) => a.left < x1 && a.right > x0 && a.top < y1 && a.bottom > y0;

export function ObjetosDaIlha() {
  const { motor: m, nascendo } = useJogo(), nivel = useNivel(), toque = useToqueObj();
  const etq = useRef<Partial<Record<Objeto, HTMLElement | null>>>({}), selo = useRef<Partial<Record<Lugar, HTMLElement | null>>>({});
  const cartao = useRef<HTMLElement | null>(null);
  const mu = m.mundo, vivo = !!mu && nascendo === 0 && !m.morte;
  const aberto = (l: Lugar) => pecaAberta(nivel, PECA_DO_LUGAR[l]);
  /* o alvo atual (I1-4); com o pet na mao ele nao vai a lugar nenhum */
  const alvo = vivo && !CENA.petNaMao ? alvoAtual(m) : null;
  const racoes = mu ? racoesNaTigela(mu, m.e.tick) : 0;
  /* os selos: uma conta por tick (e por evento novo no registro), e so do lugar aberto */
  const tick = m.e.tick, nLog = m.log.length, sacoAberto = aberto("saco"), barracaAberta = aberto("barraca");
  const saco = useMemo(() => (vivo && sacoAberto ? seloDoSaco(m) : null), [vivo, sacoAberto, m, tick, nLog]);
  const novo = useMemo(() => (vivo && barracaAberta ? diarioNovo(ultimaNovidade(m), lerDiarioVisto(m.semente)) : false), [vivo, barracaAberta, m, tick, nLog]);
  /* o aprendido so com o cartao aberto, lido uma vez ao abrir (o digibrain() le o cerebro inteiro) */
  const aprendido = useMemo(() => (toque.aberto && vivo ? m.digibrain()?.aprendido ?? null : null), [toque.aberto, vivo, m]);
  /* o tamanho do cartao: medido uma vez ao abrir (o retorno por quadro so escreve) */
  const tamCartao = useRef<[number, number]>([300, 150]);
  useLayoutEffect(() => { const c = cartao.current; if (c) tamCartao.current = [c.offsetWidth, c.offsetHeight]; }, [toque.aberto]);

  /* o cartao fecha com o Esc e depois de FECHA_MS sem mexer; com o foco do teclado dentro dele, nao fecha sozinho */
  useEffect(() => {
    if (!toque.aberto) return;
    const tecla = (e: KeyboardEvent) => { if (e.key === "Escape") fecharCartao(); };
    const t = toque.foco ? 0 : window.setTimeout(fecharCartao, Math.max(0, FECHA_MS - (performance.now() - toque.mexeu)));
    addEventListener("keydown", tecla);
    return () => { if (t) clearTimeout(t); removeEventListener("keydown", tecla); };
  }, [toque.aberto, toque.mexeu, toque.foco]);
  /* sem pet no mundo (o ovo, a morte), o cartao fecha */
  useEffect(() => { if (!vivo) fecharCartao(); }, [vivo]);

  /* a posicao de tudo, no fim de cada quadro da vista: so ESCREVE o estilo (a unica leitura e o retangulo do aviso da necessidade, antes das escritas) */
  useEffect(() => {
    if (!vivo) return;
    const ultimo = new WeakMap<HTMLElement, string>();
    const por = (el: HTMLElement | null | undefined, x: number, y: number, visivel: boolean) => {
      if (!el) return;
      const t = visivel ? `translate(${Math.round(x)}px, ${Math.round(y)}px)` : "oculto";
      if (ultimo.get(el) === t) return;
      ultimo.set(el, t);
      el.style.visibility = visivel ? "visible" : "hidden";
      if (visivel) el.style.transform = t;
    };
    CENA.aoObjetos = (p, ppc) => {
      const { motor: mm } = jogoAtual(), v = CENA.mundo, mw = mm.mundo;
      if (!v || !mw) return;
      const W = innerWidth, H = innerHeight;
      /* o aviso da necessidade so existe abaixo de 900 px (o celular): so ali se le o retangulo dele */
      const aviso = W < 900 ? document.querySelector(".mm-aviso")?.getBoundingClientRect() ?? null : null;
      /* a tigela e a bola: o pe pelo paraTela do motor, o topo e o centro pela escala da vista */
      const [bxm, bym] = v.bola ?? mw.bolaEm(mm.e.tick);
      atualizarPosicoes(p, ppc, v.paraTela(mw.comedouro[0], mw.comedouro[1]), v.paraTela(bxm, bym), W, H);
      for (const o of OBJETOS) {
        const q = POS[o]!;
        por(etq.current[o], q.x, q.topo - PONTA, q.dentro);
      }
      for (const l of LUGARES) {
        const q = POS[l]!, el = selo.current[l];
        /* o balao do pet tem prioridade (I1-6): o selo some sob o aviso da necessidade (o selo tem ~120 x 28 px acima do topo) */
        const sob = !!aviso && sobrepoe(aviso, q.x - 60, q.topo - PONTA - 30, q.x + 60, q.topo - PONTA);
        por(el, q.x, q.topo - PONTA, q.dentro && !sob);
      }
      /* o cartao acompanha o objeto: a 900 px ou mais, ao lado; abaixo, embaixo dele (acima da barra de acoes) */
      const c = cartao.current, a = TOQUE_OBJ.aberto;
      if (c && a) {
        const q = POS[a]!, lado = W >= 900, [w, h] = tamCartao.current;
        const x = lado ? q.x + q.raio + 12 : Math.max(8, Math.min(q.x - w / 2, W - w - 8));
        const y = lado ? Math.min(Math.max(8, q.cy - h / 2), H - h - 8) : Math.min(q.pe + 12, H - h - 104);
        por(c, x, y, q.dentro);
      }
    };
    return () => { CENA.aoObjetos = null; };
  }, [vivo]);

  if (!vivo || !mu) return null;
  const mostra = (o: Objeto) => toque.aberto !== o && toque.sobre === o;
  const linha = toque.aberto ? linhaAprendeu(aprendido, toque.aberto) : null;
  const IconeLinha = linha ? (linha.sinal < 0 ? TrendingDown : linha.sinal > 0 ? TrendingUp : Minus) : Minus;
  const rotRacao = racoes === 0 ? "vazia" : racoes === 1 ? "ração" : "rações";
  return (
    <div className="objetos-ilha" data-objetos-ilha="">
      {/* as etiquetas curtas (so no hover) */}
      {mostra("tigela") && <span className={"obj-etq" + (alvo === "tigela" ? " obj-etq--alvo" : "")} ref={el => { etq.current.tigela = el; }} style={{ visibility: "hidden" }}
        data-objeto="tigela" role="img" aria-label={`Tigela: ${racoes === 0 ? "vazia" : `${racoes} ${rotRacao}`}`}>
        <Soup aria-hidden="true" />{racoes > 0 && <b aria-hidden="true">{racoes}</b>}<span aria-hidden="true">{rotRacao}</span>
      </span>}
      {mostra("bola") && <span className={"obj-etq" + (alvo === "bola" ? " obj-etq--alvo" : "")} ref={el => { etq.current.bola = el; }} style={{ visibility: "hidden" }}
        data-objeto="bola" role="img" aria-label="Bola"><CircleDot aria-hidden="true" /><span aria-hidden="true">Bola</span></span>}
      {mostra("portao") && aberto("portao") && <span className="obj-etq" ref={el => { etq.current.portao = el; }} style={{ visibility: "hidden" }} data-objeto="portao"
        role="img" aria-label={PECAS.lutar.nome}><Swords aria-hidden="true" /><span aria-hidden="true">{PECAS.lutar.nome}</span></span>}
      {/* os selos dos lugares (so com o mouse sobre eles, com o nome do menu) */}
      {saco && aberto("saco") && toque.sobre === "saco" && <span className="obj-selo" ref={el => { selo.current.saco = el; }} style={{ visibility: "hidden" }} data-objeto="saco" role="img"
        aria-label={`${PECAS.crescer.nome}: ${saco.hoje} ${saco.hoje === 1 ? "treino" : "treinos"} hoje, ${saco.proxima === null ? "pode treinar" : `próximo às ${hhmm(saco.proxima)}`}`}>
        <Dumbbell aria-hidden="true" />{toque.sobre === "saco" && <span aria-hidden="true">{PECAS.crescer.nome}</span>}
        <b aria-hidden="true">{saco.hoje}</b><span aria-hidden="true">hoje</span>
        {saco.proxima === null ? <Check className="obj-ok" aria-hidden="true" /> : <span className="obj-hora" aria-hidden="true"><Clock aria-hidden="true" />{hhmm(saco.proxima)}</span>}
      </span>}
      {aberto("barraca") && toque.sobre === "barraca" && <span className="obj-selo" ref={el => { selo.current.barraca = el; }} style={{ visibility: "hidden" }}
        data-objeto="barraca" role="img" aria-label={`${PECAS.diario.nome}${novo ? ": novidade" : ""}`}>
        <BookOpen aria-hidden="true" />{toque.sobre === "barraca" && <span aria-hidden="true">{PECAS.diario.nome}</span>}{novo && <span className="obj-ponto" aria-hidden="true" />}
      </span>}
      {/* o cartao do toque */}
      {/* o anuncio da abertura do cartao, para o leitor de tela (o cartao abre pelo toque na cena, sem mover o foco) */}
      <span className="sr-only" role="status" aria-live="polite">{toque.aberto ? `${toque.aberto === "tigela" ? "Tigela" : "Bola"}: cartão aberto` : ""}</span>
      {toque.aberto && linha && <section className="obj-cartao" ref={el => { cartao.current = el; }} style={{ visibility: "hidden" }} role="dialog"
        aria-labelledby="obj-cartao-nome" data-objeto={toque.aberto} data-cartao=""
        onPointerDown={mexeu} onKeyDown={mexeu}
        onFocus={() => { if (!TOQUE_OBJ.foco) mudar(() => { TOQUE_OBJ.foco = true; }); }}
        onBlur={e => { if (!e.currentTarget.contains(e.relatedTarget as Node | null)) mudar(() => { TOQUE_OBJ.foco = false; TOQUE_OBJ.mexeu = performance.now(); }); }}>
        <div className="obj-cartao-topo">
          {toque.aberto === "tigela" ? <Soup aria-hidden="true" /> : <CircleDot aria-hidden="true" />}
          <h2 className="obj-cartao-nome" id="obj-cartao-nome">{toque.aberto === "tigela" ? "Tigela" : "Bola"}</h2>
          {toque.aberto === "tigela" && <span className="obj-cartao-num">{racoes > 0 && <b>{racoes}</b>}{rotRacao}</span>}
          <button type="button" className="obj-fechar" aria-label="Fechar" onClick={fecharCartao}><X aria-hidden="true" /></button>
        </div>
        <p className={"obj-cartao-linha" + (linha.sinal === 0 ? " obj-sem" : " obj-aprendeu")}><IconeLinha aria-hidden="true" />{linha.texto}</p>
        {toque.aberto === "tigela"
          ? <button type="button" className="obj-gesto" disabled={!podeAgir(m, nascendo)} onClick={() => { agir("alimentar"); mexeu(); }}>
              <Soup aria-hidden="true" />Servir ração</button>
          : <button type="button" className="obj-gesto" onClick={() => { porBolaEm(...lugaresNomeados(mu).perto); fecharCartao(); }}>
              <CircleDot aria-hidden="true" />Pôr perto</button>}
      </section>}
    </div>
  );
}
