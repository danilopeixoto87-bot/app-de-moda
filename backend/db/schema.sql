-- App de Moda - Polo do Agreste (PE)
-- Schema completo para PostgreSQL
-- Gerado pelo SQLAlchemy via Base.metadata.create_all() — este arquivo serve como referência documental.

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  hashed_password TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin','fabrica','lojista','cliente')),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE TABLE IF NOT EXISTS companies (
  id TEXT PRIMARY KEY,
  trade_name TEXT NOT NULL,
  company_type TEXT NOT NULL CHECK (company_type IN ('loja','fabrica','faccao','atacadista')),
  city TEXT NOT NULL CHECK (city IN ('Caruaru','Santa Cruz do Capibaribe','Toritama')),
  neighborhood TEXT,
  street_address TEXT NOT NULL,
  address_number TEXT,
  complement TEXT,
  postal_code TEXT,
  latitude DOUBLE PRECISION NOT NULL,
  longitude DOUBLE PRECISION NOT NULL,
  whatsapp TEXT,
  phone TEXT,
  instagram TEXT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_companies_city ON companies(city);
CREATE INDEX IF NOT EXISTS idx_companies_type ON companies(company_type);
CREATE INDEX IF NOT EXISTS idx_companies_trade_name ON companies(trade_name);

CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  sku TEXT NOT NULL,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL,
  gender_target TEXT,
  description TEXT,
  base_price NUMERIC(12,2) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(company_id, sku)
);

CREATE INDEX IF NOT EXISTS idx_products_company ON products(company_id);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name);

CREATE TABLE IF NOT EXISTS product_variants (
  id TEXT PRIMARY KEY,
  product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  size_label TEXT NOT NULL,
  color_name TEXT NOT NULL,
  color_hex TEXT,
  fabric_type TEXT NOT NULL,
  fabric_composition TEXT,
  gsm INTEGER,
  fit_type TEXT,
  finish_type TEXT,
  variant_price NUMERIC(12,2),
  stock_qty INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(product_id, size_label, color_name, fabric_type)
);

CREATE INDEX IF NOT EXISTS idx_variants_product ON product_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_variants_size ON product_variants(size_label);

CREATE TABLE IF NOT EXISTS excursion_carriers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  whatsapp TEXT NOT NULL,
  origin_city TEXT NOT NULL,
  route_cities JSONB NOT NULL DEFAULT '[]',
  pickup_cutoff_time TEXT NOT NULL,
  max_delivery_hours INTEGER NOT NULL,
  base_fee NUMERIC(12,2) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  customer_name TEXT NOT NULL,
  customer_whatsapp TEXT NOT NULL,
  customer_city TEXT,
  notes TEXT,
  status TEXT NOT NULL DEFAULT 'pedido_recebido'
    CHECK (status IN ('pedido_recebido','em_separacao','pronto_para_coleta','coletado_excursao','em_transito','entregue','cancelado')),
  logistics_mode TEXT NOT NULL CHECK (logistics_mode IN ('retirada_em_loco','entrega_local','excursao')),
  delivery_address TEXT,
  delivery_city TEXT,
  local_delivery_fee NUMERIC(12,2),
  excursion_carrier_id TEXT REFERENCES excursion_carriers(id),
  requested_pickup_at TEXT,
  pickup_cutoff_time TEXT,
  max_delivery_hours INTEGER,
  estimated_excursion_fee NUMERIC(12,2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_carrier ON orders(excursion_carrier_id);

CREATE TABLE IF NOT EXISTS order_items (
  id TEXT PRIMARY KEY,
  order_id TEXT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id TEXT NOT NULL REFERENCES products(id),
  variant_id TEXT REFERENCES product_variants(id),
  quantity INTEGER NOT NULL CHECK (quantity >= 1)
);

CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);

CREATE TABLE IF NOT EXISTS order_timeline (
  id TEXT PRIMARY KEY,
  order_id TEXT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  status TEXT NOT NULL,
  note TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_timeline_order ON order_timeline(order_id);

CREATE TABLE IF NOT EXISTS leads (
  id TEXT PRIMARY KEY,
  customer_name TEXT NOT NULL,
  customer_whatsapp TEXT NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lead_companies (
  lead_id TEXT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  company_id TEXT NOT NULL REFERENCES companies(id),
  PRIMARY KEY (lead_id, company_id)
);

CREATE TABLE IF NOT EXISTS product_images (
  id TEXT PRIMARY KEY,
  product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  variant_id TEXT REFERENCES product_variants(id) ON DELETE SET NULL,
  image_url TEXT NOT NULL,
  image_kind TEXT NOT NULL CHECK (image_kind IN ('catalogo','modelo_ia','anuncio')),
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
