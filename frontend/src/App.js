import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import Landing from "@/pages/Landing";
import Preparation from "@/pages/Preparation";
import PreFlight from "@/pages/PreFlight";
import ExamRoom from "@/pages/ExamRoom";
import AdminLogin from "@/pages/admin/AdminLogin";
import AdminLayout from "@/pages/admin/AdminLayout";
import Dashboard from "@/pages/admin/Dashboard";
import TokensPage from "@/pages/admin/TokensPage";
import QuestionsPage from "@/pages/admin/QuestionsPage";
import ResultsPage from "@/pages/admin/ResultsPage";
import SettingsPage from "@/pages/admin/SettingsPage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/preparation" element={<Preparation />} />
          <Route path="/preflight" element={<PreFlight />} />
          <Route path="/exam" element={<ExamRoom />} />
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="tokens" element={<TokensPage />} />
            <Route path="questions" element={<QuestionsPage />} />
            <Route path="results" element={<ResultsPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </div>
  );
}

export default App;
