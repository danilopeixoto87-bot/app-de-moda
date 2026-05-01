"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Suspense } from "react";

function FailureContent() {
  const params = useSearchParams();
  const orderId = params.get("external_reference");

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
        fontFamily: "ui-sans-serif, system-ui",
        background: "#fef2f2",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 64, marginBottom: 16 }}>❌</div>
      <h1 style={{ fontSize: 24, fontWeight: 700, color: "#b91c1c", marginBottom: 8 }}>
        Pagamento não aprovado
      </h1>
      <p style={{ color: "#4b5563", marginBottom: 24, maxWidth: 320 }}>
        Não foi possível processar o pagamento. Verifique os dados do cartão ou tente outro método de pagamento.
      </p>

      {orderId && (
        <div
          style={{
            background: "#fff",
            borderRadius: 10,
            padding: "12px 20px",
            marginBottom: 24,
            boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
            fontSize: 13,
            color: "#555",
          }}
        >
          Pedido: <strong>{orderId.slice(0, 8).toUpperCase()}</strong>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 10, width: "100%", maxWidth: 280 }}>
        <Link
          href="/"
          style={{
            background: "#b91c1c",
            color: "#fff",
            padding: "14px 32px",
            borderRadius: 10,
            textDecoration: "none",
            fontWeight: 600,
            fontSize: 15,
            textAlign: "center",
          }}
        >
          Tentar novamente
        </Link>
        <Link
          href="/"
          style={{
            background: "#f3f4f6",
            color: "#374151",
            padding: "14px 32px",
            borderRadius: 10,
            textDecoration: "none",
            fontWeight: 600,
            fontSize: 15,
            textAlign: "center",
          }}
        >
          Voltar ao portal
        </Link>
      </div>
    </div>
  );
}

export default function CheckoutFalhaPage() {
  return (
    <Suspense>
      <FailureContent />
    </Suspense>
  );
}
