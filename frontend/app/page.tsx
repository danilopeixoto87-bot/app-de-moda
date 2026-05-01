import Link from "next/link";
import PortalCentralPage from "@/features/mapa-empresas/PortalCentralPage";

const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://app-de-moda-production.up.railway.app/api";

async function getBackendStatus() {
  try {
    const res = await fetch(`${API.replace("/api", "")}/health`, { cache: "no-store" });
    if (res.ok) {
      const data = await res.json();
      return { ok: true, version: data.version ?? "?" };
    }
    return { ok: false, version: null };
  } catch {
    return { ok: false, version: null };
  }
}

export default async function Home() {
  const status = await getBackendStatus();

  return (
    <>
      {/* Status bar — only visible when backend is down */}
      {!status.ok && (
        <div style={{ background: "#fef2f2", color: "#b91c1c", padding: "8px 16px", fontSize: 13, textAlign: "center" }}>
          ⚠️ Backend indisponível no momento
        </div>
      )}
      <PortalCentralPage />
    </>
  );
}
