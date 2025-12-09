"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const menu = [
    { label: "داشبورد", path: "/dashboard" },
    { label: "کاربران", path: "/users" },
    { label: "KYC", path: "/kyc" },
    { label: "تراکنش‌ها", path: "/finance" },
    { label: "تنظیمات", path: "/settings" },
  ];

  return (
    <div className="w-64 h-screen bg-gray-200 dark:bg-gray-900 p-4 text-gray-900 dark:text-gray-200">
      <h2 className="text-xl font-bold mb-6">NOWEX Admin</h2>

      <nav className="flex flex-col gap-3">
        {menu.map((item) => (
          <Link
            key={item.path}
            href={item.path}
            className={`p-2 rounded-md transition ${
              pathname === item.path
                ? "bg-gray-300 dark:bg-gray-700"
                : "hover:bg-gray-300 dark:hover:bg-gray-800"
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </div>
  );
}
