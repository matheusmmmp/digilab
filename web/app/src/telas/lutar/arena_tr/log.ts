/* O texto do log da arena em tempo real, a partir dos eventos da simulacao (as frases do arena.html). */
import type { Evento, Lado } from "../../../../arena/index.ts";

export const NOME_ATR: Record<string, string> = { Vaccine: "Vacina", Data: "Dados", Virus: "Vírus", Free: "Livre", None: "Sem atributo", Unknown: "Desconhecido" };
const nome = (n: string) => n.replace(/_/g, " ");

/** a frase de um evento e o lado da cor (null = neutro); o dano do ambiente que nao derruba nao vai para o log */
export function textoEvento(e: Evento): { txt: string; lado: Lado | null } | null {
  switch (e.tipo) {
    case "inicio": return { txt: `Luta: equipe azul (${e.a.map(nome).join(", ")}) contra equipe vermelha (${e.b.map(nome).join(", ")}).`, lado: null };
    case "dano": {
      const atr = e.mult > 1 ? " · vantagem de atributo" : e.mult < 1 ? " · desvantagem de atributo" : "";
      return { txt: `${nome(e.at.n)} acerta ${nome(e.alvo.n)}${e.hab ? " com a habilidade" : ""}: −${e.valor}${e.crit ? " (crítico)" : ""}${atr} · resta ${e.resta}`, lado: e.at.lado };
    }
    case "esquiva": return { txt: `${nome(e.alvo.n)} esquivou do golpe de ${nome(e.at.n)}.`, lado: e.alvo.lado };
    case "atordoado": return { txt: `${nome(e.alvo.n)} ficou atordoado.`, lado: e.at.lado };
    case "queda": return { txt: `${nome(e.u.n)} caiu${e.motivo ? " " + e.motivo : ""}.`, lado: e.u.lado };
    case "troca": return { txt: e.forcada ? `${nome(e.entra.n)} entra no lugar de ${nome(e.sai.n)}.` : `${nome(e.sai.n)} volta e ${nome(e.entra.n)} entra.`, lado: e.lado };
    case "habilidade": return { txt: `${nome(e.u.n)} usa a habilidade${e.propria ? ` (${e.anim})` : ""}.`, lado: e.u.lado };
    case "golpe_ar": return { txt: `${nome(e.u.n)} golpeou o ar.`, lado: e.u.lado };
    case "tiro_bloqueado": return { txt: `O projétil de ${nome(e.u.n)} bateu ${e.obst === "arvore" ? "numa árvore" : "numa rocha"}.`, lado: e.u.lado };
    case "pilar": return { txt: `O projétil de ${nome(e.u.n)} ${e.quebrou ? "derrubou" : "rachou"} um pilar.`, lado: e.u.lado };
    case "tiro_errou": return { txt: `O projétil de ${nome(e.u.n)} errou.`, lado: e.u.lado };
    case "runa": return { txt: `${nome(e.u.n)} ativou a runa: +30% de dano por 8 s.`, lado: e.u.lado };
    case "arena_fecha": return { txt: "A arena começou a fechar.", lado: null };
    case "tempestade": return { txt: "Tempestade de areia: projéteis lentos e mira ruim por 6 s.", lado: null };
    case "queda_ringue": return { txt: `${nome(e.u.n)} caiu do ringue.`, lado: e.u.lado === "a" ? "b" : "a" };
    case "ambiente": return null;
    case "fim": return e.vencedor
      ? { txt: `Equipe ${e.vencedor === "a" ? "azul" : "vermelha"} venceu com ${e.vivos} de pé, em ${(e.relogio / 1000).toFixed(1).replace(".", ",")} s.`, lado: e.vencedor }
      : { txt: "Empate: as duas equipes caíram.", lado: null };
  }
}
