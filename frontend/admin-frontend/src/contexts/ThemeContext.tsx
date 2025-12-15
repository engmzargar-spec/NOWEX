"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { adminPalette, AdminThemeName } from "@/styles/palette";

type ThemeContextType = {
  theme: AdminThemeName;
  colors: typeof adminPalette.dark;
  toggleTheme: () => void;
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<AdminThemeName>("dark");

  // Load theme from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("admin-theme") as AdminThemeName | null;
    if (saved) setTheme(saved);
  }, []);

  // Save theme to localStorage
  useEffect(() => {
    localStorage.setItem("admin-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const colors = adminPalette[theme];

  return (
    <ThemeContext.Provider value={{ theme, colors, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used inside ThemeProvider");
  return ctx;
}
