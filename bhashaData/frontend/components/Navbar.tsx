"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { isLoggedIn, removeToken, getToken } from "@/lib/auth";
import { getCurrentUser } from "@/lib/api";
import { useEffect, useState } from "react";

interface User {
  email: string;
  full_name: string | null;
}

export default function Navbar() {
  const router = useRouter();
  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      if (isLoggedIn()) {
        try {
          const userResponse = await getCurrentUser();
          setUser({
            email: userResponse.email,
            full_name: userResponse.full_name,
          });
          setLoggedIn(true);
        } catch {
          // Token invalid, clear it
          removeToken();
          setLoggedIn(false);
        }
      } else {
        setLoggedIn(false);
      }
      setLoading(false);
    }

    checkAuth();
  }, []);

  function handleSignOut() {
    removeToken();
    setLoggedIn(false);
    setUser(null);
    router.push("/login");
  }

  if (loading) {
    return null;
  }

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/" className="text-2xl font-bold text-orange-600">
          Artha AI
        </Link>

        <div className="flex items-center gap-6">
          {loggedIn ? (
            <>
              <Link
                href="/my-datasets"
                className="text-gray-700 hover:text-orange-600 transition"
              >
                My Datasets
              </Link>
              <span className="text-gray-700">{user?.email}</span>
              <button
                onClick={handleSignOut}
                className="bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 transition"
              >
                Sign Out
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="text-gray-700 hover:text-orange-600 transition"
              >
                Sign In
              </Link>
              <Link
                href="/signup"
                className="bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 transition"
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
