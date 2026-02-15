import { useEffect } from "react";
import Lottie from "lottie-react";
import animationData from "../assets/intro.json"; // filename match karo

export default function Splash({ onFinish }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onFinish();
    }, 2000); // 2 seconds splash

    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white">
      <div className="w-64">
        <Lottie animationData={animationData} loop />
      </div>
      <h1 className="mt-6 text-xl font-semibold">
        Secure Login System
      </h1>
    </div>
  );
}
