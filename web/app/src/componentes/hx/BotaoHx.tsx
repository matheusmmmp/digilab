/* Botoes da pele XCOM. BotaoHx: escuro com borda cinza-petroleo (tom "perigo" para o que desfaz). BotaoContinuar: o principal,
   fundo escuro, borda verde e hachura verde no topo (o "CONTINUAR"). Sempre <button type="button"> com alvo de 44 px. */
import type { ComponentProps } from "react";
import clsx from "clsx";

export function BotaoHx({ tom = "normal", className, type = "button", ...props }: ComponentProps<"button"> & { tom?: "normal" | "perigo" }) {
  return <button type={type} className={clsx("hx-btn", tom === "perigo" && "hx-btn--perigo", className)} {...props} />;
}

export function BotaoContinuar({ className, type = "button", children = "Continuar", ...props }: ComponentProps<"button">) {
  return <button type={type} className={clsx("hx-continuar", className)} {...props}>{children}</button>;
}
