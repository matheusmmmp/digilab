/* O registro do WORLD-POC-01a (docs/futuro/mundo_3d.md, seção 4.1 e 5.1): por decisão, as cinco coisas separadas.
     1. a Intenção, do cérebro;
     2. a ação executada, do controlador (os ticks, a distância andada, por que parou);
     3. o resultado físico, a verdade do motor (as posições antes e depois, o que comeu, os empurrões, os contatos);
     4. a consequência no corpo de brinquedo (a fome e o tédio antes e depois);
     5. o que fica para o aprendizado: a Observação que o cérebro viu e o resultado percebido que ele verá na próxima.
   A verdade (2 a 4) fica aqui, para a análise; ao cérebro só vai a Observação. Exportável em JSON. */
import type { CorpoPoc, Intencao, Observacao, ParouPor, ResultadoPercebido } from "./tipos.ts";
import type { ContatoMundo } from "./mundo.ts";

export interface AcaoExecutada { ticks: number; distancia: number; parou_por: ParouPor }
export interface ResultadoFisico {
  pet_de: [number, number]; pet_para: [number, number]; bola_de: [number, number]; bola_para: [number, number];
  comeu: number; empurroes: number; contatos: ContatoMundo[];
}
export interface RegistroDecisao {
  n: number; tick: number;
  observacao: Observacao;
  intencao: Intencao;
  executada: AcaoExecutada;
  fisico: ResultadoFisico;
  corpo_antes: CorpoPoc; corpo_depois: CorpoPoc;
  percebido: ResultadoPercebido;
}
