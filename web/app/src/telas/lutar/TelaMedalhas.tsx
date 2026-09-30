/* Lutar · Medalhas (docs/DESIGN_MEDALHAS_ARENAS.md, secoes 3 e 4): as 6 medalhas do Tamer, quais ja sao dele, com que
   pet, onde se ganha cada uma (o lider e a regra da arena) e o que cada uma libera. Tudo sai do registro do Tamer (tamer.ts)
   e das tabelas do motor (motor/medalhas.ts e motor/arenas.ts). So leitura. */
import { ARENA_POR_ID, CARTA_DA_REVANCHE, CMD, ITEM_DA_MEDALHA, LUGARES_V6, MEDALHAS, MEDALHAS_LIGA, NOME_EST, NPC, itemDe, nomeForma, type Estagio } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { SeloMedalha } from "../../componentes/Medalha.tsx";
import { tamerAtual, useJogo } from "../../jogo.ts";
import { comoGanhar, noLugar, textoFalta } from "../../tamer.ts";
import { diaDe } from "../pet/TelaPet.tsx";

const DE: Record<string, string> = { adolescente: "Rookie", adulto: "Champion", mega: "Ultimate" };
/** "Rookie → Champion" para o estagio de destino */
const passo = (alvo: Estagio): string => `${DE[alvo]} → ${NOME_EST[alvo as keyof typeof NOME_EST]}`;
/** o que a n-esima medalha (contando as do Tamer) libera */
function libera(n: number): string {
  const alvo = (Object.entries(CMD) as [Estagio, number][]).find(([, v]) => v === n)?.[0];
  if (alvo) return `${passo(alvo)} (${n} medalha${n === 1 ? "" : "s"})`;
  return n === MEDALHAS.length ? "a coleção completa e a Fronteira (a Liga dos Líderes)" : "conta para a próxima evolução";
}

export function TelaMedalhas() {
  const { motor: m, erroTamer } = useJogo(), t = tamerAtual(), a = useAtlas();
  const espera = m.esperandoMedalha(), v6 = m.versao >= 6;
  const img = (k: string) => { if (a.tipo !== "ok") return null; const n = NPC[k]!, i = imagemAtlas(a, n.sprite ?? n.k); return <img class="dl-pix" src={i.url} width={i.w} height={i.h} alt="" />; };
  return (
    <div class="tela dl desk med-tela">
      <div class="desk-col med-lado">
        <section class="dl-card med-resumo" aria-labelledby="med-tit">
          <h2 id="med-tit">Medalhas do Tamer</h2>
          <p class="med-conta"><span class="dl-num">{t.n}</span><span>de {MEDALHAS.length}</span></p>
          <p>As medalhas são suas, não do pet: ficam quando ele é guardado ou morre, e valem para todos os pets seguintes. Vença o <b>líder</b> de cada lugar da campanha para ganhar a dele, com um item (Crescer · Itens).</p>
          <ul class="med-regras" aria-label="O que as medalhas liberam">
            {(Object.entries(CMD) as [Estagio, number][]).map(([alvo, n]) => (
              <li key={alvo} class={t.n >= n ? "ok" : ""}><b>{n}</b><span>{passo(alvo)}</span></li>
            ))}
          </ul>
          {/* a medalha de ouro: o titulo da Liga dos Lideres (Fronteira, medalhas parte 4a) */}
          <div class={`med-ouro${t.titulo ? " ganha" : ""}`}>
            <SeloMedalha n={0} ouro ganha={!!t.titulo} />
            <span><b>Medalha de ouro</b>{t.titulo
              ? <span>Campeão da Liga dos Líderes com {t.titulo.forma} no dia {diaDe(t.titulo.tick)}.{t.campeoes.length > 1 ? ` ${t.campeoes.length} títulos, um por pet.` : ""}</span>
              : <span>Ainda não: com as {MEDALHAS_LIGA} medalhas, vença a Liga dos Líderes na Fronteira (Lutar · Fronteira).</span>}</span>
          </div>
          {erroTamer && <p class="med-erro" role="alert">O registro do Tamer não abriu, e o app não vai gravar por cima dele: {erroTamer}</p>}
          {!v6 ? <p class="dl-apoio">{nomeForma(m.forma)} é de uma versão antiga: não ganha medalhas e não precisa delas para evoluir.</p>
            : espera ? <p class="med-espera" role="status"><b>{nomeForma(m.forma)} está pronto para evoluir</b> e espera o Tamer: {textoFalta(t, espera.precisa)}</p>
            : null}
        </section>
      </div>
      <ol class="med-lista" aria-label="As medalhas">
        {MEDALHAS.map((md, i) => {
          const g = t.ganha(md.id), n = NPC[md.lider]!, ar = ARENA_POR_ID[md.id];
          return (
            <li key={md.id} class={`med-card${g ? " ganha" : ""}`}>
              <SeloMedalha n={i + 1} ganha={!!g} />
              <span class="med-txt">
                <b class="med-nome">{md.nome}</b>
                <span class="med-onde">{comoGanhar(md).replace(/^v/, "V")}</span>
                {ar && <span class="med-regra"><b>{ar.titulo}:</b> {ar.frase}</span>}
                <span class={g ? "med-status ok" : "med-status"}>{g ? `ganha com ${g.forma} no dia ${diaDe(g.tick)}` : "ainda não"}</span>
                <span class="med-libera">libera: {libera(i + 1)}</span>
                <span class="med-item">dá: <b>{itemDe(ITEM_DA_MEDALHA[md.id]).nome}</b>{t.itemDaMedalha(md.lider) ? " (já é seu)" : ""} · revanche: {itemDe(CARTA_DA_REVANCHE[md.id]).nome}</span>
              </span>
              <span class="med-lider" title={`${n.nome}, líder ${noLugar(LUGARES_V6[md.lugar].nome).replace(/^n/, "d")}`}>{img(md.lider)}<small>líder</small></span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
