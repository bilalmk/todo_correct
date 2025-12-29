/**
 * Logout Button Component
 */
"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LogoutButton() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleLogout = async () => {
    setIsLoading(true);

    try {
      // Call Better Auth sign-out endpoint
      await fetch("/api/auth/sign-out", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      // Redirect to login
      router.push("/auth/login");
      router.refresh();
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleLogout}
      disabled={isLoading}
      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-4 focus:ring-red-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
    >
      {isLoading ? "Signing Out..." : "Sign Out"}
    </button>
  );
}
