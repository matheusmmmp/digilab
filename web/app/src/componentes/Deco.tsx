/* Peca de decoracao do Digimon UP (src/decoracao.ts). Sao ilustracoes em alta resolucao, nao pixel art: saem com
   suavizacao normal. Decoracao nunca carrega sentido sozinha: alt vazio (aria-hidden) quando ha texto ao lado,
   ou alt com o sentido. Sem a peca (carregando ou falhou), nada: fica o visual de antes. */
import type { CSSProperties, ReactNode } from "react";
import { falhouDeco, urlDeco, useDecoracao, type NomeDeco } from "../decoracao.ts";

export function Deco({ nome, alt = "", className: cls = "", style, largura, altura, reserva = null }: {
  nome: NomeDeco; alt?: string; className?: string; style?: CSSProperties; largura?: number; altura?: number; reserva?: ReactNode;
}) {
  useDecoracao();
  const url = urlDeco(nome);
  if (!url) return <>{reserva}</>;
  return <img className={`dl-deco ${cls}`} src={url} alt={alt} aria-hidden={alt ? undefined : "true"} width={largura} height={altura}
    style={style} decoding="async" onError={() => falhouDeco(nome, url)} />;
}
/** a peca como fundo CSS (url(...)), ou undefined sem ela */
export function fundoDeco(nome: NomeDeco): string | undefined {
  const url = urlDeco(nome);
  return url ? `url("${url}")` : undefined;
}
