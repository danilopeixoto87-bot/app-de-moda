"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Suspense } from "react";

function SuccessContent() {
  const params = useSearchParams();
  const paymentId = params.get("payment_id");
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
        background: "#f0fdf4",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 64, marginBottom: 16 }}>✅</div>
      <h1 style={{ fontSize: 24, fontWeight: 700, color: "#15803d", marginBottom: 8 }}>
        Pagamento aprovado!
      </h1>
      <p style={{ color: "#4b5563", marginBottom: 24, maxWidth: 320 }}>
        Seu pedido foi confirmado. As fábricas já foram notificadas e entrarão em contato pelo WhatsApp.
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
          <div>Pedido: <strong>{orderId.slice(0, 8).toUpperCase()}</strong></div>
          {paymentId && <div>Pagamento: <strong>{paymentId}</strong></div>}
        </div>
      )}

      <Link
        href="/"
        style={{
          background: "#1a1a2e",
          color: "#fff",
          padding: "14px 32px",
          borderRadius: 10,
          textDecoration: "none",
          fontWeight: 600,
          fontSize: 15,
        }}
      >
        Voltar ao portal
      </Link>
    </div>
  );
}

export default function CheckoutSucessoPage() {
  return (
    <Suspense>
      <SuccessContent />
    </Suspense>
  );
}
