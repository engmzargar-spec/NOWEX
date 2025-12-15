"use client";

import { useTheme } from "../theme/ThemeContext";
import { useEffect, useState } from "react";

export default function Logo({ className = "" }) {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null; // جلوگیری از Hydration Error

  const src =
    theme === "dark"
      ? "/nowex-dark.png"
      : "/nowex-light.png";

  return (
    <img
      src={src}
      alt="NOWEX Logo"
      className={`transition-all ${className}`}
    />
  );
}
