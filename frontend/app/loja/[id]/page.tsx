"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { getStorefront, type StorefrontProduct, type StorefrontResponse } from "@/features/mapa-empresas/api";

type CartItem = { product: StorefrontProduct; quantity: number };

const COMPANY_TYPE_LABEL: Record<string, string> = {
  fabrica: "Fábrica",
  loja: "Loja",
  atacadista: "Atacadista",
  faccao: "Facção",
};

function formatPrice(n: number) {
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function waLink(phone: string, text: string) {
  const clean = phone.replace(/\D/g, "");
  return `https://wa.me/${clean}?text=${encodeURIComponent(text)}`;
}

function buildWhatsAppOrder(storefront: StorefrontResponse, cart: CartItem[]) {
  const lines = cart.map(
    (i) => `• ${i.product.product_name} (x${i.quantity}) — ${formatPrice((i.product.variants[0]?.variant_price ?? i.product.base_price) * i.quantity)}`
  );
  const total = cart.reduce(
    (sum, i) => sum + (i.product.variants[0]?.variant_price ?? i.product.base_price) * i.quantity,
    0
  );
  return (
    `Olá, ${storefront.company.trade_name}! Quero fazer um pedido:\n\n` +
    lines.join("\n") +
    `\n\nTotal: ${formatPrice(total)}\n\nPode confirmar disponibilidade?`
  );
}

export default function StorePage() {
  const params = useParams();
  const router = useRouter();
  const companyId = params.id as string;

  const [storefront, setStorefront] = useState<StorefrontResponse | null>(null);
  const [error, setError] = useState("");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [showCart, setShowCart] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<StorefrontProduct | null>(null);

  useEffect(() => {
    getStorefront(companyId)
      .then(setStorefront)
      .catch(() => setError("Loja não encontrada ou indisponível."));
  }, [companyId]);

  function addToCart(product: StorefrontProduct, qty = 1) {
    setCart((prev) => {
      const existing = prev.find((i) => i.product.id === product.id);
      if (existing) return prev.map((i) => i.product.id === product.id ? { ...i, quantity: i.quantity + qty } : i);
      return [...prev, { product, quantity: qty }];
    });
    setSelectedProduct(null);
  }

  function removeFromCart(productId: string) {
    setCart((prev) => prev.filter((i) => i.product.id !== productId));
  }

  const cartTotal = cart.reduce(
    (sum, i) => sum + (i.product.variants[0]?.variant_price ?? i.product.base_price) * i.quantity,
    0
  );
  const cartCount = cart.reduce((sum, i) => sum + i.quantity, 0);

  if (error) return (
    <div style={{ padding: 24, textAlign: "center" }}>
      <div style={{ fontSize: 40, marginBottom: 12 }}>🚫</div>
      <p>{error}</p>
      <Link href="/" style={{ color: "#2563eb", marginTop: 12, display: "inline-block" }}>← Voltar ao portal</Link>
    </div>
  );

  if (!storefront) return (
    <div style={{ padding: 24, textAlign: "center", color: "#888" }}>
      <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
      Carregando loja...
    </div>
  );

  const { company, products } = storefront;

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", paddingBottom: 100, fontFamily: "ui-sans-serif, system-ui" }}>
      {/* Header */}
      <div style={{ background: "#1a1a2e", color: "#fff", padding: "20px 16px 16px" }}>
        <div style={{ fontSize: 11, opacity: 0.7, textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>
          {COMPANY_TYPE_LABEL[company.company_type] ?? company.company_type} · {company.city}
        </div>
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: "0 0 12px" }}>{company.trade_name}</h1>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {company.whatsapp && (
            <a
              href={waLink(company.whatsapp, `Olá, ${company.trade_name}! Vi seu catálogo no App de Moda.`)}
              target="_blank" rel="noreferrer"
              style={{ display: "flex", alignItems: "center", gap: 6, background: "#25d366", color: "#fff", padding: "8px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600, textDecoration: "none" }}
            >
              💬 WhatsApp
            </a>
          )}
          <a
            href={`https://www.google.com/maps/search/?api=1&query=${company.latitude},${company.longitude}`}
            target="_blank" rel="noreferrer"
            style={{ display: "flex", alignItems: "center", gap: 6, background: "rgba(255,255,255,0.15)", color: "#fff", padding: "8px 14px", borderRadius: 20, fontSize: 13, textDecoration: "none" }}
          >
            📍 Como chegar
          </a>
          {company.instagram && (
            <a
              href={`https://instagram.com/${company.instagram.replace("@", "")}`}
              target="_blank" rel="noreferrer"
              style={{ display: "flex", alignItems: "center", gap: 6, background: "rgba(255,255,255,0.15)", color: "#fff", padding: "8px 14px", borderRadius: 20, fontSize: 13, textDecoration: "none" }}
            >
              📸 Instagram
            </a>
          )}
        </div>
      </div>

      {/* Products */}
      <div style={{ padding: "16px 12px" }}>
        <div style={{ fontSize: 13, color: "#888", marginBottom: 12 }}>
          {products.length} produto{products.length !== 1 ? "s" : ""} disponíveis
        </div>

        {products.length === 0 && (
          <div style={{ textAlign: "center", padding: 40, color: "#aaa" }}>
            Nenhum produto cadastrado ainda.
          </div>
        )}

        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 12 }}>
          {products.map((product) => {
            const img = product.images[0];
            const price = product.variants[0]?.variant_price ?? product.base_price;
            const inCart = cart.find((i) => i.product.id === product.id);
            return (
              <div
                key={product.id}
                style={{ background: "#fff", borderRadius: 12, overflow: "hidden", boxShadow: "0 1px 4px rgba(0,0,0,0.08)", cursor: "pointer" }}
                onClick={() => setSelectedProduct(product)}
              >
                {img ? (
                  <img src={img.image_url} alt={product.product_name}
                    style={{ width: "100%", aspectRatio: "3/4", objectFit: "cover", display: "block" }} />
                ) : (
                  <div style={{ width: "100%", aspectRatio: "3/4", background: "#f3f4f6", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 36 }}>
                    👗
                  </div>
                )}
                <div style={{ padding: "10px 10px 12px" }}>
                  <div style={{ fontSize: 12, color: "#888", marginBottom: 2 }}>{product.category}</div>
                  <div style={{ fontSize: 14, fontWeight: 600, lineHeight: 1.3, marginBottom: 6 }}>{product.product_name}</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: "#1a1a2e" }}>{formatPrice(price)}</div>
                  <div style={{ fontSize: 11, color: "#aaa" }}>{product.variants.length} variante{product.variants.length !== 1 ? "s" : ""}</div>
                  {inCart && (
                    <div style={{ marginTop: 6, fontSize: 12, color: "#16a34a", fontWeight: 600 }}>✓ No carrinho (×{inCart.quantity})</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Product detail modal */}
      {selectedProduct && (
        <div
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 200, display: "flex", alignItems: "flex-end" }}
          onClick={() => setSelectedProduct(null)}
        >
          <div
            style={{ background: "#fff", borderRadius: "16px 16px 0 0", padding: 20, width: "100%", maxHeight: "80vh", overflowY: "auto" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
              <div>
                <div style={{ fontSize: 12, color: "#888" }}>{selectedProduct.category}</div>
                <h2 style={{ fontSize: 18, fontWeight: 700, margin: "2px 0" }}>{selectedProduct.product_name}</h2>
                <div style={{ fontSize: 20, fontWeight: 700, color: "#1a1a2e" }}>
                  {formatPrice(selectedProduct.variants[0]?.variant_price ?? selectedProduct.base_price)}
                </div>
              </div>
              <button onClick={() => setSelectedProduct(null)} style={{ background: "none", border: "none", fontSize: 22, cursor: "pointer", color: "#888" }}>✕</button>
            </div>

            {selectedProduct.description && (
              <p style={{ fontSize: 13, color: "#555", marginBottom: 12 }}>{selectedProduct.description}</p>
            )}

            {selectedProduct.variants.length > 0 && (
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "#888", marginBottom: 6 }}>VARIANTES DISPONÍVEIS</div>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {selectedProduct.variants.map((v) => (
                    <span key={v.id} style={{ border: "1px solid #e5e7eb", borderRadius: 6, padding: "4px 10px", fontSize: 12 }}>
                      {v.size_label} · {v.color_name}
                      {v.stock_qty > 0 ? ` (${v.stock_qty} un)` : " · Esgotado"}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {selectedProduct.images.length > 0 && (
              <div style={{ display: "flex", gap: 8, overflowX: "auto", marginBottom: 16, paddingBottom: 4 }}>
                {selectedProduct.images.map((img) => (
                  <img key={img.id} src={img.image_url} alt={selectedProduct.product_name}
                    style={{ height: 140, borderRadius: 8, flexShrink: 0 }} />
                ))}
              </div>
            )}

            <button
              onClick={() => addToCart(selectedProduct)}
              style={{ width: "100%", background: "#1a1a2e", color: "#fff", border: "none", borderRadius: 10, padding: "14px 0", fontSize: 15, fontWeight: 600, cursor: "pointer" }}
            >
              + Adicionar ao carrinho
            </button>
          </div>
        </div>
      )}

      {/* Cart modal */}
      {showCart && (
        <div
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 200, display: "flex", alignItems: "flex-end" }}
          onClick={() => setShowCart(false)}
        >
          <div
            style={{ background: "#fff", borderRadius: "16px 16px 0 0", padding: 20, width: "100%", maxHeight: "85vh", overflowY: "auto" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h2 style={{ fontSize: 18, fontWeight: 700 }}>Carrinho ({cartCount} itens)</h2>
              <button onClick={() => setShowCart(false)} style={{ background: "none", border: "none", fontSize: 22, cursor: "pointer" }}>✕</button>
            </div>

            {cart.map((item) => (
              <div key={item.product.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #f3f4f6" }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{item.product.product_name}</div>
                  <div style={{ fontSize: 12, color: "#888" }}>
                    {item.quantity}× {formatPrice(item.product.variants[0]?.variant_price ?? item.product.base_price)}
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontWeight: 700 }}>
                    {formatPrice((item.product.variants[0]?.variant_price ?? item.product.base_price) * item.quantity)}
                  </span>
                  <button onClick={() => removeFromCart(item.product.id)} style={{ background: "none", border: "none", color: "#ef4444", fontSize: 18, cursor: "pointer" }}>🗑</button>
                </div>
              </div>
            ))}

            <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 16 }}>
              Total: {formatPrice(cartTotal)}
            </div>

            {company.whatsapp && cart.length > 0 && (
              <a
                href={waLink(company.whatsapp, buildWhatsAppOrder(storefront, cart))}
                target="_blank" rel="noreferrer"
                style={{ display: "block", textAlign: "center", background: "#25d366", color: "#fff", padding: "14px 0", borderRadius: 10, fontSize: 15, fontWeight: 700, textDecoration: "none", marginBottom: 10 }}
              >
                💬 Pedir pelo WhatsApp
              </a>
            )}

            <Link
              href={`/?company=${company.id}`}
              style={{ display: "block", textAlign: "center", background: "#1a1a2e", color: "#fff", padding: "14px 0", borderRadius: 10, fontSize: 14, fontWeight: 600, textDecoration: "none" }}
            >
              Fazer pedido completo no App
            </Link>
          </div>
        </div>
      )}

      {/* Floating cart button */}
      {cartCount > 0 && !showCart && (
        <button
          onClick={() => setShowCart(true)}
          style={{
            position: "fixed", bottom: 24, right: 16, left: 16,
            background: "#25d366", color: "#fff",
            border: "none", borderRadius: 14, padding: "16px 20px",
            fontSize: 15, fontWeight: 700, cursor: "pointer",
            display: "flex", justifyContent: "space-between", alignItems: "center",
            boxShadow: "0 4px 16px rgba(37,211,102,0.4)",
            zIndex: 100,
          }}
        >
          <span>🛒 {cartCount} item{cartCount !== 1 ? "s" : ""}</span>
          <span>{formatPrice(cartTotal)} · Ver carrinho</span>
        </button>
      )}
    </div>
  );
}
