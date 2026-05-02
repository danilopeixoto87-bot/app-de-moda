from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.orm import Company, Product, ProductVariant, User

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

_SEED_USERS = [
    {"id": "user-admin-001",   "email": "admin@appmoda.dev",   "role": "admin",    "password": "123456", "company_id": None},
    {"id": "user-fabrica-001", "email": "fabrica@appmoda.dev", "role": "fabrica",  "password": "123456", "company_id": "scc-001"},
    {"id": "user-lojista-001", "email": "lojista@appmoda.dev", "role": "lojista",  "password": "123456", "company_id": "tor-001"},
    {"id": "user-cliente-001", "email": "cliente@appmoda.dev", "role": "cliente",  "password": "123456", "company_id": None},
]

_SEED_COMPANIES = [
    {
        "id": "car-001", "trade_name": "Moda Caruaru Atacado", "company_type": "atacadista",
        "city": "Caruaru", "neighborhood": "Centro", "street_address": "Rua Duque de Caxias",
        "address_number": "120", "latitude": -8.2848, "longitude": -35.9699,
        "whatsapp": "+55 81 99999-1001", "phone": "+55 81 3721-1001",
        "instagram": "@modacaruaruatacado", "is_active": True,
    },
    {
        "id": "car-002", "trade_name": "Agreste Style Confecções", "company_type": "fabrica",
        "city": "Caruaru", "neighborhood": "Salgado", "street_address": "Rua João Pessoa",
        "address_number": "340", "latitude": -8.2901, "longitude": -35.9745,
        "whatsapp": "+55 81 99999-1002", "phone": "+55 81 3721-1002",
        "instagram": "@agrestestyle", "is_active": True,
    },
    {
        "id": "scc-001", "trade_name": "Fabrica Santa Cruz Jeans", "company_type": "fabrica",
        "city": "Santa Cruz do Capibaribe", "neighborhood": "Nova Santa Cruz",
        "street_address": "Avenida Bela Vista", "address_number": "450",
        "latitude": -7.9575, "longitude": -36.2043, "whatsapp": "+55 81 99999-2001",
        "phone": "+55 81 3759-2001", "instagram": "@santacruzjeans", "is_active": True,
    },
    {
        "id": "scc-002", "trade_name": "Santa Cruz Modas Femininas", "company_type": "fabrica",
        "city": "Santa Cruz do Capibaribe", "neighborhood": "Centro",
        "street_address": "Rua XV de Novembro", "address_number": "88",
        "latitude": -7.9612, "longitude": -36.2010, "whatsapp": "+55 81 99999-2002",
        "phone": "+55 81 3759-2002", "instagram": "@scmodafeminina", "is_active": True,
    },
    {
        "id": "tor-001", "trade_name": "Toritama Moda Fitness", "company_type": "loja",
        "city": "Toritama", "neighborhood": "Centro", "street_address": "Rua Joao Chagas",
        "address_number": "89", "latitude": -8.0094, "longitude": -36.0565,
        "whatsapp": "+55 81 99999-3001", "phone": "+55 81 3741-3001",
        "instagram": "@toritamamodafitness", "is_active": True,
    },
]

_SEED_PRODUCTS = [
    # ── Camisas ───────────────────────────────────────────────────────────
    {
        "id": "prod-001", "company_id": "car-001", "sku": "CAM-SLIM-001",
        "product_name": "Camisa Slim Masculina Manga Curta", "category": "camisa",
        "gender_target": "masculino", "description": "Camisa casual slim manga curta para atacado. Tipo: Casual. Manga: Curta.",
        "base_price": 79.90, "is_active": True,
    },
    {
        "id": "prod-003", "company_id": "car-001", "sku": "CAM-POLO-001",
        "product_name": "Camisa Polo Masculina Manga Curta", "category": "camisa",
        "gender_target": "masculino", "description": "Polo clássica com gola e botões. Tipo: Polo. Manga: Curta. Ótima para revenda.",
        "base_price": 89.90, "is_active": True,
    },
    {
        "id": "prod-004", "company_id": "car-001", "sku": "CAM-SOC-001",
        "product_name": "Camisa Social Masculina Manga Longa", "category": "camisa",
        "gender_target": "masculino", "description": "Camisa social premium para escritório. Tipo: Social. Manga: Comprida. Passadoria fácil.",
        "base_price": 119.90, "is_active": True,
    },
    {
        "id": "prod-005", "company_id": "car-002", "sku": "REG-DRY-001",
        "product_name": "Regata Dry Fit Masculina Sem Manga", "category": "camisa",
        "gender_target": "masculino", "description": "Regata esportiva dry fit. Tipo: Regata. Manga: Sem Manga. Alta absorção de suor.",
        "base_price": 39.90, "is_active": True,
    },
    {
        "id": "prod-006", "company_id": "car-002", "sku": "CAM-HEN-001",
        "product_name": "Camiseta Henley Masculina Manga Curta", "category": "camisa",
        "gender_target": "masculino", "description": "Camiseta Henley com abotoamento. Tipo: Henley. Manga: Curta. Look casual moderno.",
        "base_price": 69.90, "is_active": True,
    },
    # ── Calças ────────────────────────────────────────────────────────────
    {
        "id": "prod-002", "company_id": "scc-001", "sku": "JEA-RET-050",
        "product_name": "Calça Jeans Reto Premium Unissex", "category": "calca",
        "gender_target": "unissex", "description": "Jeans de alta durabilidade para revenda. Tipo: Jeans Reto. Corte tradicional.",
        "base_price": 129.90, "is_active": True,
    },
    {
        "id": "prod-007", "company_id": "scc-001", "sku": "JEA-SKN-001",
        "product_name": "Calça Jeans Skinny Feminina", "category": "calca",
        "gender_target": "feminino", "description": "Skinny com elastano para conforto. Tipo: Skinny. Cintura alta. Elastano 2%.",
        "base_price": 139.90, "is_active": True,
    },
    {
        "id": "prod-008", "company_id": "car-002", "sku": "CAL-MOL-001",
        "product_name": "Calça Moletom Masculina Jogger", "category": "calca",
        "gender_target": "masculino", "description": "Moletom jogger com elástico no tornozelo. Tipo: Moletom Jogger. Conforto máximo.",
        "base_price": 99.90, "is_active": True,
    },
    {
        "id": "prod-009", "company_id": "car-002", "sku": "CAL-CAR-001",
        "product_name": "Calça Cargo Masculina Sarja", "category": "calca",
        "gender_target": "masculino", "description": "Cargo com 6 bolsos em sarja. Tipo: Cargo. Estilo streetwear. Resistente.",
        "base_price": 119.90, "is_active": True,
    },
    # ── Bermudas e Shorts ─────────────────────────────────────────────────
    {
        "id": "prod-010", "company_id": "scc-001", "sku": "BER-JEA-001",
        "product_name": "Bermuda Jeans Feminina", "category": "bermuda",
        "gender_target": "feminino", "description": "Bermuda jeans com barra desfiada. Tipo: Jeans. Cintura média. Verão.",
        "base_price": 89.90, "is_active": True,
    },
    {
        "id": "prod-011", "company_id": "tor-001", "sku": "SHO-MOL-001",
        "product_name": "Short Moletom Unissex", "category": "bermuda",
        "gender_target": "unissex", "description": "Short moletom com bolso canguru. Tipo: Moletom. Elástico na cintura. Confortável.",
        "base_price": 59.90, "is_active": True,
    },
    # ── Vestidos ──────────────────────────────────────────────────────────
    {
        "id": "prod-012", "company_id": "scc-002", "sku": "VES-LON-001",
        "product_name": "Vestido Longo Estampado Sem Manga", "category": "vestido",
        "gender_target": "feminino", "description": "Vestido longo floral em viscose. Tipo: Longo. Manga: Sem Manga. Ideal para festas e passeios.",
        "base_price": 159.90, "is_active": True,
    },
    {
        "id": "prod-013", "company_id": "scc-002", "sku": "VES-CUR-001",
        "product_name": "Vestido Curto Festa Manga Curta", "category": "vestido",
        "gender_target": "feminino", "description": "Vestido de festa com brilho. Tipo: Curto. Manga: Curta. Ocasião: Festa.",
        "base_price": 129.90, "is_active": True,
    },
    {
        "id": "prod-014", "company_id": "scc-002", "sku": "VES-MID-001",
        "product_name": "Vestido Midi Casual Manga Longa", "category": "vestido",
        "gender_target": "feminino", "description": "Vestido midi para o dia a dia. Tipo: Midi. Manga: Comprida. Crepe leve.",
        "base_price": 119.90, "is_active": True,
    },
    # ── Blusas ────────────────────────────────────────────────────────────
    {
        "id": "prod-015", "company_id": "scc-002", "sku": "BLU-CRO-001",
        "product_name": "Blusa Cropped Manga Bufante Feminina", "category": "blusa",
        "gender_target": "feminino", "description": "Cropped com manga bufante em viscose. Tipo: Cropped. Manga: Bufante. Tendência.",
        "base_price": 79.90, "is_active": True,
    },
    {
        "id": "prod-016", "company_id": "scc-002", "sku": "BLU-CIG-001",
        "product_name": "Blusa Ciganinha Ombro a Ombro Sem Manga", "category": "blusa",
        "gender_target": "feminino", "description": "Ciganinha clássica. Tipo: Ciganinha. Manga: Sem Manga. Elástico no ombro.",
        "base_price": 69.90, "is_active": True,
    },
    # ── Fitness ───────────────────────────────────────────────────────────
    {
        "id": "prod-017", "company_id": "tor-001", "sku": "FIT-CON-001",
        "product_name": "Conjunto Fitness Feminino Top e Legging", "category": "conjunto",
        "gender_target": "feminino", "description": "Conjunto esportivo top + legging. Tipo: Fitness. Alta compressão. Dry fit.",
        "base_price": 149.90, "is_active": True,
    },
    {
        "id": "prod-018", "company_id": "tor-001", "sku": "LEG-ALT-001",
        "product_name": "Legging Alta Compressão Feminina", "category": "conjunto",
        "gender_target": "feminino", "description": "Legging modeladora cintura alta. Tipo: Legging. Compressão alta. Academia e corrida.",
        "base_price": 89.90, "is_active": True,
    },
    # ── Jaquetas ──────────────────────────────────────────────────────────
    {
        "id": "prod-019", "company_id": "car-002", "sku": "JAQ-JEA-001",
        "product_name": "Jaqueta Jeans Masculina", "category": "jaqueta",
        "gender_target": "masculino", "description": "Jaqueta jeans lavada com detalhes destroyed. Tipo: Jeans. Manga: Comprida. Streetwear.",
        "base_price": 189.90, "is_active": True,
    },
]

_SEED_VARIANTS = [
    # prod-001 Camisa Slim
    {"id": "var-001", "product_id": "prod-001", "size_label": "M",  "color_name": "Azul Marinho", "color_hex": "#1F2A44", "fabric_type": "Tricoline", "fabric_composition": "100% Algodao", "gsm": 120, "fit_type": "slim", "finish_type": "lavado", "variant_price": 84.90, "stock_qty": 60, "is_active": True},
    {"id": "var-002", "product_id": "prod-001", "size_label": "G",  "color_name": "Branca",       "color_hex": "#FFFFFF", "fabric_type": "Tricoline", "fabric_composition": "100% Algodao", "gsm": 120, "fit_type": "slim", "finish_type": "lavado", "variant_price": 84.90, "stock_qty": 45, "is_active": True},
    {"id": "var-020", "product_id": "prod-001", "size_label": "P",  "color_name": "Preta",        "color_hex": "#000000", "fabric_type": "Tricoline", "fabric_composition": "100% Algodao", "gsm": 120, "fit_type": "slim", "finish_type": "lavado", "variant_price": 84.90, "stock_qty": 30, "is_active": True},
    # prod-003 Camisa Polo
    {"id": "var-021", "product_id": "prod-003", "size_label": "P",  "color_name": "Branca",       "color_hex": "#FFFFFF", "fabric_type": "Piquet",    "fabric_composition": "100% Algodao", "gsm": 180, "fit_type": "regular", "finish_type": "tingido", "variant_price": 94.90, "stock_qty": 50, "is_active": True},
    {"id": "var-022", "product_id": "prod-003", "size_label": "M",  "color_name": "Azul Royal",   "color_hex": "#2563EB", "fabric_type": "Piquet",    "fabric_composition": "100% Algodao", "gsm": 180, "fit_type": "regular", "finish_type": "tingido", "variant_price": 94.90, "stock_qty": 40, "is_active": True},
    {"id": "var-023", "product_id": "prod-003", "size_label": "G",  "color_name": "Verde",        "color_hex": "#16A34A", "fabric_type": "Piquet",    "fabric_composition": "100% Algodao", "gsm": 180, "fit_type": "regular", "finish_type": "tingido", "variant_price": 94.90, "stock_qty": 35, "is_active": True},
    {"id": "var-024", "product_id": "prod-003", "size_label": "GG", "color_name": "Vermelha",     "color_hex": "#DC2626", "fabric_type": "Piquet",    "fabric_composition": "100% Algodao", "gsm": 180, "fit_type": "regular", "finish_type": "tingido", "variant_price": 94.90, "stock_qty": 20, "is_active": True},
    # prod-004 Social Manga Longa
    {"id": "var-025", "product_id": "prod-004", "size_label": "38", "color_name": "Branca",       "color_hex": "#FFFFFF", "fabric_type": "Tricoline", "fabric_composition": "100% Algodao", "gsm": 140, "fit_type": "regular", "finish_type": "plano",   "variant_price": 124.90, "stock_qty": 30, "is_active": True},
    {"id": "var-026", "product_id": "prod-004", "size_label": "40", "color_name": "Azul Claro",   "color_hex": "#93C5FD", "fabric_type": "Tricoline", "fabric_composition": "100% Algodao", "gsm": 140, "fit_type": "regular", "finish_type": "plano",   "variant_price": 124.90, "stock_qty": 25, "is_active": True},
    {"id": "var-027", "product_id": "prod-004", "size_label": "42", "color_name": "Listrada",     "color_hex": "#6B7280", "fabric_type": "Tricoline", "fabric_composition": "100% Algodao", "gsm": 140, "fit_type": "slim",    "finish_type": "plano",   "variant_price": 129.90, "stock_qty": 20, "is_active": True},
    # prod-005 Regata Dry Fit
    {"id": "var-028", "product_id": "prod-005", "size_label": "M",  "color_name": "Preta",        "color_hex": "#000000", "fabric_type": "Dry Fit",   "fabric_composition": "100% Poliester", "gsm": 140, "fit_type": "slim", "finish_type": "sublimado", "variant_price": 44.90, "stock_qty": 80, "is_active": True},
    {"id": "var-029", "product_id": "prod-005", "size_label": "G",  "color_name": "Cinza",        "color_hex": "#9CA3AF", "fabric_type": "Dry Fit",   "fabric_composition": "100% Poliester", "gsm": 140, "fit_type": "slim", "finish_type": "sublimado", "variant_price": 44.90, "stock_qty": 60, "is_active": True},
    {"id": "var-030", "product_id": "prod-005", "size_label": "GG", "color_name": "Amarela",      "color_hex": "#FBBF24", "fabric_type": "Dry Fit",   "fabric_composition": "100% Poliester", "gsm": 140, "fit_type": "slim", "finish_type": "sublimado", "variant_price": 44.90, "stock_qty": 40, "is_active": True},
    # prod-002 Jeans Reto
    {"id": "var-003", "product_id": "prod-002", "size_label": "42", "color_name": "Jeans Escuro", "color_hex": "#213A63", "fabric_type": "Denim",     "fabric_composition": "98% Algodao, 2% Elastano", "gsm": 320, "fit_type": "reto",   "finish_type": "stone washed", "variant_price": 139.90, "stock_qty": 80, "is_active": True},
    {"id": "var-031", "product_id": "prod-002", "size_label": "40", "color_name": "Jeans Claro",  "color_hex": "#60A5FA", "fabric_type": "Denim",     "fabric_composition": "98% Algodao, 2% Elastano", "gsm": 320, "fit_type": "reto",   "finish_type": "stone washed", "variant_price": 139.90, "stock_qty": 60, "is_active": True},
    # prod-007 Skinny Feminina
    {"id": "var-032", "product_id": "prod-007", "size_label": "36", "color_name": "Jeans Escuro", "color_hex": "#213A63", "fabric_type": "Denim",     "fabric_composition": "98% Algodao, 2% Elastano", "gsm": 300, "fit_type": "skinny", "finish_type": "usado",        "variant_price": 149.90, "stock_qty": 50, "is_active": True},
    {"id": "var-033", "product_id": "prod-007", "size_label": "38", "color_name": "Preta",        "color_hex": "#000000", "fabric_type": "Denim",     "fabric_composition": "98% Algodao, 2% Elastano", "gsm": 300, "fit_type": "skinny", "finish_type": "tingido",      "variant_price": 149.90, "stock_qty": 45, "is_active": True},
    # prod-008 Moletom Jogger
    {"id": "var-034", "product_id": "prod-008", "size_label": "M",  "color_name": "Cinza Mescla", "color_hex": "#9CA3AF", "fabric_type": "Moletom",   "fabric_composition": "80% Algodao, 20% Poliester", "gsm": 280, "fit_type": "jogger", "finish_type": "mescla",      "variant_price": 109.90, "stock_qty": 40, "is_active": True},
    {"id": "var-035", "product_id": "prod-008", "size_label": "G",  "color_name": "Preta",        "color_hex": "#000000", "fabric_type": "Moletom",   "fabric_composition": "80% Algodao, 20% Poliester", "gsm": 280, "fit_type": "jogger", "finish_type": "tingido",     "variant_price": 109.90, "stock_qty": 35, "is_active": True},
    # prod-009 Cargo
    {"id": "var-036", "product_id": "prod-009", "size_label": "40", "color_name": "Bege",         "color_hex": "#D4B483", "fabric_type": "Sarja",     "fabric_composition": "100% Algodao", "gsm": 220, "fit_type": "cargo", "finish_type": "lavado",   "variant_price": 129.90, "stock_qty": 30, "is_active": True},
    {"id": "var-037", "product_id": "prod-009", "size_label": "42", "color_name": "Verde Militar","color_hex": "#4B5320", "fabric_type": "Sarja",     "fabric_composition": "100% Algodao", "gsm": 220, "fit_type": "cargo", "finish_type": "lavado",   "variant_price": 129.90, "stock_qty": 25, "is_active": True},
    # prod-010 Bermuda Jeans
    {"id": "var-038", "product_id": "prod-010", "size_label": "36", "color_name": "Jeans Claro",  "color_hex": "#BFDBFE", "fabric_type": "Denim",     "fabric_composition": "98% Algodao, 2% Elastano", "gsm": 280, "fit_type": "regular", "finish_type": "desfiado",    "variant_price": 94.90, "stock_qty": 50, "is_active": True},
    {"id": "var-039", "product_id": "prod-010", "size_label": "38", "color_name": "Jeans Escuro", "color_hex": "#213A63", "fabric_type": "Denim",     "fabric_composition": "98% Algodao, 2% Elastano", "gsm": 280, "fit_type": "regular", "finish_type": "desfiado",    "variant_price": 94.90, "stock_qty": 40, "is_active": True},
    # prod-011 Short Moletom
    {"id": "var-040", "product_id": "prod-011", "size_label": "M",  "color_name": "Cinza Mescla", "color_hex": "#9CA3AF", "fabric_type": "Moletom",   "fabric_composition": "80% Algodao, 20% Poliester", "gsm": 240, "fit_type": "regular", "finish_type": "mescla",     "variant_price": 64.90, "stock_qty": 60, "is_active": True},
    {"id": "var-041", "product_id": "prod-011", "size_label": "G",  "color_name": "Preta",        "color_hex": "#000000", "fabric_type": "Moletom",   "fabric_composition": "80% Algodao, 20% Poliester", "gsm": 240, "fit_type": "regular", "finish_type": "tingido",    "variant_price": 64.90, "stock_qty": 50, "is_active": True},
    # prod-012 Vestido Longo
    {"id": "var-042", "product_id": "prod-012", "size_label": "P",  "color_name": "Floral Rosa",  "color_hex": "#FBCFE8", "fabric_type": "Viscose",   "fabric_composition": "100% Viscose", "gsm": 120, "fit_type": "fluido", "finish_type": "estampado", "variant_price": 164.90, "stock_qty": 30, "is_active": True},
    {"id": "var-043", "product_id": "prod-012", "size_label": "M",  "color_name": "Azul Céu",     "color_hex": "#BAE6FD", "fabric_type": "Viscose",   "fabric_composition": "100% Viscose", "gsm": 120, "fit_type": "fluido", "finish_type": "estampado", "variant_price": 164.90, "stock_qty": 25, "is_active": True},
    {"id": "var-044", "product_id": "prod-012", "size_label": "G",  "color_name": "Preta",        "color_hex": "#000000", "fabric_type": "Viscose",   "fabric_composition": "100% Viscose", "gsm": 120, "fit_type": "fluido", "finish_type": "liso",      "variant_price": 164.90, "stock_qty": 20, "is_active": True},
    # prod-013 Vestido Curto Festa
    {"id": "var-045", "product_id": "prod-013", "size_label": "P",  "color_name": "Dourada",      "color_hex": "#F59E0B", "fabric_type": "Lurex",     "fabric_composition": "85% Poliester, 15% Lurex", "gsm": 160, "fit_type": "tubinho", "finish_type": "brilho", "variant_price": 134.90, "stock_qty": 20, "is_active": True},
    {"id": "var-046", "product_id": "prod-013", "size_label": "M",  "color_name": "Prata",        "color_hex": "#9CA3AF", "fabric_type": "Lurex",     "fabric_composition": "85% Poliester, 15% Lurex", "gsm": 160, "fit_type": "tubinho", "finish_type": "brilho", "variant_price": 134.90, "stock_qty": 15, "is_active": True},
    # prod-014 Vestido Midi
    {"id": "var-047", "product_id": "prod-014", "size_label": "P",  "color_name": "Verde Sage",   "color_hex": "#86EFAC", "fabric_type": "Crepe",     "fabric_composition": "100% Poliester", "gsm": 130, "fit_type": "evasê", "finish_type": "liso",  "variant_price": 124.90, "stock_qty": 25, "is_active": True},
    {"id": "var-048", "product_id": "prod-014", "size_label": "M",  "color_name": "Terracota",    "color_hex": "#C2410C", "fabric_type": "Crepe",     "fabric_composition": "100% Poliester", "gsm": 130, "fit_type": "evasê", "finish_type": "liso",  "variant_price": 124.90, "stock_qty": 20, "is_active": True},
    # prod-015 Blusa Cropped
    {"id": "var-049", "product_id": "prod-015", "size_label": "P",  "color_name": "Rosa Claro",   "color_hex": "#FBCFE8", "fabric_type": "Viscose",   "fabric_composition": "100% Viscose", "gsm": 110, "fit_type": "cropped", "finish_type": "estampado", "variant_price": 84.90, "stock_qty": 35, "is_active": True},
    {"id": "var-050", "product_id": "prod-015", "size_label": "M",  "color_name": "Lilás",        "color_hex": "#C4B5FD", "fabric_type": "Viscose",   "fabric_composition": "100% Viscose", "gsm": 110, "fit_type": "cropped", "finish_type": "liso",      "variant_price": 84.90, "stock_qty": 30, "is_active": True},
    # prod-016 Ciganinha
    {"id": "var-051", "product_id": "prod-016", "size_label": "P",  "color_name": "Branca",       "color_hex": "#FFFFFF", "fabric_type": "Malha",     "fabric_composition": "95% Viscose, 5% Elastano", "gsm": 160, "fit_type": "ciganinha", "finish_type": "liso", "variant_price": 74.90, "stock_qty": 40, "is_active": True},
    {"id": "var-052", "product_id": "prod-016", "size_label": "M",  "color_name": "Vermelha",     "color_hex": "#DC2626", "fabric_type": "Malha",     "fabric_composition": "95% Viscose, 5% Elastano", "gsm": 160, "fit_type": "ciganinha", "finish_type": "liso", "variant_price": 74.90, "stock_qty": 30, "is_active": True},
    # prod-017 Conjunto Fitness
    {"id": "var-053", "product_id": "prod-017", "size_label": "P",  "color_name": "Preta",        "color_hex": "#000000", "fabric_type": "Supplex",   "fabric_composition": "80% Poliamida, 20% Elastano", "gsm": 200, "fit_type": "fitness", "finish_type": "sublimado", "variant_price": 154.90, "stock_qty": 30, "is_active": True},
    {"id": "var-054", "product_id": "prod-017", "size_label": "M",  "color_name": "Rosa Neon",    "color_hex": "#F472B6", "fabric_type": "Supplex",   "fabric_composition": "80% Poliamida, 20% Elastano", "gsm": 200, "fit_type": "fitness", "finish_type": "sublimado", "variant_price": 154.90, "stock_qty": 25, "is_active": True},
    {"id": "var-055", "product_id": "prod-017", "size_label": "G",  "color_name": "Azul Marinho", "color_hex": "#1E3A5F", "fabric_type": "Supplex",   "fabric_composition": "80% Poliamida, 20% Elastano", "gsm": 200, "fit_type": "fitness", "finish_type": "sublimado", "variant_price": 154.90, "stock_qty": 20, "is_active": True},
    # prod-018 Legging
    {"id": "var-056", "product_id": "prod-018", "size_label": "P",  "color_name": "Preta",        "color_hex": "#000000", "fabric_type": "Supplex",   "fabric_composition": "80% Poliamida, 20% Elastano", "gsm": 220, "fit_type": "cintura alta", "finish_type": "liso", "variant_price": 94.90, "stock_qty": 50, "is_active": True},
    {"id": "var-057", "product_id": "prod-018", "size_label": "M",  "color_name": "Verde Militar","color_hex": "#4B5320", "fabric_type": "Supplex",   "fabric_composition": "80% Poliamida, 20% Elastano", "gsm": 220, "fit_type": "cintura alta", "finish_type": "liso", "variant_price": 94.90, "stock_qty": 40, "is_active": True},
    # prod-019 Jaqueta Jeans
    {"id": "var-058", "product_id": "prod-019", "size_label": "M",  "color_name": "Jeans Escuro", "color_hex": "#213A63", "fabric_type": "Denim",     "fabric_composition": "100% Algodao", "gsm": 360, "fit_type": "regular", "finish_type": "destroyed", "variant_price": 194.90, "stock_qty": 20, "is_active": True},
    {"id": "var-059", "product_id": "prod-019", "size_label": "G",  "color_name": "Jeans Claro",  "color_hex": "#BFDBFE", "fabric_type": "Denim",     "fabric_composition": "100% Algodao", "gsm": 360, "fit_type": "regular", "finish_type": "delavê",   "variant_price": 194.90, "stock_qty": 15, "is_active": True},
    # prod-006 Henley
    {"id": "var-060", "product_id": "prod-006", "size_label": "M",  "color_name": "Bege",         "color_hex": "#D4B483", "fabric_type": "Mescla",    "fabric_composition": "60% Algodao, 40% Poliester", "gsm": 160, "fit_type": "regular", "finish_type": "mescla", "variant_price": 74.90, "stock_qty": 35, "is_active": True},
    {"id": "var-061", "product_id": "prod-006", "size_label": "G",  "color_name": "Cinza",        "color_hex": "#9CA3AF", "fabric_type": "Mescla",    "fabric_composition": "60% Algodao, 40% Poliester", "gsm": 160, "fit_type": "regular", "finish_type": "mescla", "variant_price": 74.90, "stock_qty": 30, "is_active": True},
]


def run_seed(db: Session) -> None:
    for u in _SEED_USERS:
        if not db.query(User).filter(User.id == u["id"]).first():
            db.add(User(
                id=u["id"], email=u["email"], role=u["role"], is_active=True,
                company_id=u.get("company_id"),
                hashed_password=_pwd.hash(u["password"]),
            ))

    for c in _SEED_COMPANIES:
        if not db.query(Company).filter(Company.id == c["id"]).first():
            db.add(Company(**c))

    for p in _SEED_PRODUCTS:
        if not db.query(Product).filter(Product.id == p["id"]).first():
            db.add(Product(**p))

    for v in _SEED_VARIANTS:
        if not db.query(ProductVariant).filter(ProductVariant.id == v["id"]).first():
            db.add(ProductVariant(**v))

    db.commit()
