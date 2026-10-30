/* Lutar · Medalhas (docs/DESIGN_MEDALHAS_ARENAS.md, secoes 3 e 4): as 6 medalhas do Tamer, quais ja sao dele, com que
   pet, onde se ganha cada uma (o lider e a regra da arena) e o que cada uma libera. Tudo sai do registro do Tamer (tamer.ts)
   e das tabelas do motor (motor/medalhas.ts e motor/arenas.ts). So leitura. */
import { ARENA_POR_ID, CARTA_DA_REVANCHE, CMD, ESTAGIOS_SALAO, FABRICA, INSTALACOES, SALAO, ITEM_DA_MEDALHA, LUGARES_V6, MEDALHAS, MEDALHAS_LIGA, NOME_EST, NPC, itemDe, nomeForma, type Estagio } from "../../../motor/index.ts";
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
  const espera = m.esperandoMedalha();
  const img = (k: string) => { if (a.tipo !== "ok") return null; const n = NPC[k]!, i = imagemAtlas(a, n.sprite ?? n.k); return <img className="dl-pix" src={i.url} width={i.w} height={i.h} alt="" />; };
  return (
    <div className="tela dl desk med-tela">
      <div className="desk-col med-lado">
        <section className="dl-card med-resumo" aria-labelledby="med-tit">
          <h2 id="med-tit">Medalhas do Tamer</h2>
          <p className="med-conta"><span className="dl-num">{t.n}</span><span>de {MEDALHAS.length}</span></p>
          <p>As medalhas são suas, não do pet: ficam quando ele é guardado ou morre, e valem para todos os pets seguintes. Vença o <b>líder</b> de cada lugar da campanha para ganhar a dele, com um item (Crescer · Itens).</p>
          <ul className="med-regras" aria-label="O que as medalhas liberam">
            {(Object.entries(CMD) as [Estagio, number][]).map(([alvo, n]) => (
              <li key={alvo} className={t.n >= n ? "ok" : ""}><b>{n}</b><span>{passo(alvo)}</span></li>
            ))}
          </ul>
          {/* a medalha de ouro: o titulo da Liga dos Lideres (Fronteira, medalhas parte 4a) */}
          <div className={`med-ouro${t.titulo ? " ganha" : ""}`}>
            <SeloMedalha n={0} ouro ganha={!!t.titulo} />
            <span><b>Medalha de ouro</b>{t.titulo
              ? <span>Campeão da Liga dos Líderes com {t.titulo.forma} no dia {diaDe(t.titulo.tick)}.{t.campeoes.length > 1 ? ` ${t.campeoes.length} títulos, um por pet.` : ""}</span>
              : <span>Ainda não: com as {MEDALHAS_LIGA} medalhas, vença a Liga dos Líderes na Fronteira (Lutar · Fronteira).</span>}</span>
          </div>
          {/* os recordes das instalacoes da Fronteira (medalhas parte 4b): do registro do Tamer */}
          <ul className="med-recordes" aria-label="Recordes da Fronteira">
            {INSTALACOES.map(x => { const r = t.recorde(x.id); return (
              <li key={x.id} className={r ? "ganha" : ""}>
                <span className="dl-num" aria-hidden="true">{r?.valor ?? 0}</span>
                <span><b>Recorde · {x.nome}</b><span>{r ? `${r.valor} vitória${r.valor === 1 ? "" : "s"} seguida${r.valor === 1 ? "" : "s"}, com ${r.forma}, no dia ${diaDe(r.tick)}.`
                  : t.titulo ? "Nenhuma vitória ainda (Lutar · Fronteira)." : "Abre depois do título da Liga dos Líderes."}</span></span>
              </li>); })}
            {/* a Fabrica e o Salao (parte 4c): o recorde sai das tentativas do registro do Tamer */}
            {([[FABRICA.nome, t.recordeFabrica, (v: number) => `${v} série${v === 1 ? "" : "s"} seguida${v === 1 ? "" : "s"} com os alugados`],
              [SALAO.nome, t.recordeSalao, (v: number) => `${v} de ${ESTAGIOS_SALAO.length} níveis seguidos`]] as const).map(([nome, r, txt]) => (
              <li key={nome} className={r ? "ganha" : ""}>
                <span className="dl-num" aria-hidden="true">{r?.valor ?? 0}</span>
                <span><b>Recorde · {nome}</b><span>{r ? `${txt(r.valor)}, na tentativa ${r.n}.`
                  : t.titulo ? "Nenhum ainda (Lutar · Fronteira)." : "Abre depois do título da Liga dos Líderes."}</span></span>
              </li>))}
          </ul>
          {erroTamer && <p className="med-erro" role="alert">O registro do Tamer não abriu, e o app não vai gravar por cima dele: {erroTamer}</p>}
          {espera ? <p className="med-espera" role="status"><b>{nomeForma(m.forma)} está pronto para evoluir</b> e espera o Tamer: {textoFalta(t, espera.precisa)}</p>
            : null}
        </section>
      </div>
      <ol className="med-lista" aria-label="As medalhas">
        {MEDALHAS.map((md, i) => {
          const g = t.ganha(md.id), n = NPC[md.lider]!, ar = ARENA_POR_ID[md.id];
          return (
            <li key={md.id} className={`med-card${g ? " ganha" : ""}`}>
              <SeloMedalha n={i + 1} ganha={!!g} />
              <span className="med-txt">
                <b className="med-nome">{md.nome}</b>
                <span className="med-onde">{comoGanhar(md).replace(/^v/, "V")}</span>
                {ar && <span className="med-regra"><b>{ar.titulo}:</b> {ar.frase}</span>}
                <span className={g ? "med-status ok" : "med-status"}>{g ? `ganha com ${g.forma} no dia ${diaDe(g.tick)}` : "ainda não"}</span>
                <span className="med-libera">libera: {libera(i + 1)}</span>
                <span className="med-item">dá: <b>{itemDe(ITEM_DA_MEDALHA[md.id]).nome}</b>{t.itemDaMedalha(md.lider) ? " (já é seu)" : ""} · revanche: {itemDe(CARTA_DA_REVANCHE[md.id]).nome}</span>
              </span>
              <span className="med-lider" title={`${n.nome}, líder ${noLugar(LUGARES_V6[md.lugar].nome).replace(/^n/, "d")}`}>{img(md.lider)}<small>líder</small></span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
