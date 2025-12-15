// src/styles/palette.ts

export type AdminThemeName = "dark" | "light";

export const adminPalette = {
  dark: {
    background1: "#030535ff",
    background2: "#000000ff",

    headerBg1: "#6130aaff",
    headerBg2: "#261c30ff",
    headerText: "#ffffffff",

    cardBg1: "rgba(0, 0, 0, 0.7)",
    cardBg2: "rgba(0, 0, 0, 0.6)",
    cardText: "#DDDDDD",

    mainText: "#ffffffff",

    border1: "#ffffffff",
    border2: "#ffffffff",

    shadow1: "rgba(114, 45, 114, 0.41)",
    shadow2: "rgba(0, 0, 0, 0.41)",

    glassReflex: "rgba(248, 243, 243, 1)",

    button1: "#0428f5ff",
    button2: "#0428f5ff",

    fieldBg: "#ffffffff",
    fieldText: "#ffffffff",

    footerBg1: "#0a0a0a",
    footerBg2: "#1a1a1a",
    footerText: "#CCCCCC",
  },

  light: {
    background1: "#FBFBFB",
    background2: "#FBFBFB",

    headerBg1: "#ffffffff",
    headerBg2: "#ffffffff",
    headerText: "#020649ff",

    cardBg1: "#e2e2e2ff",
    cardBg2: "#F8F8F8",
    cardText: "#333333",

    mainText: "#030863ff",

    border1: "#000000ff",
    border2: "#000000ff",

    shadow1: "rgba(0, 0, 0, 0.25)",
    shadow2: "hsla(0, 0%, 0%, 0.28)",

    glassReflex: "rgba(255,255,255,0.25)",

    button1: "#C7DB9C",
    button2: "#C7DB9C",

    fieldBg: "#8b8989ff",
    fieldText: "#222222",

    footerBg1: "#F0F0F0",
    footerBg2: "#FFFFFF",
    footerText: "#555555",
  },
} as const;

export type AdminPalette = typeof adminPalette;
export type AdminTheme = keyof AdminPalette;
