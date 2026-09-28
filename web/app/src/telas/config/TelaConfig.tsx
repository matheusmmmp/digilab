/* Configuracoes (pranchas CfgPrincipal, CfgAparencia, CfgFala, CfgDados, CfgSobre): lista por grupo (Jogo, Fala, Dados,
   Sobre); cada linha abre o seu painel ali mesmo. Aparencia = tema; Fala = modo e estado do modelo; Registro e replay =
   resumo e atalho para o Diario; Tempo (teste) = velocidade e +1 h (saiu da tela Pet). Nada aqui muda o pet, a nao ser o
   tempo de teste, que passa pelo motor como o tempo normal. */
import type { ComponentChildren } from "preact";
import { Peca } from "../../componentes/Imagens.tsx";
import { Deco } from "../../decoracao.tsx";
import { rotuloLLM, useFalaLLM } from "../../fala.ts";
import { escolherModo, useFalaLivre, type ModoFala } from "../../falaLivre.ts";
import { useJogo } from "../../jogo.ts";
import { NOME_TEMA, escolherTema, useTema, type Tema } from "../../tema.ts";
import { VELOCIDADES, escolherVelocidade, pularUmaHora, useTempo } from "../../tempo.ts";

const MODOS: [ModoFala, string][] = [["template", "Frases prontas"], ["moldura", "Moldura"], ["livre", "Livre"]];
const NOME_MODO: Record<ModoFala, string> = { template: "frases prontas", moldura: "modo moldura", livre: "modo livre" };

function Item({ icone, titulo, sub, teste, cls = "", children }: { icone: ComponentChildren; titulo: string; sub: string; teste?: boolean; cls?: string; children: ComponentChildren }) {
  return (
    <details class={`cfg-item ${cls}`}>
      <summary><span class="cfg-ic">{icone}</span><span class="cfg-txt"><b>{titulo}{teste && <span class="dl-tag dl-tag--estagio">TESTE</span>}</b><span>{sub}</span></span><span class="cfg-seta" aria-hidden="true">›</span></summary>
      <div class="cfg-painel">{children}</div>
    </details>
  );
}
/** escolhe o tema direto (Auto, Claro, Escuro); a preferencia fica na chave propria do tema */
function EscolhaTema() {
  const tema = useTema();
  return (
    <div class="cfg-opcoes" role="group" aria-label="Tema">
      {(["sistema", "claro", "escuro"] as Tema[]).map(t => <button type="button" key={t} class="dl-chip" aria-pressed={tema === t} onClick={() => escolherTema(t)}>{NOME_TEMA[t]}</button>)}
      <div class="cfg-item cfg-item--off" aria-disabled="true"><span class="cfg-ic">🔈</span><span class="cfg-txt"><b>Som</b><span>o jogo ainda não tem som (proposta)</span></span></div>
    </div>
  );
}

export function TelaConfig({ irRegistro, irConversar }: { irRegistro: () => void; irConversar: () => void }) {
  const { motor: m } = useJogo(), tema = useTema(), fl = useFalaLivre(), llm = useFalaLLM(), { velocidade } = useTempo(), r = rotuloLLM();
  const vel = VELOCIDADES.find(([, v]) => v === velocidade)?.[0] ?? "pausado";
  return (
    <div class="tela dl cfg-tela">
      <span class="cfg-grupo">JOGO</span>
      <Item icone={<Deco nome="Growth_Guide_Icon_10" w={34} h={34} reserva={<Peca nome="emoji_estrela" escala={2} />} />} titulo="Aparência" sub={`tema ${NOME_TEMA[tema].toLowerCase()}`}>
        <EscolhaTema />
        <p class="dl-apoio">Tamanho do texto e movimento reduzido ainda não existem no app (o movimento segue a preferência do sistema).</p>
      </Item>
      <Item icone={<Deco nome="Growth_Guide_Icon_05" w={34} h={34} reserva={<Peca nome="emoji_surpreso" escala={2} />} />} titulo="Dicas" sub="ainda não existem no app">
        <p class="dl-apoio">As dicas da primeira vez (chamado, ensino, navegação) ainda não foram feitas.</p>
      </Item>
      <span class="cfg-grupo">FALA</span>
      <Item icone={<Peca nome="emoji_joinha" escala={2} />} titulo="Fala do pet" sub={`${NOME_MODO[fl.modo]} · ${r.texto}`}>
        <div class="cfg-opcoes" role="group" aria-label="Modo da fala">
          {MODOS.map(([k, rot]) => <button type="button" key={k} class="dl-chip" aria-pressed={fl.modo === k} onClick={() => escolherModo(k)}>{rot}</button>)}
        </div>
        <p class="dl-apoio">{llm.ativo ? r.titulo : "Sem o servidor local, o pet fala por frases prontas; nada do jogo depende disso."}</p>
        <button type="button" class="dl-btn dl-btn--sec" onClick={irConversar}>Abrir a conversa</button>
      </Item>
      <span class="cfg-grupo">DADOS</span>
      <Item icone={<Deco nome="Growth_Guide_Icon_09" w={26} h={34} reserva={<Peca nome="emoji_nota" escala={2} />} />} titulo="Registro e replay" sub={`semente ${m.semente} · ${m.log.length} eventos`}>
        <p class="dl-apoio">O estado do pet nunca é salvo: só o registro, e a vida é refeita a partir dele.</p>
        <button type="button" class="dl-btn dl-btn--sec" onClick={irRegistro}>Abrir o registro</button>
      </Item>
      <Item icone={<Deco nome="Growth_Guide_Icon_11" w={34} h={34} reserva={<Peca nome="icone_tempo" />} />} titulo="Tempo" teste cls="tempo-teste" sub={vel}>
        <div class="tempo-pet" role="group" aria-label="Velocidade do tempo">
          {VELOCIDADES.map(([rot, v, dica]) => (
            <button type="button" key={rot} class="dl-btn dl-btn--sec" aria-pressed={velocidade === v} title={dica} onClick={() => escolherVelocidade(v)}>{rot}</button>
          ))}
          <button type="button" class="dl-btn dl-btn--sec" onClick={pularUmaHora}>+1 h</button>
        </div>
      </Item>
      <span class="cfg-grupo">SOBRE</span>
      <Item icone={<Deco nome="Common_Icon_Setting" w={34} h={34} reserva="⚙" />} titulo="Sobre o Digilab" sub="versão, créditos e uso pessoal">
        <p class="dl-apoio">Motor do Digilab em TypeScript: mesmas regras e parâmetros de <code>config.py</code>. O gerador aleatório é outro, então os resultados não batem bit a bit com os artefatos de pesquisa em Python.</p>
        <p class="dl-apoio"><b>Versão local com sprites do Digimon UP (Bandai), só para uso pessoal. Não publicar nem distribuir.</b></p>
        <p class="dl-apoio"><a class="cfg-link" href="../digilab_sprites.html?antigo=1">Versão antiga (HTML)</a>: mesmo save; não abra as duas ao mesmo tempo no mesmo pet.</p>
      </Item>
      <div class="cfg-item cfg-item--off" aria-disabled="true"><span class="cfg-ic">🔈</span><span class="cfg-txt"><b>Som</b><span>o jogo ainda não tem som (proposta)</span></span></div>
    </div>
  );
}
