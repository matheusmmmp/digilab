/* Lutar · Medalhas (docs/DESIGN_MEDALHAS_ARENAS.md, secoes 3 e 4; L3 de "Lugares da ilha", prancha lutar_medalhas_*): as 6 medalhas do Tamer, quais ja sao
   dele, com que pet, onde se ganha cada uma (o lider e a regra da arena) e o que cada uma libera. Tudo sai do registro do Tamer (tamer.ts) e das
   tabelas do motor (motor/medalhas.ts e motor/arenas.ts). So leitura. O corte de texto da prancha: a vista so tem o numero, o lugar, o que libera e os
   dois itens da proxima; as frases vao nos baloes (e no textContent), e os recordes da Fronteira num "Recordes" fechado. */
import { Check, Layers, Lock, Package } from "lucide-react";
import { ARENA_POR_ID, CARTA_DA_REVANCHE, CMD, ESTAGIOS_SALAO, FABRICA, INSTALACOES, SALAO, ITEM_DA_MEDALHA, LUGARES_V6, MEDALHAS, MEDALHAS_LIGA, NOME_EST, NPC, itemDe, nomeForma, type Estagio } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { ComDica, ComoFunciona } from "../../componentes/Dica.tsx";
import { SeloMedalha } from "../../componentes/Medalha.tsx";
import { tamerAtual, useJogo } from "../../jogo.ts";
import { comoGanhar, noLugar, textoFalta } from "../../tamer.ts";
import { nomeCurto } from "../crescer/TelaItens.tsx";
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
  const proxima = MEDALHAS.findIndex(md => !t.ganha(md.id));
  return (
    <div className="tela dl md2-tela lg">
      <div className="md2-cab">
        <p className="md2-conta" aria-label={`${t.n} de ${MEDALHAS.length} medalhas`}><span className="dl-num lg-num md2-num">{t.n}</span><span className="lg-num" aria-hidden="true">/{MEDALHAS.length}</span></p>
        <ul className="md2-regras" aria-label="O que as medalhas liberam">
          {(Object.entries(CMD) as [Estagio, number][]).map(([alvo, n]) => (
            <li key={alvo} className={t.n >= n ? "ok" : ""}><b>{n}</b>{NOME_EST[alvo as keyof typeof NOME_EST]}<span className="sr-so"> {passo(alvo)} ({n} medalha{n === 1 ? "" : "s"})</span></li>
          ))}
        </ul>
      </div>
      {erroTamer && <p className="md2-erro" role="alert">O registro do Tamer não abriu, e o app não vai gravar por cima dele: {erroTamer}</p>}
      {espera && (
        <ComDica className="md2-espera" rotulo={`${nomeForma(m.forma)} está pronto para evoluir`} dica={<><b>{nomeForma(m.forma)} está pronto para evoluir</b> e espera o Tamer: {textoFalta(t, espera.precisa)}</>}>
          <Check aria-hidden="true" /><b>Pronto para evoluir</b>
        </ComDica>
      )}
      <ol className="md2-lista" aria-label="As medalhas">
        {MEDALHAS.map((md, i) => {
          const g = t.ganha(md.id), n = NPC[md.lider]!, ar = ARENA_POR_ID[md.id], prox = i === proxima, it = itemDe(ITEM_DA_MEDALHA[md.id]), carta = itemDe(CARTA_DA_REVANCHE[md.id]);
          const lib = (Object.entries(CMD) as [Estagio, number][]).find(([, v]) => v === i + 1)?.[0];
          const etq = lib ? NOME_EST[lib as keyof typeof NOME_EST] : i + 1 === MEDALHAS.length ? "Fronteira" : "";
          const dica = (
            <>
              <b>{md.nome}</b>: {comoGanhar(md).replace(/^v/, "V")}.{ar && <> {ar.titulo}: {ar.frase}</>}
              {" "}{g ? `Medalha ganha com ${g.forma} no dia ${diaDe(g.tick)}.` : "Ainda não."}
              {" "}Libera: {libera(i + 1)}. Dá: {it.nome}{t.itemDaMedalha(md.lider) ? " (já é seu)" : ""}; revanche: {carta.nome}.
              <span className="sr-so"> {n.nome}, líder {noLugar(LUGARES_V6[md.lugar].nome).replace(/^n/, "d")}</span>
            </>
          );
          return (
            <li key={md.id} className={`md2-card${g ? " ganha" : ""}${prox ? " md2-proxima lg-destaque" : ""}`}>
              <ComDica className="md2-linha" rotulo={`${md.nome}: ${g ? "ganha" : "falta"}${etq ? `, libera ${etq}` : ""}`} dica={dica} lado={i % 2 ? "dir" : undefined}>
                <SeloMedalha n={i + 1} ganha={!!g} />
                <b className="md2-nome">{LUGARES_V6[md.lugar].nome}</b>
                {etq && <span className="lg-etq">{etq}</span>}
                {prox && <span className="md2-lider" aria-hidden="true">{img(md.lider)}</span>}
              </ComDica>
              {prox && <span className="lg-linha md2-premios"><span className="lg-etq"><Package aria-hidden="true" />{nomeCurto(it)}</span><span className="lg-etq"><Layers aria-hidden="true" />{nomeCurto(carta)}</span></span>}
            </li>
          );
        })}
      </ol>
      {/* a medalha de ouro: o titulo da Liga dos Lideres (Fronteira, medalhas parte 4a) */}
      <ComDica className={`md2-ouro${t.titulo ? " ganha" : ""}`} rotulo={t.titulo ? "Medalha de ouro: campeão da Liga dos Líderes" : "Medalha de ouro: ainda não"}
        dica={<><b>Medalha de ouro</b>{t.titulo
          ? <> Campeão da Liga dos Líderes com {t.titulo.forma} no dia {diaDe(t.titulo.tick)}.{t.campeoes.length > 1 ? ` ${t.campeoes.length} títulos, um por pet.` : ""}</>
          : <> Ainda não: com as {MEDALHAS_LIGA} medalhas, vença a Liga dos Líderes na Fronteira (Lutar · Fronteira).</>}</>}>
        <SeloMedalha n={0} ouro ganha={!!t.titulo} /><b>Liga</b>{t.titulo ? <Check aria-hidden="true" /> : <Lock aria-hidden="true" />}
      </ComDica>
      {/* os recordes das instalacoes da Fronteira (medalhas parte 4b e 4c): do registro do Tamer, fechados */}
      <details className="lg-como md2-rec">
        <summary><Layers aria-hidden="true" />Recordes<span className="lg-seta" aria-hidden="true">›</span></summary>
        <ul className="md2-recordes" aria-label="Recordes da Fronteira">
          {INSTALACOES.map(x => { const r = t.recorde(x.id); return (
            <li key={x.id} className={r ? "ganha" : ""}>
              <span className="dl-num" aria-hidden="true">{r?.valor ?? 0}</span>
              <span><b>Recorde · {x.nome}</b><span>{r ? `${r.valor} vitória${r.valor === 1 ? "" : "s"} seguida${r.valor === 1 ? "" : "s"}, com ${r.forma}, no dia ${diaDe(r.tick)}.`
                : t.titulo ? "Nenhuma vitória ainda (Lutar · Fronteira)." : "Abre depois do título da Liga dos Líderes."}</span></span>
            </li>); })}
          {([[FABRICA.nome, t.recordeFabrica, (v: number) => `${v} série${v === 1 ? "" : "s"} seguida${v === 1 ? "" : "s"} com os alugados`],
            [SALAO.nome, t.recordeSalao, (v: number) => `${v} de ${ESTAGIOS_SALAO.length} níveis seguidos`]] as const).map(([nome, r, txt]) => (
            <li key={nome} className={r ? "ganha" : ""}>
              <span className="dl-num" aria-hidden="true">{r?.valor ?? 0}</span>
              <span><b>Recorde · {nome}</b><span>{r ? `${txt(r.valor)}, na tentativa ${r.n}.`
                : t.titulo ? "Nenhum ainda (Lutar · Fronteira)." : "Abre depois do título da Liga dos Líderes."}</span></span>
            </li>))}
        </ul>
      </details>
      <ComoFunciona>As medalhas são suas, não do pet: ficam quando ele é guardado ou morre, e valem para todos os pets seguintes. Vença o líder de cada lugar da campanha para ganhar a dele, com um item (Crescer · Itens). Com as {MEDALHAS.length}, a Liga dos Líderes abre na Fronteira.</ComoFunciona>
    </div>
  );
}
