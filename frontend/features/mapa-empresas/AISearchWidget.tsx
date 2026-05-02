"use client";

import { useState, useRef } from "react";
import { aiSearch, type AISearchResult } from "./api";

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export default function AISearchWidget() {
  const [text, setText] = useState("");
  const [listening, setListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AISearchResult | null>(null);
  const [error, setError] = useState("");
  const [location, setLocation] = useState<{ lat: number; lon: number } | null>(null);
  const recognitionRef = useRef<any>(null);

  function requestLocation() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => setLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      () => {}
    );
  }

  function startVoice() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      setError("Seu navegador não suporta reconhecimento de voz. Use Chrome ou Edge.");
      return;
    }
    const rec = new SR();
    rec.lang = "pt-BR";
    rec.continuous = false;
    rec.interimResults = false;
    rec.onstart = () => setListening(true);
    rec.onend = () => setListening(false);
    rec.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript;
      setText(transcript);
      handleSearch(transcript);
    };
    rec.onerror = () => {
      setListening(false);
      setError("Não foi possível captar o áudio. Tente digitar.");
    };
    recognitionRef.current = rec;
    rec.start();
    requestLocation();
  }

  function stopVoice() {
    recognitionRef.current?.stop();
    setListening(false);
  }

  async function handleSearch(query?: string) {
    const q = (query ?? text).trim();
    if (!q) { setError("Descreva o produto que você procura."); return; }
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const data = await aiSearch(q, location ?? undefined);
      setResult(data);
    } catch (e: any) {
      setError(e?.message || "Erro na busca por IA");
    } finally {
      setLoading(false);
    }
  }

  const waLink = (whatsapp: string, loja: string, query: string) => {
    const clean = whatsapp.replace(/\D/g, "");
    const msg = encodeURIComponent(`Olá! Procuro: "${query}". Vi que a ${loja} tem esse produto no App de Moda do Agreste.`);
    return `https://wa.me/${clean}?text=${msg}`;
  };

  return (
    <div style={{ background: "linear-gradient(135deg,#f0f4ff,#fff)", border: "1.5px solid #c7d2fe", borderRadius: 16, padding: "20px 18px", margin: "16px 0" }}>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
        <div style={{ width: 40, height: 40, borderRadius: 12, background: "linear-gradient(135deg,#6366f1,#8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, flexShrink: 0 }}>
          🤖
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 15, color: "#1e1b4b" }}>Assistente de Compra por IA</div>
          <div style={{ fontSize: 12, color: "#6b7280" }}>Fale ou escreva o que procura — a IA encontra as melhores lojas</div>
        </div>
      </div>

      {/* Input + botões */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder='Ex: "camisa polo azul algodão tamanho G"'
          style={{ flex: 1, minWidth: 200, padding: "11px 14px", borderRadius: 10, border: "1.5px solid #c7d2fe", fontSize: 14, outline: "none" }}
        />

        {/* Botão microfone */}
        <button
          onClick={listening ? stopVoice : startVoice}
          disabled={loading}
          title={listening ? "Parar gravação" : "Buscar por voz"}
          style={{
            padding: "11px 14px",
            borderRadius: 10,
            border: "none",
            background: listening ? "#ef4444" : "#6366f1",
            color: "#fff",
            fontSize: 18,
            cursor: "pointer",
            animation: listening ? "pulse 1s infinite" : "none",
          }}
        >
          {listening ? "⏹" : "🎤"}
        </button>

        {/* Botão pesquisar */}
        <button
          onClick={() => handleSearch()}
          disabled={loading || !text.trim()}
          style={{
            padding: "11px 18px",
            borderRadius: 10,
            border: "none",
            background: loading ? "#a5b4fc" : "#4f46e5",
            color: "#fff",
            fontWeight: 700,
            fontSize: 14,
            cursor: loading ? "default" : "pointer",
          }}
        >
          {loading ? "Buscando..." : "Encontrar lojas"}
        </button>
      </div>

      {listening && (
        <div style={{ marginTop: 10, padding: "8px 12px", background: "#fef2f2", borderRadius: 8, color: "#b91c1c", fontSize: 13, display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", background: "#ef4444", animation: "pulse 1s infinite" }} />
          Ouvindo... fale o nome e características do produto
        </div>
      )}

      {error && (
        <div style={{ marginTop: 10, color: "#b91c1c", fontSize: 13 }}>{error}</div>
      )}

      {/* Resultado */}
      {result && (
        <div style={{ marginTop: 16 }}>
          {!result.found ? (
            <div style={{ color: "#6b7280", fontSize: 14 }}>
              Nenhuma loja encontrada para "<strong>{result.query}</strong>". Tente outras palavras.
            </div>
          ) : (
            <>
              <div style={{ fontSize: 13, color: "#6b7280", marginBottom: 12 }}>
                Encontrei <strong>{result.products_matched}</strong> produto(s) para "<strong>{result.query}</strong>"
              </div>

              <div style={{ display: "grid", gap: 12, gridTemplateColumns: result.nearest.length > 0 ? "1fr 1fr" : "1fr" }}>

                {/* Top 5 mais próximas */}
                {result.nearest.length > 0 && (
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 13, color: "#1e40af", marginBottom: 8, display: "flex", alignItems: "center", gap: 6 }}>
                      📍 Lojas mais próximas
                    </div>
                    {result.nearest.map((c, i) => (
                      <div key={c.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid #e0e7ff" }}>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 13, color: "#1e1b4b" }}>
                            {i + 1}. {c.trade_name}
                          </div>
                          <div style={{ fontSize: 12, color: "#6b7280" }}>
                            {c.neighborhood}, {c.city}
                            {c.distance_km !== undefined && ` · ${c.distance_km} km`}
                          </div>
                          {c.min_price && (
                            <div style={{ fontSize: 12, color: "#16a34a", fontWeight: 600 }}>
                              a partir de R$ {c.min_price.toFixed(2).replace(".", ",")}
                            </div>
                          )}
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                          <a href={c.storefront_url} target="_blank" rel="noreferrer"
                            style={{ fontSize: 11, background: "#1e1b4b", color: "#fff", padding: "4px 8px", borderRadius: 6, textDecoration: "none", textAlign: "center" }}>
                            Ver loja
                          </a>
                          <a href={waLink(c.whatsapp, c.trade_name, result.query)} target="_blank" rel="noreferrer"
                            style={{ fontSize: 11, background: "#25d366", color: "#fff", padding: "4px 8px", borderRadius: 6, textDecoration: "none", textAlign: "center" }}>
                            WhatsApp
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Top 5 mais baratas */}
                <div>
                  <div style={{ fontWeight: 700, fontSize: 13, color: "#15803d", marginBottom: 8, display: "flex", alignItems: "center", gap: 6 }}>
                    💰 Melhores preços
                  </div>
                  {result.cheapest.map((c, i) => (
                    <div key={c.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid #dcfce7" }}>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 13, color: "#1e1b4b" }}>
                          {i + 1}. {c.trade_name}
                        </div>
                        <div style={{ fontSize: 12, color: "#6b7280" }}>
                          {c.neighborhood}, {c.city}
                        </div>
                        {c.min_price != null && (
                          <div style={{ fontSize: 13, color: "#15803d", fontWeight: 700 }}>
                            R$ {c.min_price.toFixed(2).replace(".", ",")}
                          </div>
                        )}
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                        <a href={c.storefront_url} target="_blank" rel="noreferrer"
                          style={{ fontSize: 11, background: "#1e1b4b", color: "#fff", padding: "4px 8px", borderRadius: 6, textDecoration: "none", textAlign: "center" }}>
                          Ver loja
                        </a>
                        <a href={waLink(c.whatsapp, c.trade_name, result.query)} target="_blank" rel="noreferrer"
                          style={{ fontSize: 11, background: "#25d366", color: "#fff", padding: "4px 8px", borderRadius: 6, textDecoration: "none", textAlign: "center" }}>
                          WhatsApp
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {!result.nearest.length && (
                <div style={{ marginTop: 8, fontSize: 12, color: "#9ca3af" }}>
                  💡 Permita a localização no navegador para ver as lojas mais próximas de você
                </div>
              )}
            </>
          )}
        </div>
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}
