import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  applicationName: "Polícia Militar do Estado do Acre",
  title: "PMAC | Consulta Funcional",
  description: "Consulta exploratória de correspondências entre formação acadêmica e áreas funcionais previstas na estrutura da Polícia Militar do Estado do Acre.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
