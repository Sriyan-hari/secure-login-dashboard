import { useState } from "react";
import api from "../api/api";
import Lottie from "lottie-react";
import animationData from "../assets/LOCK WITH GREEN TICK.json";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showAnimation, setShowAnimation] = useState(false);

  const handleLogin = async () => {
    try {
      const res = await api.post("/login", {
        email,
        password,
      });

      localStorage.setItem("token", res.data.token);

      // 🔐 show login success animation
      setShowAnimation(true);

      // ⏳ after animation → dashboard
      setTimeout(() => {
        window.location.href = "/";
      }, 2000);

    } catch (err) {
      alert("Invalid email or password");
    }
  };

  // 🔒 Animation screen during login
  if (showAnimation) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white">
        <div className="w-64">
          <Lottie animationData={animationData} loop />
        </div>
        <h2 className="mt-6 text-lg">
          Securing your account...
        </h2>
      </div>
    );
  }

  // 🔑 Normal login UI
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-black p-6 rounded w-80">
        <h2 className="text-white text-xl mb-4 text-center">
          Secure Login
        </h2>

        <input
          type="email"
          placeholder="Email"
          className="w-full mb-3 p-2 rounded bg-gray-800 text-white"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full mb-4 p-2 rounded bg-gray-800 text-white"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          onClick={handleLogin}
          className="w-full bg-green-600 text-white p-2 rounded"
        >
          Login
        </button>
      </div>
    </div>
  );
}
