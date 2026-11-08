/* A luta da POC ainda sem tela (LUTA_POC, LP2): com a chave ligada (?luta_poc=1), um pet v21 luta no motor (Motor.lutarPoc), mas a tela da
   luta nova (o palco 2D, os 8 mapas, a escolha do rival e do mapa) e a LP3. Ate la, a Arena, a Campanha e a Fronteira dizem isso em vez de
   abrir as telas do combate de antes, que nao servem a v21. */
export function LutaPocSemTela({ lugar }: { lugar: string }) {
  return (
    <section className="hx-painel luta-poc-sem-tela" aria-labelledby="lpst-tit">
      <h2 id="lpst-tit">{lugar}</h2>
      <p>A luta nova, na arena em tempo real, já roda no seu pet, mas a tela dela ainda está sendo feita.</p>
      <p>Quando ela chegar, você escolhe o rival e o mapa aqui e assiste ao seu pet lutar sozinho.</p>
    </section>
  );
}
