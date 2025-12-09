"use client";

import { useState } from "react";
import { useTheme } from "../../contexts/ThemeContext";

export default function LoginPage() {
  const { isDarkMode, toggleTheme } = useTheme();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Login:", { username, password });
  };

  return (
    <main
      className="
        min-h-screen 
        flex items-center justify-center 
        bg-gradient-to-br 
        from-background 
        via-background/80 
        to-primary/10 
        dark:from-background 
        dark:via-background/70 
        dark:to-primary/20
        transition-all
        relative
      "
    >
      {/* Theme Toggle Icon Top Left */}
      <button
        onClick={toggleTheme}
        className="
          absolute top-6 left-6 
          text-2xl 
          bg-background/30 
          dark:bg-background/40 
          p-2 rounded-full 
          border border-border 
          hover:opacity-80 transition
        "
        aria-label="Toggle Theme"
      >
        {isDarkMode ? "☀️" : "🌙"}
      </button>

      <div className="w-full max-w-md bg-background/60 dark:bg-background/40 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-border">
        
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <img
            src={isDarkMode ? "/nowex-dark.png" : "/nowex-light.png"}
            alt="NOWEX Logo"
            className="w-20 h-20 mb-4 opacity-90 transition-all"
          />
          <h1 className="text-2xl font-bold">ورود به پنل مدیریت</h1>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block mb-2 text-sm font-medium">نام کاربری</label>
            <input
              type="text"
              className="w-full px-4 py-3 rounded-xl bg-background border border-border focus:ring-2 focus:ring-primary outline-none transition"
              placeholder="admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div>
            <label className="block mb-2 text-sm font-medium">رمز عبور</label>
            <input
              type="password"
              className="w-full px-4 py-3 rounded-xl bg-background border border-border focus:ring-2 focus:ring-primary outline-none transition"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-semibold hover:opacity-90 transition text-lg"
          >
            ورود
          </button>
        </form>

        <p className="text-center text-sm mt-6 opacity-70">
          نسخه آزمایشی پنل مدیریت NOWEX
        </p>
      </div>
    </main>
  );
}
