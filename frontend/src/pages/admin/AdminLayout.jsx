import { useEffect, useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { ShieldCheck, SquaresFour, Key, ListChecks, ChartBar, Gear, SignOut } from "@phosphor-icons/react";

const links = [
  { to: "/admin", label: "Dashboard", icon: SquaresFour, end: true },
  { to: "/admin/tokens", label: "Token", icon: Key },
  { to: "/admin/questions", label: "Bank Soal", icon: ListChecks },
  { to: "/admin/results", label: "Hasil & Analitik", icon: ChartBar },
  { to: "/admin/settings", label: "Konfigurasi", icon: Gear },
];

export default function AdminLayout() {
  const nav = useNavigate();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("admin_token")) { nav("/admin/login"); return; }
    api.get("/auth/me").then(() => setReady(true)).catch(() => {
      localStorage.removeItem("admin_token");
      nav("/admin/login");
    });
  }, [nav]);

  const logout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    nav("/admin/login");
  };

  if (!ready) return <div className="min-h-screen flex items-center justify-center text-zinc-400">Memuat...</div>;

  return (
    <div className="min-h-screen bg-zinc-50 flex text-left">
      <aside className="w-64 shrink-0 bg-white border-r border-zinc-200 flex flex-col fixed inset-y-0">
        <div className="flex items-center gap-2 px-6 h-16 border-b border-zinc-200">
          <ShieldCheck size={22} weight="fill" className="text-[#0055FF]" />
          <span className="font-semibold tracking-tight">SecureCBT</span>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {links.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} data-testid={`nav-${label.toLowerCase().replace(/[^a-z]/g, "-")}`}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-sm font-medium ${isActive ? "bg-zinc-900 text-white" : "text-zinc-600 hover:bg-zinc-100"}`}>
              <Icon size={18} /> {label}
            </NavLink>
          ))}
        </nav>
        <button onClick={logout} data-testid="admin-logout-btn"
          className="flex items-center gap-3 px-6 py-4 text-sm text-zinc-500 hover:text-zinc-900 border-t border-zinc-200">
          <SignOut size={18} /> Keluar
        </button>
      </aside>
      <main className="flex-1 ml-64 p-8">
        <Outlet />
      </main>
    </div>
  );
}
