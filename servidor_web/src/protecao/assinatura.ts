/* A URL assinada dos assets (CN4, docs/PLANO_V3_CONTA.md seção 6): o atlas, os sons e os pacotes saem por um endereço de vida curta, que
   só o servidor sabe fazer. O formato é o do token da Cloudflare (a função `is_timed_hmac_valid_v0` das regras de WAF), para que a borda da
   CN5 confira sem passar pelo servidor:

     <caminho>?verify=<hora>-<mac>        hora: segundos Unix de quando a URL foi feita; mac: base64 do HMAC-SHA256(segredo, caminho + hora)

   A regra da borda recusa o que passou da validade (o TTL da função); aqui, `verificar` faz a mesma conta, para o servidor local e os
   testes, e é o mesmo código que um Worker na frente do R2 usaria. NÃO CONFERIDO contra a Cloudflare de verdade: a conferência é da CN5
   (D-CONTA-212). O segredo só vem do ambiente (DIGILAB_SEGREDO_ASSETS), nunca do repositório. */
import { createHmac, timingSafeEqual } from "node:crypto";

/** o nome do parâmetro da assinatura (o separador "?verify=" tem 8 caracteres: o `lengthOfSeparator` da regra da Cloudflare) */
export const PARAMETRO = "verify";
/** a folga do relógio para uma URL feita "no futuro" (um servidor adiantado em relação a quem confere), em segundos (PROPOSTO, SEM FONTE) */
export const FOLGA_RELOGIO_S = 60;

/** o MAC de um caminho numa hora, em base64 padrão (com "+", "/" e "="; vai codificado na URL) */
export function macDe(segredo: string, caminho: string, horaS: number): string {
  return createHmac("sha256", segredo).update(caminho + String(horaS)).digest("base64");
}

/** o valor do parâmetro `verify` de um caminho, feito na hora dada */
export function assinarCaminho(segredo: string, caminho: string, horaS: number): string {
  if (!Number.isInteger(horaS) || horaS < 0) throw new Error(`hora inválida: ${horaS}`);
  if (!caminhoValido(caminho)) throw new Error(`caminho inválido: ${JSON.stringify(caminho)}`);
  return `${horaS}-${macDe(segredo, caminho, horaS)}`;
}

/** a URL inteira: a base dos assets mais o caminho, com o `verify` (a parte assinada é o caminho do endereço final, o que a borda vê) */
export function urlAssinada(segredo: string, base: string, caminho: string, horaS: number): string {
  const u = new URL(base.replace(/\/+$/, "") + caminho);
  u.searchParams.set(PARAMETRO, assinarCaminho(segredo, u.pathname, horaS));
  return u.toString();
}

export type Veredito = "ok" | "sem_assinatura" | "malformada" | "nao_confere" | "vencida" | "do_futuro";

/** confere o `verify` de um caminho (já decodificado da URL) pela hora de agora e pela validade */
export function verificar(segredo: string, caminho: string, verify: string | undefined, agoraS: number, validadeS: number): Veredito {
  if (verify === undefined || verify === "") return "sem_assinatura";
  const m = /^(\d{1,12})-([A-Za-z0-9+/]{43}=)$/.exec(verify);
  if (!m) return "malformada";
  const hora = Number(m[1]);
  const esperado = Buffer.from(macDe(segredo, caminho, hora)), dado = Buffer.from(m[2]!);
  if (esperado.length !== dado.length || !timingSafeEqual(esperado, dado)) return "nao_confere";
  if (hora > agoraS + FOLGA_RELOGIO_S) return "do_futuro";
  if (agoraS - hora > validadeS) return "vencida";
  return "ok";
}

/** o caminho de um asset: começa com "/", só letras, números, ".", "_", "-" e "/", sem "..", sem "//", até 200 caracteres */
export function caminhoValido(caminho: unknown): caminho is string {
  return typeof caminho === "string" && /^\/[A-Za-z0-9._/-]{1,200}$/.test(caminho) && !caminho.includes("..") && !caminho.includes("//");
}
