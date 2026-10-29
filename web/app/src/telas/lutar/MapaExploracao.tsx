/* O mapa da Exploracao (docs/TAREFA_V2_EXPLORACAO.md): a vista 3D das ilhas (mapa3d.ts, import dinamico) e, por cima, o cartao de cada
   lugar e o marcador do proximo desafio. Tudo sai do motor: os lugares da versao do pet (3, 4 ou 6, e a Fronteira nos pets v6 em
   diante), se cada um esta aberto (o anterior vencido), as vitorias, o nivel sugerido, a medalha do lider (o Tamer) e a Liga. O motor nao
   tem a posicao do pet: o marcador fica no proximo desafio (o primeiro lugar aberto e nao vencido), e diz isso. */
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Check, ChevronRight, Lock } from "lucide-react";
import { MEDALHAS, MEDALHAS_LIGA, VERSAO_LIGA, chaveSprite, corDominante, medalhaDoLider, type Lugar, type Motor } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { SeloMedalha } from "../../componentes/Medalha.tsx";
import { S, gradeDe, imagemGrade, paleta } from "../../grades.ts";
import { tamerAtual, useJogo } from "../../jogo.ts";
import { campAtual, campProximoLugar, useLuta } from "../../luta.ts";
import { caixaMarcador, layoutCelular, layoutDesktop, type LayoutMapa } from "./mapaLayout.ts";
import type { CenaMapa, Mapa3D, TemaIlha } from "./mapa3d.ts";

/** o tema da ilha de cada lugar, pelo nome (o indice muda com a versao do pet); um lugar sem tema falha alto */
const TEMA: Readonly<Record<string, TemaIlha>> = {
  "Campina": "campina", "Torre de pedra": "torre", "Floresta": "floresta", "Cidadela": "cidadela", "Lago": "lago", "Montanha Espiral": "espiral",
};
const NIVEL: Readonly<Record<string, string>> = { crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate", mega: "Mega" };
const nivelDoLugar = (L: Lugar): string => NIVEL[L.est] ?? L.sugerido;

type Situacao = "vencido" | "aberto" | "trancado";
interface Entrada { nome: string; tema: TemaIlha; situacao: Situacao; texto: string; selo: { n: number; ganha: boolean; ouro: boolean } | null; fronteira: boolean }

/** os lugares do mapa, na ordem do motor, e a Fronteira no fim (pets v6 em diante) */
export function entradasDoMapa(m: Motor): Entrada[] {
  const Ls = m.lugares, t = tamerAtual();
  const out: Entrada[] = Ls.map((L, i) => {
    const tema = TEMA[L.nome];
    if (!tema) throw new Error("lugar da campanha sem ilha no mapa: " + L.nome);
    const vit = L.rivais.reduce((n, k) => n + m.campanha[k], 0), aberto = m.desafioAberto(L.rivais[0]);
    const situacao: Situacao = vit ? "vencido" : aberto ? "aberto" : "trancado";
    const texto = vit ? `vencido · ${vit} vitória${vit === 1 ? "" : "s"}` : aberto ? `sugerido: ${nivelDoLugar(L)}` : `vença alguém em ${Ls[i - 1].nome}`;
    const md = L.rivais.map(medalhaDoLider).find(x => x) ?? null;
    return { nome: L.nome, tema, situacao, texto, selo: md ? { n: MEDALHAS.indexOf(md) + 1, ganha: t.tem(md.id), ouro: false } : null, fronteira: false };
  });
  if (Ls.length === 6) {
    const aberta = m.medalhas >= MEDALHAS_LIGA, campeao = m.liga.titulos > 0;
    out.push({
      nome: "Fronteira", tema: "fronteira", situacao: campeao ? "vencido" : aberta ? "aberto" : "trancado", fronteira: true,
      texto: campeao ? "campeão da Liga dos Líderes" : aberta ? "a Liga dos Líderes está aberta" : `abre com as ${MEDALHAS_LIGA} medalhas (${Math.min(m.medalhas, MEDALHAS_LIGA)} de ${MEDALHAS_LIGA})`,
      selo: { n: 0, ganha: campeao, ouro: true },
    });
  }
  return out;
}
/** onde fica o marcador e o que ele diz: o proximo desafio; com a campanha vencida, a Fronteira aberta, ou "campanha vencida" */
function marcadorDe(m: Motor, ent: readonly Entrada[]): { i: number; rotulo: string } {
  const Ls = m.lugares, todos = Ls.every((_, i) => m.lugarVencido(i)), F = ent.length - 1;
  if (todos && ent[F].fronteira && ent[F].situacao !== "trancado") return { i: F, rotulo: ent[F].situacao === "vencido" ? "campeão" : "próximo desafio" };
  const i = campProximoLugar(m);
  return { i, rotulo: m.lugarVencido(i) ? "campanha vencida" : "próximo desafio" };
}

function Retrato({ m }: { m: Motor }) {
  const a = useAtlas();
  const img = a.tipo === "ok" ? imagemAtlas(a, chaveSprite(m.forma)) : imagemGrade(S[gradeDe(m.estagioAtual)], 2, paleta(corDominante(m.tracos)));
  return <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />;
}

/** o mapa: a caixa mede a largura (no desktop tambem a altura), a disposicao sai de mapaLayout.ts e a vista 3D desenha as ilhas nela.
    abrir(i): o cartao do lugar i (o da Fronteira leva a Lutar · Fronteira); aoFalhar: a vista 3D nao subiu (a tela volta ao mapa 2D) */
export function MapaExploracao({ desk, abrir, aoFalhar }: { desk: boolean; abrir: (i: number) => void; aoFalhar: () => void }) {
  const { motor: m } = useJogo(), luta = useLuta(), sel = campAtual(m);
  const caixa = useRef<HTMLDivElement>(null), tela = useRef<HTMLCanvasElement>(null), vista = useRef<Mapa3D | null>(null);
  const [medida, setMedida] = useState<[number, number] | null>(null), [ligado, setLigado] = useState(false);
  useLayoutEffect(() => {
    const el = caixa.current;
    if (!el) return;
    const medir = () => setMedida(v => (v && v[0] === el.clientWidth && v[1] === el.clientHeight ? v : [el.clientWidth, el.clientHeight]));
    medir();
    const obs = new ResizeObserver(medir); obs.observe(el);
    return () => obs.disconnect();
  }, []);
  useEffect(() => {
    let vivo = true;
    import("./mapa3d.ts")
      .then(mod => {
        if (!vivo || !tela.current) return;
        try { vista.current = mod.iniciarMapa3D(tela.current, aoFalhar); setLigado(true); }
        catch (err) { console.warn("o mapa 3D da Exploração não subiu; fica o mapa 2D:", err); aoFalhar(); }
      })
      .catch(err => { console.warn("o mapa 3D da Exploração não carregou; fica o mapa 2D:", err); if (vivo) aoFalhar(); });
    return () => { vivo = false; vista.current?.parar(); vista.current = null; };
  }, []);

  const ent = entradasDoMapa(m), n = ent.length;
  /* uma caixa pequena demais para as ilhas (layoutDesktop falha alto) tambem leva ao mapa 2D */
  let L: LayoutMapa | null = null, naoCabe = false;
  try { if (medida && medida[0] > 0) L = desk ? (medida[1] > 0 ? layoutDesktop(n, medida[0], medida[1]) : null) : layoutCelular(n, medida[0]); }
  catch (err) { console.warn("o mapa da Exploração não cabe; fica o mapa 2D:", err); naoCabe = true; }
  useEffect(() => { if (naoCabe) aoFalhar(); }, [naoCabe]);
  const marc = marcadorDe(m, ent), Lsel = m.lugarDe(sel);
  const cena: CenaMapa | null = L && {
    larg: L.larg, alt: L.alt, tam: L.tam,
    ilhas: ent.map((e, i) => ({ tema: e.tema, cx: L!.ilhas[i].cx, cy: L!.ilhas[i].cy, tranca: e.situacao === "trancado" })),
    /* o trecho ate um lugar fica azul quando o lugar de baixo foi vencido; o da Fronteira, com o titulo da Liga (como no mapa 2D) */
    trilhos: ent.slice(1).map((e, k) => ({ de: k, ate: k + 1, feito: e.fronteira ? m.liga.titulos > 0 : m.lugarVencido(k) })),
  };
  const chave = JSON.stringify(cena);
  /* desktop numa janela baixa (a caixa rola): na primeira vez, o marcador no meio da caixa */
  const rolou = useRef(false);
  useEffect(() => {
    const el = caixa.current;
    if (!desk || !L || !el || rolou.current) return;
    rolou.current = true;
    if (L.alt > el.clientHeight) el.scrollTop = Math.max(0, Math.min(L.alt - el.clientHeight, L.ilhas[marc.i].cy - el.clientHeight / 2));
  }, [chave]);
  useEffect(() => {
    if (!ligado || !cena || !vista.current) return;
    try { vista.current.desenhar(cena); caixa.current?.setAttribute("data-pronto", "1"); }
    catch (err) { console.warn("o mapa 3D da Exploração falhou ao desenhar; fica o mapa 2D:", err); aoFalhar(); }
  }, [ligado, chave]);

  return (
    /* a caixa (medida) e, dentro dela, o mundo do tamanho do mapa: no celular os dois tem a altura do mapa; no desktop a caixa enche a
       coluna e rola se o mapa passar dela (janela baixa) */
    <div ref={caixa} className={`mapa-expl${desk ? " mapa-expl--desk" : ""}`} role="group" aria-label="Mapa da Exploração" style={!desk && L ? { height: L.alt } : undefined}>
      <div className="mapa-expl-mundo" style={L ? { height: L.alt } : undefined}>
        <canvas ref={tela} className="mapa-expl-tela" aria-hidden="true" />
        {L && ent.map((e, i) => {
          const c = L!.cartoes[i], eSel = !e.fronteira && Lsel === i, aqui = marc.i === i;
          return (
            <button key={e.nome} type="button" className={`expl-cartao expl-cartao--${e.situacao}${e.fronteira ? " expl-cartao--fronteira" : ""}${eSel ? " sel" : ""}`}
              data-lado={c.lado} style={{ left: c.x, top: c.y, width: c.w }} disabled={luta.lutando} aria-current={eSel ? "true" : undefined}
              aria-label={`${e.fronteira ? "Fronteira de Batalha" : `${i + 1}. ${e.nome}`}: ${e.texto}${aqui ? `; ${marc.rotulo}` : ""}`}
              onClick={() => (e.fronteira ? (location.hash = "#/lutar/fronteira") : abrir(i))}>
              <span className="expl-cartao-cab">
                {e.selo && <SeloMedalha n={e.selo.n} ganha={e.selo.ganha} ouro={e.selo.ouro} tam={18} />}
                <b className="expl-nome">{e.nome}</b>
                <ChevronRight className="expl-seta" size={16} aria-hidden="true" />
              </span>
              <span className="expl-sit">
                {e.situacao === "trancado" ? <Lock size={13} aria-hidden="true" /> : e.situacao === "vencido" ? <Check size={13} aria-hidden="true" /> : null}
                <span>{e.texto}</span>
              </span>
            </button>
          );
        })}
        {L && (() => {
          const b = caixaMarcador(L, marc.i);
          return (
            <span className="expl-marcador" style={{ left: (b.x0 + b.x1) / 2, top: b.y1 }} aria-hidden="true">
              <span className="expl-marcador-rot">{marc.rotulo}</span>
              <span className="expl-marcador-circ"><Retrato m={m} /></span>
              <span className="expl-marcador-seta" />
            </span>
          );
        })()}
      </div>
    </div>
  );
}
