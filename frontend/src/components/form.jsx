import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";

function Form(props) {
  // console.log(props);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  function handleChange(e) {
    props.setInputs((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  }

  async function handleSubmit(e) {
    setLoading(true);
    e.preventDefault();

    try {
      const res = await api.post(props.apiUrl, props.inputs);
      if (props.type === "Login") {
        localStorage.setItem("access_token", res.data.access_token);
        localStorage.setItem("refresh_token", res.data.refresh_token);
        navigate("/");
      } else {
        navigate("/login");
      }
    } catch (error) {
      alert(error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-50 px-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-lg rounded-xl p-6 w-full max-w-md space-y-4"
      >
        <h2 className="text-2xl font-bold text-center text-gray-800">
          {props.type} Here
        </h2>
        {/* Username */}
        {props.type === "Register" && (
          <input
            type="text"
            name="username"
            placeholder="Username"
            onChange={handleChange}
            value={props.inputs.username}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        )}
        {/* Email (only on Register) */}
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={props.inputs.email}
          onChange={handleChange}
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {/* Password */}
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={props.inputs.password}
          onChange={handleChange}
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {/* Error message */}
        {error && <p className="text-sm text-red-500">{error}</p>}
        {/* Submit button */}
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
        >
          {loading ? (
            <div className="flex justify-center">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : (
            props.type
          )}
        </button>
        {/* Auth links */}
        {props.type === "Login" ? (
          <p className="text-sm text-center text-gray-600">
            Don’t have an account?{" "}
            <Link to={"/register"} className="text-blue-600 hover:underline">
              Register here
            </Link>
          </p>
        ) : (
          <p className="text-sm text-center text-gray-600">
            Have an account?{" "}
            <Link to={"/login"} className="text-blue-600 hover:underline">
              Login here
            </Link>
          </p>
        )}
      </form>
    </div>
  );
}

export default Form;
