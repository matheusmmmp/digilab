/* Campanha (desenho CampMapa; porte do HTML): uma ilha do UP por lugar, nuvem nos trancados, marcador com o NPC
   em 1x, caminho entre os lugares, o pet no proximo desafio; cartao do lugar com os rivais, a licao, os stats e
   o historico de tentativas (contado do registro). A luta acontece no palco desta aba. */
import { useEffect } from "preact/hooks";
import { LUGARES, NOME_ESTAGIO_FALA, NOME_V2, NPC, STATS, chaveSprite, nomeEstiloNPC } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { fundoDeco } from "../../componentes/Deco.tsx";
import { Peca, RetratoRival } from "../../componentes/Imagens.tsx";
import { FAIXA_LUGAR, FUNDO_NPC, molduraArena, urlDeco, useDecoracao } from "../../decoracao.ts";
import { useJogo } from "../../jogo.ts";
import { LUTA, campAtual, escolherDesafio, escolherLugar, lutarAnimado, previa, tentativas, useLuta } from "../../luta.ts";
import { ENDERECO_LUTA } from "../../rotas.ts";

/* coordenadas da prancha CampMapa (mapa de 390 x 420), em % para acompanhar a largura: ilha 150 px, centro do lugar
   (trilho, plaquinha, marcador do pet) e o pad embaixo */
const W0 = 390, H0 = 420;
export const ILHA = [{ peca: "ilha_campina", x: 6, y: 231, cx: 81, cy: 316, placa: 389 }, { peca: "ilha_torre", x: 120, y: 118, cx: 195, cy: 197, placa: 265 },
  { peca: "ilha_cidadela", x: 230, y: 6, cx: 305, cy: 91, placa: 163 }];
const px = (x: number) => `${x / W0 * 100}%`, py = (y: number) => `${y / H0 * 100}%`;
const ORDEM_EST = ["ovo", "bebe", "crianca", "adolescente", "adulto"];
const NIVEL: Record<string, string> = { crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate" };

function Mapa() {
  const { motor: m } = useJogo(), a = useAtlas(), luta = useLuta(), sel = campAtual(m);
  if (a.tipo !== "ok") return <div class="mapa-ilhas"><p class="dl-apoio">Carregando o mapa…</p></div>;
  const vencidos = LUGARES.filter((_, i) => m.lugarVencido(i)).length, url = (n: string) => imagemAtlas(a, n).url;
  const aqui = ILHA[Math.min(vencidos, LUGARES.length - 1)], pet = imagemAtlas(a, chaveSprite(m.forma));
  return (
    <div class="mapa-ilhas" role="group" aria-label="Mapa da campanha">
      <svg class="mapa-caminho" viewBox={`0 0 ${W0} ${H0}`} preserveAspectRatio="none" aria-hidden="true">
        {LUGARES.slice(1).map((_, i) => {
          const A = ILHA[i], Bq = ILHA[i + 1], feito = i < vencidos;
          return <g key={i}><line x1={A.cx} y1={A.cy} x2={Bq.cx} y2={Bq.cy} class="trilho-sombra" />
            <line x1={A.cx} y1={A.cy} x2={Bq.cx} y2={Bq.cy} class={feito ? "trilho feito" : "trilho"} /></g>;
        })}
      </svg>
      {LUGARES.map((L, i) => {
        const vit = L.rivais.reduce((n, k) => n + m.campanha[k], 0), aberto = m.desafioAberto(L.rivais[0]), eSel = NPC[sel]!.lug === i, I = ILHA[i];
        const st = vit ? `vencido ${vit}×` : aberto ? "aberto" : "trancado";
        return [
          <img key={"p" + i} class="mapa-pad" src={url(i === LUGARES.length - 1 ? "marcador_chefe" : vit ? "marcador_3" : "marcador_1")} alt="" style={{ left: px(I.cx - 34), top: py(I.placa - 29) }} />,
          <img key={"i" + i} class={`ilha${aberto ? "" : " fechada"}`} src={url(I.peca)} alt="" style={{ left: px(I.x), top: py(I.y) }} />,
          !aberto && <img key={"n" + i} class="nuvem" src={url("nuvem")} alt="" style={{ left: px(I.x - 12), top: py(I.y - 6) }} />,
          <button key={"b" + i} type="button" class={`lugar${eSel ? " sel" : ""}${aberto ? "" : " bloq"}`} disabled={luta.lutando}
            style={{ left: px(I.cx - 70), top: py(I.placa) }} aria-label={`${i + 1}. ${L.nome}: ${st}`} aria-current={eSel ? "true" : undefined} onClick={() => escolherLugar(i)}>
            <span class="lugar-placa">{L.nome}</span>
            {vit ? <span class="lugar-tag lugar-tag--ok">VENCIDO</span> : aberto ? <span class="lugar-tag">{(NIVEL[L.est] ?? L.sugerido).toUpperCase()}</span>
              : <span class="lugar-tag lugar-tag--tranca"><Peca nome="icone_cadeado" />trancado</span>}
          </button>,
        ];
      })}
      {/* seu pet: no proximo desafio (ou no primeiro lugar, se nada foi vencido) */}
      <span class="pet-mapa-ilha" style={{ left: px(aqui.cx - 26), top: py(aqui.cy - 39) }} aria-hidden="true">
        <span class="pet-mapa-circ"><img class="dl-pix" src={pet.url} width={pet.w} height={pet.h} alt="" /></span><span class="pet-mapa-seta" /></span>
    </div>
  );
}
function Detalhe() {
  const { motor: m } = useJogo(), a = useAtlas(), luta = useLuta(), sel = campAtual(m), Li = NPC[sel]!.lug, L = LUGARES[Li], aberto = m.desafioAberto(L.rivais[0]);
  const est = m.forma.est, cedo = ORDEM_EST.indexOf(est) < ORDEM_EST.indexOf(L.est), podeLutar = est !== "bebe";
  const prox = LUGARES[Li + 1], c = NPC[sel]!, vit = m.campanha[sel], tent = tentativas(m, sel);
  useDecoracao();
  const faixa = fundoDeco(FAIXA_LUGAR[Li] ?? FUNDO_NPC[sel]);
  const cab = !aberto ? `Trancado: vença alguém em ${LUGARES[Li - 1].nome} antes.` : prox ? `Vencer ${L.rivais.length > 1 ? "qualquer um" : c.nome} abre ${prox.nome}.` : "Último lugar da campanha.";
  const st = vit ? `vencido ${vit}× em ${tent} luta${tent === 1 ? "" : "s"}` : tent ? `${tent} tentativa${tent === 1 ? "" : "s"}, nenhuma vitória` : "ainda não enfrentado";
  return (
    <>
      <section class="camp-det" aria-live="polite" aria-label="Lugar selecionado">
        {faixa && <div class="camp-faixa" style={{ backgroundImage: faixa }}><span aria-hidden="true">{L.nome} · luta contra {c.nome}</span></div>}
        <span class="camp-det-cab"><b>{L.nome}</b><span>sugerido: {L.sugerido}</span></span>
        <div class="camp-rivais" role="radiogroup" aria-label="Rivais do lugar">
          {L.rivais.map(k => {
            const n = NPC[k]!, img = a.tipo === "ok" ? imagemAtlas(a, n.k) : null, moldura = molduraArena(m.campanha[k]);
            return (
              <button type="button" key={k} class="camp-rival" role="radio" aria-checked={k === sel} disabled={luta.lutando} onClick={() => { if (k !== sel) escolherDesafio(k); }}>
                {urlDeco(moldura) ? <RetratoRival sprite={n.k} moldura={moldura} lado={52} />
                  : <span class="camp-rival-spr">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>}
                <b>{n.nome}</b><span>{m.campanha[k]} vitória{m.campanha[k] === 1 ? "" : "s"}</span>
              </button>
            );
          })}
        </div>
        <span class="camp-det-txt">{cab}</span>
        {cedo && aberto && <p class="camp-aviso">Seu pet ainda é {NOME_ESTAGIO_FALA[est]}: este lugar é pensado para {L.sugerido} em diante.</p>}
        {!podeLutar && <p class="dl-apoio">O In-Training ainda não luta na campanha.</p>}
        <p class="dl-apoio"><b>{c.nome}</b> · {nomeEstiloNPC(c.estilo)} · stats {(c.total / STATS.length).toFixed(1).replace(".0", "").replace(".", ",")} em cada (total {c.total}) · {st}</p>
        <p class="licao">{c.licao}</p>
      </section>
      <button type="button" class={`dl-btn camp-lutar${vit ? " dl-btn--sec" : ""}`} disabled={!aberto || luta.lutando || !podeLutar}
        onClick={() => { LUTA.campSel = sel; lutarAnimado(sel, NOME_V2); if (LUTA.lutando) location.hash = ENDERECO_LUTA; }}>
        {vit ? `Lutar de novo com ${c.nome}` : `Desafiar ${c.nome}`}</button>
    </>
  );
}
export function TelaCampanha({ voltarPet }: { voltarPet: () => void }) {
  const luta = useLuta();
  /* a aba abre com o palco do proprio modo (a mensagem da arena nao aparece aqui) */
  useEffect(() => { if (!LUTA.palco || LUTA.palco.modo !== "campanha") previa("campanha"); }, []);
  return (
    <div class="tela dl camp-tela">
      <div class="camp-principal"><Mapa /></div>
      <div class="camp-lado"><Detalhe />
      <details class="dl-apoio"><summary>Como funciona</summary><p>Três lugares pelo mapa, em sequência: o próximo só abre depois de vencer um rival do anterior. Na Torre há três rivais com estilos diferentes. Todo pet bem treinado vence qualquer um deles; sem treino, a luta vira sorte. Os NPCs têm stats iguais em todos os atributos (somando de 72 a 110; um pet sem treino tem 60), lutam com um estilo fixo e são imprevisíveis; o primeiro tem o tamanho de um Rookie. <b>Treine o pet no estágio sugerido</b> para vencer com segurança (na campanha o treino vale inteiro, stats absolutos). As lutas entram no registro e ensinam as regras de combate do seu pet.</p></details>
      </div>
    </div>
  );
}
