/* O cerebro dos pets v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 4): o cerebro A com o aprendiz do ponto (CLB_V11) e o corpo do ponto
   (CCO_CORPO_V11), atras do braco da consequencia (o P1-c-tapa do gabarito). E o mesmo cerebro que os gates do laco e da vontade rejogam
   contra o Python; nenhum numero novo. */
import { CLB, CLB_V11 } from "./constantes.ts";
import { CCO_CORPO_V11 } from "./corpo.ts";
import { BracoConsequencia, CerebroA } from "./lobos.ts";

export function bracoV11(): BracoConsequencia {
  const co = CCO_CORPO_V11;
  const cerebro = new CerebroA({
    aprendizadoLigado: true, ...CLB,
    aprendiz: { passo: CLB_V11.passo, teto: CLB_V11.teto, piso: CLB_V11.piso, recompensaTapa: CLB_V11.recompensaTapa },
    corpo: { ligada: co.ligada, drives_novos: co.drives_novos, gestos: co.gestos, banheiro: co.banheiro, escala_receptor: co.escala_receptor },
  });
  return new BracoConsequencia(cerebro, { drives: CLB_V11.drives, ganho: CLB_V11.ganho, canais: CLB_V11.canais, pesosDrivesCorpo: CLB_V11.pesosDrivesCorpo });
}
