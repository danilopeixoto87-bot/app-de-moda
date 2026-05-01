"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { API_BASE } from "./api";

type Company = {
  id: string;
  trade_name: string;
  company_type: "loja" | "fabrica" | "faccao" | "atacadista";
  city: string;
  neighborhood?: string;
  whatsapp?: string;
  latitude?: number;
  longitude?: number;
  distance_km?: number;
};

type ApiResponse = {
  count: number;
  total: number;
  items: Company[];
};

const FALLBACK_CENTER: [number, number] = [-8.2845, -35.9699];

function MapUpdater({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => { map.setView(center, map.getZoom()); }, [center, map]);
  return null;
}

const markerIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function MapaEmpresasPage() {
  const [city, setCity] = useState("");
  const [companyType, setCompanyType] = useState("");
  const [query, setQuery] = useState("");
  const [userLat, setUserLat] = useState<number | null>(null);
  const [userLng, setUserLng] = useState<number | null>(null);

  const [companies, setCompanies] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchCompanies = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (city) params.set("city", city);
      if (companyType) params.set("type", companyType);
      if (query.trim()) params.set("q", query.trim());
      if (userLat !== null) params.set("lat", String(userLat));
      if (userLng !== null) params.set("lng", String(userLng));

      const res = await fetch(`${API_BASE}/companies?${params.toString()}`);
      if (!res.ok) throw new Error(`Erro ${res.status} ao buscar empresas`);
      const data: ApiResponse = await res.json();
      setCompanies(data.items);
      setTotal(data.total ?? data.count);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro ao carregar empresas");
    } finally {
      setLoading(false);
    }
  }, [city, companyType, query, userLat, userLng]);

  const openCompanyLink = useCallback(async (companyId: string, linkType: "navigation-link" | "whatsapp-link") => {
    try {
      const res = await fetch(`${API_BASE}/companies/${companyId}/${linkType}`);
      if (!res.ok) throw new Error("Falha ao gerar link");
      const payload = (await res.json()) as Record<string, string>;
      // navigation-link retorna {google_maps, waze}; whatsapp-link retorna {whatsapp_url}
      const url = payload.google_maps ?? payload.whatsapp_url;
      if (!url) throw new Error("Resposta sem URL");
      window.open(url, "_blank", "noopener,noreferrer");
    } catch {
      setError("Não foi possível abrir o link externo da empresa.");
    }
  }, []);

  const companiesWithCoords = useMemo(
    () =>
      companies.filter(
        (company) => typeof company.latitude === "number" && typeof company.longitude === "number",
      ),
    [companies],
  );

  const mapCenter = useMemo<[number, number]>(() => {
    if (userLat !== null && userLng !== null) return [userLat, userLng];
    if (companiesWithCoords.length > 0) {
      return [companiesWithCoords[0].latitude as number, companiesWithCoords[0].longitude as number];
    }
    return FALLBACK_CENTER;
  }, [companiesWithCoords, userLat, userLng]);

  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  function requestLocation() {
    if (!navigator.geolocation) return setError("Geolocalização não suportada neste dispositivo");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLat(pos.coords.latitude);
        setUserLng(pos.coords.longitude);
      },
      () => setError("Permissão de localização negada"),
    );
  }

  return (
    <main style={{ padding: 16, maxWidth: 720, margin: "0 auto", fontFamily: "ui-sans-serif, system-ui" }}>
      <h1 style={{ fontSize: 22, marginBottom: 4 }}>Mapa de Empresas de Moda</h1>
      <p style={{ marginTop: 0, color: "#555", fontSize: 14 }}>
        {total > 0 ? `${total} empresa(s) encontrada(s)` : "Buscando..."}
      </p>

      <section style={{ display: "grid", gap: 8, marginBottom: 12 }}>
        <input
          placeholder="Buscar por nome ou bairro"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && fetchCompanies()}
        />

        <select value={city} onChange={(e) => setCity(e.target.value)}>
          <option value="">Todas as cidades</option>
          <option value="Caruaru">Caruaru</option>
          <option value="Santa Cruz do Capibaribe">Santa Cruz do Capibaribe</option>
          <option value="Toritama">Toritama</option>
        </select>

        <select value={companyType} onChange={(e) => setCompanyType(e.target.value)}>
          <option value="">Todos os tipos</option>
          <option value="loja">Loja</option>
          <option value="fabrica">Fábrica</option>
          <option value="faccao">Facção</option>
          <option value="atacadista">Atacadista</option>
        </select>

        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={fetchCompanies} disabled={loading}>
            {loading ? "Buscando..." : "Buscar"}
          </button>
          <button onClick={requestLocation} style={{ background: "#e8f5e9" }}>
            📍 Usar minha localização
          </button>
        </div>
      </section>

      {error && (
        <div style={{ background: "#ffebee", padding: 12, borderRadius: 8, marginBottom: 12, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <p style={{ color: "#b00020", fontSize: 14, margin: 0 }}>{error}</p>
          <button onClick={() => { setError(""); fetchCompanies(); }} style={{ fontSize: 12, padding: "4px 8px" }}>
            Tentar novamente
          </button>
        </div>
      )}

      {userLat !== null && (
        <p style={{ fontSize: 13, color: "#388e3c" }}>
          Localização ativa — empresas ordenadas por distância
        </p>
      )}

      <section style={{ marginBottom: 14, border: "1px solid #ddd", borderRadius: 10, overflow: "hidden" }}>
        <MapContainer center={mapCenter} zoom={11} style={{ width: "100%", height: 320 }}>
          <MapUpdater center={mapCenter} />
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {companiesWithCoords.map((c) => (
            <Marker key={c.id} position={[c.latitude as number, c.longitude as number]} icon={markerIcon}>
              <Popup>
                <strong>{c.trade_name}</strong>
                <div>{c.city}</div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </section>

      <section style={{ display: "grid", gap: 10 }}>
        {companies.length === 0 && !loading && (
          <p style={{ color: "#777" }}>Nenhuma empresa encontrada com os filtros selecionados.</p>
        )}

        {companies.map((c) => (
          <article key={c.id} style={{ border: "1px solid #ddd", borderRadius: 10, padding: 12 }}>
            <strong style={{ fontSize: 16 }}>{c.trade_name}</strong>
            <div style={{ color: "#555", fontSize: 14, marginTop: 2 }}>
              {c.city}{c.neighborhood ? ` — ${c.neighborhood}` : ""}
            </div>
            <div style={{ fontSize: 13, color: "#777" }}>
              {c.company_type}
              {c.distance_km !== undefined && ` · ${c.distance_km.toFixed(1)} km`}
            </div>
            <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
              <button
                type="button"
                onClick={() => openCompanyLink(c.id, "navigation-link")}
                style={{ fontSize: 13, color: "#1565c0" }}
              >
                Como chegar
              </button>
              {c.whatsapp && (
                <button
                  type="button"
                  onClick={() => openCompanyLink(c.id, "whatsapp-link")}
                  style={{ fontSize: 13, color: "#2e7d32" }}
                >
                  WhatsApp
                </button>
              )}
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
