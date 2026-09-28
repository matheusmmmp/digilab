/* Campanha (desenho CampMapa; porte do HTML): uma ilha do UP por lugar, nuvem nos trancados, marcador com o NPC
   em 1x, caminho entre os lugares, o pet no proximo desafio; cartao do lugar com os rivais, a licao, os stats e
   o historico de tentativas (contado do registro). A luta acontece no palco desta aba. */
import { useEffect } from "preact/hooks";
import { LUGARES, NOME_ESTAGIO_FALA, NOME_V2, NPC, STATS, chaveSprite, nomeEstiloNPC } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { useJogo } from "../../jogo.ts";
import { LUTA, campAtual, escolherDesafio, escolherLugar, lutarAnimado, previa, tentativas, useLuta } from "../../luta.ts";
import { PalcoLuta } from "./PalcoLuta.tsx";

const ILHA = [{ peca: "ilha_campina", x: 44, y: 57 }, { peca: "ilha_torre", x: 2, y: 29 }, { peca: "ilha_cidadela", x: 44, y: 0 }];
const ORDEM_EST = ["ovo", "bebe", "crianca", "adolescente", "adulto"];
const centro = (i: number): [number, number] => [ILHA[i].x + 27, ILHA[i].y + 22];   /* em % da largura e da altura */

function Mapa() {
  const { motor: m } = useJogo(), a = useAtlas(), luta = useLuta(), sel = campAtual(m);
  if (a.tipo !== "ok") return <div class="mapa-ilhas"><p class="dl-apoio">Carregando o mapa…</p></div>;
  const vencidos = LUGARES.filter((_, i) => m.lugarVencido(i)).length, url = (n: string) => imagemAtlas(a, n).url;
  const [px, py] = centro(Math.min(vencidos, LUGARES.length - 1)), pet = imagemAtlas(a, chaveSprite(m.forma)), ph = dimSprite(a.dados, chaveSprite(m.forma))[1];
  return (
    <div class="mapa-ilhas" role="group" aria-label="Mapa da campanha">
      <svg class="mapa-caminho" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        {LUGARES.slice(1).map((_, i) => { const [x1, y1] = centro(i), [x2, y2] = centro(i + 1);
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} class={i < vencidos ? "feito" : ""} />; })}
      </svg>
      {LUGARES.map((L, i) => {
        const vit = L.rivais.reduce((n, k) => n + m.campanha[k], 0), aberto = m.desafioAberto(L.rivais[0]), c = NPC[L.rivais[0]]!, eSel = NPC[sel]!.lug === i;
        const st = vit ? `vencido ${vit}×` : aberto ? "aberto" : "trancado", quem = L.rivais.length > 1 ? `${L.rivais.length} rivais` : c.nome;
        const h = dimSprite(a.dados, c.k)[1], top = h > 48 ? -Math.round(h * .08) : Math.round((48 - h) / 2), [cx, cy] = centro(i);
        return [
          <img key={"i" + i} class="ilha" src={url(ILHA[i].peca)} alt="" style={{ left: `${ILHA[i].x}%`, top: `${ILHA[i].y}%` }} />,
          !aberto && <img key={"n" + i} class="nuvem" src={url("nuvem")} alt="" style={{ left: `${ILHA[i].x - 2}%`, top: `${ILHA[i].y - 1}%` }} />,
          <button key={"b" + i} type="button" class={`lugar${eSel ? " sel" : ""}${aberto ? "" : " bloq"}${vit ? " vencido" : ""}`} disabled={luta.lutando}
            style={{ left: `${cx}%`, top: `${cy}%` }} aria-label={`${i + 1}. ${L.nome}: ${quem}, ${st}`} aria-current={eSel ? "true" : undefined} onClick={() => escolherLugar(i)}>
            <img class="marcador" src={url(i === LUGARES.length - 1 ? "marcador_chefe" : vit ? "marcador_3" : "marcador_1")} alt="" />
            <span class="lugar-npc"><img class="dl-pix" src={url(c.k)} alt="" style={{ marginTop: `${top}px` }} /></span>
            <span class="lugar-placa"><b>{i + 1}. {L.nome}</b><small>{quem} · {st}</small></span>
          </button>,
        ];
      })}
      {/* seu pet: no proximo desafio (ou no primeiro lugar, se nada foi vencido) */}
      <span class="pet-mapa-ilha" style={{ left: `calc(${px}% + 34px)`, top: `calc(${py}% - 40px)` }}>
        <img class="dl-pix" src={pet.url} alt="seu pet" style={{ marginTop: `${ph > 44 ? -Math.round(ph * .08) : Math.round((44 - ph) / 2)}px` }} /></span>
    </div>
  );
}
function Detalhe() {
  const { motor: m } = useJogo(), luta = useLuta(), sel = campAtual(m), Li = NPC[sel]!.lug, L = LUGARES[Li], aberto = m.desafioAberto(L.rivais[0]);
  const est = m.forma.est, cedo = ORDEM_EST.indexOf(est) < ORDEM_EST.indexOf(L.est), podeLutar = est !== "bebe";
  const cab = aberto ? (L.rivais.length > 1 ? "Vença qualquer um dos rivais para abrir o próximo lugar." : "") : `Trancado: vença alguém em ${LUGARES[Li - 1].nome} antes.`;
  return (
    <div class="dl-card camp-det" aria-live="polite">
      <h3>{Li + 1}. {L.nome}</h3>
      {cab && <p><b>{cab}</b></p>}
      <p class="dl-apoio">sugerido a partir de: {L.sugerido}</p>
      {cedo && aberto && <p class="camp-aviso">Seu pet ainda é {NOME_ESTAGIO_FALA[est]}: este lugar é pensado para {L.sugerido} em diante.</p>}
      {!podeLutar && <p class="dl-apoio">O In-Training ainda não luta na campanha.</p>}
      {L.rivais.map(k => {
        const c = NPC[k]!, vit = m.campanha[k], tent = tentativas(m, k);
        const st = vit ? `vencido ${vit}× em ${tent} luta${tent === 1 ? "" : "s"}` : tent ? `${tent} tentativa${tent === 1 ? "" : "s"}, nenhuma vitória` : "ainda não enfrentado";
        return (
          <div key={k} class={`camp-rival${k === sel ? " sel" : ""}`} onClick={() => { if (k !== sel) escolherDesafio(k); }}>
            <div><b>{c.nome}</b> <span class="dl-apoio">· {nomeEstiloNPC(c.estilo)} · stats {(c.total / STATS.length).toFixed(1).replace(".0", "").replace(".", ",")} em cada (total {c.total})</span></div>
            <p class="licao">{c.licao}</p>
            <div class="dl-linha">
              <button type="button" class={`dl-btn${vit ? " dl-btn--sec" : ""}`} disabled={!aberto || luta.lutando || !podeLutar}
                onClick={ev => { ev.stopPropagation(); LUTA.campSel = k; lutarAnimado(k, NOME_V2); document.querySelector(".palco-luta")?.scrollIntoView({ behavior: "smooth", block: "nearest" }); }}>
                {vit ? "Lutar de novo" : "Desafiar"}</button>
              <span class="dl-apoio">{st}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
export function TelaCampanha({ voltarPet }: { voltarPet: () => void }) {
  const luta = useLuta();
  /* a aba abre com o palco do proprio modo (a mensagem da arena nao aparece aqui) */
  useEffect(() => { if (!LUTA.palco || LUTA.palco.modo !== "campanha") previa("campanha"); }, []);
  return (
    <div class="tela dl">
      <p>Três lugares em sequência: vença um rival para abrir o próximo. Treine o pet no nível sugerido.</p>
      <details class="dl-apoio"><summary>Como funciona</summary><p>Três lugares pelo mapa, em sequência: o próximo só abre depois de vencer um rival do anterior. Na Torre há três rivais com estilos diferentes. Todo pet bem treinado vence qualquer um deles; sem treino, a luta vira sorte. Os NPCs têm stats iguais em todos os atributos (somando de 72 a 110; um pet sem treino tem 60), lutam com um estilo fixo e são imprevisíveis; o primeiro tem o tamanho de um Rookie. <b>Treine o pet no estágio sugerido</b> para vencer com segurança (na campanha o treino vale inteiro, stats absolutos). As lutas entram no registro e ensinam as regras de combate do seu pet.</p></details>
      <Mapa />
      <Detalhe />
      {/* o palco mora na aba visivel: numa luta em andamento, ele vem junto */}
      {luta.palco && <PalcoLuta voltarPet={voltarPet} />}
    </div>
  );
}
