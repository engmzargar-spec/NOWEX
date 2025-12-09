import "./globals.css";
import { ThemeProvider } from "../contexts/ThemeContext";

export const metadata = {
  title: "NOWEX Admin Panel",
  description: "پنل مدیریت نواکس",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fa" dir="rtl">
      <body className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
