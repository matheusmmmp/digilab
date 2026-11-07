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

/* a escala (2026-11-06, pedido do Matheus: "esses objetos tem que ser muito maiores do que o pet; ele e uma crianca, tem que ser
   pequenininho perto deles"): as arvores, os postes, o carro, a geladeira e o trilho cresceram (arvore 4,2 -> 6, pinheiro 5 -> 7, poste
   3 -> 4,5, carro 1,9 -> 3,4, geladeira 1,7 -> 3, trilho 1 -> 2), para um pet de ~1 celula. PROPOSTO, SEM FONTE */
const qua = (...n: string[]) => n.map(x => `quaternius/${x}.gltf`), kay = (...n: string[]) => n.map(x => `kaykit/${x}.gltf`);

export const MODELOS = {
  arvore_redonda: { arquivos: qua("CommonTree_1", "CommonTree_2", "CommonTree_3", "CommonTree_4", "CommonTree_5"), altura: 6.0, vento: 0.004, sombra: 1.5, baixo: false },
  pinheiro: { arquivos: qua("Pine_1", "Pine_2", "Pine_3", "Pine_5"), altura: 7.0, vento: 0.003, sombra: 1.3, baixo: false },
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

/* Os itens gerados da ilha (docs/TAREFA_V3_ITENS_3D.md, D-I4: uma tabela irma, fora da grade e dos estilos): os arquivos ficam em
   web/app/public/itens/<item>/ com o License.txt de procedencia propria, e o teste test/ilha_itens3d.test.ts confere os gates G1 a G8.
   A vista (itens.ts) carrega o item pelo mesmo carregarVariante dos kits, que normaliza a caixa para a altura da tabela. A altura da bola
   e o diametro da bola procedural de antes (2 x R_BOLA), para o tamanho na tela nao mudar. PROPOSTO, SEM FONTE. */
export const ITENS_MODELOS = {
  bola: { arquivos: ["bola/bola.gltf"], altura: 0.72, vento: 0, sombra: 0.4, baixo: false },
  /* o saco: a altura do saco procedural de antes (o alto do braco, 2,48), e a mesma sombra */
  saco: { arquivos: ["saco/saco.gltf"], altura: 2.48, vento: 0, sombra: 0.7, baixo: false },
  /* o kit: mais alto que a maleta procedural (0,385 com a alca), para ficar um pouco mais largo que ela (0,56; o revisor achou o caixote pequeno em 390 px); o coco: a
     altura do coco procedural (0,46 com a ponta) menos a ponta mais curta do gerado; as sombras, as de antes */
  kit: { arquivos: ["kit/kit.gltf"], altura: 0.58, vento: 0, sombra: 0.45, baixo: false },
  coco: { arquivos: ["coco/coco.gltf"], altura: 0.42, vento: 0, sombra: 0.3, baixo: false },
} as const satisfies Record<string, Modelo>;
export type NomeItem = keyof typeof ITENS_MODELOS;

/* Os enfeites do mundo humano na moldura (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 3): outra tabela irma, em public/enfeites/<nome>/, com
   o License.txt de procedencia propria. A grade (grade.ts, porEnfeites) sorteia onde ficam; a vista (enfeites.ts) os poe instanciados.
   O poste: o lampiao gerado pela Meshy (o poste do City Kit Roads da Kenney, CC0, foi testado e saiu um poste de rodovia, sem nada da
   ilha); a altura e a de um poste na escala do pet (o pet tem cerca de 1 celula). PROPOSTO, SEM FONTE */
export const ENFEITES_MODELOS = {
  poste: { arquivos: ["poste/poste.gltf"], altura: 4.5, vento: 0, sombra: 0.4, baixo: false },
  /* o carro: a caminhonete com o jardim na cacamba, gerada pela Meshy (E2); maior que um carro na escala do pet, como um brinquedo, para
     ser visto na beira do plato (o revisor achou 1,3 pequeno demais) */
  carro: { arquivos: ["carro/carro.gltf"], altura: 3.4, vento: 0, sombra: 2.3, baixo: false },
  /* a geladeira com o vaso e o trilho com o vagao (E3), com os tracos de nanquim na textura; na escala de brinquedo do carro */
  geladeira: { arquivos: ["geladeira/geladeira.gltf"], altura: 3.0, vento: 0, sombra: 1.4, baixo: false },
  trilho: { arquivos: ["trilho/trilho.gltf"], altura: 2.0, vento: 0, sombra: 2.6, baixo: false },
} as const satisfies Record<string, Modelo>;
export type NomeEnfeite = keyof typeof ENFEITES_MODELOS;
/** a mascara das partes que acendem a noite (o emissiveMap; fora do glTF, ao lado dele), por enfeite que tem luz */
export const ENFEITES_LUZ: Partial<Record<NomeEnfeite, string>> = { poste: "poste/poste_luz.png" };

/* Os lugares da ilha (docs/TAREFA_V3_LUGARES_3D.md; os "Lugares da ilha" de docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, P-11): outra tabela irma,
   em public/lugares/<nome>/, gerada pela Meshy, com o License.txt ao lado. Quem os poe na cena (o ponto, o giro, o trancado e o aberto) e o
   modulo ilha/lugares.ts da frente UX_TELA_PET, pelo carregarVariante (cena.ts), que normaliza o modelo para a altura daqui. O portao: o arco
   de pedra com o portal ciano (o lugar do Lutar), um pouco mais alto que um pinheiro baixo, para o pet (~1 celula) passar folgado. PROPOSTO,
   SEM FONTE */
export const LUGARES_MODELOS = {
  portao: { arquivos: ["portao/portao.gltf"], altura: 5, vento: 0, sombra: 1.6, baixo: false },
} as const satisfies Record<string, Modelo>;
export type NomeLugar = keyof typeof LUGARES_MODELOS;
/** a mascara das partes que acendem com o lugar aberto (o emissiveMap; fora do glTF, ao lado dele): o portal do portao */
export const LUGARES_LUZ: Partial<Record<NomeLugar, string>> = { portao: "portao/portao_luz.png" };
/** os modelos que podem entrar na area andavel sem um objeto do motor (regra 5) */
export const MODELOS_BAIXOS = (Object.keys(MODELOS) as NomeModelo[]).filter(n => MODELOS[n].baixo);
/** o modelo das arvores do layout do motor (as `arvores`, J* e M*), as unicas coisas altas dentro da area andavel */
export const MODELO_ARVORE_DO_MOTOR: NomeModelo = "arvore_redonda";
