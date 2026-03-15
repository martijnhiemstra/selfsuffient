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

// Register service worker for PWA functionality
serviceWorkerRegistration.register({
  onUpdate: (registration) => {
    // Show a toast or notification when new content is available
    console.log('[PWA] New version available! Refresh to update.');
  },
  onSuccess: (registration) => {
    console.log('[PWA] Content cached for offline use.');
  },
});
