/* Topo flutuante da casca (docs/TAREFA_V2_LAYOUT_HABITAT.md, M2), por cima do habitat em toda rota menos a luta em tela cheia: o retrato
   do pet (abre Meus pets), o logo, o relogio do jogo com o aviso de salvo e, so abaixo de 900 px, Conversar e Ajustes. O retrato, o
   relogio e o visual deles seguiam nos tokens --dl-*; desde o HUD (docs/TAREFA_V3_LAYOUT_HUD.md) a plaquinha e o relogio sao caixas
   escuras chanfradas (estilo/pet_hud.css), no mesmo sistema dos menus. Com a camera solta da ilha (telas/pet/cameraLivre.ts), o retrato
   volta a camera ao pet. */
import { BookOpen, Cloud, CloudOff, Coins, Lock, MessageCircle, Moon, Settings, Sprout, Sun, Swords, type LucideIcon } from "lucide-react";
import { DO_ESP, NOME_ESP, NOME_EST, TPD, eNoite, nomeEstagio, nomeForma } from "../../motor/index.ts";
import { BRASAO } from "../decoracao.ts";
import { sairDoLab, tamerAtual, useJogo } from "../jogo.ts";
import { usePainelLado } from "../desktop.ts";
import { alternarLeque, useLeque } from "../movel.ts";
import { NOME_DESTINO, type Destino } from "../rotas.ts";
import { SeloExperimental } from "../telas/config/Laboratorio.tsx";
import { Retrato, diaDe, hhmm, necessidadeMovel } from "../telas/pet/TelaPet.tsx";
import { dAbreDiario } from "../atalhosLugar.ts";
import { BotaoMovel } from "./BotaoMovel.tsx";
import { Deco } from "./Deco.tsx";
import { seguirPet, useCameraLivre } from "../telas/pet/cameraLivre.ts";
import { useNivel } from "../nivelTela.ts";
import { PECAS, nivelDaPeca, nivelDe, pecaAberta, pecaDoDestino, type Peca } from "../nivel.ts";

/** `lugar`: o menu do lugar aberto (L2 e L3): no celular, o icone dele na coluna fica em destaque */
interface PropsTopo { abrirMeusPets: () => void; irConversar: () => void; irDestino: (d: Destino) => void; abrirConfig: () => void; lugar?: Destino | null }

/** a partir de 900 px o topo de sempre; abaixo, o do mobile minimo (M1): o retrato e a hora, e a coluna dos destinos */
export function TopoHabitat(p: PropsTopo) { return usePainelLado() ? <TopoLargo {...p} /> : <TopoMovel {...p} />; }

const ICONE_DESTINO: Partial<Record<Destino, LucideIcon>> = { crescer: Sprout, lutar: Swords, diario: BookOpen };
/** o atalho de cada lugar; o D so vale quando nao e o "direita" do WASD da camera solta (atalhosLugar.ts) */
const atalhoLugar = (d: Destino): string | undefined => d === "crescer" ? "C" : d === "lutar" ? "L" : d === "diario" && dAbreDiario() ? "D" : undefined;
const DESTINOS_COLUNA: Destino[] = ["crescer", "lutar", "diario"];

/** o saldo de Bits do Tamer (docs/PLANO_V3_MOEDA.md, MO1), ao lado do relogio. Some com o registro do Tamer que nao abriu (o erro dele
    aparece em outro lugar) e antes do primeiro Bit, para o primeiro dia nao ganhar mais um numero na tela */
function SaldoBits({ classe }: { classe: string }) {
  const { erroTamer } = useJogo(), b = tamerAtual().bits;
  if (erroTamer || b < 1) return null;
  return (
    <span className={classe} role="img" aria-label={`${b} Bits`} title="Bits: a moeda do Tamer">
      <Coins aria-hidden="true" /><b aria-hidden="true">{b.toLocaleString("pt-BR")}</b>
    </span>
  );
}

/* O topo do celular (docs/PROPOSTAS_V3_UX_TELA_PET.md, "Mobile mínimo", M1; prancha em docs/pranchas/ux-mobile/): no canto de cima à esquerda o retrato
   (redondo no Vidro, reto no Militar), que abre o leque dos vitais e dos painéis (TelaPet.tsx, LequePet), com o ponto rosa quando há uma necessidade, e a
   hora; no canto de cima à direita a coluna Conversar, Crescer, Lutar e Diário, só ícone. Sem barra de abas: a tela Pet é a casa. O nome e o estágio do
   pet ficam no Meus pets e na Evolução; o "salvo" fica escondido e só o erro de gravação aparece (M1-12). */
function TopoMovel({ irConversar, irDestino, lugar }: PropsTopo) {
  const { motor: m, nascendo, erroSave } = useJogo(), ovo = nascendo > 0, e = m.e, aberto = useLeque() === "paineis", nec = necessidadeMovel(m, nascendo), nivel = useNivel();
  /* o menu trancado (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.4): o icone apagado, o cadeado com o "Nv N" ao lado e o marco no nome acessivel; o toque abre o cartao do motivo */
  const trancada = (d: Destino): Peca | null => { const p = pecaDoDestino(d); return p && !pecaAberta(nivel, p) ? p : null; };
  const rotuloTrancado = (d: Destino, p: Peca): string => `${NOME_DESTINO[d]}, trancado, Nv ${nivelDaPeca(p)}: ${PECAS[p].motivo}`;
  const nvTrancado = (p: Peca) => <span className="nivel-nv" aria-hidden="true"><Lock />Nv {nivelDaPeca(p)}</span>;
  const pc = trancada("conversar");
  return (
    <header className="mm-topo">
      <BotaoMovel className="mm-caixa mm-forma mm-bt mm-retrato" rotulo="Painéis do pet" lado="baixo" aria-label="Painéis do pet" aria-haspopup="true" aria-expanded={aberto} aria-controls="leque-pet"
        onClick={() => alternarLeque("paineis")}>
        <Retrato m={m} ovo={ovo} semArrastar />{nec && <span className="mm-ponto" aria-hidden="true" />}
      </BotaoMovel>
      <span className="mm-caixa mm-pilula mm-relogio" role="group" aria-label={`${hhmm(e.tick)}, dia ${diaDe(e.tick)}${erroSave ? ", não salva" : ""}`}>
        <small aria-hidden="true">D{diaDe(e.tick)}</small><b aria-hidden="true">{hhmm(e.tick)}</b>
        {erroSave && <CloudOff className="mm-salvo-erro" aria-hidden="true" />}
        <SaldoBits classe="mm-bits" />
      </span>
      <div className="mm-coluna">
        <span className="mm-item">
          <BotaoMovel className={"mm-caixa mm-forma mm-bt mm-bt48 topo-bt" + (pc ? " mm-bt--trancado" : "")} rotulo="Conversar" lado="esq" aria-label={pc ? rotuloTrancado("conversar", pc) : "Conversar"}
            aria-disabled={pc ? true : undefined} onClick={irConversar}><MessageCircle aria-hidden="true" /></BotaoMovel>
          {pc && nvTrancado(pc)}
        </span>
        <nav className="mm-destinos" aria-label="Destinos">
          {DESTINOS_COLUNA.map(d => {
            const I = ICONE_DESTINO[d]!, p = trancada(d);
            return (
              <span className="mm-item" key={d}>
                <BotaoMovel className={"mm-caixa mm-forma mm-bt mm-bt48" + (p ? " mm-bt--trancado" : "")} rotulo={NOME_DESTINO[d]} lado="esq" aria-current={lugar === d ? "page" : undefined}
                  aria-keyshortcuts={atalhoLugar(d)} {...(p ? { "aria-label": rotuloTrancado(d, p), "aria-disabled": true } : {})} onClick={() => irDestino(d)}><I aria-hidden="true" /></BotaoMovel>
                {p && nvTrancado(p)}
              </span>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

function TopoLargo({ abrirMeusPets, irConversar, abrirConfig }: PropsTopo) {
  const { motor: m, nascendo, erroSave, emLab } = useJogo(), ovo = nascendo > 0, e = m.e, noite = eNoite(e.tick % TPD), cam = useCameraLivre(), nivelTamer = nivelDe(useNivel());
  return (
    <header className="topo-hab">
      <div className="topo-pet">
        {/* com a camera solta (L1 de "Lugares da ilha", so a partir de 900 px), um toque no retrato volta a camera ao pet, como o F; senao, Meus pets */}
        {cam.solta
          ? <button type="button" className="topo-retrato" aria-label="Seguir o pet" aria-keyshortcuts="F" onClick={() => seguirPet()}><Retrato m={m} ovo={ovo} /></button>
          : <button type="button" className="topo-retrato" aria-haspopup="dialog" aria-label="Meus pets" onClick={abrirMeusPets}><Retrato m={m} ovo={ovo} /></button>}
        <span className="topo-pet-txt">
          <span className="topo-pet-nome"><b>{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</b></span>
          <span className="topo-pet-sub"><span className="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span>
            <span aria-hidden="true">·</span><Deco nome={BRASAO[m.especie].peca} largura={20} altura={13} alt="" />{NOME_ESP[m.especie]}
            {/* o nivel do Tamer (P-8): no desktop o retrato abre Meus pets direto (sem leque), entao o numero fica na plaquinha */}
            <span className="tamer-nv tamer-nv--topo" role="img" aria-label={`Tamer, nível ${nivelTamer}`}>Tamer Nv {nivelTamer}</span></span>
          {emLab && <span className="topo-lab"><SeloExperimental /><button type="button" className="topo-lab__volta" onClick={sairDoLab}>voltar ao meu pet</button></span>}
        </span>
      </div>
      {/* o encaixe da linha do agora (TelaPet, por portal): logo depois da plaquinha na ordem do DOM (a tabulacao segue o visual) e sem largura, para o logo e o relogio ficarem onde estao */}
      <span className="topo-agora" />
      <b className="topo-logo" aria-hidden="true"><span className="topo-logo-marca" />DIGILAB</b>
      <span className="topo-relogio" role="group" aria-label={`${hhmm(e.tick)}, dia ${diaDe(e.tick)}`}>
        {noite ? <Moon className="topo-sol" aria-hidden="true" /> : <Sun className="topo-sol" aria-hidden="true" />}
        <span className="topo-hora-txt"><span className="topo-dia">dia {diaDe(e.tick)}</span><span className="topo-hora">{hhmm(e.tick)}</span></span>
        <span className={`pet-salvo${erroSave ? " erro" : ""}`}>{erroSave ? <CloudOff aria-hidden="true" /> : <Cloud aria-hidden="true" />}{erroSave ? "não salva" : "salvo"}</span>
      </span>
      <SaldoBits classe="topo-bits" />
      <span className="topo-bts">
        <button type="button" className="topo-bt" aria-label="Conversar" onClick={irConversar}><MessageCircle aria-hidden="true" /></button>
        <button type="button" className="topo-bt" aria-label="Configurações" onClick={abrirConfig}><Settings aria-hidden="true" /></button>
      </span>
    </header>
  );
}
