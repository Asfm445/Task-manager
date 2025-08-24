import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../api";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate()

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post(`/auth/reset-password?token=${token}`, { new_password: newPassword });
      setMessage("Your password has been reset. You can now log in.");
        navigate("/login");
    } catch (err) {
      setMessage("Failed to reset password.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-12 p-6 bg-white rounded-xl shadow">
      <h2 className="text-2xl font-bold mb-4 text-blue-700">Set New Password</h2>
      <form onSubmit={handleResetPassword} className="flex flex-col gap-4">
        <input
          type="password"
          value={newPassword}
          onChange={e => setNewPassword(e.target.value)}
          placeholder="New password"
          required
          className="px-4 py-2 border rounded-lg"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold"
        >
          {loading ? "Resetting..." : "Reset Password"}
        </button>
      </form>
      {message && <div className="mt-4 text-green-600">{message}</div>}
    </div>
  );
}