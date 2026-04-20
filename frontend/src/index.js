import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import * as serviceWorkerRegistration from "./serviceWorkerRegistration";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// Unregister service worker and clear all caches to fix stale deployments
serviceWorkerRegistration.unregister();
if ('caches' in window) {
  caches.keys().then((names) => names.forEach((name) => caches.delete(name)));
}
