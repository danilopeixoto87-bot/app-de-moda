"use client";

import { useEffect, useMemo, useState } from "react";
import {
  createOrder,
  generateImagePrompt,
  initOrderCheckout,
  listExcursionCarriers,
  login,
  searchPortal,
  uploadProductImage,
  generateProductImage,
  listProductImages,
  type CheckoutResponse,
  type ExcursionCarrier,
  type PortalSearchResponse,
  type ProductImage,
} from "./api";

export default function PortalCentralPage() {
  const [email, setEmail] = useState("cliente@appmoda.dev");
  const [password, setPassword] = useState("123456");
  const [token, setToken] = useState<string>(() =>
    typeof window !== "undefined" ? (localStorage.getItem("auth_token") ?? "") : ""
  );

  const [query, setQuery] = useState("");
  const [city, setCity] = useState("");
  const [size, setSize] = useState("");
  const [color, setColor] = useState("");
  const [fabric, setFabric] = useState("");

  const [customerName, setCustomerName] = useState("");
  const [customerWhatsapp, setCustomerWhatsapp] = useState("");
  const [deliveryAddress, setDeliveryAddress] = useState("");

  const [logisticsMode, setLogisticsMode] = useState<"retirada_em_loco" | "entrega_local" | "excursao">("retirada_em_loco");
  const [localDeliveryFee, setLocalDeliveryFee] = useState("0");
  const [requestedPickupAt, setRequestedPickupAt] = useState("");
  const [selectedCarrierId, setSelectedCarrierId] = useState("");

  const [selectedProductIds, setSelectedProductIds] = useState<string[]>([]);
  const [carriers, setCarriers] = useState<ExcursionCarrier[]>([]);
  const [imageProductId, setImageProductId] = useState("");
  const [imageKind, setImageKind] = useState<"catalogo" | "modelo_ia" | "anuncio">("catalogo");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<{ image_url?: string } | null>(null);

  // Sprint 3 — geração de imagem com IA
  const [genProductId, setGenProductId] = useState("");
  const [genKind, setGenKind] = useState<"catalogo" | "modelo_ia" | "anuncio">("modelo_ia");
  const [genResult, setGenResult] = useState<{ prompt_usado: string; image: ProductImage } | null>(null);
  const [genLoading, setGenLoading] = useState(false);
  const [gallery, setGallery] = useState<ProductImage[]>([]);
  const [galleryProductId, setGalleryProductId] = useState("");

  const [result, setResult] = useState<PortalSearchResponse | null>(null);
  const [promptResult, setPromptResult] = useState<{ prompt: string } | null>(null);
  const [orderResult, setOrderResult] = useState<any>(null);
  const [checkoutResult, setCheckoutResult] = useState<CheckoutResponse | null>(null);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const searchParams = useMemo(() => ({ q: query, city, size, color, fabric }), [query, city, size, color, fabric]);

  async function runLogin() {
    setError("");
    setLoading(true);
    try {
      const data = await login(email, password);
      setToken(data.access_token);
      localStorage.setItem("auth_token", data.access_token);
    } catch (e: any) {
      setError(e?.message || "Erro no login");
    } finally {
      setLoading(false);
    }
  }

  async function runSearch() {
    setError("");
    setLoading(true);
    try {
      const data = await searchPortal(searchParams);
      setResult(data);
      if (city) {
        const carrierData = await listExcursionCarriers(city);
        setCarriers(carrierData.items || []);
      }
    } catch (e: any) {
      setError(e?.message || "Erro na pesquisa");
    } finally {
      setLoading(false);
    }
  }

  async function runPrompt() {
    if (!token) return setError("Faca login antes de gerar prompt");
    if (!query) return setError("Informe o nome do produto para gerar prompt de imagem");

    setError("");
    setLoading(true);
    try {
      const data = await generateImagePrompt(
        {
          city,
          product_name: query,
          category: "moda",
          scenario: "ambiente editorial minimalista",
          lighting: "golden hour suave",
          style_lens: "fotografia de moda, lente 85mm",
          vibe: "sofisticacao acessivel",
          quality: "Ultra-HD",
          audience: "atacado",
        },
        token
      );
      setPromptResult(data);
    } catch (e: any) {
      setError(e?.message || "Erro ao gerar prompt");
    } finally {
      setLoading(false);
    }
  }

  function toggleProduct(productId: string) {
    setSelectedProductIds((prev) => (prev.includes(productId) ? prev.filter((id) => id !== productId) : [...prev, productId]));
  }

  async function runOrder() {
    if (!token) return setError("Faca login antes de criar pedido");
    if (!customerName || !customerWhatsapp) return setError("Preencha nome e WhatsApp do cliente");
    if (!selectedProductIds.length) return setError("Selecione ao menos 1 produto para pedido");
    if (logisticsMode === "excursao" && !selectedCarrierId) return setError("Selecione um transportador de excursao");

    setError("");
    setLoading(true);

    try {
      const payload = {
        customer_name: customerName,
        customer_whatsapp: customerWhatsapp,
        customer_city: city || null,
        items: selectedProductIds.map((id) => ({ product_id: id, quantity: 1 })),
        logistics: {
          mode: logisticsMode,
          delivery_address: deliveryAddress || null,
          delivery_city: city || null,
          local_delivery_fee: logisticsMode === "entrega_local" ? Number(localDeliveryFee || "0") : null,
          excursion_carrier_id: logisticsMode === "excursao" ? selectedCarrierId : null,
          requested_pickup_at: requestedPickupAt || null,
        },
      };

      const data = await createOrder(payload, token);
      setOrderResult(data);
      setCheckoutResult(null);
    } catch (e: any) {
      setError(e?.message || "Erro ao criar pedido");
    } finally {
      setLoading(false);
    }
  }

  async function runCheckout() {
    if (!token) return setError("Faca login antes de pagar");
    const orderId = orderResult?.order?.id;
    if (!orderId) return setError("Crie um pedido primeiro");
    setError("");
    setCheckoutLoading(true);
    try {
      const data = await initOrderCheckout(orderId, token);
      setCheckoutResult(data);
    } catch (e: any) {
      setError(e?.message || "Erro ao iniciar pagamento");
    } finally {
      setCheckoutLoading(false);
    }
  }

  async function runUploadImage() {
    if (!token) return setError("Faca login antes de enviar imagem");
    if (!imageProductId) return setError("Selecione um produto para upload");
    if (!imageFile) return setError("Selecione um arquivo de imagem");
    setError("");
    setLoading(true);
    try {
      const data = await uploadProductImage(imageProductId, imageFile, token, { imageKind });
      setUploadResult(data?.image ?? null);
    } catch (e: any) {
      setError(e?.message || "Erro no upload da imagem");
    } finally {
      setLoading(false);
    }
  }

  async function runGenerateImage() {
    if (!token) return setError("Faca login antes de gerar imagem");
    if (!genProductId) return setError("Selecione um produto para gerar imagem");
    setError("");
    setGenLoading(true);
    setGenResult(null);
    try {
      const data = await generateProductImage(genProductId, token, genKind);
      setGenResult({ prompt_usado: data.prompt_usado, image: data.image });
    } catch (e: any) {
      setError(e?.message || "Erro ao gerar imagem com IA");
    } finally {
      setGenLoading(false);
    }
  }

  async function loadGallery(productId: string) {
    if (!productId) return;
    try {
      const data = await listProductImages(productId);
      setGallery(data.images);
      setGalleryProductId(productId);
    } catch {
      setGallery([]);
    }
  }

  return (
    <main style={{ maxWidth: 980, margin: "0 auto", padding: 16, fontFamily: "ui-sans-serif, system-ui" }}>
      <h1 style={{ marginBottom: 6 }}>Portal Central de Moda</h1>
      <p style={{ marginTop: 0 }}>Busca unificada, pedido online, logistica previsivel e contato com lojas/fabricas.</p>

      <section style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))" }}>
        <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input placeholder="Senha" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </section>
      {!token ? (
        <button onClick={runLogin} disabled={loading} style={{ marginTop: 8 }}>Login</button>
      ) : (
        <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 13, color: "#16a34a" }}>✓ Logado</span>
          <button
            onClick={() => { setToken(""); localStorage.removeItem("auth_token"); }}
            style={{ fontSize: 12, padding: "2px 10px", background: "#ef4444", color: "#fff", border: "none", borderRadius: 4 }}
          >
            Sair
          </button>
        </div>
      )}

      <section style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", marginTop: 12 }}>
        <input placeholder="Produto ou descricao" value={query} onChange={(e) => setQuery(e.target.value)} />
        <select value={city} onChange={(e) => setCity(e.target.value)}>
          <option value="">Todas cidades</option>
          <option value="Caruaru">Caruaru</option>
          <option value="Santa Cruz do Capibaribe">Santa Cruz do Capibaribe</option>
          <option value="Toritama">Toritama</option>
        </select>
        <input placeholder="Tamanho" value={size} onChange={(e) => setSize(e.target.value)} />
        <input placeholder="Cor" value={color} onChange={(e) => setColor(e.target.value)} />
        <input placeholder="Tecido" value={fabric} onChange={(e) => setFabric(e.target.value)} />
      </section>

      <section style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
        <button onClick={runSearch} disabled={loading}>Pesquisar</button>
        <button onClick={runPrompt} disabled={loading}>Gerar Prompt IA</button>
      </section>

      {error && <p style={{ color: "#b00020" }}>{error}</p>}

      {promptResult?.prompt && (
        <section style={{ marginTop: 14 }}>
          <h2 style={{ fontSize: 18 }}>Prompt Otimizado</h2>
          <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 10, borderRadius: 8 }}>{promptResult.prompt}</pre>
        </section>
      )}

      {result && (
        <section style={{ marginTop: 20, display: "grid", gap: 16 }}>
          <div>
            <h2 style={{ fontSize: 18 }}>Empresas ({result.companies_count})</h2>
            {result.companies.map((c) => (
              <div key={c.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 0", borderBottom: "1px solid #f3f4f6" }}>
                <span style={{ fontSize: 14 }}>{c.trade_name} — {c.city} <span style={{ color: "#888", fontSize: 12 }}>({c.company_type})</span></span>
                <a
                  href={`/loja/${c.id}`}
                  target="_blank"
                  rel="noreferrer"
                  style={{ fontSize: 12, background: "#1a1a2e", color: "#fff", padding: "4px 10px", borderRadius: 6, textDecoration: "none", whiteSpace: "nowrap", flexShrink: 0 }}
                >
                  Ver loja →
                </a>
              </div>
            ))}
          </div>

          <div>
            <h2 style={{ fontSize: 18 }}>Produtos ({result.products_count})</h2>
            {result.products.map((p) => (
              <label key={p.id} style={{ display: "block", marginBottom: 6 }}>
                <input type="checkbox" checked={selectedProductIds.includes(p.id)} onChange={() => toggleProduct(p.id)} /> {p.product_name} - {p.category}
              </label>
            ))}
          </div>

          <div>
            <h2 style={{ fontSize: 18 }}>Logistica e Pedido</h2>
            <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))" }}>
              <input placeholder="Nome do cliente" value={customerName} onChange={(e) => setCustomerName(e.target.value)} />
              <input placeholder="WhatsApp do cliente" value={customerWhatsapp} onChange={(e) => setCustomerWhatsapp(e.target.value)} />
              <input placeholder="Endereco de entrega (opcional)" value={deliveryAddress} onChange={(e) => setDeliveryAddress(e.target.value)} />
              <select value={logisticsMode} onChange={(e) => setLogisticsMode(e.target.value as any)}>
                <option value="retirada_em_loco">Retirada em loco</option>
                <option value="entrega_local">Entrega local</option>
                <option value="excursao">Excursao</option>
              </select>
            </div>

            {logisticsMode === "entrega_local" && (
              <input style={{ marginTop: 8 }} placeholder="Taxa de entrega local" value={localDeliveryFee} onChange={(e) => setLocalDeliveryFee(e.target.value)} />
            )}

            {logisticsMode === "excursao" && (
              <div style={{ marginTop: 8 }}>
                <select value={selectedCarrierId} onChange={(e) => setSelectedCarrierId(e.target.value)}>
                  <option value="">Selecione o transportador</option>
                  {carriers.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} | Corte: {c.pickup_cutoff_time} | Ate {c.max_delivery_hours}h | R$ {c.base_fee}</option>
                  ))}
                </select>
                <input style={{ marginTop: 8 }} placeholder="Horario desejado de coleta (ISO)" value={requestedPickupAt} onChange={(e) => setRequestedPickupAt(e.target.value)} />
              </div>
            )}

            <button onClick={runOrder} disabled={loading} style={{ marginTop: 8 }}>Criar Pedido</button>
          </div>

          <div>
            <h2 style={{ fontSize: 18 }}>Upload de Imagem (Sprint 2)</h2>
            <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))" }}>
              <select value={imageProductId} onChange={(e) => setImageProductId(e.target.value)}>
                <option value="">Selecione o produto</option>
                {result.products.map((p) => (
                  <option key={p.id} value={p.id}>{p.product_name}</option>
                ))}
              </select>
              <select value={imageKind} onChange={(e) => setImageKind(e.target.value as "catalogo" | "modelo_ia" | "anuncio")}>
                <option value="catalogo">Catalogo</option>
                <option value="modelo_ia">Modelo IA</option>
                <option value="anuncio">Anuncio</option>
              </select>
              <input type="file" accept="image/png,image/jpeg,image/webp" onChange={(e) => setImageFile(e.target.files?.[0] ?? null)} />
            </div>
            <button onClick={runUploadImage} disabled={loading} style={{ marginTop: 8 }}>Enviar imagem</button>
            {uploadResult?.image_url && (
              <div style={{ marginTop: 8 }}>
                <a href={uploadResult.image_url} target="_blank" rel="noreferrer">Ver imagem pública</a>
              </div>
            )}
          </div>

          {/* Sprint 3 — Gerar imagem com IA */}
          <div style={{ marginTop: 20, borderTop: "1px solid #eee", paddingTop: 16 }}>
            <h2 style={{ fontSize: 18, marginBottom: 8 }}>Gerar Imagem com IA</h2>
            <p style={{ fontSize: 13, color: "#666", marginTop: 0 }}>
              Gera foto profissional automaticamente usando IA (Replicate flux-schnell ~R$0,016/imagem).
            </p>
            <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fit,minmax(200px,1fr))" }}>
              <select value={genProductId} onChange={(e) => { setGenProductId(e.target.value); loadGallery(e.target.value); }}>
                <option value="">Selecione o produto</option>
                {result?.products.map((p) => (
                  <option key={p.id} value={p.id}>{p.product_name}</option>
                ))}
              </select>
              <select value={genKind} onChange={(e) => setGenKind(e.target.value as "catalogo" | "modelo_ia" | "anuncio")}>
                <option value="modelo_ia">Modelo IA</option>
                <option value="catalogo">Catálogo</option>
                <option value="anuncio">Anúncio</option>
              </select>
            </div>
            <button
              onClick={runGenerateImage}
              disabled={genLoading || !genProductId}
              style={{ marginTop: 8, background: genLoading ? "#ccc" : "#1a73e8", color: "#fff", padding: "8px 16px", border: "none", borderRadius: 6, cursor: genLoading ? "default" : "pointer" }}
            >
              {genLoading ? "Gerando... (pode levar 10–20s)" : "✨ Gerar Imagem com IA"}
            </button>

            {genResult && (
              <div style={{ marginTop: 12, padding: 12, background: "#f0f7ff", borderRadius: 8 }}>
                <div style={{ fontSize: 12, color: "#555", marginBottom: 8 }}>
                  <strong>Prompt usado:</strong> {genResult.prompt_usado}
                </div>
                <img
                  src={genResult.image.image_url}
                  alt="Imagem gerada por IA"
                  style={{ maxWidth: "100%", maxHeight: 400, borderRadius: 6, display: "block" }}
                />
                <a href={genResult.image.image_url} target="_blank" rel="noreferrer" style={{ fontSize: 13, display: "block", marginTop: 6 }}>
                  Abrir imagem completa
                </a>
              </div>
            )}

            {/* Galeria de imagens do produto */}
            {gallery.length > 0 && galleryProductId === genProductId && (
              <div style={{ marginTop: 16 }}>
                <h3 style={{ fontSize: 15, marginBottom: 8 }}>Imagens do produto ({gallery.length})</h3>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {gallery.map((img) => (
                    <div key={img.id} style={{ position: "relative" }}>
                      <a href={img.image_url} target="_blank" rel="noreferrer">
                        <img
                          src={img.image_url}
                          alt={img.image_kind}
                          style={{ width: 100, height: 130, objectFit: "cover", borderRadius: 6, border: "1px solid #ddd" }}
                        />
                      </a>
                      <div style={{ fontSize: 11, color: "#666", textAlign: "center" }}>{img.image_kind}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {orderResult && (
        <section style={{ marginTop: 16 }}>
          <h2 style={{ fontSize: 18 }}>Pedido Criado</h2>
          <div>ID: {orderResult.order?.id}</div>
          <div>Status: {orderResult.order?.status}</div>
          <div>Empresas envolvidas: {(orderResult.order?.company_ids || []).join(", ")}</div>

          {orderResult.order?.logistics && (
            <div style={{ marginTop: 8 }}>
              <div>Modo logistico: {orderResult.order.logistics.mode}</div>
              <div>Previsao maxima: {orderResult.order.logistics.max_delivery_hours ?? 0}h</div>
              <div>Custo estimado: R$ {orderResult.order.logistics.estimated_excursion_fee ?? orderResult.order.logistics.local_delivery_fee ?? 0}</div>
            </div>
          )}

          {orderResult.carrier_contact && (
            <div style={{ marginTop: 8 }}>
              <a href={orderResult.carrier_contact.whatsapp_url} target="_blank">Falar com transportador: {orderResult.carrier_contact.carrier_name}</a>
            </div>
          )}

          {orderResult.order?.logistics_timeline?.length > 0 && (
            <div style={{ marginTop: 10 }}>
              <strong>Linha do tempo logistica</strong>
              {orderResult.order.logistics_timeline.map((x: any, idx: number) => (
                <div key={`${x.status}-${idx}`}>{x.status} - {x.at}</div>
              ))}
            </div>
          )}

          <div style={{ marginTop: 8 }}>Contatos das empresas:</div>
          {(orderResult.contact_links || []).map((x: any) => (
            <div key={x.company_id}>
              <a href={x.whatsapp_url} target="_blank">{x.trade_name} - WhatsApp</a>
            </div>
          ))}

          {/* Notificações WhatsApp para as fábricas */}
          {(orderResult.factory_notifications || []).length > 0 && (
            <div style={{ marginTop: 14, background: "#f0fdf4", borderRadius: 8, padding: 12 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: "#15803d", marginBottom: 8 }}>
                📣 Notificar fábricas sobre o pedido:
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {(orderResult.factory_notifications as any[]).map((n) => (
                  <a
                    key={n.company_id}
                    href={n.whatsapp_url}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      background: "#25d366",
                      color: "#fff",
                      padding: "8px 12px",
                      borderRadius: 8,
                      textDecoration: "none",
                      fontSize: 13,
                      fontWeight: 600,
                    }}
                  >
                    💬 Avisar {n.trade_name}
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Sprint 4 — Pagamento Mercado Pago */}
          <div style={{ marginTop: 16, borderTop: "1px solid #eee", paddingTop: 14 }}>
            {!checkoutResult ? (
              <button
                onClick={runCheckout}
                disabled={checkoutLoading}
                style={{
                  background: checkoutLoading ? "#ccc" : "#009ee3",
                  color: "#fff",
                  padding: "10px 20px",
                  border: "none",
                  borderRadius: 6,
                  fontSize: 15,
                  cursor: checkoutLoading ? "default" : "pointer",
                  fontWeight: 600,
                }}
              >
                {checkoutLoading ? "Gerando link de pagamento..." : "💳 Pagar com Mercado Pago"}
              </button>
            ) : (
              <div style={{ background: "#e8f5e9", padding: 14, borderRadius: 8 }}>
                <div style={{ fontWeight: 600, marginBottom: 8, color: "#2e7d32" }}>
                  ✅ Link de pagamento gerado!
                </div>
                <a
                  href={checkoutResult.init_point}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    display: "inline-block",
                    background: "#009ee3",
                    color: "#fff",
                    padding: "10px 20px",
                    borderRadius: 6,
                    textDecoration: "none",
                    fontWeight: 600,
                    fontSize: 15,
                  }}
                >
                  Ir para o pagamento →
                </a>
                <div style={{ fontSize: 12, color: "#555", marginTop: 8 }}>
                  ID da preferência: {checkoutResult.preference_id}
                </div>
              </div>
            )}
          </div>
        </section>
      )}
    </main>
  );
}
