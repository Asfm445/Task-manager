import { jwtDecode } from "jwt-decode";
import api from "./api"; // Adjust the import based on your project structure

export async function checkIsAuthorized() {
  const accessToken = localStorage.getItem("access_token");
  if (!accessToken) {
    return false; // No access token means not authorized
  }
  try {
    // Check for refresh token first (fundamental requirement)
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      return false;
    }

    // Check access token if it exists
    if (accessToken) {
      const decoded = jwtDecode(accessToken);
      const now = Date.now() / 1000;

      // If token is still valid
      if (decoded.exp > now) {
        return true;
      }
    } else {
      return false;
    }

    // Attempt token refresh if no valid access token
    try {
      console.log("Attempting to refresh token...");
      const response = await api.post("auth/refresh", {
        refresh_token: refreshToken,
      });

      if (response.status === 200) {
        localStorage.setItem("access_token", response.data.access_token);
        return true;
      }
    } catch (refreshError) {
      console.error("Token refresh failed:", refreshError);
    }

    return false;
  } catch (error) {
    console.error("Authorization check failed:", error);
    return false;
  }
}
