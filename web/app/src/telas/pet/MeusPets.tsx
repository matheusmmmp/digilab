/* Meus pets (desenho MeusPets): o pet ativo, exportar o registro e voltar ao pet anterior (guardado pelos
   Cenarios). Um pet por vez: o jogo guarda o registro de um pet so; ovo novo e no Registro, com confirmacao. */
import { useEffect, useMemo, useRef, useState } from "preact/hooks";
import { DO_ESP, Motor, NOME_ESP, NOME_EST, OVO, chaveSprite, lutadorPet, nomeEstagio, nomeForma, vidaExibida } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { trocarMotor, useJogo } from "../../jogo.ts";
import { LUTA, previa } from "../../luta.ts";
import { CHAVE } from "../../save.ts";
import { useDesktop } from "../../desktop.ts";
import { abrirGuardado, ativarGuardado, lerGuardados } from "../../pets.ts";
import { dec } from "../../componentes/Barras.tsx";
import { diaDe } from "./TelaPet.tsx";
import { Deco } from "../../componentes/Deco.tsx";
import { BRASAO } from "../../decoracao.ts";

export const CHAVE_ANTERIOR = CHAVE + "-anterior";
const lerAnterior = (): string | null => { try { return localStorage.getItem(CHAVE_ANTERIOR); } catch { return null; } };

/** volta ao pet guardado antes de um cenario (replay do registro guardado); falha alto se nao abrir */
export function voltarAoAnterior(): string {
  const bruto = lerAnterior();
  if (!bruto) return "Não há pet anterior guardado.";
  const d = JSON.parse(bruto);
  if (!Number.isInteger(d?.semente) || !Array.isArray(d?.log)) throw new Error("pet anterior guardado não tem semente e registro");
  trocarMotor(Motor.reproduzir(d.semente, d.log, d.versao ?? 1), "save");
  try { localStorage.removeItem(CHAVE_ANTERIOR); } catch { /* ja trocou */ }
  LUTA.rivalFixo = null; previa("arena");
  return "Pet anterior restaurado pelo replay do registro.";
}

/** os pets guardados (varios pets, um ativo): parados no tempo; Ativar troca com o ativo */
function Guardados({ ativar }: { ativar: (i: number) => void }) {
  const a = useAtlas();
  const lista = useMemo(() => {
    try { return lerGuardados().map(g => abrirGuardado(g)); } catch { return null; }
  }, []);
  if (lista === null) return <p class="dl-apoio erro">Os pets guardados não abriram.</p>;
  if (!lista.length) return null;
  return (
    <section class="mp-guardados" aria-labelledby="mp-guard-tit">
      <h3 id="mp-guard-tit">Guardados <small>o tempo deles está parado</small></h3>
      <ul>
        {lista.map((g, i) => {
          const img = a.tipo === "ok" ? imagemAtlas(a, chaveSprite(g.forma)) : null, p = lutadorPet(g, "", true).cond;
          return (
            <li key={i} class="mp-guardado">
              <span class="mpd-ret mp-g-ret">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
              <span class="mp-g-txt"><b>{nomeForma(g.forma)}</b>
                <span><span class="dl-tag dl-tag--estagio">{nomeEstagio(g.forma)}</span> dia {diaDe(g.e.tick)}</span>
                <span class="mp-g-num">vida {Math.round(vidaExibida(p, g.forma.est, g.treino.total)).toLocaleString("pt-BR")} · treino +{dec(g.treino.total, 0)}</span></span>
              <button type="button" class="dl-btn dl-btn--sec mp-g-ativar" onClick={() => ativar(i)}>Ativar</button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

/** Meus pets (prancha MpAtual): tela cheia com voltar, o pet ativo no palco (anel, escala inteira), o aviso de um pet
    por vez, o pet anterior guardado (se houver) e os botoes. Exportar copia o registro (mesmo conteudo do save). */
export function MeusPets({ fechar, irRegistro }: { fechar: () => void; irRegistro: () => void }) {
  const { motor: m, nascendo } = useJogo(), a = useAtlas(), ref = useRef<HTMLDialogElement>(null), [msg, setMsg] = useState(""), desk = useDesktop();
  useEffect(() => { abrirModal(ref.current); }, []);
  const ovo = nascendo > 0, nome = ovo ? OVO[m.especie] : chaveSprite(m.forma);
  let img = null;
  if (a.tipo === "ok") { const h = dimSprite(a.dados, nome)[1]; img = imagemAtlas(a, nome, Math.max(1, Math.min(3, Math.floor(170 / h)))); }
  const anterior = lerAnterior();
  let antImg = null;
  if (anterior && a.tipo === "ok") {
    try { const d = JSON.parse(anterior); antImg = Number.isInteger(d?.semente) ? imagemAtlas(a, OVO[Motor.reproduzir(d.semente, [], d.versao ?? 1).especie]) : null; } catch { antImg = null; }
  }
  const ativar = (i: number) => {
    try { ativarGuardado(i); setMsg(""); ref.current?.close(); } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  const exportar = async () => {
    /* o mesmo conteudo do save: semente, registro e versao do pet */
    const txt = JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao });
    try { await navigator.clipboard.writeText(txt); setMsg("Registro copiado para a área de transferência."); }
    catch { console.log(txt); setMsg("Não foi possível copiar automaticamente. O registro está no console do navegador."); }
  };
  /* desktop (MpDesktop): modal no centro com x, o slot do pet ativo, o do ovo novo (vai ao Registro, que confirma) e os botoes */
  if (desk) {
    const ret = a.tipo === "ok" ? imagemAtlas(a, nome) : null;
    return (
      <dialog class="meus-pets mp-desk dl" ref={ref} aria-labelledby="mp-titulo" onClose={fechar}>
        <div class="mpd-cab"><h2 class="dl-num" id="mp-titulo">Meus pets</h2>
          <button type="button" class="mpd-x" aria-label="Fechar" onClick={() => ref.current?.close()}>×</button></div>
        <div class="mpd-slots">
          <div class="mpd-ativo">
            <span class="mpd-ret">{ret && <img class="dl-pix" src={ret.url} width={ret.w} height={ret.h} alt="" />}</span>
            <span class="mpd-txt"><span class="mpd-nome"><b>{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</b>
              <Deco nome={BRASAO[m.especie].peca} largura={30} altura={20} alt={NOME_ESP[m.especie]} /></span>
              <span class="mpd-tags"><span class="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span><span class="dl-tag dl-tag--ativo">ATIVO</span></span></span>
          </div>
          <button type="button" class="mpd-novo" onClick={() => { ref.current?.close(); irRegistro(); }}>
            {/* a especie do ovo novo sai da semente nova: o ovo aparece apagado */}
            {a.tipo === "ok" && <img class="dl-pix mpd-novo-ovo" src={imagemAtlas(a, OVO[m.especie]).url} width={26} height={36} alt="" />}<span>novo ovo</span></button>
        </div>
        <p class="mpd-aviso">Só o pet ativo tem o tempo correndo; os guardados ficam parados onde estavam. Um ovo novo apaga o pet ativo (com confirmação, no Registro).</p>
        <Guardados ativar={ativar} />
        <div class="mpd-bts">
          <button type="button" class="dl-btn dl-btn--sec" onClick={exportar}>Exportar</button>
          {anterior && <button type="button" class="dl-btn dl-btn--sec" onClick={() => { setMsg(voltarAoAnterior()); ref.current?.close(); }}>Voltar ao pet anterior</button>}
        </div>
        {msg && <p class="dl-apoio" aria-live="polite" style={{ margin: 0 }}>{msg}</p>}
      </dialog>
    );
  }
  return (
    <dialog class="meus-pets mp-tela dl" ref={ref} aria-labelledby="mp-titulo" onClose={fechar}>
      <div class="mp-cab dl-faixa">
        <button type="button" class="conv-voltar" aria-label="Voltar" onClick={() => ref.current?.close()}>
          <svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path d="M10 3 5 8l5 5" /></svg></button>
        <h2 class="dl-num" id="mp-titulo">Meus pets</h2>
      </div>
      <div class="mp-corpo">
        <section class="mp-palco dl-hexcard" aria-label="Pet ativo">
          <span class="dl-tag dl-tag--ativo mp-ativo">ATIVO</span>
          <span class="mp-anel" aria-hidden="true" />
          {img && <img class="dl-pix mp-spr" src={img.url} width={img.w} height={img.h} alt="" />}
          <span class="mp-placa"><span class="dl-placa">{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</span>
            <span class="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span></span>
        </section>
        <p class="mp-aviso">Só o pet ativo tem o tempo correndo; os guardados ficam parados onde estavam.</p>
        <Guardados ativar={ativar} />
        {anterior && <div class="mp-anterior">{antImg && <img class="dl-pix" src={antImg.url} width={antImg.w / 2} height={antImg.h / 2} alt="" />}
          <span><b>Pet anterior guardado</b><span>ficou salvo quando você usou o Laboratório</span></span></div>}
        {anterior && <button type="button" class="dl-btn dl-btn--sec dl-btn--largo" onClick={() => { setMsg(voltarAoAnterior()); ref.current?.close(); }}>Voltar ao pet anterior</button>}
        <button type="button" class="dl-btn dl-btn--sec dl-btn--largo" onClick={() => { ref.current?.close(); irRegistro(); }}>Registro e novo ovo</button>
        <button type="button" class="dl-btn dl-btn--sec dl-btn--largo" onClick={exportar}>Exportar registro</button>
        <p class="dl-apoio" aria-live="polite" style={{ margin: 0 }}>{msg}</p>
      </div>
    </dialog>
  );
}
