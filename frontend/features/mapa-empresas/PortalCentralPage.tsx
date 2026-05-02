"use client";

import { useEffect, useMemo, useState } from "react";
import AISearchWidget from "./AISearchWidget";
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
  importCatalogCSV,
  catalogTemplateUrl,
  type CatalogImportResult,
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
  const [category, setCategory] = useState("");
  const [tipo, setTipo] = useState("");
  const [manga, setManga] = useState("");
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

  const [catalogFile, setCatalogFile] = useState<File | null>(null);
  const [catalogImportResult, setCatalogImportResult] = useState<CatalogImportResult | null>(null);
  const [catalogImportLoading, setCatalogImportLoading] = useState(false);

  const [result, setResult] = useState<PortalSearchResponse | null>(null);
  const [promptResult, setPromptResult] = useState<{ prompt: string } | null>(null);
  const [orderResult, setOrderResult] = useState<any>(null);
  const [checkoutResult, setCheckoutResult] = useState<CheckoutResponse | null>(null);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const searchParams = useMemo(
    () => ({ q: query, city, category, tipo, manga, size, color, fabric }),
    [query, city, category, tipo, manga, size, color, fabric]
  );

  const ALL_COLORS = [
    "Preto", "Branco", "Azul", "Cinza", "Vermelho", "Verde", "Rosa",
    "Amarelo", "Bege", "Marrom", "Vinho", "Azul Marinho", "Laranja",
    "Roxo", "Nude", "Coral", "Khaki", "Turquesa", "Dourado", "Off-white",
  ];

  const ALL_FABRICS = [
    "Algodão", "Poliéster", "Viscose", "Malha", "Denim/Jeans",
    "Linho", "Moletom", "Dry Fit", "Couro Sintético", "Spandex",
  ];

  const CATEGORY_FILTERS: Record<string, {
    label: string;
    tipos?: string[];
    mangas?: string[];
    fabrics?: string[];
    sizes?: string[];
  }> = {
    camisa: {
      label: "Camisa",
      tipos: ["Polo", "Social", "Regata", "Camiseta", "Henley", "Gola V", "Gola Careca", "Manga Longa", "Flanela", "Xadrez"],
      mangas: ["Curta", "Longa", "Sem Manga", "3/4"],
      fabrics: ["Algodão", "Poliéster", "Dry Fit", "Viscose", "Linho", "Oxford", "Malha", "Jersey", "Flanela"],
      sizes: ["PP", "P", "M", "G", "GG", "XGG", "2XGG"],
    },
    calca: {
      label: "Calça",
      tipos: ["Jeans Reto", "Skinny", "Slim", "Wide Leg", "Flare", "Jogger", "Cargo", "Social", "Legging", "Cigarrete"],
      fabrics: ["Denim/Jeans", "Sarja", "Moletom", "Viscose", "Alfaiataria", "Linho", "Couro Sintético", "Bengaline"],
      sizes: ["36", "38", "40", "42", "44", "46", "48", "P", "M", "G", "GG"],
    },
    bermuda: {
      label: "Bermuda / Short",
      tipos: ["Jeans", "Moletom", "Sarja", "Social", "Dry Fit", "Tactel", "Surf", "Ciclista"],
      fabrics: ["Denim/Jeans", "Moletom", "Sarja", "Tactel", "Dry Fit", "Linho", "Poliéster"],
      sizes: ["36", "38", "40", "42", "44", "46", "P", "M", "G", "GG"],
    },
    vestido: {
      label: "Vestido",
      tipos: ["Longo", "Curto", "Midi", "Festa", "Casual", "Evasê", "Tubinho", "Envelope", "Ombro a Ombro", "Chemise"],
      fabrics: ["Viscose", "Chiffon", "Malha", "Linho", "Seda", "Crepe", "Jacquard", "Cetim", "Renda"],
      sizes: ["PP", "P", "M", "G", "GG", "XGG", "36", "38", "40", "42", "44"],
    },
    blusa: {
      label: "Blusa",
      tipos: ["Cropped", "Ciganinha", "Regata", "Camiseta", "Alcinha", "Blusão", "Estampada", "Listrada", "Decote V"],
      mangas: ["Curta", "Longa", "Sem Manga", "3/4", "Bufante"],
      fabrics: ["Algodão", "Viscose", "Malha", "Poliéster", "Linho", "Seda", "Dry Fit", "Chiffon"],
      sizes: ["PP", "P", "M", "G", "GG", "XGG"],
    },
    conjunto: {
      label: "Conjunto",
      tipos: ["Fitness", "Moletom", "Social", "Praia", "Pijama", "Jogger", "Alfaiataria", "Ciclismo"],
      fabrics: ["Malha", "Dry Fit", "Spandex", "Viscose", "Algodão", "Moletom", "Poliamida"],
      sizes: ["PP", "P", "M", "G", "GG", "XGG"],
    },
    jaqueta: {
      label: "Jaqueta / Casaco",
      tipos: ["Jeans", "Couro", "Moletom", "Puffer", "Corta-vento", "Bomber", "Trench Coat", "Sobretudo", "Cardigã"],
      mangas: ["Longa"],
      fabrics: ["Denim/Jeans", "Couro Sintético", "Nylon", "Veludo", "Moletom", "Lã", "Poliéster", "Sherpa"],
      sizes: ["PP", "P", "M", "G", "GG", "XGG"],
    },
    "moda-praia": {
      label: "Moda Praia",
      tipos: ["Biquíni", "Maiô", "Sunga", "Bermuda Surf", "Saída de Praia", "Top Fitness", "Canga", "Conjunto Praia"],
      fabrics: ["Lycra", "Poliamida", "Dry Fit", "Nylon", "Tactel"],
      sizes: ["PP", "P", "M", "G", "GG", "36", "38", "40", "42", "44"],
    },
    acessorio: {
      label: "Acessório",
      tipos: ["Bolsa", "Carteira", "Cinto", "Boné / Chapéu", "Óculos", "Relógio", "Colar", "Brinco", "Pulseira", "Mochila"],
      fabrics: ["Couro", "Couro Sintético", "Lona", "Palha", "Metal", "Tecido", "Madeira"],
      sizes: ["Único", "P", "M", "G"],
    },
  };

  const activeCategoryKey = Object.keys(CATEGORY_FILTERS).find((k) =>
    category.toLowerCase().includes(k)
  );
  const categoryConfig = activeCategoryKey ? CATEGORY_FILTERS[activeCategoryKey] : null;
  const activeSizes = categoryConfig?.sizes ?? ["PP", "P", "M", "G", "GG", "XGG", "36", "38", "40", "42", "44", "46", "48", "Único"];
  const activeFabrics = categoryConfig?.fabrics ?? ALL_FABRICS;

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

  async function runCatalogImport() {
    if (!token) return setError("Faça login antes de importar o catálogo");
    if (!catalogFile) return setError("Selecione um arquivo CSV");
    setError("");
    setCatalogImportLoading(true);
    setCatalogImportResult(null);
    try {
      const data = await importCatalogCSV(catalogFile, token);
      setCatalogImportResult(data);
    } catch (e: any) {
      setError(e?.message || "Erro na importação do catálogo");
    } finally {
      setCatalogImportLoading(false);
    }
  }

  const QUICK_CATEGORIES = [
    { key: "camisa", label: "👕 Camisas" },
    { key: "calca", label: "👖 Calças" },
    { key: "bermuda", label: "🩳 Bermudas" },
    { key: "vestido", label: "👗 Vestidos" },
    { key: "blusa", label: "🫧 Blusas" },
    { key: "conjunto", label: "🎽 Conjuntos" },
    { key: "jaqueta", label: "🧥 Jaquetas" },
    { key: "moda-praia", label: "🏖️ Praia" },
    { key: "acessorio", label: "👜 Acessórios" },
  ];

  return (
    <main style={{ fontFamily: "ui-sans-serif, system-ui", background: "#f8f9fa", minHeight: "100vh" }}>

      {/* ── HERO ── */}
      <div style={{ background: "linear-gradient(135deg,#1a1a2e 0%,#16213e 60%,#0f3460 100%)", color: "#fff", padding: "32px 16px 24px", textAlign: "center" }}>
        <div style={{ maxWidth: 680, margin: "0 auto" }}>
          <div style={{ fontSize: 12, letterSpacing: 3, textTransform: "uppercase", color: "#a5b4fc", marginBottom: 8 }}>
            Polo de Confecções do Agreste · PE
          </div>
          <h1 style={{ margin: "0 0 10px", fontSize: "clamp(22px,5vw,36px)", fontWeight: 800, lineHeight: 1.2 }}>
            Compre moda direto da fábrica
          </h1>
          <p style={{ margin: "0 0 20px", color: "#cbd5e1", fontSize: "clamp(13px,3vw,16px)" }}>
            Marketplace B2B com as melhores lojas de Caruaru, Santa Cruz e Toritama
          </p>

          {/* Stats bar */}
          <div style={{ display: "flex", justifyContent: "center", gap: "clamp(16px,4vw,40px)", marginBottom: 24, flexWrap: "wrap" }}>
            {[
              { n: result ? `${result.companies_count}` : "200+", label: "Lojas" },
              { n: result ? `${result.products_count}` : "5.000+", label: "Produtos" },
              { n: "3", label: "Cidades" },
            ].map(({ n, label }) => (
              <div key={label} style={{ textAlign: "center" }}>
                <div style={{ fontSize: "clamp(20px,4vw,28px)", fontWeight: 800, color: "#a5b4fc" }}>{n}</div>
                <div style={{ fontSize: 12, color: "#94a3b8", textTransform: "uppercase", letterSpacing: 1 }}>{label}</div>
              </div>
            ))}
          </div>

          {/* Barra de busca principal */}
          <div style={{ display: "flex", gap: 0, maxWidth: 560, margin: "0 auto", borderRadius: 12, overflow: "hidden", boxShadow: "0 4px 24px rgba(0,0,0,0.3)" }}>
            <input
              placeholder="Buscar produto, tecido ou loja..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && runSearch()}
              style={{ flex: 1, padding: "14px 16px", border: "none", fontSize: 15, outline: "none", minWidth: 0 }}
            />
            <button
              onClick={runSearch}
              disabled={loading}
              style={{ padding: "14px 20px", background: "#a5b4fc", color: "#1a1a2e", border: "none", fontWeight: 700, fontSize: 15, cursor: "pointer", whiteSpace: "nowrap" }}
            >
              {loading ? "..." : "Buscar"}
            </button>
          </div>
        </div>
      </div>

      {/* ── CATEGORIAS RÁPIDAS ── */}
      <div style={{ background: "#fff", borderBottom: "1px solid #e5e7eb", overflowX: "auto", padding: "0 8px" }}>
        <div style={{ display: "flex", gap: 4, padding: "10px 0", minWidth: "max-content", margin: "0 auto", maxWidth: 980 }}>
          <button
            onClick={() => { setCategory(""); setTipo(""); setManga(""); }}
            style={{
              padding: "6px 14px", borderRadius: 20, border: "1.5px solid",
              borderColor: !category ? "#6366f1" : "#e5e7eb",
              background: !category ? "#eef2ff" : "transparent",
              color: !category ? "#4338ca" : "#374151",
              fontWeight: !category ? 700 : 400, fontSize: 13, cursor: "pointer", whiteSpace: "nowrap",
            }}
          >
            Tudo
          </button>
          {QUICK_CATEGORIES.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => { setCategory(key); setTipo(""); setManga(""); setTimeout(runSearch, 50); }}
              style={{
                padding: "6px 14px", borderRadius: 20, border: "1.5px solid",
                borderColor: category === key ? "#6366f1" : "#e5e7eb",
                background: category === key ? "#eef2ff" : "transparent",
                color: category === key ? "#4338ca" : "#374151",
                fontWeight: category === key ? 700 : 400, fontSize: 13, cursor: "pointer", whiteSpace: "nowrap",
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* ── ASSISTENTE IA / VOZ ── */}
      <div style={{ maxWidth: 980, margin: "0 auto", padding: "10px 16px 0" }}>
        <AISearchWidget />
      </div>

      {/* ── FILTROS AVANÇADOS (expansível) ── */}
      <div style={{ maxWidth: 980, margin: "0 auto", padding: "10px 16px" }}>
        <details style={{ background: "#fff", borderRadius: 10, border: "1px solid #e5e7eb", padding: "10px 14px" }}>
          <summary style={{ cursor: "pointer", fontWeight: 600, fontSize: 14, color: "#374151", listStyle: "none", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>Filtros avançados {(city || tipo || manga || size || color || fabric) ? `(${[city,tipo,manga,size,color,fabric].filter(Boolean).length} ativos)` : ""}</span>
            <span style={{ fontSize: 12, color: "#6b7280" }}>▼</span>
          </summary>

          <div style={{ marginTop: 12, display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))" }}>
            <select value={city} onChange={(e) => setCity(e.target.value)}>
              <option value="">Todas as cidades</option>
              <option value="Caruaru">Caruaru</option>
              <option value="Santa Cruz do Capibaribe">Santa Cruz do Capibaribe</option>
              <option value="Toritama">Toritama</option>
            </select>

            {categoryConfig?.tipos && (
              <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
                <option value="">Tipo</option>
                {categoryConfig.tipos.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            )}

            {categoryConfig?.mangas && (
              <select value={manga} onChange={(e) => setManga(e.target.value)}>
                <option value="">Manga</option>
                {categoryConfig.mangas.map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
            )}

            <select value={size} onChange={(e) => setSize(e.target.value)}>
              <option value="">Tamanho</option>
              {activeSizes.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>

            <select value={color} onChange={(e) => setColor(e.target.value)}>
              <option value="">Cor</option>
              {ALL_COLORS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>

            <select value={fabric} onChange={(e) => setFabric(e.target.value)}>
              <option value="">Tecido</option>
              {activeFabrics.map((f) => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>

          <div style={{ marginTop: 10, display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              onClick={runSearch}
              disabled={loading}
              style={{ background: "#1a1a2e", color: "#fff", border: "none", borderRadius: 8, padding: "8px 18px", fontWeight: 600, fontSize: 14, cursor: "pointer" }}
            >
              Aplicar filtros
            </button>
            <button
              onClick={() => { setCity(""); setCategory(""); setTipo(""); setManga(""); setSize(""); setColor(""); setFabric(""); }}
              style={{ background: "transparent", color: "#6b7280", border: "1px solid #d1d5db", borderRadius: 8, padding: "8px 14px", fontSize: 14, cursor: "pointer" }}
            >
              Limpar
            </button>
            <button onClick={runPrompt} disabled={loading} style={{ background: "transparent", color: "#6366f1", border: "1px solid #6366f1", borderRadius: 8, padding: "8px 14px", fontSize: 13, cursor: "pointer" }}>
              ✨ Gerar Prompt IA
            </button>
          </div>
        </details>

        {/* Auth compacto */}
        <details style={{ marginTop: 8, background: "#fff", borderRadius: 10, border: "1px solid #e5e7eb", padding: "10px 14px" }}>
          <summary style={{ cursor: "pointer", fontSize: 13, color: token ? "#16a34a" : "#6b7280", listStyle: "none" }}>
            {token ? "✓ Logado — clique para sair" : "Entrar na conta (lojistas e fábricas)"}
          </summary>
          {!token ? (
            <div style={{ marginTop: 10, display: "grid", gap: 8, gridTemplateColumns: "1fr 1fr auto" }}>
              <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} style={{ fontSize: 13 }} />
              <input placeholder="Senha" type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ fontSize: 13 }} />
              <button onClick={runLogin} disabled={loading} style={{ background: "#1a1a2e", color: "#fff", border: "none", borderRadius: 8, padding: "8px 14px", fontSize: 13 }}>
                Entrar
              </button>
            </div>
          ) : (
            <button
              onClick={() => { setToken(""); localStorage.removeItem("auth_token"); }}
              style={{ marginTop: 8, fontSize: 12, padding: "4px 12px", background: "#ef4444", color: "#fff", border: "none", borderRadius: 6 }}
            >
              Sair
            </button>
          )}
        </details>
      </div>

      {/* Conteúdo principal */}
      <div style={{ maxWidth: 980, margin: "0 auto", padding: "0 16px 32px" }}>

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

          {/* Importação de catálogo CSV */}
          <div style={{ marginTop: 20, borderTop: "1px solid #eee", paddingTop: 16 }}>
            <h2 style={{ fontSize: 18, marginBottom: 4 }}>Importar Catálogo de Produtos</h2>
            <p style={{ fontSize: 13, color: "#666", marginTop: 0, marginBottom: 8 }}>
              Atualize seus produtos em tempo real via CSV. Produtos existentes (mesmo SKU) serão atualizados; novos serão criados.
            </p>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setCatalogFile(e.target.files?.[0] ?? null)}
                style={{ fontSize: 13 }}
              />
              <button
                onClick={runCatalogImport}
                disabled={catalogImportLoading || !catalogFile}
                style={{ background: "#16a34a", color: "#fff", border: "none", borderRadius: 6, padding: "7px 14px", cursor: "pointer" }}
              >
                {catalogImportLoading ? "Importando..." : "📥 Importar CSV"}
              </button>
              <a
                href={catalogTemplateUrl()}
                download="catalogo_modelo.csv"
                style={{ fontSize: 13, color: "#1a73e8" }}
              >
                Baixar modelo CSV
              </a>
            </div>

            {catalogImportResult && (
              <div style={{ marginTop: 10, padding: 12, background: catalogImportResult.errors_count > 0 ? "#fffbeb" : "#f0fdf4", borderRadius: 8, fontSize: 13 }}>
                <div style={{ fontWeight: 600, marginBottom: 6 }}>{catalogImportResult.message}</div>
                <div>✅ Produtos criados: <strong>{catalogImportResult.created_products}</strong></div>
                <div>🔄 Produtos atualizados: <strong>{catalogImportResult.updated_products}</strong></div>
                <div>📦 Variantes criadas: <strong>{catalogImportResult.created_variants}</strong></div>
                {catalogImportResult.errors_count > 0 && (
                  <div style={{ marginTop: 8, color: "#b45309" }}>
                    <div>⚠️ Erros ({catalogImportResult.errors_count}):</div>
                    {catalogImportResult.errors.map((e) => (
                      <div key={e.row} style={{ fontSize: 12, paddingLeft: 8 }}>Linha {e.row}: {e.error}</div>
                    ))}
                  </div>
                )}
              </div>
            )}
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
      </div>{/* fim conteúdo principal */}
    </main>
  );
}
