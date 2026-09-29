/* Meus pets no desktop (prancha MpListaDesktop): pagina inteira dentro da casca. Grade de espacos (o ativo, os
   guardados em espera, um espaco livre para o ovo novo) e, a direita, o pet escolhido: como ele ficou congelado,
   estagio, vinculo, brasao, dias de vida e as acoes (Exportar, Tornar ativo, Cruzar, Apagar). O celular segue com
   Meus pets (MpAtual). Tudo sai do motor de cada pet (replay do registro guardado). */
import { useMemo, useState } from "preact/hooks";
import { NOME_ESP, NOME_EST, OVO, chaveSprite, nomeEstagio, nomeForma, type Motor } from "../../../motor/index.ts";
import { imagemAtlas, dimSprite, useAtlas } from "../../atlas.ts";
import { Seg, blocos } from "../../componentes/Barras.tsx";
import { Deco } from "../../componentes/Deco.tsx";
import { BRASAO } from "../../decoracao.ts";
import { useJogo } from "../../jogo.ts";
import { novoOvoGuardandoAtivo } from "../../jornada.ts";
import { abrirImportar, exportarArquivo, nomeArquivo, useImportar } from "../../importar.ts";
import { abrirGuardado, apagarGuardado, ativarGuardado, cruzarComAtivo, lerGuardados } from "../../pets.ts";
import { diaDe, hhmm } from "./TelaPet.tsx";

type Sel = "ativo" | number;
const vinculoTxt = (m: Motor): string | null => m.versao < 2 ? null : m.vinc.valor >= .66 ? "vínculo alto" : m.vinc.valor >= .33 ? "vínculo médio" : "vínculo baixo";

/** o botao "Novo ovo" do topo (o ativo vai para a espera: ninguem e apagado sem pedir) */
export const AcoesMeusPets = () => <>
  <button type="button" class="dl-btn dl-btn--sec mpl-novo" onClick={abrirImportar}>Importar</button>
  <button type="button" class="dl-btn mpl-novo" onClick={novoOvoGuardandoAtivo}>Novo ovo</button></>;

export function MeusPetsDesktop({ fechar }: { fechar: () => void }) {
  const { motor: ativo, nascendo } = useJogo(), a = useAtlas();
  const [rev, setRev] = useState(0), [sel, setSel] = useState<Sel>("ativo"), [msg, setMsg] = useState(""), [apagar, setApagar] = useState(false);
  const importando = useImportar();
  /* recalcula ao voltar da importacao (um pet novo pode ter entrado na espera) */
  const guardados = useMemo(() => { try { return lerGuardados().map(g => ({ g, m: abrirGuardado(g) })); } catch { return null; } }, [rev, importando]);
  const ovoAtivo = nascendo > 0;
  const lista: { k: Sel; m: Motor; ovo: boolean }[] = [{ k: "ativo", m: ativo, ovo: ovoAtivo },
    ...(guardados ?? []).map(({ m }, i) => ({ k: i as Sel, m, ovo: false }))];
  const atual = lista.find(x => x.k === sel) ?? lista[0], m = atual.m, eAtivo = atual.k === "ativo";
  const escolher = (k: Sel) => { setSel(k); setMsg(""); setApagar(false); };
  const agir = (f: () => void, depois?: () => void) => { try { f(); setMsg(""); setRev(r => r + 1); depois?.(); } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); } };
  const exportar = () => { exportarArquivo(m); setMsg("Registro baixado: " + nomeArquivo(m)); };
  const podeCruzar = !eAtivo && !ovoAtivo && ativo.estagioAtual === "adulto" && !ativo.morte && m.estagioAtual === "adulto" && !m.morte;
  const nome = (x: { m: Motor; ovo: boolean }) => x.ovo ? "Digi-Egg" : nomeForma(x.m.forma);
  const img = (x: Motor, ovo: boolean, alvo: number) => {
    if (a.tipo !== "ok") return null;
    const k = ovo ? OVO[x.especie] : chaveSprite(x.forma);
    return imagemAtlas(a, k, Math.max(1, Math.min(3, Math.floor(alvo / dimSprite(a.dados, k)[1]))));
  };
  return (
    <section class="mpl dl" aria-label="Meus pets">
      <div class="mpl-lista">
        <div class="mpl-cab"><h2>{lista.length} {lista.length === 1 ? "pet" : "pets"}</h2><small>um ativo; os outros ficam congelados até voltar</small></div>
        {guardados === null && <p class="dl-apoio erro">Os pets guardados não abriram.</p>}
        <div class="mpl-grade">
          {lista.map(x => {
            const s = img(x.m, x.ovo, 110), ativoX = x.k === "ativo";
            return (
              <button type="button" key={String(x.k)} class={`mpl-slot${sel === x.k ? " sel" : ""}`} aria-pressed={sel === x.k} onClick={() => escolher(x.k)}>
                <span class={`mpl-palco${ativoX ? "" : " congelado dl-malha"}`}>{s && <img class="dl-pix" src={s.url} width={s.w} height={s.h} alt="" />}</span>
                <span class="mpl-nome"><b>{nome(x)}</b><span class={`dl-tag ${ativoX ? "dl-tag--ativo" : "mpl-tag-espera"}`}>{ativoX ? "ATIVO" : "EM ESPERA"}</span></span>
                <span class="mpl-sub"><span>{x.ovo ? "ainda não chocou" : nomeEstagio(x.m.forma)}</span><span class="dl-lcd">D{diaDe(x.m.e.tick)}</span></span>
              </button>
            );
          })}
          <button type="button" class="mpl-slot mpl-livre" onClick={novoOvoGuardandoAtivo}><span aria-hidden="true">+</span>espaço livre<small>novo ovo</small></button>
        </div>
      </div>
      <aside class="mpl-detalhe" aria-labelledby="mpl-det-tit">
        <div class="mpl-det-cab"><h2 id="mpl-det-tit">{nome(atual)}</h2><span class={`dl-tag ${eAtivo ? "dl-tag--ativo" : "mpl-tag-espera"}`}>{eAtivo ? "ATIVO" : "EM ESPERA"}</span></div>
        <div class={`mpl-det-palco${eAtivo ? "" : " congelado dl-malha"}`}>
          {!eAtivo && <span class="mpl-desde">em espera desde D{diaDe(m.e.tick)} {hhmm(m.e.tick)}</span>}
          {(() => { const s = img(m, atual.ovo, 170); return s && <img class="dl-pix" src={s.url} width={s.w} height={s.h} alt={nome(atual)} />; })()}
        </div>
        <div class="mpl-det-cab2"><b>{eAtivo ? "Como ele está" : "Como ele ficou"}</b><small>{eAtivo ? "agora" : "congelado assim"}</small></div>
        <div class="mpl-barras">
          {([["fome", m.e.fome], ["energia", m.e.energia], ["higiene", m.e.higiene]] as [string, number][]).map(([r, v]) => (
            <div class="mpl-barra" key={r}><span>{r}</span><Seg n={blocos(v, 5)} m={5} cls={v < .5 ? "dl-seg--necessidade" : "dl-seg--acao"} /></div>
          ))}
        </div>
        <div class="mpl-tags">
          <span class="dl-tag dl-tag--estagio">{atual.ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span>
          {vinculoTxt(m) && <span class="mpl-tag-vinculo">{vinculoTxt(m)}</span>}
          <Deco nome={BRASAO[m.especie].peca} largura={30} altura={20} alt={NOME_ESP[m.especie]} />
          <span>{diaDe(m.e.tick)} {diaDe(m.e.tick) === 1 ? "dia" : "dias"} de vida</span>
          {m.morte && <span class="mpl-tag-morto">se foi</span>}
        </div>
        <div class="mpl-bts">
          <button type="button" class="dl-btn dl-btn--sec" onClick={exportar}>Exportar</button>
          {eAtivo ? <button type="button" class="dl-btn" onClick={fechar}>Voltar ao pet</button>
            : <button type="button" class="dl-btn" onClick={() => agir(() => ativarGuardado(atual.k as number), fechar)}>Tornar ativo</button>}
        </div>
        {podeCruzar && <button type="button" class="dl-btn dl-btn--sec mpl-cruzar" onClick={() => agir(() => cruzarComAtivo(atual.k as number), fechar)}
          title="o filho herda o temperamento dos dois e o brasão de um deles">Cruzar com {nomeForma(ativo.forma)}</button>}
        {!eAtivo && (apagar
          ? <button type="button" class="dl-btn dl-btn--perigo mpl-apagar" onClick={() => agir(() => apagarGuardado(atual.k as number), () => { setSel("ativo"); setApagar(false); })}>Confirmar: apagar {nome(atual)}</button>
          : <button type="button" class="mpl-apagar mpl-apagar--pedir" onClick={() => setApagar(true)}>Apagar este pet</button>)}
        {msg && <p class="dl-apoio" aria-live="polite">{msg}</p>}
      </aside>
    </section>
  );
}
