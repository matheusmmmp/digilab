/* Cabecalho do pet (desenho UpPet): retrato, plaquinha com o nome do Digimon, nivel e relogio do jogo.
   Tudo derivado do motor na hora de desenhar. */
import { TICK_INICIAL, TPD, chaveSprite, nomeEstagio, nomeForma } from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import { Sprite } from "./Sprite.tsx";

export const hhmm = (t: number): string => { const m = t % TPD; return String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0"); };
export const diaDe = (t: number): number => Math.floor((t - TICK_INICIAL) / TPD) + 1;

export function Cabecalho() {
  const { motor } = useJogo(), f = motor.forma, nome = nomeForma(f);
  return (
    <header class="pet-cab dl-faixa" aria-label="Seu pet">
      <span class="pet-retrato"><Sprite nome={chaveSprite(f)} rotulo={nome} /></span>
      <span class="pet-cab-nome">
        <span class="dl-placa">{nome}</span>
        <span class="dl-tag dl-tag--estagio">{nomeEstagio(f)}</span>
        {motor.sombria && <span class="dl-tag dl-tag--sombria">sombria</span>}
      </span>
      <span class="dl-lcd pet-relogio">DIA {diaDe(motor.e.tick)} · {hhmm(motor.e.tick)}</span>
    </header>
  );
}
