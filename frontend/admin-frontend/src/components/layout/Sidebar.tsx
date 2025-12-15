"use client";

import { useTheme } from "@/contexts/ThemeContext";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import {
  FiChevronRight,
  FiChevronLeft,
  FiUsers,
  FiSettings,
  FiHome,
  FiShield,
  FiMapPin,
  FiChevronDown
} from "react-icons/fi";

export default function Sidebar() {
  const { colors } = useTheme();
  const pathname = usePathname();
  const router = useRouter();

  const [collapsed, setCollapsed] = useState(false);
  const [pinned, setPinned] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [openMenu, setOpenMenu] = useState(null);

  const toggleSidebar = () => {
    if (!pinned) setCollapsed(!collapsed);
  };

  const menuTree = [
    {
      label: "داشبورد",
      href: "/dashboard",
      icon: <FiHome size={20} />
    },
    {
      label: "مدیریت ادمین‌ها",
      href: "/admins",
      icon: <FiShield size={20} />,
      children: [
        { label: "لیست ادمین‌ها", href: "/admins/list" },
        { label: "افزودن ادمین", href: "/admins/new" }
      ]
    },
    {
      label: "مدیریت کاربران",
      href: "/users",
      icon: <FiUsers size={20} />,
      children: [
        { label: "لیست کاربران", href: "/users/list" },
        { label: "کاربران جدید", href: "/users/new" },
        {
          label: "گزارش‌ها",
          href: "/users/reports",
          children: [
            { label: "گزارش مالی", href: "/users/reports/finance" },
            { label: "گزارش فعالیت", href: "/users/reports/activity" }
          ]
        }
      ]
    },
    {
      label: "مدیریت تراکنش‌ها",
      href: "/transactions",
      icon: <FiSettings size={20} />,
      children: [
        { label: "لیست تراکنش‌ها", href: "/transactions/list" },
        { label: "درخواست‌های برداشت", href: "/transactions/withdraw" },
        { label: "درخواست‌های واریز", href: "/transactions/deposit" }
      ]
    },
    {
      label: "مانیتورینگ سیستم",
      href: "/monitoring",
      icon: <FiSettings size={20} />,
      children: [
        { label: "وضعیت سرورها", href: "/monitoring/servers" },
        { label: "لاگ‌ها", href: "/monitoring/logs" },
        { label: "هشدارها", href: "/monitoring/alerts" }
      ]
    },
    {
      label: "تنظیمات سیستم",
      href: "/settings",
      icon: <FiSettings size={20} />
    }
  ];

  const searchTree = (items, term) => {
    return items
      .map((item) => {
        const match = item.label.toLowerCase().includes(term.toLowerCase());
        const children = item.children ? searchTree(item.children, term) : [];

        if (match || children.length > 0) {
          return { ...item, children };
        }
        return null;
      })
      .filter(Boolean);
  };

  const filteredTree = searchTerm.trim().length > 0 ? searchTree(menuTree, searchTerm) : menuTree;
  return (
    <aside
      className={`relative h-screen overflow-y-auto scrollbar-thin p-4 flex flex-col transition-all duration-300 ${
        collapsed ? "w-20" : "w-64"
      }`}
      style={{
        background: `linear-gradient(180deg, ${colors.cardBg1}, ${colors.cardBg2})`,
        borderLeft: `1px solid ${colors.border1}`
      }}
    >
      
      {/* دکمه‌های کوچک زیر لوگو */}
      <div className="flex items-center justify-center gap-2 mb-4">
        <button
          onClick={toggleSidebar}
          className="p-1.5 rounded-full shadow-md transition-all"
          style={{
            background: colors.button1,
            color: colors.headerText,
            border: `1px solid ${colors.border1}`
          }}
        >
          {collapsed ? <FiChevronRight size={12} /> : <FiChevronLeft size={12} />}
        </button>

        <button
          onClick={() => setPinned(!pinned)}
          className="p-1.5 rounded-full shadow-md transition-all"
          style={{
            background: pinned ? colors.headerBg1 : colors.button1,
            color: colors.headerText,
            border: `1px solid ${colors.border1}`
          }}
        >
          <FiMapPin size={12} />
        </button>
      </div>

      {/* فیلد جستجو */}
      {!collapsed && (
        <input
          type="text"
          placeholder="جستجوی منو..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="mb-6 px-3 py-2 rounded-md outline-none transition-all"
          style={{
            background: colors.headerBg1,
            color: colors.headerText,
            border: `1px solid ${colors.border1}`
          }}
        />
      )}

      {/* شروع رندر منوها */}
      <nav className="flex flex-col gap-2">
        {filteredTree.map((item) => {
          const isActive = pathname.startsWith(item.href);
          const isOpen = openMenu === item.label;
          const hasChildren = item.children && item.children.length > 0;

          return (
            <div key={item.label}>
              {/* ردیف اصلی */}
              <button
                onClick={() => {
                  if (hasChildren) {
                    setOpenMenu(isOpen ? null : item.label);
                  } else {
                    router.push(item.href);
                  }
                }}
                className="w-full flex items-center justify-between px-4 py-2 rounded-md transition-all"
                style={{
                  background: isActive ? colors.headerBg1 : "transparent",
                  color: isActive ? colors.headerText : colors.mainText,
                  border: isActive ? `1px solid ${colors.border1}` : "none"
                }}
              >
                <div className="flex items-center gap-3">
                  {item.icon}
                  {!collapsed && item.label}
                </div>

                {!collapsed && hasChildren && (
                  <FiChevronDown
                    size={14}
                    className={`transition-transform duration-300 ${isOpen ? "rotate-180" : "rotate-0"}`}
                  />
                )}
              </button>

              {/* زیرمنوهای سطح ۱ */}
              {hasChildren && (
                <div
                  className="overflow-hidden transition-all duration-300"
                  style={{ height: isOpen ? "auto" : "0px" }}
                >
                  <div className="flex flex-col pr-6 mt-1">
                    {item.children.map((child) => {
                      const childActive = pathname.startsWith(child.href);
                      const childHasChildren = child.children && child.children.length > 0;
                      const childIsOpen = openMenu === child.label;

                      return (
                        <div key={child.label}>
                          {/* ردیف زیرمنو سطح ۱ */}
                          <button
                            onClick={() => {
                              if (childHasChildren) {
                                setOpenMenu(childIsOpen ? null : child.label);
                              } else {
                                router.push(child.href);
                              }
                            }}
                            className="w-full flex items-center justify-between px-3 py-2 rounded-md transition-all"
                            style={{
                              background: childActive ? colors.headerBg1 : "transparent",
                              color: childActive ? colors.headerText : colors.mainText,
                              border: childActive ? `1px solid ${colors.border1}` : "none"
                            }}
                          >
                            <span>{child.label}</span>

                            {childHasChildren && (
                              <FiChevronDown
                                size={12}
                                className={`transition-transform duration-300 ${childIsOpen ? "rotate-180" : "rotate-0"}`}
                              />
                            )}
                          </button>

                          {/* زیرمنوهای سطح ۲ */}
                          {childHasChildren && (
                            <div
                              className="overflow-hidden transition-all duration-300"
                              style={{ height: childIsOpen ? "auto" : "0px" }}
                            >
                              <div className="flex flex-col pr-8 mt-1">
                                {child.children.map((sub) => {
                                  const subActive = pathname.startsWith(sub.href);

                                  return (
                                    <button
                                      key={sub.label}
                                      onClick={() => router.push(sub.href)}
                                      className="w-full text-right px-3 py-2 rounded-md transition-all"
                                      style={{
                                        background: subActive ? colors.headerBg1 : "transparent",
                                        color: subActive ? colors.headerText : colors.mainText,
                                        border: subActive ? `1px solid ${colors.border1}` : "none"
                                      }}
                                    >
                                      {sub.label}
                                    </button>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {/* اگر جستجو نتیجه نداشت */}
        {filteredTree.length === 0 && !collapsed && (
          <div className="text-center py-4 text-sm opacity-70" style={{ color: colors.mainText }}>
            نتیجه‌ای یافت نشد
          </div>
        )}
      </nav>
    </aside>
  );
}
