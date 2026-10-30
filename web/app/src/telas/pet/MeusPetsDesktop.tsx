/* Meus pets no painel do desktop (layout habitat, M5), na pele XCOM e numa coluna de ate 760 px: a grade de espacos (o ativo, os
   guardados em espera, um espaco livre para o ovo novo) e, embaixo, o pet escolhido: como ele ficou congelado, estagio, vinculo,
   brasao, dias de vida e as acoes (Exportar, Tornar ativo, Cruzar, Apagar). O celular segue com MeusPets (caixa centralizada).
   Tudo sai do motor de cada pet (replay do registro guardado). */
import { useMemo, useState } from "react";
import "../../estilo/menus_config.css";
import { NOME_ESP, NOME_EST, OVO, chaveSprite, nomeEstagio, nomeForma, type Motor } from "../../../motor/index.ts";
import { imagemAtlas, dimSprite, useAtlas } from "../../atlas.ts";
import { blocos } from "../../componentes/Barras.tsx";
import { Deco } from "../../componentes/Deco.tsx";
import { BotaoContinuar, BotaoHx, ChipHx, MedidorHx } from "../../componentes/hx/index.ts";
import { BRASAO } from "../../decoracao.ts";
import { useJogo } from "../../jogo.ts";
import { novoOvoGuardandoAtivo } from "../../jornada.ts";
import { abrirImportar, exportarArquivo, nomeArquivo, useImportar } from "../../importar.ts";
import { abrirGuardado, apagarGuardado, ativarGuardado, lerGuardados } from "../../pets.ts";
import { abrirHeranca, podeSerPai } from "../../heranca.ts";
import { diaDe, hhmm } from "./TelaPet.tsx";

type Sel = "ativo" | number;
const vinculoTxt = (m: Motor): string | null => m.vinc.valor >= .66 ? "vínculo alto" : m.vinc.valor >= .33 ? "vínculo médio" : "vínculo baixo";

/** os botoes do topo do painel: Importar e Novo ovo (o ativo vai para a espera: ninguem e apagado sem pedir) */
export const AcoesMeusPets = () => <>
  <BotaoHx className="mpl-novo" onClick={abrirImportar}>Importar</BotaoHx>
  <BotaoContinuar className="mpl-novo" onClick={novoOvoGuardandoAtivo}>Novo ovo</BotaoContinuar></>;

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
  const podeCruzar = !eAtivo && !ovoAtivo && podeSerPai(ativo) && podeSerPai(m);
  const nome = (x: { m: Motor; ovo: boolean }) => x.ovo ? "Digi-Egg" : nomeForma(x.m.forma);
  const img = (x: Motor, ovo: boolean, alvo: number) => {
    if (a.tipo !== "ok") return null;
    const k = ovo ? OVO[x.especie] : chaveSprite(x.forma);
    return imagemAtlas(a, k, Math.max(1, Math.min(3, Math.floor(alvo / dimSprite(a.dados, k)[1]))));
  };
  const chipEstado = (ativoX: boolean) => <ChipHx tom={ativoX ? "ok" : "neutro"}>{ativoX ? "ATIVO" : "EM ESPERA"}</ChipHx>;
  return (
    <section className="mc mc-pets" aria-label="Meus pets">
      <p className="mc-apoio">{lista.length} {lista.length === 1 ? "pet" : "pets"} · um ativo; os outros ficam congelados até voltar</p>
      {guardados === null && <p className="mc-erro">Os pets guardados não abriram.</p>}
      <div className="mc-grade">
        {lista.map(x => {
          const s = img(x.m, x.ovo, 110), ativoX = x.k === "ativo";
          return (
            <button type="button" key={String(x.k)} className="mc-slot" aria-pressed={sel === x.k} onClick={() => escolher(x.k)}>
              <span className={`mc-palco${ativoX ? "" : " mc-palco--congelado"}`}>{s && <img className="dl-pix" src={s.url} width={s.w} height={s.h} alt="" />}</span>
              <b>{nome(x)}</b>
              {chipEstado(ativoX)}
              <span className="mc-subl"><span>{x.ovo ? "ainda não chocou" : nomeEstagio(x.m.forma)}</span><span className="mc-num">D{diaDe(x.m.e.tick)}</span></span>
            </button>
          );
        })}
        <button type="button" className="mc-slot mc-slot--livre" onClick={novoOvoGuardandoAtivo}><span aria-hidden="true">+</span>espaço livre<small>novo ovo</small></button>
      </div>
      <aside className="mc-detalhe" aria-labelledby="mpl-det-tit">
        <div className="mc-detalhe__cab"><h2 id="mpl-det-tit">{nome(atual)}</h2>{chipEstado(eAtivo)}</div>
        <div className={`mc-palco mc-palco--ativo${eAtivo ? "" : " mc-palco--congelado"}`}>
          {!eAtivo && <span className="mc-desde">em espera desde D{diaDe(m.e.tick)} {hhmm(m.e.tick)}</span>}
          {(() => { const s = img(m, atual.ovo, 170); return s && <img className="dl-pix" src={s.url} width={s.w} height={s.h} alt={nome(atual)} />; })()}
        </div>
        <h3 className="mc-sec">{eAtivo ? "Como ele está agora" : "Como ele ficou, congelado assim"}</h3>
        <div className="mc-barras">
          {([["fome", m.e.fome], ["energia", m.e.energia], ["higiene", m.e.higiene]] as [string, number][]).map(([r, v]) => (
            <MedidorHx key={r} rotulo={r} valor={blocos(v, 5)} max={5} tom={v < .5 ? "alerta" : "neutro"} />
          ))}
        </div>
        <div className="mc-tags">
          <ChipHx tom="rotulo">{atual.ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</ChipHx>
          {vinculoTxt(m) && <span>{vinculoTxt(m)}</span>}
          <Deco nome={BRASAO[m.especie].peca} largura={30} altura={20} alt={NOME_ESP[m.especie]} />
          <span>{diaDe(m.e.tick)} {diaDe(m.e.tick) === 1 ? "dia" : "dias"} de vida</span>
          {m.morte && <ChipHx tom="perigo">se foi</ChipHx>}
        </div>
        <div className="mc-linha">
          <BotaoHx onClick={exportar}>Exportar</BotaoHx>
          {eAtivo ? <BotaoContinuar onClick={fechar}>Voltar ao pet</BotaoContinuar>
            : <BotaoContinuar onClick={() => agir(() => ativarGuardado(atual.k as number), fechar)}>Tornar ativo</BotaoContinuar>}
        </div>
        {podeCruzar && <BotaoHx className="mc-largo" onClick={() => abrirHeranca(atual.k as number)}
          title="o filho herda o temperamento dos dois e o brasão de um deles">Nova geração com {nomeForma(ativo.forma)}</BotaoHx>}
        {!eAtivo && (apagar
          ? <BotaoHx tom="perigo" onClick={() => agir(() => apagarGuardado(atual.k as number), () => { setSel("ativo"); setApagar(false); })}>Confirmar: apagar {nome(atual)}</BotaoHx>
          : <BotaoHx tom="perigo" onClick={() => setApagar(true)}>Apagar este pet</BotaoHx>)}
        {msg && <p className="mc-apoio" aria-live="polite">{msg}</p>}
      </aside>
    </section>
  );
}
