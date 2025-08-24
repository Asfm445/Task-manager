import { jwtDecode } from "jwt-decode";
import api from "./api"; // Adjust the import based on your project structure

export async function checkIsAuthorized() {
  const accessToken = localStorage.getItem("access_token");
  const refreshToken = localStorage.getItem("refresh_token");

  if (!accessToken || !refreshToken) return false;

  try {
    const decoded = jwtDecode(accessToken);
    const now = Date.now() / 1000;

    if (decoded.exp > now) {
      return true; // Access token still valid
    }

    // Access token expired, try refresh
    const response = await api.post("auth/refresh", { refresh_token: refreshToken });
    if (response.status === 200) {
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);
      return true;
    }

    return false;
  } catch (error) {
    console.error("Authorization check failed:", error);
    return false;
  }
}
