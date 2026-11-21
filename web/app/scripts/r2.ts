/* O pedido assinado para o R2 pela API compatível com o S3 (AWS Signature Version 4), só com o node:crypto (CN5): sem SDK nem dependência.
   A conta segue a documentação da AWS ("Create a signed AWS API request"); o test/r2_assinatura.test.ts confere com o exemplo dela. */
import { createHash, createHmac } from "node:crypto";

export interface Credencial { id: string; segredo: string }
export interface PedidoAssinavel {
  metodo: string;
  url: URL;
  cabecalhos: Record<string, string>;
  /** o sha256 do corpo, em hex; "UNSIGNED-PAYLOAD" não é usado aqui */
  hashCorpo: string;
  regiao: string;
  servico: string;
  /** AAAAMMDDTHHMMSSZ */
  quando: string;
}

export const sha256Hex = (dados: string | Uint8Array): string => createHash("sha256").update(dados).digest("hex");
const hmac = (chave: string | Buffer, texto: string): Buffer => createHmac("sha256", chave).update(texto, "utf8").digest();

/** o RFC 3986, como o SigV4 pede: tudo menos A-Z a-z 0-9 - _ . ~ vira %XX */
const codificar = (s: string): string => encodeURIComponent(s).replace(/[!'()*]/g, c => "%" + c.charCodeAt(0).toString(16).toUpperCase());

export function quandoAgora(d = new Date()): string {
  return d.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
}

/** devolve o cabeçalho Authorization (e a assinatura, para o teste) */
export function assinar(p: PedidoAssinavel, cred: Credencial): { authorization: string; assinatura: string } {
  const dia = p.quando.slice(0, 8);
  const cab = Object.entries(p.cabecalhos).map(([k, v]) => [k.toLowerCase(), v.trim().replace(/\s+/g, " ")] as const)
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
  const assinados = cab.map(([k]) => k).join(";");
  const consulta = [...p.url.searchParams.entries()].map(([k, v]) => [codificar(k), codificar(v)] as const)
    .sort(([a, x], [b, y]) => (a < b ? -1 : a > b ? 1 : x < y ? -1 : x > y ? 1 : 0)).map(([k, v]) => `${k}=${v}`).join("&");
  const caminho = p.url.pathname.split("/").map(s => codificar(decodeURIComponent(s))).join("/") || "/";
  const canonico = [p.metodo, caminho, consulta, ...cab.map(([k, v]) => `${k}:${v}`), "", assinados, p.hashCorpo].join("\n");
  const escopo = `${dia}/${p.regiao}/${p.servico}/aws4_request`;
  const texto = ["AWS4-HMAC-SHA256", p.quando, escopo, sha256Hex(canonico)].join("\n");
  const chave = hmac(hmac(hmac(hmac("AWS4" + cred.segredo, dia), p.regiao), p.servico), "aws4_request");
  const assinatura = createHmac("sha256", chave).update(texto, "utf8").digest("hex");
  return { assinatura, authorization: `AWS4-HMAC-SHA256 Credential=${cred.id}/${escopo}, SignedHeaders=${assinados}, Signature=${assinatura}` };
}

/** um pedido ao R2 (a região é "auto", o serviço é "s3"), com o corpo assinado */
export async function pedirR2(conta: string, cred: Credencial, metodo: "PUT" | "HEAD" | "GET", chaveObjeto: string, bucket: string,
  corpo?: Uint8Array, extras: Record<string, string> = {}): Promise<Response> {
  const url = new URL(`https://${conta}.r2.cloudflarestorage.com/${bucket}/${chaveObjeto.split("/").map(codificar).join("/")}`);
  const hashCorpo = sha256Hex(corpo ?? new Uint8Array());
  const quando = quandoAgora();
  const cabecalhos: Record<string, string> = { host: url.host, "x-amz-content-sha256": hashCorpo, "x-amz-date": quando, ...extras };
  const { authorization } = assinar({ metodo, url, cabecalhos, hashCorpo, regiao: "auto", servico: "s3", quando }, cred);
  const { host: _host, ...semHost } = cabecalhos;
  return fetch(url, { method: metodo, headers: { ...semHost, authorization }, body: corpo });
}
