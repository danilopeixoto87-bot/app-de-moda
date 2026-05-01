"use client";
import dynamic from "next/dynamic";

const MapaEmpresasPage = dynamic(
  () => import("@/features/mapa-empresas/MapaEmpresasPage"),
  { ssr: false, loading: () => <p style={{ padding: 24 }}>Carregando mapa...</p> }
);

export default function MapaPage() {
  return <MapaEmpresasPage />;
}
