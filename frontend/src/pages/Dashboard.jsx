import { useEffect, useState } from "react";
import api from "../api/api";

export default function Dashboard() {
  const [data, setData] = useState({
    failed_logins_24h: 0,
    locked_accounts: 0
  });

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/";
  };

  useEffect(() => {
    api.get("/dashboard/summary")
      .then((res) => setData(res.data))
      .catch(() => alert("Unauthorized or token expired"));
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Security Dashboard</h1>
        <button
          onClick={handleLogout}
          className="bg-red-600 px-4 py-2 rounded"
        >
          Logout
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-black p-6 rounded shadow">
          <h2 className="text-lg mb-2">Failed Logins (24h)</h2>
          <p className="text-3xl text-yellow-400">
            {data.failed_logins_24h}
          </p>
        </div>

        <div className="bg-black p-6 rounded shadow">
          <h2 className="text-lg mb-2">Locked Accounts</h2>
          <p className="text-3xl text-red-400">
            {data.locked_accounts}
          </p>
        </div>
      </div>
    </div>
  );
}
