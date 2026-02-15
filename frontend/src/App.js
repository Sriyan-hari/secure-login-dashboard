import { useState } from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Splash from "./pages/Splash";

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const token = localStorage.getItem("token");

  if (showSplash) {
    return <Splash onFinish={() => setShowSplash(false)} />;
  }

  return token ? <Dashboard /> : <Login />;
}

export default App;
