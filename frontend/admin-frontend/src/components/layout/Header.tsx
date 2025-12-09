"use client";

import { useTheme } from "../../contexts/ThemeContext";
import { SunIcon, MoonIcon } from "@heroicons/react/24/outline";

export default function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="w-full h-16 bg-gray-100 dark:bg-gray-800 flex items-center justify-between px-6 shadow">
      <h1 className="text-lg font-semibold">پنل مدیریت نواکس</h1>

      <button
        onClick={toggleTheme}
        className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition"
      >
        {theme === "light" ? (
          <MoonIcon className="w-6 h-6" />
        ) : (
          <SunIcon className="w-6 h-6" />
        )}
      </button>
    </header>
  );
}
