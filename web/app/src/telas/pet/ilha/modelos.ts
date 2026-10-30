/* Os modelos dos kits 3D CC0 da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, H1): a tabela MODELOS do POC poc/mapa_ac/cena.ts, sem o
   Kenney (H-6), mais a samambaia e os cogumelos da mata (secao 5). So dados, sem three e sem DOM: o carregador fica na cena (cena.ts).
   Os arquivos ficam em web/app/public/kits3d/<kit>/ (H-1), copiados por scripts/kits3d_copiar.py, que tem a mesma lista; o teste
   test/ilha_modelos.test.ts confere a tabela contra a pasta.
   - altura: a altura alvo do modelo, em celulas do motor (o carregador normaliza a caixa do modelo para ela);
   - vento: a amplitude do balanco das folhagens (0 = parado);
   - sombra: o raio da sombra redonda no chao, em celulas (0 = sem sombra);
   - baixo: decoracao que pode entrar na area andavel (regra 5: o pet a atravessa; nada acima de ALTURA_BAIXA).
   Todos os numeros sao do desenho: PROPOSTO, SEM FONTE. */

/** a altura maxima da decoracao dentro da area andavel, em celulas (regra 5) */
export const ALTURA_BAIXA = 0.5;

export interface Modelo { arquivos: readonly string[]; altura: number; vento: number; sombra: number; baixo: boolean }

const qua = (...n: string[]) => n.map(x => `quaternius/${x}.gltf`), kay = (...n: string[]) => n.map(x => `kaykit/${x}.gltf`);

export const MODELOS = {
  arvore_redonda: { arquivos: qua("CommonTree_1", "CommonTree_2", "CommonTree_3", "CommonTree_4", "CommonTree_5"), altura: 4.2, vento: 0.004, sombra: 1.5, baixo: false },
  pinheiro: { arquivos: qua("Pine_1", "Pine_2", "Pine_3", "Pine_5"), altura: 5.0, vento: 0.003, sombra: 1.3, baixo: false },
  arbusto: { arquivos: [...qua("Bush_Common", "Bush_Common_Flowers"), ...kay("Bush_1_A_Color1", "Bush_2_A_Color1")], altura: 1.0, vento: 0.02, sombra: 0.7, baixo: false },
  pedra: { arquivos: kay("Rock_1_A_Color1", "Rock_2_A_Color1", "Rock_3_A_Color1"), altura: 0.6, vento: 0, sombra: 0.5, baixo: false },
  flor: { arquivos: qua("Flower_3_Group", "Flower_4_Group", "Flower_3_Single", "Flower_4_Single"), altura: 0.45, vento: 0.06, sombra: 0, baixo: true },
  trevo: { arquivos: qua("Clover_1", "Clover_2"), altura: 0.2, vento: 0.05, sombra: 0, baixo: true },
  grama: { arquivos: qua("Grass_Common_Short", "Grass_Wispy_Short"), altura: 0.3, vento: 0.08, sombra: 0, baixo: true },
  grama_alta: { arquivos: qua("Grass_Common_Tall"), altura: 0.45, vento: 0.08, sombra: 0, baixo: true },
  samambaia: { arquivos: qua("Fern_1"), altura: 0.45, vento: 0.05, sombra: 0, baixo: true },
  cogumelo: { arquivos: qua("Mushroom_Common", "Mushroom_Laetiporus"), altura: 0.3, vento: 0, sombra: 0, baixo: true },
} as const satisfies Record<string, Modelo>;

export type NomeModelo = keyof typeof MODELOS;
/** os modelos que podem entrar na area andavel sem um objeto do motor (regra 5) */
export const MODELOS_BAIXOS = (Object.keys(MODELOS) as NomeModelo[]).filter(n => MODELOS[n].baixo);
/** o modelo das arvores do layout do motor (as `arvores`, J* e M*), as unicas coisas altas dentro da area andavel */
export const MODELO_ARVORE_DO_MOTOR: NomeModelo = "arvore_redonda";
