/* Treinar (desenhos TreinoNormal, TreinoPausa, TreinoForcar; porte do HTML): cena com o pet, fadiga com as
   marcas 40 (pede pausa) e 60 (forcar), sobrecarga com 30 (aviso) e 60 (sombria), treinado na vida e os 6
   exercicios com o ganho de base e o selo de aptidao do brasao. Acima de 60 de fadiga o botao vira FORCAR,
   com confirmacao. */
import { useState } from "preact/hooks";
import {
  APTIDAO, CSO, CTR, NOME_ESP, NOME_EXERCICIO, NOME_STAT, STATS, chaveSprite, nomeForma, type Exercicio,
} from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { Seg, blocos, dec } from "../../componentes/Barras.tsx";
import { mudarMotor, useJogo } from "../../jogo.ts";

/* icones de treino do UP (hexagonos pintados, nao pixel art): 54 x 61 no botao, como pede o guia (secao 6) */
const ICONE_TREINO: Record<Exercicio, string> = { levantar_pedra: "treino_pedra", corrida: "treino_corrida", alvo: "treino_soco", esquiva: "treino_arrancada", meditar: "treino_cachoeira", resistencia: "treino_saco" };

function IconeTreino({ ex }: { ex: Exercicio }) {
  const a = useAtlas();
  if (a.tipo !== "ok") return null;
  return <img class="treino-ic" src={imagemAtlas(a, ICONE_TREINO[ex]).url} width={54} height={61} alt="" />;
}

export function TelaTreinar({ lutando = false }: { lutando?: boolean }) {
  const { motor: m, nascendo } = useJogo(), a = useAtlas(), [msg, setMsg] = useState("");
  const t = m.treino, bebe = m.estagioAtual === "bebe", pode = t.podeTocar(m.e.tick);
  const treinar = (ex: Exercicio) => {
    if (t.forcaria && !confirm(`Forçar ${NOME_EXERCICIO[ex].toLowerCase()}? Rende mais agora, mas gera ${CTR.sobreForcar} de sobrecarga${m.versao >= 2 ? " e derruba o vínculo" : ""}. Sobrecarga ${CSO.sombrio}+ na virada para Ultimate leva à forma sombria.`)) return;
    try {
      let texto = "";
      mudarMotor(mm => {
        const s = mm.treinar(ex);
        const g = Object.entries(s.ganho).map(([k, v]) => `+${dec(v as number, 2)} ${NOME_STAT[k as keyof typeof NOME_STAT] || k}`).join(", ");
        texto = s.enrolou ? "Ele enrolou: a sessão não rendeu." + (s.forcada ? " A sobrecarga entrou mesmo assim." : "")
          : `${s.forcada ? "Forçado: " : ""}${g || "sem ganho (teto atingido)"}.${mm.pausaTreino ? " Ele pediu pausa." : ""}`;
      });
      setMsg(texto);
    } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  const pet = a.tipo === "ok" && nascendo === 0 ? imagemAtlas(a, chaveSprite(m.forma)) : null;
  return (
    <div class="tela dl">
      <div class="treino-cab dl-card dl-hexcard">
        <span class="treino-pet">{pet && <img class="dl-pix" src={pet.url} width={pet.w} height={pet.h} alt={nomeForma(m.forma)} />}</span>
        {t.pedePausa ? <span class="dl-balao">pausa?</span> : <span class="dl-apoio">{bebe ? "O In-Training ainda não treina." : "pronto para treinar"}</span>}
      </div>
      <div class="dl-card treino-medidores">
        <div class="med">
          <span class="med-cab"><b>Fadiga</b><span class="dl-lcd">{t.fadiga.toFixed(0)} de 100</span></span>
          <Seg n={blocos(t.fadiga / 100, 10)} m={10} cls={t.forcaria ? "dl-seg--necessidade" : "dl-seg--acao"} marca={[CTR.limiarPausa / 10, CTR.limiteForcar / 10]} />
          <span class="med-marcas"><span>{CTR.limiarPausa}: pede pausa</span><span>{CTR.limiteForcar}: forçar</span></span>
          <span class="dl-apoio">{t.forcaria ? "Acima do limite: treinar agora é forçar." : t.pedePausa ? "Pedindo pausa." : "Treinar sobe a fadiga; ela cai com o tempo acordado e com o sono."}</span>
        </div>
        <div class="med">
          <span class="med-cab"><b>Sobrecarga</b><span class="dl-lcd">{t.sobrecarga.toFixed(0)} de 100</span></span>
          <Seg n={blocos(t.sobrecarga / 100, 10)} m={10} cls="dl-seg--sombrio" marca={[CSO.aviso / 10, CSO.sombrio / 10]} />
          <span class="med-marcas"><span>{CSO.aviso}: aviso</span><span>{CSO.sombrio}: forma sombria</span></span>
          <span class="dl-apoio">{t.sobrecarga >= CSO.sombrio ? "Na virada para Ultimate a forma vai ser sombria."
            : t.sobrecarga >= CSO.aviso ? `Aviso: com ${CSO.sombrio} ou mais na virada para Ultimate, a forma fica sombria.`
            : `Com ${CSO.sombrio} ou mais na virada para Ultimate, a forma fica sombria.`}</span>
        </div>
        <div class="med">
          <span class="med-cab"><b>Treinado na vida</b><span class="dl-lcd">+{dec(t.total, 1).replace(/,0$/, "")} de {CTR.tetoVida}</span></span>
          <span class="dl-apoio">{STATS.filter(k => t.pontos[k] > 0).map(k => `${NOME_STAT[k]} +${dec(t.pontos[k], 1)}`).join(", ") || "nada ainda"}</span>
        </div>
      </div>
      <div class="treino-grade">
        {(Object.keys(CTR.exercicios) as Exercicio[]).map(ex => {
          const [pri, sec] = CTR.exercicios[ex], apt = APTIDAO[m.especie][pri], des = bebe || !pode || lutando || nascendo > 0;
          return (
            <div class="dl-card treino-ex" key={ex}>
              {apt > 1 && <span class="treino-selo" title={`aptidão do brasão ${NOME_ESP[m.especie]}`}>{NOME_ESP[m.especie]} ×{dec(apt, 1)}</span>}
              <IconeTreino ex={ex} />
              <b>{NOME_EXERCICIO[ex]}</b>
              <span class="dl-apoio">+{CTR.ganhoPri} {NOME_STAT[pri]} · +{CTR.ganhoSec} {NOME_STAT[sec]}</span>
              {t.forcaria
                ? <button type="button" class="dl-btn dl-btn--forcar" disabled={des} aria-label={`Forçar ${NOME_EXERCICIO[ex]}: gera sobrecarga`} onClick={() => treinar(ex)}>FORÇAR<small>+ sobrecarga</small></button>
                : <button type="button" class="dl-btn" disabled={des} onClick={() => treinar(ex)}>Treinar</button>}
            </div>
          );
        })}
      </div>
      <p class="dl-apoio" aria-live="polite" style={{ margin: 0 }}>{msg}</p>
      <p class="dl-apoio" style={{ margin: 0 }}>{bebe ? "O In-Training ainda não treina." : !pode ? `Próximo treino em ${CTR.intervalo - (m.e.tick - t.ultimo!)} min de jogo.` : ""}</p>
      <p class="dl-apoio" style={{ margin: 0 }}>O ganho no card é o de base; a aptidão do brasão aumenta, e a fadiga e a proximidade do teto diminuem.</p>
      <details class="dl-apoio"><summary>Como o treino funciona</summary>
        <p>Um toque por sessão, com pelo menos 10 min entre elas. Cada exercício sobe um stat principal e um secundário (com a aptidão do brasão e retorno decrescente; tetos de +10 por stat e +36 na vida). A fadiga reduz o ganho e passa com o tempo acordado e com o sono; com fadiga 40 ele pede pausa. Com fadiga 60 o botão vira <b>Forçar</b>: rende mais, mas gera <b>sobrecarga</b>, que não some na evolução. Sobrecarga alta na virada para Ultimate leva à <b>forma sombria</b>. Cada ponto treinado vale 3 pontos de stat no combate. Na arena o treino muda o perfil (stats normalizados); na campanha vale o ganho inteiro.</p>
      </details>
    </div>
  );
}
