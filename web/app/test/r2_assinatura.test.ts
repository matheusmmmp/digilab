/* A assinatura SigV4 do envio ao R2 (scripts/r2.ts, CN5), conferida com o exemplo da documentação da AWS ("Create a signed AWS API
   request", o ListUsers do IAM com a chave de exemplo AKIDEXAMPLE). */
import { describe, expect, it } from "vitest";
import { assinar, quandoAgora, sha256Hex } from "../scripts/r2.ts";

describe("a assinatura SigV4", () => {
  it("dá a assinatura do exemplo da AWS", () => {
    const { assinatura, authorization } = assinar({
      metodo: "GET",
      url: new URL("https://iam.amazonaws.com/?Action=ListUsers&Version=2010-05-08"),
      cabecalhos: { "Content-Type": "application/x-www-form-urlencoded; charset=utf-8", Host: "iam.amazonaws.com", "X-Amz-Date": "20150830T123600Z" },
      hashCorpo: sha256Hex(""),
      regiao: "us-east-1",
      servico: "iam",
      quando: "20150830T123600Z",
    }, { id: "AKIDEXAMPLE", segredo: "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY" });
    expect(assinatura).toBe("5d672d79c15b13162d9279b0855cfba6789a8edb4c82c400e06b5924a6f2b5d7");
    expect(authorization).toBe("AWS4-HMAC-SHA256 Credential=AKIDEXAMPLE/20150830/us-east-1/iam/aws4_request, "
      + "SignedHeaders=content-type;host;x-amz-date, Signature=5d672d79c15b13162d9279b0855cfba6789a8edb4c82c400e06b5924a6f2b5d7");
  });

  it("o carimbo da hora no formato do SigV4", () => {
    expect(quandoAgora(new Date(Date.UTC(2026, 10, 20, 16, 5, 9, 123)))).toBe("20261120T160509Z");
  });
});
