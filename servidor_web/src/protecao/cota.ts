/* A cota da fala por conta (CN4, docs/PLANO_V3_CONTA.md seção 6): no máximo `limite` falas pela LLM por conta por dia de Brasília, pelo
   relógio do servidor. Conta só a chamada que vai mesmo à LLM (a do cache e a do template não custam); quando a cota acaba, a fala é o
   template. O teto de gasto TOTAL (gasto.ts) continua por cima de todas as contas. */
import { diaDe } from "../../../web/app/src/ranking/pontos.ts";
import type { Banco } from "../conta/banco.ts";

/** o que o gerador da fala pergunta antes de chamar a LLM (fala.ts) */
export interface CotaFala {
  /** ainda pode chamar a LLM? (false: a fala é o template, com `motivo` no detalhe) */
  resta(): boolean;
  /** a chamada foi feita: conta uma */
  gastar(): void;
  readonly motivo: string;
}

/** a cota que nunca deixa (a fala sem a sessão, quando a LLM é só para quem tem conta) */
export const SEM_CONTA: CotaFala = { resta: () => false, gastar: () => { throw new Error("a fala sem conta não chama a LLM"); },
  motivo: "sem conta: só o template" };

export interface EstadoCota { limite: number; usadas: number; restam: number; dia: string }

export class CotaDaConta implements CotaFala {
  readonly motivo: string;
  private readonly banco: Banco;
  private readonly contaId: string;
  private readonly limite: number;
  private readonly dia: string;

  constructor(banco: Banco, contaId: string, limite: number, agora: number) {
    this.banco = banco;
    this.contaId = contaId;
    this.limite = limite;
    this.dia = diaDe(agora);
    this.motivo = `a cota do dia acabou (${limite} falas pela LLM por conta)`;
  }

  usadas(): number {
    const r = this.banco.prepare("SELECT usadas FROM cota_fala WHERE conta_id = ? AND dia = ?").get(this.contaId, this.dia) as { usadas: number } | undefined;
    return r?.usadas ?? 0;
  }

  resta(): boolean { return this.usadas() < this.limite; }

  gastar(): void {
    this.banco.prepare(`INSERT INTO cota_fala (conta_id, dia, usadas) VALUES (?, ?, 1)
      ON CONFLICT (conta_id, dia) DO UPDATE SET usadas = usadas + 1`).run(this.contaId, this.dia);
    /* os dias passados não servem para nada: só o de hoje fica (o "ontem" fica pela virada do dia de quem está jogando) */
    this.banco.prepare("DELETE FROM cota_fala WHERE conta_id = ? AND dia < date(?, '-1 day')").run(this.contaId, this.dia);
  }

  estado(): EstadoCota {
    const usadas = this.usadas();
    return { limite: this.limite, usadas, restam: Math.max(0, this.limite - usadas), dia: this.dia };
  }
}

/** o que vai no "baixar os meus dados": os dias e as contagens */
export function cotaDaConta(banco: Banco, contaId: string): { dia: string; usadas: number }[] {
  return banco.prepare("SELECT dia, usadas FROM cota_fala WHERE conta_id = ? ORDER BY dia").all(contaId) as { dia: string; usadas: number }[];
}
