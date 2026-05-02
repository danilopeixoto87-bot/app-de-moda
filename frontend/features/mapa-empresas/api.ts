export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

function authHeaders(token: string) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function login(email: string, password: string): Promise<{ access_token: string; role: string }> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("Falha no login");
  return res.json();
}

export type PortalSearchResponse = {
  companies_count: number;
  products_count: number;
  variants_count: number;
  companies: Array<{ id: string; trade_name: string; city: string; company_type: string }>;
  products: Array<{ id: string; company_id: string; product_name: string; category: string }>;
  variants: Array<{ id: string; product_id: string; size_label: string; color_name: string; fabric_type: string; stock_qty: number }>;
  compact_context?: unknown;
};

export type ExcursionCarrier = {
  id: string;
  name: string;
  whatsapp: string;
  origin_city: string;
  route_cities: string[];
  pickup_cutoff_time: string;
  max_delivery_hours: number;
  base_fee: number;
  is_active: boolean;
};

export async function searchPortal(params: Record<string, string>): Promise<PortalSearchResponse> {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v) q.set(k, v);
  });
  const res = await fetch(`${API_BASE}/portal/search?${q.toString()}`);
  if (!res.ok) throw new Error("Falha na pesquisa centralizada");
  return res.json();
}

export async function listExcursionCarriers(city?: string): Promise<{ count: number; items: ExcursionCarrier[] }> {
  const q = new URLSearchParams();
  if (city) q.set("city", city);
  const res = await fetch(`${API_BASE}/portal/logistics/excursion-carriers?${q.toString()}`);
  if (!res.ok) throw new Error("Falha ao listar transportadores de excursao");
  return res.json();
}

export async function createOrder(payload: unknown, token: string): Promise<any> {
  const res = await fetch(`${API_BASE}/portal/orders`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Falha ao criar pedido");
  return res.json();
}

export async function generateImagePrompt(payload: unknown, token: string): Promise<any> {
  const res = await fetch(`${API_BASE}/portal/image/prompt`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ payload }),
  });
  if (!res.ok) throw new Error("Falha ao gerar prompt de imagem");
  return res.json();
}

export async function uploadProductImage(
  productId: string,
  file: File,
  token: string,
  opts?: { imageKind?: "catalogo" | "modelo_ia" | "anuncio"; variantId?: string; sortOrder?: number }
): Promise<any> {
  const form = new FormData();
  form.append("file", file);
  form.append("image_kind", opts?.imageKind ?? "catalogo");
  if (opts?.variantId) form.append("variant_id", opts.variantId);
  if (opts?.sortOrder !== undefined) form.append("sort_order", String(opts.sortOrder));

  const res = await fetch(`${API_BASE}/portal/catalog/products/${productId}/images`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  if (!res.ok) throw new Error("Falha ao enviar imagem do produto");
  return res.json();
}

export type ProductImage = {
  id: string;
  product_id: string;
  variant_id: string | null;
  image_url: string;
  image_kind: "catalogo" | "modelo_ia" | "anuncio";
  sort_order: number;
  created_at: string;
};

export async function listProductImages(
  productId: string,
  imageKind?: "catalogo" | "modelo_ia" | "anuncio"
): Promise<{ product_id: string; count: number; images: ProductImage[] }> {
  const q = new URLSearchParams();
  if (imageKind) q.set("image_kind", imageKind);
  const res = await fetch(`${API_BASE}/portal/catalog/products/${productId}/images?${q}`);
  if (!res.ok) throw new Error("Falha ao listar imagens do produto");
  return res.json();
}

export type CheckoutResponse = {
  preference_id: string;
  init_point: string;
  sandbox_init_point?: string;
};

export async function initOrderCheckout(orderId: string, token: string): Promise<CheckoutResponse> {
  const res = await fetch(`${API_BASE}/portal/orders/${orderId}/checkout`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as any).detail ?? "Falha ao iniciar checkout");
  }
  return res.json();
}

export type StorefrontProduct = {
  id: string;
  product_name: string;
  category: string;
  base_price: number;
  gender_target: string | null;
  description: string | null;
  images: Array<{ id: string; image_url: string; image_kind: string }>;
  variants: Array<{ id: string; size_label: string; color_name: string; variant_price: number | null; stock_qty: number }>;
};

export type StorefrontResponse = {
  company: {
    id: string;
    trade_name: string;
    company_type: string;
    city: string;
    whatsapp: string;
    instagram: string | null;
    latitude: number;
    longitude: number;
  };
  products: StorefrontProduct[];
  product_count: number;
};

export async function getStorefront(companyId: string): Promise<StorefrontResponse> {
  const res = await fetch(`${API_BASE}/portal/storefront/${companyId}`);
  if (!res.ok) throw new Error("Loja não encontrada");
  return res.json();
}

export type AISearchResult = {
  query: string;
  found: boolean;
  products_matched?: number;
  nearest: Array<{
    id: string;
    trade_name: string;
    city: string;
    neighborhood: string;
    whatsapp: string;
    min_price: number | null;
    storefront_url: string;
    distance_km?: number;
  }>;
  cheapest: Array<{
    id: string;
    trade_name: string;
    city: string;
    neighborhood: string;
    whatsapp: string;
    min_price: number | null;
    storefront_url: string;
  }>;
};

export async function aiSearch(
  text: string,
  location?: { lat: number; lon: number }
): Promise<AISearchResult> {
  const body: Record<string, unknown> = { text };
  if (location) { body.customer_lat = location.lat; body.customer_lon = location.lon; }
  const res = await fetch(`${API_BASE}/portal/ai-search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as any).detail ?? "Erro na busca por IA");
  }
  return res.json();
}

export type CatalogImportResult = {
  message: string;
  created_products: number;
  updated_products: number;
  created_variants: number;
  errors_count: number;
  errors: Array<{ row: number; error: string }>;
};

export async function importCatalogCSV(file: File, token: string): Promise<CatalogImportResult> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/portal/catalog/import`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as any).detail ?? "Falha na importação do catálogo");
  }
  return res.json();
}

export function catalogTemplateUrl(): string {
  return `${API_BASE}/portal/catalog/import/template`;
}

export async function generateProductImage(
  productId: string,
  token: string,
  imageKind: "catalogo" | "modelo_ia" | "anuncio" = "modelo_ia"
): Promise<{ message: string; prompt_usado: string; image: ProductImage }> {
  const res = await fetch(
    `${API_BASE}/portal/catalog/products/${productId}/generate-image?image_kind=${imageKind}`,
    { method: "POST", headers: { Authorization: `Bearer ${token}` } }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as any).detail ?? "Falha ao gerar imagem com IA");
  }
  return res.json();
}
