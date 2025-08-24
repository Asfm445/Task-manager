// src/pages/VerifyEmail.jsx
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../api";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const navigate = useNavigate();

  const [message, setMessage] = useState("Verifying your email...");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verify = async () => {
      try {
        await api.get(`/auth/verify-email?token=${token}`);
        setMessage("✅ Your email has been verified. Redirecting to login...");
        setTimeout(() => navigate("/login"), 2000);
      } catch (err) {
        setMessage("❌ Verification failed. Please request a new verification link.");
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      verify();
    } else {
      setMessage("❌ Invalid verification link.");
      setLoading(false);
    }
  }, [token, navigate]);

  return (
    <div className="max-w-md mx-auto mt-12 p-6 bg-white rounded-xl shadow text-center">
      <h2 className="text-2xl font-bold mb-4 text-blue-700">Email Verification</h2>
      <p className={`${loading ? "text-gray-600" : "text-green-700"}`}>{message}</p>
    </div>
  );
}
