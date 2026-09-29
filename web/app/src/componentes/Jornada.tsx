/* Jornada do jogador (src/jornada.ts): a escolha do brasao antes de todo ovo novo e a mensagem de conclusao ao vencer o
   chefe da campanha. Mesmo visual das boas-vindas (tela cheia listrada, ovo no anel); nomes na tela em Digimon. */
import { useEffect, useRef, useState } from "preact/hooks";
import { DIGIMON_DA_FORMA, ESPECIES, NPC, OVO, chaveSprite, nomeEstagio, nomeForma, type Especie, type Motor, type Ritmo } from "../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../atlas.ts";
import { useDesktop } from "../desktop.ts";
import { BRASAO } from "../decoracao.ts";
import { chefeDe, chocarDoBrasao, fecharEscolhaBrasao, guardarAtivoNoProximoOvo, marcarConclusao, marcos, novoOvoGuardandoAtivo } from "../jornada.ts";
import { abrirModal } from "./modal.ts";
import { Deco } from "./Deco.tsx";
import { Peca } from "./Imagens.tsx";
import { diaDe } from "../telas/pet/TelaPet.tsx";

const d = (k: string): string => DIGIMON_DA_FORMA[k]?.[0] ?? "?";

/** antes de todo ovo novo: os quatro brasoes, com o ovo e os Digimon que cada um pode ter no comeco */
export function EscolherBrasao({ podeVoltar }: { podeVoltar: boolean }) {
  const ref = useRef<HTMLDialogElement>(null), a = useAtlas(), [msg, setMsg] = useState(""), desk = useDesktop();
  const [ritmo, setRitmo] = useState<Ritmo>("rapida");
  useEffect(() => { abrirModal(ref.current); }, []);
  const escolher = (esp: Especie) => {
    try { chocarDoBrasao(esp, guardarAtivoNoProximoOvo(), ritmo); } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  return (
    <dialog class="brasao-tela dl" ref={ref} aria-labelledby="br-tit" onCancel={e => { if (!podeVoltar) e.preventDefault(); }} onClose={fecharEscolhaBrasao}>
      <div class="br-cab">
        <h1 class="bv-tit br-tit" id="br-tit">Escolha seu brasão</h1>
        <p class="bv-slogan">O brasão decide a família do seu Digimon. O resto, você decide cuidando.</p>
      </div>
      <div class="br-ritmo" role="radiogroup" aria-label="Ritmo de crescimento">
        {([["rapida", "Rápido", "3 h · 12 h · 18 h por estágio"], ["classica", "Clássico", "6 h · 24 h · 36 h, como os v-pets"]] as [Ritmo, string, string][]).map(([r, t, d]) => (
          <button type="button" key={r} role="radio" aria-checked={ritmo === r} class={`br-ritmo-op${ritmo === r ? " sel" : ""}`} onClick={() => setRitmo(r)}>
            <b>{t}</b><small>{d}</small></button>
        ))}
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
  const lutas = m.log.filter(e => e[1] === "l").length, chefe = NPC[chefeDe(m)]!;
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
        <p class="bv-slogan">{nomeForma(m.forma)} venceu {chefe.nome} na {m.lugares[chefe.lug].nome}.</p>
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

/* ------------------------------------------------ como jogar (pranchas PvComoCuidar, PvComoEnsinar, PvComoCrescer) */
const PAGINAS: { tit: string; txt: string; sprites: string[]; chips?: [string, string][]; faixa?: string }[] = [
  { tit: "Cuide", txt: "Ele chama quando tem fome, fica sujo ou quer carinho. Atender logo conta.", sprites: ["brasa_bebe"], chips: [["emoji_carne", ""]] },
  { tit: "Ensine", txt: "Elogie ou repreenda o que ele acabou de fazer. Ele aprende de verdade, e às vezes vai desobedecer.",
    sprites: ["brasa_crianca_sereno"], chips: [["emoji_joinha", "Elogiar"], ["emoji_exclam", "Repreender"]] },
  { tit: "Veja crescer", txt: "Como você cuida decide a criança. O que ele aprende com você decide o adolescente e o adulto. Depois ele luta sozinho.",
    sprites: ["brasa_bebe", "brasa_crianca_sereno", "brasa_adolescente_brigao", "brasa_adulto_duelista"], faixa: "cuidado → caráter" },
];
const ROTULO_EST = ["bebê", "criança", "adolescente", "adulto"];

/** primeira vez, depois das boas-vindas: tres paginas (Pular a qualquer momento); no fim, a escolha do brasao */
export function ComoJogar({ fechar }: { fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), a = useAtlas(), [i, setI] = useState(0);
  useEffect(() => { abrirModal(ref.current); }, []);
  const p = PAGINAS[i], ultima = i === PAGINAS.length - 1;
  const img = (k: string, alvo: number) => a.tipo === "ok" ? imagemAtlas(a, k, Math.max(1, Math.min(3, Math.floor(alvo / dimSprite(a.dados, k)[1])))) : null;
  return (
    <dialog class="como-tela dl" ref={ref} aria-labelledby="cj-tit" onClose={fechar}>
      <div class="cj-topo"><button type="button" class="cj-pular" onClick={() => ref.current?.close()}>Pular</button></div>
      <div class="cj-corpo">
        <div class={`cj-cartao dl-hexcard${p.sprites.length > 1 ? " cj-cartao--linha" : ""}`}>
          {p.faixa && <span class="dl-num cj-faixa">{p.faixa}</span>}
          {p.chips && <span class="cj-chips">{p.chips.map(([e, t]) => <span class="cj-chip" key={e}><Peca nome={e} escala={2} />{t && <b>{t}</b>}</span>)}</span>}
          <span class="cj-sprites">{p.sprites.map((k, j) => {
            const s = img(k, p.sprites.length > 1 ? 64 : 110);
            return <span class="cj-spr" key={k}>{s && <img class="dl-pix" src={s.url} width={s.w} height={s.h} alt="" />}
              {p.sprites.length > 1 && <small class="dl-tag dl-tag--estagio">{ROTULO_EST[j]}</small>}</span>;
          })}</span>
          <span class="cj-anel" aria-hidden="true" />
        </div>
        <h1 class="bv-tit cj-tit" id="cj-tit">{p.tit}</h1>
        <p class="cj-txt">{p.txt}</p>
        <span class="cj-pontos" aria-label={`página ${i + 1} de ${PAGINAS.length}`}>{PAGINAS.map((_, j) => <i key={j} class={j === i ? "on" : ""} />)}</span>
      </div>
      <div class="cj-pe">
        <button type="button" class="dl-btn dl-btn--largo" onClick={() => ultima ? ref.current?.close() : setI(i + 1)}>{ultima ? "Chocar meu ovo" : "Próximo"}</button>
      </div>
    </dialog>
  );
}
