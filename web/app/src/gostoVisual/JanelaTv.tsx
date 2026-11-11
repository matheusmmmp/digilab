/* A janela pequena da TV (docs/PLANO_UX_GOSTO_VISUAL.md, seções 3.3, 5.3 e 7.3; a prancha `janela_360`; a etapa 3 do código): a companhia
   quando o jogo sai de vista (UX-GV-1). Só o pet, a reação num balão, uma linha do gosto e dois botões: o Carinho do jogo (UX-GV-7) e o
   Parar. Sem barras, sem o porquê e sem rolagem: quem quer entender volta ao painel da TV (PainelTv.tsx).
   - o balão fica fora do elemento que espelha o pet: o "Não curtiu" não sai mais invertido (o problema 4 do plano);
   - o selo "Vendo a sua tela" aparece enquanto a tela do dono é lida (UX-GV-6); na TV do jogo, uma linha diz o programa;
   - a janela é sempre escura (a pele dos menus, tokens --hx-*), para não disputar com o que o dono assiste.
   A vista não tem estado próprio (o teste a renderiza no node); o hospedeiro (GostoVisual.tsx) a põe na janela flutuante
   (janelaPequena.ts). Só existe com `?gosto_visual=1`. Fora do motor, do log e do save, exceto o Carinho, que é o do jogo: o hospedeiro
   o grava pela porta de sempre das ações do dono e só onde o jogo aceita o toque no pet (`podeCarinho`). */
import { Hand, Square } from "lucide-react";
import { COMPONENTES, alvos, gostaMaisDe, type EstadoGosto, type Inato, type Reacao } from "./gosto.ts";
import { IMAGEM, PALAVRA_REACAO } from "./leituraGosto.ts";

export interface VistaJanela {
  /** o quadro do pet (data URL), ou null antes do primeiro */
  sprite: string | null;
  /** a reação mostrada (já com o mínimo de tempo do sinal, sinalTv.ts); null antes da primeira leitura */
  reacao: Reacao | null;
  inato: Inato;
  estado: EstadoGosto;
  /** de onde vem a imagem */
  origem: "tela" | "jogo";
  /** o programa da TV do jogo; null na tela do dono */
  programa: string | null;
  /** a captura tem som (sem ele, o grupo do som não entra na frase do gosto) */
  temSom: boolean;
  /** o nome da forma do pet (o do Digimon), para o texto alternativo */
  nome: string;
  /** o que o leitor de tela ouve (a reação, no ritmo do hospedeiro) */
  dito: string;
  erro: string | null;
  /** o jogo aceita o carinho agora (o mesmo critério do toque no pet: sem luta na tela, sem menu nem lugar aberto por cima da cena) */
  podeCarinho: boolean;
}

/** a janela pequena: o selo ou o programa, o palco com o balão e o pet, a linha do gosto e os dois botões */
export function JanelaDaTv({ v, carinho, parar }: { v: VistaJanela; carinho: () => void; parar: () => void }) {
  const quais = v.origem === "tela" && !v.temSom ? IMAGEM : COMPONENTES;
  return (
    <div className="jtv" data-testid="janela-tv">
      {v.erro && <p className="jtv-erro" role="alert" data-testid="janela-tv-erro">{v.erro}</p>}
      {v.origem === "tela"
        ? <p className="jtv-selo" data-testid="janela-tv-selo"><i aria-hidden="true" />Vendo a sua tela</p>
        : <p className="jtv-fraco" data-testid="janela-tv-passando">Passando: {v.programa ? `a TV do jogo, ${v.programa}` : "a TV do jogo"}</p>}
      <div className="jtv-palco">
        {v.reacao && <span className="jtv-balao" aria-hidden="true" data-testid="janela-tv-balao">{PALAVRA_REACAO[v.reacao]}</span>}
        <span className={"jtv-pet" + (v.reacao ? ` jtv-pet--${v.reacao}` : "")}>
          {v.sprite ? <img className="dl-pix jtv-sprite" src={v.sprite} alt={v.nome} /> : <span className="jtv-sprite jtv-sprite--vazio" role="img" aria-label={v.nome} />}
        </span>
      </div>
      <p className="sr-only" role="status" data-testid="janela-tv-status">{v.dito}</p>
      <p className="jtv-gosto" data-testid="janela-tv-gosto">Gosta mais de: {gostaMaisDe(alvos(v.inato, v.estado), quais)}.</p>
      {!v.podeCarinho && <p className="jtv-fraco" id="jtv-sem-carinho" data-testid="janela-tv-sem-carinho">O carinho volta quando o jogo estiver na tela do pet.</p>}
      <div className="jtv-bts">
        <button type="button" className="hx-continuar" data-janela-tv-carinho="" disabled={!v.podeCarinho} aria-describedby={v.podeCarinho ? undefined : "jtv-sem-carinho"}
          onClick={carinho}><Hand aria-hidden="true" />Carinho</button>
        <button type="button" className="hx-btn" onClick={parar}><Square aria-hidden="true" />Parar</button>
      </div>
    </div>
  );
}
