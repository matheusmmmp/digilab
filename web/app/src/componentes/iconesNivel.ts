/* O icone (lucide) de cada peca trancavel, o mesmo do trilho, da coluna e das abas (Nav.tsx, Topo.tsx, App.tsx). So vista. */
import { BookOpen, MessageCircle, Mountain, Package, Sprout, Swords, Zap, type LucideIcon } from "lucide-react";
import type { Peca } from "../nivel.ts";

export const ICONE_PECA: Record<Peca, LucideIcon> = {
  diario: BookOpen, crescer: Sprout, conversar: MessageCircle, lutar: Swords, itens: Package, forcar: Zap, fronteira: Mountain,
};
