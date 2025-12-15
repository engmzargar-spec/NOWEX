"use client";

import { useTheme } from "@/contexts/ThemeContext";
import Header from "./Header";
import Sidebar from "./Sidebar";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { colors } = useTheme();

  return (
    <div
      className="min-h-screen flex"
      style={{
        background: `linear-gradient(135deg, ${colors.background1}, ${colors.background2})`,
        color: colors.mainText,
      }}
    >
      {/* Sidebar */}
      <Sidebar />

      {/* Main Section */}
      <div className="flex-1 flex flex-col">
        <Header />

        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
