/* Meus pets (desenho MeusPets): o pet ativo, exportar o registro e voltar ao pet anterior (guardado pelos
   Cenarios). Um pet por vez: o jogo guarda o registro de um pet so; ovo novo e no Registro, com confirmacao. */
import { useEffect, useMemo, useRef, useState } from "react";
import { DO_ESP, Motor, NOME_EST, OVO, chaveSprite, lutadorPet, nomeEstagio, nomeForma, vidaExibida } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { trocarMotor, useJogo } from "../../jogo.ts";
import { LUTA, previa } from "../../luta.ts";
import { CHAVE } from "../../save.ts";
import { abrirGuardado, ativarGuardado, lerGuardados } from "../../pets.ts";
import { abrirHeranca, podeSerPai } from "../../heranca.ts";
import { abrirImportar, exportarArquivo, nomeArquivo } from "../../importar.ts";
import { dec } from "../../componentes/Barras.tsx";
import { diaDe } from "./TelaPet.tsx";

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
function Guardados({ ativar, cruzar }: { ativar: (i: number) => void; cruzar: ((i: number) => void) | null }) {
  const a = useAtlas();
  const lista = useMemo(() => {
    try { return lerGuardados().map(g => abrirGuardado(g)); } catch { return null; }
  }, []);
  if (lista === null) return <p className="dl-apoio erro">Os pets guardados não abriram.</p>;
  if (!lista.length) return null;
  return (
    <section className="mp-guardados" aria-labelledby="mp-guard-tit">
      <h3 id="mp-guard-tit">Guardados <small>o tempo deles está parado</small></h3>
      {cruzar && <p className="dl-apoio mp-cruzar-dica">Seu pet é adulto: ele pode cruzar com outro adulto. O filho herda o temperamento dos dois e o brasão de um deles; nada aprendido passa adiante.</p>}
      <ul>
        {lista.map((g, i) => {
          const img = a.tipo === "ok" ? imagemAtlas(a, chaveSprite(g.forma)) : null, p = lutadorPet(g, "", true).cond;
          return (
            <li key={i} className="mp-guardado">
              <span className="mpd-ret mp-g-ret">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
              <span className="mp-g-txt"><b>{nomeForma(g.forma)}</b>
                <span><span className="dl-tag dl-tag--estagio">{nomeEstagio(g.forma)}</span> dia {diaDe(g.e.tick)}</span>
                <span className="mp-g-num">vida {Math.round(vidaExibida(p, g.forma.est, g.treino.total, g.versao)).toLocaleString("pt-BR")} · treino +{dec(g.treino.total, 0)}</span></span>
              <span className="mp-g-bts">
                <button type="button" className="dl-btn dl-btn--sec mp-g-ativar" onClick={() => ativar(i)}>Ativar</button>
                {cruzar && podeSerPai(g) &&
                  <button type="button" className="dl-btn dl-btn--sec mp-g-cruzar" onClick={() => cruzar(i)}
                    title="o filho herda o temperamento dos dois e a espécie de um deles">Nova geração</button>}
              </span>
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
  const { motor: m, nascendo } = useJogo(), a = useAtlas(), ref = useRef<HTMLDialogElement>(null), [msg, setMsg] = useState("");
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
  /* heranca: so com o ativo adulto e vivo; o filho vira o ativo */
  const podeCruzar = !ovo && podeSerPai(m);
  const cruzar = (i: number) => {
    ref.current?.close(); abrirHeranca(i);
  };
  /* o arquivo .digilab e o proprio save do pet (semente, registro e versao) */
  const exportar = () => { exportarArquivo(m); setMsg("Registro baixado: " + nomeArquivo(m)); };
  /* desktop: Meus pets e uma pagina (MeusPetsDesktop, prancha MpListaDesktop); aqui so o celular (MpAtual) */
  return (
    <dialog className="meus-pets mp-tela dl" ref={ref} aria-labelledby="mp-titulo" onClose={fechar}>
      <div className="mp-cab dl-faixa">
        <button type="button" className="conv-voltar" aria-label="Voltar" onClick={() => ref.current?.close()}>
          <svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path d="M10 3 5 8l5 5" /></svg></button>
        <h2 className="dl-num" id="mp-titulo">Meus pets</h2>
      </div>
      <div className="mp-corpo">
        <section className="mp-palco dl-hexcard" aria-label="Pet ativo">
          <span className="dl-tag dl-tag--ativo mp-ativo">ATIVO</span>
          <span className="mp-anel" aria-hidden="true" />
          {img && <img className="dl-pix mp-spr" src={img.url} width={img.w} height={img.h} alt="" />}
          <span className="mp-placa"><span className="dl-placa">{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</span>
            <span className="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span></span>
        </section>
        <p className="mp-aviso">Só o pet ativo tem o tempo correndo; os guardados ficam parados onde estavam.</p>
        {!ovo && m.versao < 5 && <p className="mp-aviso">Pet de uma versão antiga: evolui até o Ultimate (o Mega é dos ovos novos).</p>}
        <Guardados ativar={ativar} cruzar={podeCruzar ? cruzar : null} />
        {anterior && <div className="mp-anterior">{antImg && <img className="dl-pix" src={antImg.url} width={antImg.w / 2} height={antImg.h / 2} alt="" />}
          <span><b>Pet anterior guardado</b><span>ficou salvo quando você usou o Laboratório</span></span></div>}
        {anterior && <button type="button" className="dl-btn dl-btn--sec dl-btn--largo" onClick={() => { setMsg(voltarAoAnterior()); ref.current?.close(); }}>Voltar ao pet anterior</button>}
        <button type="button" className="dl-btn dl-btn--sec dl-btn--largo" onClick={() => { ref.current?.close(); irRegistro(); }}>Registro e novo ovo</button>
        <button type="button" className="dl-btn dl-btn--sec dl-btn--largo" onClick={exportar}>Exportar registro</button>
        <button type="button" className="dl-btn dl-btn--sec dl-btn--largo" onClick={() => { ref.current?.close(); abrirImportar(); }}>Importar pet</button>
        <p className="dl-apoio" aria-live="polite" style={{ margin: 0 }}>{msg}</p>
      </div>
    </dialog>
  );
}
