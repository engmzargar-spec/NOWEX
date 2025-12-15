"use client";

import { useTheme } from "@/contexts/ThemeContext";

export default function Header() {
  const { colors, toggleTheme, theme } = useTheme();

  return (
    <header
      className="w-full flex items-center justify-between px-6 py-4 shadow-md"
      style={{
        background: `linear-gradient(90deg, ${colors.headerBg1}, ${colors.headerBg2})`,
        color: colors.headerText,
        borderBottom: `1px solid ${colors.border1}`,
      }}
    >
      {/* Title */}
      <h1 className="text-xl font-semibold tracking-wide">
        NOWEX Admin Panel
      </h1>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="px-4 py-2 rounded-md transition-all"
          style={{
            background: colors.button1,
            color: colors.headerText,
            border: `1px solid ${colors.border1}`,
          }}
        >
          {theme === "dark" ? "Light Mode" : "Dark Mode"}
        </button>

        {/* Admin Profile */}
        <div
          className="px-4 py-2 rounded-md"
          style={{
            background: colors.cardBg1,
            border: `1px solid ${colors.border1}`,
          }}
        >
          Admin
        </div>
      </div>
    </header>
  );
}
