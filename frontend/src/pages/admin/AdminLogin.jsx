import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API, errDetail } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { ShieldCheck } from "@phosphor-icons/react";

export default function AdminLogin() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await axios.post(`${API}/auth/login`, { email, password });
      localStorage.setItem("admin_token", data.access_token);
      localStorage.setItem("admin_user", JSON.stringify(data.user));
      nav("/admin");
    } catch (err) {
      setError(errDetail(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 flex items-center justify-center px-6">
      <div className="w-full max-w-sm bg-white border border-zinc-200 p-8">
        <div className="flex items-center gap-2 mb-8">
          <ShieldCheck size={24} weight="fill" className="text-[#0055FF]" />
          <span className="font-semibold tracking-tight">SecureCBT Admin</span>
        </div>
        <h1 className="text-2xl font-semibold tracking-tight mb-6">Masuk Admin</h1>
        <form onSubmit={submit} className="space-y-4" data-testid="admin-login-form">
          <div className="space-y-1.5">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" data-testid="admin-email-input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="admin@sekolah.id" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" data-testid="admin-password-input" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
          </div>
          {error && <p data-testid="admin-login-error" className="text-sm text-red-600">{error}</p>}
          <Button type="submit" data-testid="admin-login-submit" disabled={loading} className="w-full bg-zinc-900 text-white hover:bg-zinc-800">
            {loading ? "Memproses..." : "Masuk"}
          </Button>
        </form>
      </div>
    </div>
  );
}
