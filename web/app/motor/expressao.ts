/* Expressao por estagio (espelho de digilab/expressao.py). So templates: a fala nunca decide nada e
   nunca inventa causa, so cita fatores do motivo. Cada fator tem um marcador unico; a carga do modulo
   confere cobertura, bebe sem causa e marcadores unicos (falha alto).
   Estagio da fala: o estagio da evolucao (bebe, crianca, adolescente, adulto). */
import { ACOES_PET, CDJ, EIXOS_TEMP, FATORES_ESPACOS } from "./constantes.ts";
import { CATALOGO_V2 } from "./combate.ts";
import { ESTADOS_CONFIANCA, type EstadoConfianca } from "./confianca.ts";
import type { Emocao } from "./memoria.ts";
import { FATOR_DA_FEATURE } from "./motivo.ts";
import type { CategoriaMemoria } from "./constantes.ts";
import type { Desejo, Estagio, EstagioBase, Motivo, Temperamento } from "./tipos.ts";
import { baseDe } from "./constantes.ts";

type TextoPorEstagio = { marcador: string; bebe: string; crianca: string; adolescente: string; adulto: string };

export const EMOCAO_TXT: Record<string, [string, string, string]> = {
  raiva: ["raiva", "(>_<)#", "Senti raiva"], tristeza: ["tristeza", "(T.T)", "Senti tristeza"], incomodo: ["incômodo", "(-_-;)", "Senti incômodo"],
  ferido: ["ferido", "(;_;)!", "Fiquei ferido"], desdem: ["desdém", "(-.-)z", "Senti desdém"], vergonha: ["vergonha", "(>///<)", "Senti vergonha"],
  euforia: ["euforia", "(^o^)//", "Senti euforia"], indiferenca: ["indiferença", "(._.)~", "Senti indiferença"], orgulho: ["orgulho", "(^_^)v", "Senti orgulho"],
  ternura: ["ternura", "(^3^)", "Senti ternura"], timidez: ["timidez", "(//_//)", "Senti timidez"], alegria: ["alegria", "(^v^)", "Senti alegria"],
};
export const CAUSA_EMOCAO: Record<CategoriaMemoria, string> = { demora: "quando você demorou", bronca: "quando você brigou comigo", elogio: "quando você falou bem de mim", carinho: "quando você me deu atenção" };
export function expressarEmocao(em: Emocao, cat: CategoriaMemoria, est0: Estagio, ref: number | null | undefined): string {
  const est = baseDe(est0);   /* o Mega (pets v5) fala como o adulto */
  const [pal, emote, adulto] = EMOCAO_TXT[em.nome];
  if (est === "bebe") return emote;
  if (est === "crianca") return `[${pal}]`;
  if (est === "adolescente") return `${pal}...`;
  return `${adulto} ${CAUSA_EMOCAO[cat]}${ref != null ? " (lembro do evento #" + ref + ")" : ""}.`;
}

export const ESTAGIOS_FALA: readonly Estagio[] = ["bebe", "crianca", "adolescente", "adulto"];
export const NOME_ESTAGIO_FALA: Record<Estagio, string> = { bebe: "In-Training", crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate", mega: "Mega" };
export const GENERICO_ADULTO = "Não sei, só quis.";
/* vida sem fator e sem exploracao: quem decidiu foi o prior do instinto (espelho de expressao.py, 2026-09-29) */
export const GENERICO_INSTINTO = "Foi instinto: é o meu jeito.";
const F = (marcador: string, adulto: string): TextoPorEstagio => ({ marcador, bebe: "", crianca: `[:${marcador}:]`, adolescente: `${marcador}...`, adulto });
export const FATORES_TXT: Record<string, TextoPorEstagio> = {
  habito: F("costume", "por costume"),
  fome: F("fome", "por causa da fome"),
  higiene: F("higiene", "por causa da higiene"),
  energia: F("cansaço", "por causa do cansaço"),
  humor: F("humor", "por causa do meu humor"),
  saude: F("saúde", "por causa da saúde"),
  sujeira: F("sujeira", "por causa da sujeira"),
  dormindo: F("sono", "porque eu estava com sono"),
  hora: F("hora do dia", "por causa da hora do dia"),
  tempo_sem_cuidado: F("sem cuidado", "porque fiquei muito tempo sem cuidado"),
  latencia_fome: F("demorou com a comida", "porque você demorou com a comida da última vez"),
  latencia_higiene: F("demorou para me limpar", "porque você demorou para me limpar da última vez"),
  repreensoes: F("bronca", "por causa das broncas recentes"),
  elogios: F("elogio", "por causa dos elogios recentes"),
  sempre: F("sempre faço", "porque sempre faço isso"),
  distancia_eh: F("distância", "porque a distância era {p0}"),
  hp_proprio_abaixo: F("machucado", "porque eu estava machucado (menos de {p0} da vida)"),
  guts_proprio_abaixo: F("exausto", "porque eu estava exausto (guts abaixo de {p0})"),
  guts_proprio_acima: F("folga de guts", "porque eu tinha folga de guts ({p0} ou mais)"),
  oponente_preparando: F("você ia usar o golpe pesado", "porque você ia usar o golpe pesado"),
  oponente_hp_abaixo: F("você estava fraco", "porque você estava fraco (menos de {p0} da vida)"),
  oponente_guts_abaixo: F("você estava sem guts", "porque você estava sem guts (abaixo de {p0})"),
  oponente_repete: F("você repetiu", "porque você repetiu '{p0}' {p1} vezes"),
  oponente_frequente: F("você insiste", "porque você insiste em '{p0}'"),
  turno_execucao: F("luta longa", "porque já era uma luta longa (turno {p0} ou mais)"),
  oponente_vai_preparar: F("vi o pesado vindo", "porque vi o pesado vindo antes de você preparar"),
  executando_pesado: F("hora do pesado", "porque era a hora do pesado"),
  /* memoria por espacos */
  demora: F("me deixou esperando", "porque lembro que você me deixou esperando"),
  bronca: F("repreensão", "porque lembro da sua repreensão"),
  elogio: F("parabéns", "porque lembro dos seus parabéns"),
  carinho: F("carinho", "porque lembro do seu carinho"),
  /* desobediencia: termo de maior contribuicao negativa na obediencia */
  vinculo_baixo: F("não confio", "porque ainda não confio em você"),
  teimosia: F("teimoso", "porque eu sou teimoso"),
  necessidade_fome: F("barriga vazia", "porque eu estava de barriga vazia"),
  necessidade_higiene: F("todo sujo", "porque eu estava todo sujo"),
  necessidade_energia: F("sem forças", "porque eu estava sem forças"),
  necessidade_humor: F("chateado", "porque eu estava chateado"),
  fadiga_treino: F("treino puxado", "por causa do treino puxado"),
};
export const ACOES_VIDA_TXT: Record<string, [string, string, string]> = {
  ocioso: ["[à toa]", "à toa", "Fiquei à toa"], dormir: ["[dormir]", "dormir", "Dormi"], comer: ["[comer]", "comer", "Comi"],
  brincar: ["[brincar]", "brincar", "Brinquei"], chamar_atencao: ["[chamar]", "chamar", "Chamei você"],
  explorar: ["[explorar]", "explorar", "Explorei"], emburrar: ["[emburrar]", "emburrar", "Emburrei"],
  recusar: ["[não!]", "não quero", "Não quis fazer o que você pediu"],
  fazer_outra: ["[outra coisa]", "outra coisa", "Fiz outra coisa em vez do que você pediu"],
  forcar_treino: ["[forçado]", "forçado", "Treinei além do meu limite"],
  treinar_cansado: ["[sem pausa]", "sem pausa", "Treinei mesmo pedindo para parar"],
  enrolar: ["[enrolei]", "enrolei", "Enrolei no treino"],
};
export const ACOES_V2_TXT: Record<string, [string, string, string]> = {
  avancar: ["[avançar]", "avançar", "Avancei"], recuar: ["[recuar]", "recuar", "Recuei"], golpe_rapido: ["[golpe]", "golpe", "Dei um golpe rápido"],
  preparar_pesado: ["[preparar]", "preparar", "Preparei o pesado"], disparo: ["[disparo]", "disparo", "Disparei"],
  defender: ["[defender]", "defender", "Defendi"], esquivar: ["[esquivar]", "esquivar", "Esquivei"], carregar: ["[carregar]", "carregar", "Carreguei guts"],
  pesado: ["[pesado!]", "pesado!", "Soltei o pesado que eu tinha preparado"],
  investida: ["[investida]", "investida", "Investi"], contra_golpe: ["[contra]", "contra-golpe", "Fiz o contra-golpe"],
  marcar: ["[marcar]", "marcar", "Marquei você"], pele_dura: ["[pele dura]", "pele dura", "Endureci a pele"],
  fintar: ["[finta]", "finta", "Fintei em vez de soltar o pesado"],
};
export const REACAO_BEBE: Record<string, string> = {
  avancar: "(o_o)>", recuar: "<(o_o)", golpe_rapido: "(>_<)!", preparar_pesado: "(ò_ó)...", disparo: "(>_<)~",
  defender: "(-_-)#", esquivar: "(^o^)~", carregar: "(ò_ó)*", pesado: "(ò_ó)!!",
  investida: "(ò_ó)>>", contra_golpe: "(ò_ó)|", marcar: "(o_o)+", pele_dura: "(-_-)[]", fintar: "(¬‿¬)!",
};
export const EMOTE_HUMOR = ["(T_T)", "(-_-)", "(^_^)"];

export function validarTabelasFala(obrigatorios: readonly string[]): void {
  const falta = obrigatorios.filter(f => !FATORES_TXT[f]);
  if (falta.length) throw new Error("fatores sem texto: " + falta.join(", "));
  const marc = Object.entries(FATORES_TXT).map(([n, e]) => [n, e.marcador] as const);
  for (const [n, e] of Object.entries(FATORES_TXT)) {
    if (e.bebe !== "") throw new Error(`fator ${n}: bebê não pode citar causa`);
    for (const est of ["crianca", "adolescente", "adulto"] as const) {
      if (!e[est].includes(e.marcador)) throw new Error(`fator ${n}/${est} sem marcador`);
      for (const [n2, m2] of marc) if (n2 !== n && e[est].includes(m2)) throw new Error(`marcador de ${n2} aparece no texto de ${n}`);
    }
  }
  const fixos = [...Object.values(ACOES_VIDA_TXT).flat(), ...Object.values(ACOES_V2_TXT).flat(), ...Object.values(REACAO_BEBE), ...EMOTE_HUMOR, GENERICO_ADULTO, GENERICO_INSTINTO];
  for (const [n, m] of marc) for (const t of fixos) if (t.includes(m)) throw new Error(`marcador de ${n} aparece em texto fixo ${t}`);
  for (const a of ACOES_PET) if (!ACOES_VIDA_TXT[a]) throw new Error("acao de vida sem texto: " + a);
}

/* temperamento e desejo na fala (espelho de expressao.py: TOM_TEMPERAMENTO, DESEJO_TIPO, ALVOS_DESEJO).
   Mesma regra de marcador unico: so cita eixo com |valor| >= limiar e so a necessidade do calculo. */
const TOM = (marcador: string, bebe: string, adulto: string): TextoPorEstagio => ({ marcador, bebe, crianca: `[:${marcador}:]`, adolescente: `${marcador}...`, adulto });
export const TOM_TEMPERAMENTO: Record<string, TextoPorEstagio> = {
  "curiosidade+": TOM("fuçador", "(o.o)?", "Nasci fuçador, sempre atrás de novidade."),
  "curiosidade-": TOM("cauteloso", "(._.)", "Nasci cauteloso com o que não conheço."),
  "teimosia+": TOM("cabeça-dura", "(¬_¬)", "Nasci cabeça-dura."),
  "teimosia-": TOM("dócil", "(u_u)", "Nasci dócil, fácil de convencer."),
  "sensibilidade+": TOM("derretido", "(*^_^*)", "Nasci derretido com qualquer agrado."),
  "sensibilidade-": TOM("melindroso", "(;_;)", "Nasci melindroso com qualquer reclamação."),
  "rancor+": TOM("guardo mágoa", "(ò_ó)", "Nasci assim: guardo mágoa por muito tempo."),
  "rancor-": TOM("esqueço rápido", "(^o^)", "Nasci assim: esqueço rápido o que passou."),
};
export const TEMPERAMENTO_NEUTRO_TXT: Record<EstagioBase, string> = { bebe: "(o_o)", crianca: "[~]", adolescente: "...", adulto: "Nasci sem nada que se destaque." };
export const DESEJO_TIPO: Record<"necessidade" | "vontade", { marcador: string; crianca: string; adolescente: string; adulto: string }> = {
  necessidade: { marcador: "preciso", crianca: "[preciso!]", adolescente: "preciso", adulto: "Eu preciso" },
  vontade: { marcador: "queria", crianca: "[queria?]", adolescente: "queria", adulto: "Eu queria" },
};
export const DESEJO_BEBE = "(>o<)", VONTADE_ADULTO = "é o que mais deu certo até agora";
export const ALVOS_DESEJO: Record<string, [string, string]> = {
  comer: ["[comer]", "comer"], limpar: ["[banho]", "tomar banho"], dormir: ["[dormir]", "dormir"],
  brincar: ["[brincar]", "brincar"], ocioso: ["[à toa]", "ficar à toa"], chamar_atencao: ["[chamar]", "chamar você"],
  explorar: ["[explorar]", "explorar"], emburrar: ["[emburrar]", "emburrar"], descansar: ["[descanso]", "descansar"],
};
export function eixosMarcantes(t: Temperamento): string[] {
  return EIXOS_TEMP.map((e, i) => [Math.abs(t[e]), -i, e] as const).sort((a, b) => b[0] - a[0] || b[1] - a[1])
    .filter(([v]) => v >= CDJ.limiarTom).map(([, , e]) => e + (t[e] > 0 ? "+" : "-"));
}
export function expressarTemperamento(t: Temperamento, est0: Estagio): string {
  const est = baseDe(est0);
  const mk = eixosMarcantes(t);
  if (!mk.length) return TEMPERAMENTO_NEUTRO_TXT[est];
  if (est === "adulto") return mk.slice(0, 2).map((k, i) => i ? "E n" + TOM_TEMPERAMENTO[k].adulto.slice(1) : TOM_TEMPERAMENTO[k].adulto).join(" ");
  return TOM_TEMPERAMENTO[mk[0]][est];
}
export function expressarDesejo(d: Desejo, est0: Estagio): string {
  const est = baseDe(est0);
  if (!ALVOS_DESEJO[d.alvo]) throw new Error("alvo de desejo sem texto: " + d.alvo);
  if (est === "bebe") return DESEJO_BEBE;
  const [ic, verbo] = ALVOS_DESEJO[d.alvo], t = DESEJO_TIPO[d.tipo];
  if (est === "crianca") return `${t.crianca} ${ic}`;
  if (d.tipo === "necessidade") return est === "adolescente" ? `${t.adolescente} ${verbo}... ${textoFator(d.causa!, est)}` : `${t.adulto} ${verbo} ${textoFator(d.causa!, est)}.`;
  return est === "adolescente" ? `${t.adolescente} ${verbo}...` : `${t.adulto} ${verbo}: ${VONTADE_ADULTO}.`;
}
/* confianca de combate (M1, espelho de expressao.CONFIANCA_TXT): estado derivado das lutas, nao e causa de decisao.
   Bebe so emote, crianca a versao curta, adolescente o fragmento, adulto a frase; "neutro" nao tem frase. */
export const CONFIANCA_TXT: Record<Exclude<EstadoConfianca, "neutro">, TextoPorEstagio> = {
  confiante: { marcador: "confiante", bebe: "(^o^)b", crianca: "[:confiante:] Ganhei!", adolescente: "confiante... ganhei as últimas", adulto: "Tô confiante: ganhei as últimas." },
  inseguro: { marcador: "inseguro", bebe: "(;_;)?", crianca: "[:inseguro:] Perdi de novo…", adolescente: "inseguro... depois daquelas derrotas", adulto: "Ando inseguro depois daquelas derrotas." },
  entediado: { marcador: "sei tudo dele", bebe: "(-.-)~", crianca: "[:sei tudo dele:] De novo?", adolescente: "de novo esse aí... sei tudo dele", adulto: "De novo esse aí? Já sei tudo dele." },
};
/** frase de estado da confianca (M1): null no neutro. O "porque" sao as lutas em VistaConfianca.lutas */
export function expressarConfianca(estado: EstadoConfianca, est0: Estagio): string | null {
  const est = baseDe(est0);
  if (estado === "neutro") return null;
  const e = CONFIANCA_TXT[estado];
  if (!e) throw new Error("estado de confiança sem texto: " + estado);
  return e[est];
}
export function validarTabelasPersonalidade(): void {
  for (const e of EIXOS_TEMP) for (const p of "+-") if (!TOM_TEMPERAMENTO[e + p]) throw new Error("eixo sem tom: " + e + p);
  for (const s of ESTADOS_CONFIANCA) if (s !== "neutro" && !CONFIANCA_TXT[s]) throw new Error("estado de confiança sem texto: " + s);
  if (new Set(Object.values(CONFIANCA_TXT).map(e => e.bebe)).size !== Object.keys(CONFIANCA_TXT).length) throw new Error("emotes de confiança repetidos");
  const marc = [...Object.entries(FATORES_TXT).map(([n, e]) => ["fator " + n, e.marcador] as const),
    ...Object.entries(TOM_TEMPERAMENTO).map(([k, e]) => ["tom " + k, e.marcador] as const), ...Object.entries(DESEJO_TIPO).map(([k, e]) => ["desejo " + k, e.marcador] as const),
    ...Object.entries(CONFIANCA_TXT).map(([k, e]) => ["confianca " + k, e.marcador] as const)];
  const textos = [...Object.entries(TOM_TEMPERAMENTO).map(([k, e]) => ["tom " + k, [e.crianca, e.adolescente, e.adulto]] as const),
    ...Object.entries(DESEJO_TIPO).map(([k, e]) => ["desejo " + k, [e.crianca, e.adolescente, e.adulto]] as const),
    ...Object.entries(CONFIANCA_TXT).map(([k, e]) => ["confianca " + k, [e.crianca, e.adolescente, e.adulto]] as const),
    ...Object.entries(FATORES_TXT).map(([n, e]) => ["fator " + n, [e.crianca, e.adolescente, e.adulto]] as const)];
  for (const [dono, ts] of textos.filter(([d]) => !d.startsWith("fator"))) {
    const m = marc.find(([d]) => d === dono)![1];
    if (!ts.every(t => t.includes(m))) throw new Error(`${dono}: texto sem o marcador`);
  }
  const fixos = [...Object.values(TEMPERAMENTO_NEUTRO_TXT), DESEJO_BEBE, VONTADE_ADULTO, ...Object.values(ALVOS_DESEJO).flat()];
  for (const [dono, m] of marc) {
    for (const [outro, ts] of textos) if (outro !== dono && !(dono.startsWith("fator") && outro.startsWith("fator")) && ts.some(t => t.includes(m)))
      throw new Error(`marcador ${m} de ${dono} aparece no texto de ${outro}`);
    for (const t of fixos) if (t.includes(m)) throw new Error(`marcador ${m} de ${dono} aparece em texto fixo ${t}`);
  }
  for (const a of ACOES_PET) if (!ALVOS_DESEJO[a]) throw new Error("acao sem texto de desejo: " + a);
}
export function paramsFator(f: string): string[] {
  if (!f.includes("(")) return [];
  return f.slice(f.indexOf("(") + 1, -1).split(",").map(p => { const n = Number(p); return p !== "" && !isNaN(n) && n > 0 && n < 1 ? `${Math.round(n * 100)}%` : p.replace(/_/g, " "); });
}
export function textoFator(f: string, est: "crianca" | "adolescente" | "adulto"): string {
  const base = f.split("(")[0], e = FATORES_TXT[base];
  if (!e) throw new Error("fator sem texto: " + base);
  const ps = paramsFator(f); return e[est].replace(/\{p(\d)\}/g, (_, i) => ps[Number(i)]);
}
/** refs: numeros ja convertidos (indice de evento na vida; turno no combate) */
export function expressar(mot: Motivo, est0: Estagio, refs?: readonly number[] | null): string {
  const est = baseDe(est0);
  const [ic, pal, fr] = (mot.origem === "vida" ? ACOES_VIDA_TXT : ACOES_V2_TXT)[mot.acao];
  const fat = mot.exploracao ? [] : mot.fatores;
  const humor = mot.origem === "vida" ? mot.humor : 0;
  if (est === "bebe") return mot.origem === "vida" ? EMOTE_HUMOR[humor >= .66 ? 2 : humor >= .33 ? 1 : 0] : REACAO_BEBE[mot.acao];
  if (est === "crianca") {
    if (fat.length) return `${ic} ${textoFator(fat[0], est)}`;
    /* sem causa: acao + humor (vida) ou reacao (luta). Humor e estado, nao causa. */
    return `${ic} ${mot.origem === "vida" ? EMOTE_HUMOR[humor >= .66 ? 2 : humor >= .33 ? 1 : 0] : REACAO_BEBE[mot.acao]}`;
  }
  if (est === "adolescente") return `${pal}... ` + (fat.length ? textoFator(fat[0], est) : "");
  if (!fat.length) return `${fr}. ${mot.origem === "vida" && !mot.exploracao ? GENERICO_INSTINTO : GENERICO_ADULTO}`;
  const causas = fat.slice(0, 2).map(f => textoFator(f, "adulto")).join(" e ");
  const r = refs && refs.length ? (mot.origem === "vida" ? " (lembro do evento #" + refs.join(", #") + ")" : " (turno " + refs.join(", ") + ")") : "";
  return `${fr} ${causas}${r}.`;
}

/* confere as tabelas na carga (como o HTML): falha alto */
validarTabelasFala(["fadiga_treino", ...FATOR_DA_FEATURE, ...FATORES_ESPACOS, ...Object.keys(CATALOGO_V2), "vinculo_baixo", "teimosia", ...["fome", "higiene", "energia", "humor"].map(n => "necessidade_" + n)]);
validarTabelasPersonalidade();
