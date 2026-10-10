import axios from "axios";

let backendUrl = process.env.REACT_APP_BACKEND_URL;
if (!backendUrl) {
  if (window.location.hostname.includes('devtunnels.ms')) {
    // Replace the frontend port in the VS Code tunnel URL with the backend port (8000)
    const tunnelHostname = window.location.hostname.replace(/-\d+\./, '-8000.');
    backendUrl = `${window.location.protocol}//${tunnelHostname}`;
  } else {
    backendUrl = ""; // Use current origin, will be intercepted by setupProxy.js or Nginx
  }
}

export const API = backendUrl ? backendUrl + '/api' : '/api';

export const api = axios.create({ baseURL: API });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  config.headers['Bypass-Tunnel-Reminder'] = 'true';
  return config;
});

export function errDetail(e) {
  const d = e?.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => x?.msg || JSON.stringify(x)).join(" ");
  return e?.message || "Terjadi kesalahan";
}
