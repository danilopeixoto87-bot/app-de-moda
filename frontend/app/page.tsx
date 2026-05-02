"use client";

import { useEffect, useState } from "react";
import PortalCentralPage from "@/features/mapa-empresas/PortalCentralPage";

const API_ROOT = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://app-de-moda-production.up.railway.app/api")
  .replace(/\/api$/, "");

export default function Home() {
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  useEffect(() => {
    fetch(`${API_ROOT}/health`)
      .then((r) => setBackendOk(r.ok))
      .catch(() => setBackendOk(false));
  }, []);

  return (
    <>
      {backendOk === false && (
        <div style={{
          background: "#fef2f2", color: "#b91c1c",
          padding: "8px 16px", fontSize: 13, textAlign: "center"
        }}>
          Backend indisponível no momento
        </div>
      )}
      <PortalCentralPage />
    </>
  );
}
