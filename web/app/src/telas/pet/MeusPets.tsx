/* Meus pets (desenho MeusPets): o pet ativo, exportar o registro e voltar ao pet anterior (guardado pelos
   Cenarios). Um pet por vez: o jogo guarda o registro de um pet so; ovo novo e no Registro, com confirmacao. */
import { useEffect, useRef, useState } from "preact/hooks";
import { DO_ESP, Motor, NOME_EST, OVO, chaveSprite, nomeEstagio, nomeForma } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { trocarMotor, useJogo } from "../../jogo.ts";
import { LUTA, previa } from "../../luta.ts";
import { CHAVE } from "../../save.ts";

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
  const exportar = async () => {
    /* o mesmo conteudo do save: semente, registro e versao do pet */
    const txt = JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao });
    try { await navigator.clipboard.writeText(txt); setMsg("Registro copiado para a área de transferência."); }
    catch { console.log(txt); setMsg("Não foi possível copiar automaticamente. O registro está no console do navegador."); }
  };
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
        <p class="mp-aviso">Um pet por vez: o jogo guarda o registro de um pet só.</p>
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
