/* Rotulos de tela (so texto; ids internos, log e save nao mudam). Pedido do Matheus, 2026-09-27: especie
   = brasao do Digimon Adventure, forma = nome do Digimon do mapa aprovado, estagio = nivel do Digimon.
   O motor usa nomeForma em um lugar: GambitsPet.linha, que entra na assinatura (paridade com o HTML). */
import { SOMBRIA } from "./constantes.ts";
import type { AcaoPet, Chamado, Especie, Estagio, Exercicio, FormaOuOvo, Stat, TracoCombate } from "./tipos.ts";

export const NOME_ESP: Record<Especie, string> = { brasa: "Coragem", cirro: "Amizade", ferrugem: "Conhecimento", limo: "Sinceridade" };
export const DO_ESP: Record<Especie, string> = { brasa: "da Coragem", cirro: "da Amizade", ferrugem: "do Conhecimento", limo: "da Sinceridade" };
/* forma (chave de sprite) -> [nome do Digimon, nivel]; mapa da Etapa 0 (Assets/catalogo_sprites_up.json) */
export const DIGIMON_DA_FORMA: Record<string, [string, string]> = {"brasa_bebe":["Koromon","In-Training"],"brasa_crianca_sereno":["Agumon","Rookie"],"brasa_crianca_arisco":["Guilmon","Rookie"],"brasa_adolescente_brigao":["Greymon","Champion"],"brasa_adulto_duelista":["MetalGreymon","Ultimate"],"brasa_adulto_furioso":["WarGreymon","Mega"],"brasa_adolescente_guardiao":["Kyubimon","Champion"],"brasa_adulto_espelho":["Taomon","Ultimate"],"brasa_adulto_muralha":["Sakuyamon","Mega"],"brasa_adolescente_cacador":["Birdramon","Champion"],"brasa_adulto_sentinela":["Garudamon","Ultimate"],"brasa_adulto_emboscador":["Phoenixmon","Mega"],"brasa_adolescente_colosso":["Growlmon","Champion"],"brasa_adulto_vigia":["WarGrowlmon","Ultimate"],"brasa_adulto_tita":["Gallantmon","Mega"],"cirro_bebe":["Tsunomon","In-Training"],"cirro_crianca_sereno":["Patamon","Rookie"],"cirro_crianca_arisco":["Gabumon","Rookie"],"cirro_adolescente_brigao":["Garurumon","Champion"],"cirro_adulto_duelista":["WereGarurumon","Ultimate"],"cirro_adulto_furioso":["MetalGarurumon","Mega"],"cirro_adolescente_guardiao":["Angemon","Champion"],"cirro_adulto_espelho":["MagnaAngemon","Ultimate"],"cirro_adulto_muralha":["Seraphimon","Mega"],"cirro_adolescente_cacador":["Aquilamon","Champion"],"cirro_adulto_sentinela":["Silphymon","Ultimate"],"cirro_adulto_emboscador":["Valkyrimon","Mega"],"cirro_adolescente_colosso":["Gatomon","Champion"],"cirro_adulto_vigia":["Angewomon","Ultimate"],"cirro_adulto_tita":["Magnadramon","Mega"],"ferrugem_bebe":["DemiVeemon","In-Training"],"ferrugem_crianca_sereno":["Armadillomon","Rookie"],"ferrugem_crianca_arisco":["Veemon","Rookie"],"ferrugem_adolescente_brigao":["ExVeemon","Champion"],"ferrugem_adulto_duelista":["Paildramon","Ultimate"],"ferrugem_adulto_furioso":["Imperialdramon Dragon Mode","Mega"],"ferrugem_adolescente_guardiao":["Ankylomon","Champion"],"ferrugem_adulto_espelho":["Shakkoumon","Ultimate"],"ferrugem_adulto_muralha":["SlashAngemon","Mega"],"ferrugem_adolescente_cacador":["Gargomon","Champion"],"ferrugem_adulto_sentinela":["Rapidmon","Ultimate"],"ferrugem_adulto_emboscador":["MegaGargomon","Mega"],"ferrugem_adolescente_colosso":["Kabuterimon","Champion"],"ferrugem_adulto_vigia":["MegaKabuterimon","Ultimate"],"ferrugem_adulto_tita":["HerculesKabuterimon","Mega"],"limo_bebe":["Tanemon","In-Training"],"limo_crianca_sereno":["Palmon","Rookie"],"limo_crianca_arisco":["Gomamon","Rookie"],"limo_adolescente_brigao":["Stingmon","Champion"],"limo_adulto_duelista":["DinoBeemon","Ultimate"],"limo_adulto_furioso":["Imperialdramon Fighter Mode","Mega"],"limo_adolescente_guardiao":["Togemon","Champion"],"limo_adulto_espelho":["Lillymon","Ultimate"],"limo_adulto_muralha":["Rosemon","Mega"],"limo_adolescente_cacador":["Seadramon","Champion"],"limo_adulto_sentinela":["MegaSeadramon","Ultimate"],"limo_adulto_emboscador":["MetalSeadramon","Mega"],"limo_adolescente_colosso":["Ikkakumon","Champion"],"limo_adulto_vigia":["Zudomon","Ultimate"],"limo_adulto_tita":["Vikemon","Mega"]};
export const NOME_ARQ: Record<string, string> = {
  sereno: "Sereno", arisco: "Arisco", brigao: "Brigão", guardiao: "Guardião", cacador: "Caçador", colosso: "Colosso",
  duelista: "Duelista", furioso: "Furioso", espelho: "Espelho", muralha: "Muralha", sentinela: "Sentinela", emboscador: "Emboscador",
  vigia: "Vigia", tita: "Titã", devastador: "Devastador", bastiao_rachado: "Bastião rachado", predador: "Predador", colosso_partido: "Colosso partido",
};
export const NOME_EST: Record<Estagio | "ovo", string> = { ovo: "Digi-Egg", bebe: "In-Training", crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate/Mega" };
export const NOME_STAT: Record<Stat, string> = { vigor: "vigor", folego: "fôlego", recuperacao: "recuperação", forca: "força", mira: "mira", guarda: "guarda" };
export const NOME_PET: Record<AcaoPet, string> = { ocioso: "à toa", dormir: "dormindo", comer: "comendo", brincar: "brincando", chamar_atencao: "chamando você", explorar: "explorando", emburrar: "emburrado" };
export const NOME_DONO: Record<string, string> = { atencioso: "atencioso", relapso: "relapso", aleatorio: "aleatório", incoerente: "incoerente" };
export const NOME_COMB: Record<TracoCombate, string> = { golpe: "Golpe", bloqueio: "Bloqueio", agarrao: "Agarrão", finta: "Finta", carga: "Carga" };
export const NOME_EXERCICIO: Record<Exercicio, string> = { levantar_pedra: "Levantar pedra", corrida: "Corrida", alvo: "Alvo", esquiva: "Esquiva", meditar: "Meditar", resistencia: "Resistência" };
export const NOME_CHAMADO: Record<Chamado, string> = { fome: "fome", higiene: "higiene", carinho: "carinho" };
export const OVO: Record<Especie, string> = { brasa: "ovo0", cirro: "ovo1", ferrugem: "ovo2", limo: "ovo3" };
export const NOME_V2: Record<string, string> = {
  avancar: "avançar", recuar: "recuar", golpe_rapido: "golpe rápido", preparar_pesado: "preparar pesado",
  disparo: "disparo", defender: "defender", esquivar: "esquivar", carregar: "carregar", pesado: "pesado",
  investida: "investida", contra_golpe: "contra-golpe", marcar: "marcar", pele_dura: "pele dura", fintar: "finta",
};
export const DESC_TECNICA: Record<string, string> = {
  investida: "médio, 20 guts: avança e acerta 8 no mesmo turno; esquivar não adianta; defender apara (sem dano e sem avanço)",
  contra_golpe: "perto, 15 guts: postura de defesa que devolve 50% do dano corpo a corpo (bruto)",
  marcar: "médio/longe, 10 guts: o próximo disparo em até 3 turnos dobra e ignora a redução da defesa",
  pele_dura: "20 guts: neste turno e no próximo, dano recebido pela metade e o preparo do pesado não é interrompido",
};
export const DESC_PASSIVA: Record<string, string> = {
  duelista: "pesado contra esquiva ainda causa 4 e devolve o guts do preparo",
  furioso: "abaixo de 50% de vida, corpo a corpo +25%; não pode defender",
  espelho: "contra-golpe em qualquer distância, e devolve 100% do disparo",
  muralha: "defender rende +3 guts extra",
  sentinela: "recuar vale mesmo se o oponente avança (a cada 4 turnos)",
  emboscador: "o primeiro disparo da luta causa o dobro",
  vigia: "vê o pesado do oponente um turno antes",
  tita: "pesado causa +30%",
  devastador: "sombria: corpo a corpo +30%; não pode defender nem esquivar; bate sem ler o rival", bastiao_rachado: "sombria: contra-golpe devolve 100%; defender não rende guts; não lê o rival",
  predador: "sombria: disparo +40%; não pode recuar; parte para cima sem ler o rival", colosso_partido: "sombria: pele dura dura 3 turnos; regenera 85% do guts",
};

/** chave de sprite da forma (a sombria usa o sprite da forma base) */
export function chaveSprite(f: FormaOuOvo): string {
  return f.est === "bebe" ? `${f.esp}_bebe` : f.est === "crianca" ? `${f.esp}_crianca_${f.ramo}`
    : f.est === "adolescente" ? `${f.esp}_adolescente_${f.linha}` : `${f.esp}_adulto_${SOMBRIA[f.adulta!] ? SOMBRIA[f.adulta!]!.base : f.adulta}`;
}
export function nomeForma(f: FormaOuOvo): string {
  if (f.est === "ovo") return "Digi-Egg " + DO_ESP[f.esp];
  const d = DIGIMON_DA_FORMA[chaveSprite(f)];
  if (!d) throw new Error("forma sem Digimon: " + chaveSprite(f));
  return SOMBRIA[f.adulta!] ? d[0] + " sombrio" : d[0];
}
/** nivel de uma forma: o adulto e Ultimate ou Mega conforme a forma (a sombria herda o da base) */
export function nomeEstagio(f: FormaOuOvo | null | undefined): string {
  if (!f || f.est === "ovo") return NOME_EST.ovo;
  if (f.est !== "adulto") return NOME_EST[f.est];
  const d = DIGIMON_DA_FORMA[chaveSprite(f)];
  if (!d) throw new Error("forma sem Digimon: " + chaveSprite(f));
  return d[1];
}
