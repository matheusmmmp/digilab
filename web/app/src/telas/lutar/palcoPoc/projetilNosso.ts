/* O projetil nosso (LUTA_POC, LP-8; docs/TAREFA_V3_LUTA_POC.md, secao 8): os golpes que sao de longe na serie, mas que nos dados do Digimon
   UP nao tem projetil (`proj: null`, o fogo aparece so no alvo). Pedido do Matheus (2026-11-08): "Eu quero que tenha realmente um projetil e
   va atacar e acertar o inimigo. Por exemplo, a rajada do Gabumon".

   Nesta etapa (LP3, so a tela) o projetil e do DESENHO: ele sai da boca de quem ataca no meio da preparacao do golpe e chega ao alvo no
   instante do golpe da simulacao (o `t` do golpe), quando o dano sai. A regra da luta (o alcance de quem atira, o voo que pode errar ou ser
   desviado) continua a do golpe corpo a corpo, porque a tela nao muda o resultado nem o log; mudar a regra e mexer no nucleo
   (motor/arena/formas.ts) e numa versao do pet, e fica registrado como pendencia (docs/registro/2026-11.md, LP3).

   O desenho: o proprio efeito de acerto do Digimon (o prefab do `hits`) voando, com o rastro e o brilho do elemento (E2); quando o efeito nao
   carrega, so a cabeca procedural do elemento (como a bola de fogo do Agumon no mapa AC). Puro (sem DOM). */

/** um golpe de longe sem projetil nos dados: o efeito que voa (o do acerto do proprio Digimon) */
export interface ProjetilNosso { digimon: string; golpe: string; prefab: string }

/** A lista curta (LP-8), pelo nome do Digimon na tabela da arena (FORMAS_ARENA[...].digimon). PROPOSTA, SEM FONTE alem da serie: so os
    golpes que, no anime, saem da boca ou da mao e cruzam a distancia ate o alvo. O Gabumon e o primeiro, pedido pelo Matheus. */
export const PROJETEIS_NOSSOS: Readonly<Record<string, ProjetilNosso>> = {
  Gabumon: { digimon: "Gabumon", golpe: "Petit Fire (Blue Blaster)", prefab: "Fx_Gabumon_Attack_Hit" },
  Garurumon: { digimon: "Garurumon", golpe: "Fox Fire (Howling Blaster)", prefab: "Fx_Garurumon_Attack_Hit" },
  MetalGarurumon: { digimon: "MetalGarurumon", golpe: "Metal Wolf Claw", prefab: "Fx_MetalGarurumon_Attack_Hit" },
  Angemon: { digimon: "Angemon", golpe: "Hand of Fate", prefab: "Fx_Angelmon_Attack_Hit" },
  Gargomon: { digimon: "Gargomon", golpe: "Gargo Laser", prefab: "Fx_Gargomon_Attack_Hit" },
};

/** o projetil nosso do Digimon (null: ele nao esta na lista) */
export const projetilNosso = (digimon: string): ProjetilNosso | null => PROJETEIS_NOSSOS[digimon] ?? null;

/** Quando o projetil nosso sai e quanto ele fica: sai na fracao `saida` da preparacao do golpe (do inicio do ataque ao instante do golpe) e
    chega ao alvo no instante do golpe; num golpe no ar segue reto por `passaPassos` passos e some. PROPOSTO, SEM FONTE: ajustar nas capturas */
export const VOO_NOSSO = { saida: .35, passaPassos: 8 } as const;
