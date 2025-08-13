import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { BrowserRouter } from "react-router-dom";
import { TaskProvider } from "./TaskContext.jsx";

createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <StrictMode>
      <TaskProvider>
        <App />
      </TaskProvider>
    </StrictMode>
  </BrowserRouter>
);
