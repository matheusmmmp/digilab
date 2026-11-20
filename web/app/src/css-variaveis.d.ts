/* As variáveis CSS (--x) no style das telas: o React tipa o style sem elas; o Preact aceitava. */
import "react";
declare module "react" {
  interface CSSProperties { [variavel: `--${string}`]: string | number | undefined }
}
