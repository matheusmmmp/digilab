/* Nova geracao (pranchas HerEscolher, HerPrevia, HerConfirmar, HerOvo; desktop HerDesktop). Passo 1: os pais (o ativo
   e um log em espera, ou importado de outro dono). Passo 2: o que o filho herda (especie 1 em 2, temperamento na faixa
   media +- acaso) e o que NAO passa. Cruzar pede confirmacao (nao da para desfazer); depois, o ovo da nova geracao. */
import { useEffect, useRef, useState } from "preact/hooks";
import { OVO, chaveSprite, nomeEstagio, nomeForma, type EixoTemperamento, type Motor } from "../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../atlas.ts";
import { BRASAO } from "../decoracao.ts";
import { candidatos, cruzar, fecharHeranca, geracao, podeSerPai, previa } from "../heranca.ts";
import { abrirImportar, useImportar } from "../importar.ts";
import { useJogo } from "../jogo.ts";
import { diaDe } from "../telas/pet/TelaPet.tsx";
import { Deco } from "./Deco.tsx";
import { abrirModal } from "./modal.ts";

const NAO_PASSA = ["regras de luta", "caráter aprendido", "memórias", "disciplina", "vínculo", "o que aprendeu com você"];
const EIXO_TXT: Record<EixoTemperamento, string> = { curiosidade: "curiosidade", teimosia: "teimosia", sensibilidade: "sensibilidade", rancor: "rancor" };
const sinal = (x: number) => (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(2).replace(".", ",");
const pos = (x: number) => `${((x + 1) / 2) * 100}%`;

function Spr({ m, alvo, ovo = false }: { m: Motor; alvo: number; ovo?: boolean }) {
  const a = useAtlas();
  if (a.tipo !== "ok") return null;
  const k = ovo ? OVO[m.especie] : chaveSprite(m.forma), s = imagemAtlas(a, k, Math.max(1, Math.min(3, Math.floor(alvo / dimSprite(a.dados, k)[1]))));
  return <img class="dl-pix" src={s.url} width={s.w} height={s.h} alt="" />;
}
/** trilho -1..1: a faixa onde o filho pode cair (hachurada), os pais (laranja e azul) e, no ovo, o filho */
function Trilho({ p, q, faixa, filho }: { p: number; q: number; faixa: [number, number]; filho?: number }) {
  return (
    <span class="her-trilho" aria-hidden="true">
      <i class="her-faixa" style={{ left: pos(faixa[0]), width: `${((faixa[1] - faixa[0]) / 2) * 100}%` }} />
      <i class="her-pt her-pt--p" style={{ left: pos(p) }} /><i class="her-pt her-pt--q" style={{ left: pos(q) }} />
      {filho !== undefined && <i class="her-filho" style={{ left: pos(filho) }} />}
    </span>
  );
}
function Temperamento({ p, q, filho }: { p: Motor; q: Motor; filho?: Motor }) {
  const pv = previa(p, q);
  return (
    <div class="her-temp">
      <div class="her-legenda"><span><i class="her-pt her-pt--p" />{nomeForma(p.forma)}</span><span><i class="her-pt her-pt--q" />{nomeForma(q.forma)}</span>
        {filho ? <span><i class="her-filho" />o filho</span> : <span><i class="her-faixa her-faixa--leg" />onde o filho pode cair</span>}</div>
      {pv.eixos.map(x => (
        <div class="her-eixo" key={x.e}>
          <span class="her-eixo-cab"><b>{EIXO_TXT[x.e]}</b><span class="dl-lcd">{filho ? `filho ${sinal(filho.temp[x.e])}` : `média ${sinal(x.media)}`}</span></span>
          <Trilho p={x.p} q={x.q} faixa={x.faixa} filho={filho?.temp[x.e]} />
        </div>
      ))}
    </div>
  );
}
function NaoPassa() {
  return (
    <section class="her-nao dl-malha" aria-label="Não passa para o filho">
      <b>NÃO PASSA PARA O FILHO</b>
      <ul>{NAO_PASSA.map(t => <li key={t}><span aria-hidden="true">✕</span>{t}</li>)}</ul>
      <small>O filho nasce sem nada aprendido: você ensina tudo de novo.</small>
    </section>
  );
}

/** passo 1: o pai 1 e o ativo; o pai 2, um log em espera (adulto) ou importado */
function Pais({ ativo, sel, escolher }: { ativo: Motor; sel: number | null; escolher: (i: number) => void }) {
  const importando = useImportar();
  const [lista, setLista] = useState(() => candidatos());
  useEffect(() => { if (!importando) setLista(candidatos()); }, [importando]);
  return (
    <div class="her-pais">
      <h3 class="her-sec">PAI 1 · SEU PET AGORA</h3>
      <div class="her-pai"><span class="her-pai-spr"><Spr m={ativo} alvo={48} /></span>
        <span class="her-pai-txt"><b>{nomeForma(ativo.forma)}</b><small>{nomeEstagio(ativo.forma)} · dia {diaDe(ativo.e.tick)} · {ativo.log.filter(e => e[1] === "l").length} lutas</small></span>
        <span class={`dl-tag ${podeSerPai(ativo) ? "her-tag-ok" : "her-tag-nao"}`}>{podeSerPai(ativo) ? "✓ ADULTO" : "precisa ser adulto"}</span></div>
      <h3 class="her-sec">PAI 2 · ESCOLHA UM LOG <small>{lista.length} em espera</small></h3>
      <div class="her-lista">
        {lista.map(c => (
          <button type="button" key={c.i} class={`her-pai her-pai--op${sel === c.i ? " sel" : ""}`} disabled={!c.ok} aria-pressed={sel === c.i} onClick={() => escolher(c.i)}>
            <span class="her-pai-spr"><Spr m={c.m} alvo={48} /></span>
            <span class="her-pai-txt"><b>{nomeForma(c.m.forma)}</b><small>{nomeEstagio(c.m.forma)} · geração {geracao(c.m)}</small></span>
            <span class={`dl-tag ${c.ok ? "her-tag-ok" : "her-tag-nao"}`}>{c.ok ? "✓ ADULTO" : "precisa ser adulto"}</span>
          </button>
        ))}
      </div>
      <button type="button" class="her-importar" onClick={abrirImportar}>Importar log de outro dono</button>
      <p class="dl-apoio her-nota">Tudo acontece aqui, sem rede: o outro pai é só o arquivo de log dele. Os dois precisam ser adultos.</p>
    </div>
  );
}

/** passo 2: o que o filho herda */
function Previa({ ativo, outro }: { ativo: Motor; outro: Motor }) {
  const pv = previa(ativo, outro), chance = pv.especies.length === 1 ? "certo" : "1 em 2";
  return (
    <div class="her-previa">
      <section class="her-casal dl-hexcard">
        <span class="her-rot her-rot--p">{nomeForma(ativo.forma)} · seu</span><span class="her-rot her-rot--q">{nomeForma(outro.forma)} · log</span>
        <span class="her-casal-spr"><Spr m={ativo} alvo={96} /></span>
        <span class="her-cruz" aria-hidden="true"><Deco nome={BRASAO[ativo.especie].peca} largura={36} altura={24} /><Deco nome={BRASAO[outro.especie].peca} largura={36} altura={24} /></span>
        <span class="her-casal-spr"><Spr m={outro} alvo={96} /></span>
      </section>
      <div class="her-sub"><b>Espécie</b><small>sorteada entre as dos pais</small></div>
      <div class="her-especies">{pv.especies.map(e => (
        <div class="her-esp" key={e}><Spr m={e === ativo.especie ? ativo : outro} alvo={40} ovo />
          <span><span class="her-esp-nome"><Deco nome={BRASAO[e].peca} largura={24} altura={16} />{BRASAO[e].nome}</span><b class="dl-num">{chance}</b></span></div>
      ))}</div>
    </div>
  );
}

/** fim: depois de "Chocar o ovo" (a casca leva ao pet e fecha Meus pets) */
export function Heranca({ pai2, pagina = false, fim }: { pai2: number | null; pagina?: boolean; fim?: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), { motor: ativo } = useJogo();
  const [sel, setSel] = useState<number | null>(pai2), [etapa, setEtapa] = useState<"pais" | "previa">(pai2 !== null ? "previa" : "pais");
  const [confirmar, setConfirmar] = useState(false), [filho, setFilho] = useState<{ m: Motor; pais: [Motor, Motor] } | null>(null), [erro, setErro] = useState("");
  useEffect(() => { if (!pagina) abrirModal(ref.current); }, []);
  const sair = () => { if (pagina) fecharHeranca(); else ref.current?.close(); };
  const outro = sel !== null ? candidatos().find(c => c.i === sel)?.m ?? null : null;
  const ger = outro ? 1 + Math.max(geracao(ativo), geracao(outro)) : 0;
  const fazer = () => {
    try { const p1 = ativo, p2 = outro!, f = cruzar(sel!); setFilho({ m: f, pais: [p1, p2] }); setConfirmar(false); }
    catch (err) { setErro(err instanceof Error ? err.message : String(err)); setConfirmar(false); }
  };

  /* depois de cruzar: o ovo da nova geracao (HerOvo) */
  if (filho) {
    const f = filho.m, [p, q] = filho.pais, o = f.origem!;
    const corpo = (
      <div class="her-ovo">
        <span class="dl-tag her-ger">GERAÇÃO {geracao(f)}</span>
        <h1 class="bv-tit her-ovo-tit">Nova geração!</h1>
        <div class="her-ovo-palco"><Deco nome={BRASAO[f.especie].esquerda} class="her-ovo-asa" /><Spr m={f} alvo={150} ovo /><Deco nome={BRASAO[f.especie].direita} class="her-ovo-asa" /></div>
        <span class="dl-placa her-ovo-placa"><Deco nome={BRASAO[f.especie].peca} largura={24} altura={16} />Ovo de {BRASAO[f.especie].nome}</span>
        <section class="her-card"><b>Temperamento do filho</b><Temperamento p={p} q={q} filho={f} /></section>
        <p class="her-conferida">✓ origem conferida no log do filho<small>pais {o.pais[0].h.toString(16).slice(0, 4)}…, {o.pais[1].h.toString(16).slice(0, 4)}… · semente {o.s}</small></p>
        <button type="button" class="dl-btn dl-btn--destaque dl-btn--largo" onClick={() => { sair(); fim?.(); }}>Chocar o ovo</button>
      </div>
    );
    return pagina ? <section class="her-pagina her-pagina--ovo dl">{corpo}</section>
      : <dialog class="heranca-tela heranca-tela--ovo dl" ref={ref} aria-label="Nova geração" onClose={fecharHeranca}>{corpo}</dialog>;
  }

  const podeIr = podeSerPai(ativo) && outro !== null;
  const passo1 = <Pais ativo={ativo} sel={sel} escolher={i => { setSel(i); setErro(""); }} />;
  const passo2 = outro && <Previa ativo={ativo} outro={outro} />;
  const botoes = etapa === "pais"
    ? <button type="button" class="dl-btn dl-btn--largo" disabled={!podeIr} onClick={() => setEtapa("previa")}>Ver o que o filho herda</button>
    : <div class="her-bts"><button type="button" class="dl-btn dl-btn--sec" onClick={() => setEtapa("pais")}>Trocar pai</button>
      <button type="button" class="dl-btn dl-btn--destaque" disabled={!podeIr} onClick={() => setConfirmar(true)}>Cruzar</button></div>;
  const dialogo = confirmar && outro && (
    <div class="her-conf-fundo" role="presentation">
      <section class="her-conf" role="alertdialog" aria-labelledby="her-conf-tit">
        <h2 id="her-conf-tit">Começar a geração {ger}?</h2>
        <ul>
          <li><Spr m={ativo} alvo={28} /><span><b>{nomeForma(ativo.forma)} se aposenta</b><small>O log dele fica em Diário · Gerações, só para ver.</small></span></li>
          <li><Spr m={ativo} alvo={28} ovo /><span><b>O filho começa do ovo</b><small>Com o temperamento herdado e nada aprendido.</small></span></li>
          <li><span class="her-conf-ic" aria-hidden="true">#</span><span><b>O log do filho guarda a origem</b><small>A impressão dos registros dos pais e a semente da herança.</small></span></li>
        </ul>
        <p class="her-conf-aviso">Não dá para desfazer.</p>
        <div class="her-bts"><button type="button" class="dl-btn dl-btn--sec" onClick={() => setConfirmar(false)}>Cancelar</button>
          <button type="button" class="dl-btn dl-btn--destaque" onClick={fazer}>Cruzar</button></div>
      </section>
    </div>
  );
  const depois = <section class="her-card"><b>Depois de cruzar</b>
    <p>{nomeForma(ativo.forma)} se aposenta e vai para Diário · Gerações. O filho começa do ovo. Não dá para desfazer.</p></section>;

  if (pagina) return (
    <section class="her-pagina dl" aria-label="Nova geração">
      <div class="her-passos" role="tablist" aria-label="Passos">
        <button type="button" role="tab" aria-selected={etapa === "pais"} onClick={() => setEtapa("pais")}>1 · Pais</button>
        <button type="button" role="tab" aria-selected={etapa === "previa"} disabled={!podeIr} onClick={() => setEtapa("previa")}>2 · Herança</button>
      </div>
      {etapa === "pais" ? <div class="her-desk-pais">{passo1}<div class="her-desk-pe">{erro && <p class="imp-erro">{erro}</p>}{botoes}</div></div> : (
        <div class="her-desk">
          <section class="her-col"><h3 class="her-col-tit">Os pais <small>os dois adultos ✓</small></h3>{passo2}</section>
          <section class="her-col"><h3 class="her-col-tit">Temperamento <small>média + acaso</small></h3>{outro && <Temperamento p={ativo} q={outro} />}
            <p class="dl-apoio">O temperamento muda como ele aprende, não o que aprende.</p></section>
          <section class="her-col her-col--lado"><NaoPassa />{depois}{erro && <p class="imp-erro">{erro}</p>}{botoes}</section>
        </div>
      )}
      {dialogo}
    </section>
  );
  return (
    <dialog class="heranca-tela dl" ref={ref} aria-labelledby="her-tit" onClose={fecharHeranca}>
      <div class="imp-cab dl-faixa">
        <button type="button" class="conv-voltar" aria-label="Voltar" onClick={() => (etapa === "previa" ? setEtapa("pais") : sair())}>
          <svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path d="M10 3 5 8l5 5" /></svg></button>
        <span><h2 class="dl-num" id="her-tit">Nova geração</h2><small class="her-passo">passo {etapa === "pais" ? "1 de 2 · escolher os pais" : "2 de 2 · o que o filho herda"}</small></span>
      </div>
      <div class="her-corpo">
        {etapa === "pais" ? passo1 : <>{passo2}<section class="her-card"><div class="her-sub"><b>Temperamento</b><small>média dos pais + um pouco de acaso</small></div>
          {outro && <Temperamento p={ativo} q={outro} />}</section><NaoPassa /></>}
        {erro && <p class="imp-erro">{erro}</p>}
      </div>
      <div class="her-pe">{botoes}</div>
      {dialogo}
    </dialog>
  );
}
