/* Meus pets (desenho MeusPets): o pet ativo, exportar o registro e voltar ao pet anterior (guardado pelos
   Cenarios). Um pet por vez: o jogo guarda o registro de um pet so; ovo novo e no Registro, com confirmacao. */
import { useEffect, useRef, useState } from "preact/hooks";
import { DO_ESP, Motor, NOME_EST, OVO, chaveSprite, nomeEstagio, nomeForma } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { Deco, fundoDeco } from "../../componentes/Deco.tsx";
import { ICONE } from "../../decoracao.ts";
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

export function MeusPets({ fechar, irRegistro }: { fechar: () => void; irRegistro: () => void }) {
  const { motor: m, nascendo } = useJogo(), a = useAtlas(), ref = useRef<HTMLDialogElement>(null), [msg, setMsg] = useState("");
  useEffect(() => { ref.current?.showModal(); }, []);
  const ovo = nascendo > 0, img = a.tipo === "ok" ? imagemAtlas(a, ovo ? OVO[m.especie] : chaveSprite(m.forma)) : null;
  const exportar = async () => {
    /* o mesmo conteudo do save: semente, registro e versao do pet */
    const txt = JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao });
    try { await navigator.clipboard.writeText(txt); setMsg("Registro copiado para a área de transferência."); }
    catch { console.log(txt); setMsg("Não foi possível copiar automaticamente. O registro está no console do navegador."); }
  };
  return (
    <dialog class="meus-pets dl" ref={ref} aria-labelledby="mp-titulo" onClose={fechar}>
      <div class="dl-card">
        <div class="dl-linha" style={{ justifyContent: "space-between" }}>
          <h2 class="dl-titulo-card mp-titulo" id="mp-titulo"><Deco nome={ICONE.pets} class="mp-titulo-ic" />Meus pets</h2>
          <button type="button" class="dl-btn dl-btn--icone" aria-label="Fechar" onClick={() => ref.current?.close()}>
            <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 5l10 10M15 5 5 15" /></svg></button>
        </div>
        <div class="mp-slots">
          <div class="slot">
            <span class="mp-retrato-anel">
              <Deco nome="Digivice_Circle_01" class="mp-anel gira" />
              <span class="pet-retrato" aria-hidden="true">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
            </span>
            <span style={{ display: "grid", gap: "4px", minWidth: 0 }}>
              <b style={{ fontWeight: 900 }}>{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</b>
              <span><span class="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span> <span class="dl-tag dl-tag--ativo">ativo</span></span>
            </span>
          </div>
          <button type="button" class="slot-novo" style={{ "--padrao": fundoDeco("Icon_Pattern_2") ?? "none" }} onClick={() => { ref.current?.close(); irRegistro(); }}>
            <span class="dl-num" style={{ fontSize: "1.5rem" }} aria-hidden="true">+</span>novo ovo</button>
        </div>
        <p class="dl-apoio" style={{ margin: 0 }}>Um pet por vez: o jogo guarda o registro de um pet só. Um ovo novo apaga este pet (com confirmação, no Registro).</p>
        <div class="acoes-mp">
          <button type="button" class="dl-btn dl-btn--sec" onClick={exportar}>Exportar</button>
          {lerAnterior() && <button type="button" class="dl-btn dl-btn--sec" onClick={() => { setMsg(voltarAoAnterior()); ref.current?.close(); }}>Voltar ao pet anterior</button>}
        </div>
        <p class="dl-apoio" aria-live="polite" style={{ margin: 0 }}>{msg}</p>
      </div>
    </dialog>
  );
}
