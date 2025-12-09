"use client";

import Sidebar from "./Sidebar";
import Header from "./Header";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        <Header />
        <main className="p-6 bg-gray-50 dark:bg-gray-800 min-h-screen">
          {children}
        </main>
      </div>
    </div>
  );
}
