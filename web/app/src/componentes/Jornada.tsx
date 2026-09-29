/* Jornada do jogador (src/jornada.ts): a escolha do brasao antes de todo ovo novo e a mensagem de conclusao ao vencer o
   chefe da campanha. Mesmo visual das boas-vindas (tela cheia listrada, ovo no anel); nomes na tela em Digimon. */
import { useEffect, useRef, useState } from "preact/hooks";
import { DIGIMON_DA_FORMA, ESPECIES, LUGARES, NPC, OVO, chaveSprite, nomeEstagio, nomeForma, type Especie, type Motor } from "../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../atlas.ts";
import { useDesktop } from "../desktop.ts";
import { BRASAO } from "../decoracao.ts";
import { CHEFE, chocarDoBrasao, fecharEscolhaBrasao, guardarAtivoNoProximoOvo, marcarConclusao, marcos, novoOvoGuardandoAtivo } from "../jornada.ts";
import { abrirModal } from "./modal.ts";
import { Deco } from "./Deco.tsx";
import { diaDe } from "../telas/pet/TelaPet.tsx";

const d = (k: string): string => DIGIMON_DA_FORMA[k]?.[0] ?? "?";

/** antes de todo ovo novo: os quatro brasoes, com o ovo e os Digimon que cada um pode ter no comeco */
export function EscolherBrasao({ podeVoltar }: { podeVoltar: boolean }) {
  const ref = useRef<HTMLDialogElement>(null), a = useAtlas(), [msg, setMsg] = useState(""), desk = useDesktop();
  useEffect(() => { abrirModal(ref.current); }, []);
  const escolher = (esp: Especie) => {
    try { chocarDoBrasao(esp, guardarAtivoNoProximoOvo()); } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  return (
    <dialog class="brasao-tela dl" ref={ref} aria-labelledby="br-tit" onCancel={e => { if (!podeVoltar) e.preventDefault(); }} onClose={fecharEscolhaBrasao}>
      <div class="br-cab">
        <h1 class="bv-tit br-tit" id="br-tit">Escolha seu brasão</h1>
        <p class="bv-slogan">O brasão decide a família do seu Digimon. O resto, você decide cuidando.</p>
      </div>
      <ul class="br-lista">
        {ESPECIES.map(esp => {
          const ovo = a.tipo === "ok" ? imagemAtlas(a, OVO[esp], desk ? 2 : 1) : null, b = BRASAO[esp];
          return (
            <li key={esp}>
              <button type="button" class="br-card" onClick={() => escolher(esp)} aria-label={`Brasão da ${b.nome}`}>
                <Deco nome={b.peca} class="br-brasao" largura={64} altura={44} />
                <b class="br-nome">{b.nome}</b>
                {ovo && <img class="dl-pix br-ovo" src={ovo.url} width={ovo.w} height={ovo.h} alt="" />}
                <span class="br-linha">nasce <b>{d(`${esp}_bebe`)}</b></span>
                <span class="br-linha">Rookie: <b>{d(`${esp}_crianca_sereno`)}</b> ou <b>{d(`${esp}_crianca_arisco`)}</b></span>
              </button>
            </li>
          );
        })}
      </ul>
      <div class="br-pe">
        {msg && <p class="dl-apoio">{msg}</p>}
        {podeVoltar && <button type="button" class="dl-btn dl-btn--sec" onClick={() => ref.current?.close()}>Voltar</button>}
      </div>
    </dialog>
  );
}

/** vencer o chefe: a jornada acabou (uma vez por pet). Continuar com ele ou chocar outro (este vai para os guardados) */
export function Conclusao({ m, fechar }: { m: Motor; fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), a = useAtlas();
  useEffect(() => { abrirModal(ref.current); marcarConclusao(m); }, []);
  /* escala inteira que cabe no palco (170 px de altura, como em Meus pets) */
  const k = chaveSprite(m.forma), spr = a.tipo === "ok" ? imagemAtlas(a, k, Math.max(1, Math.min(3, Math.floor(170 / dimSprite(a.dados, k)[1])))) : null;
  const b = BRASAO[m.especie];
  const lutas = m.log.filter(e => e[1] === "l").length, chefe = NPC[CHEFE]!;
  return (
    <dialog class="brasao-tela conclusao-tela dl" ref={ref} aria-labelledby="cc-tit" onClose={fechar}>
      <div class="bv-centro">
        <div class="bv-palco" aria-hidden="true">
          <span class="bv-luz" /><span class="bv-anel" />
          {spr && <img class="dl-pix bv-ovo cc-pet" src={spr.url} width={spr.w} height={spr.h} alt="" />}
        </div>
      </div>
      <div class="bv-texto">
        <h1 class="bv-tit cc-tit" id="cc-tit">Jornada concluída!</h1>
        <p class="bv-slogan">{nomeForma(m.forma)} venceu {chefe.nome} na {LUGARES[chefe.lug].nome}.</p>
        <p class="cc-texto">
          Do Digi-Egg ao {nomeEstagio(m.forma)}, com o brasão da <b>{b.nome}</b>, em {diaDe(m.e.tick)} dia{diaDe(m.e.tick) > 1 ? "s" : ""} e {lutas} luta{lutas === 1 ? "" : "s"}.
          Tudo o que ele é saiu do que vocês viveram juntos.
        </p>
        <ul class="cc-marcos">{marcos(m).map(x => <li key={x.rotulo} class={x.feito ? "feito" : ""}>{x.feito ? "✓" : "·"} {x.rotulo}</li>)}</ul>
        <div class="bv-pe">
          <button type="button" class="dl-btn dl-btn--destaque bv-comecar" onClick={() => ref.current?.close()}>Continuar com {nomeForma(m.forma)}</button>
          <button type="button" class="dl-btn dl-btn--sec" onClick={() => { ref.current?.close(); novoOvoGuardandoAtivo(); }}>Chocar um ovo novo (ele fica guardado)</button>
        </div>
      </div>
    </dialog>
  );
}
