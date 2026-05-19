import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import ErrorBoundary from "./components/ErrorBoundary";
import "./theme.css";

document.documentElement.dataset.theme =
  localStorage.getItem("mscc-theme") === "light" ? "light" : "dark";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary name="app-root">
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
