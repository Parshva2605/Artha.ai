"use client";

import { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { isLoggedIn, removeToken } from "@/lib/auth";

export default function Navbar() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    setLoggedIn(isLoggedIn());
  }, [pathname]);

  useEffect(() => {
    const handleStorage = () => {
      setLoggedIn(isLoggedIn());
    };

    window.addEventListener("storage", handleStorage);

    return () => {
      window.removeEventListener("storage", handleStorage);
    };
  }, []);

  const handleSignOut = () => {
    removeToken();
    setLoggedIn(false);
    setMenuOpen(false);
    router.push("/login");
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-800 bg-[#0F172A]">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-xl font-bold text-white">Artha AI</span>
            <span className="bg-[#E8690A] text-white text-xs font-semibold px-2 py-0.5 rounded-full">
              BETA
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            <Link href="/#how-it-works" className="text-sm text-gray-300 hover:text-white">
              How it works
            </Link>
            <Link href="/generate" className="text-sm text-gray-300 hover:text-white">
              Generate
            </Link>
            <Link href="/upload-dataset" className="text-sm text-gray-300 hover:text-white">
              Label My Data
            </Link>
            <Link
              href="/custom-dataset"
              className="text-sm font-medium text-[#E8690A] border border-[#E8690A] rounded-full px-4 py-1.5 hover:bg-[#E8690A] hover:text-white transition-all"
            >
              Custom Dataset
            </Link>
            {loggedIn ? (
              <div className="flex items-center gap-4">
                <Link href="/my-datasets" className="text-sm text-gray-300 hover:text-white">
                  My Datasets
                </Link>
                <button onClick={handleSignOut} className="text-sm text-gray-300 hover:text-white">
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/login" className="text-sm text-gray-300 hover:text-white">
                  Sign In
                </Link>
                <Link
                  href="/signup"
                  className="bg-[#E8690A] text-white text-sm px-4 py-2 rounded-lg hover:bg-orange-600 transition-all"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          <button
            className="md:hidden text-gray-300 hover:text-white p-2"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle navigation menu"
          >
            {menuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {menuOpen && (
          <div className="md:hidden border-t border-gray-800 pb-4 pt-4 space-y-2">
            <Link
              href="/#how-it-works"
              onClick={() => setMenuOpen(false)}
              className="block text-gray-300 hover:text-white text-sm py-2 px-2"
            >
              How it works
            </Link>
            <Link
              href="/generate"
              onClick={() => setMenuOpen(false)}
              className="block text-gray-300 hover:text-white text-sm py-2 px-2"
            >
              Generate
            </Link>
            <Link
              href="/upload-dataset"
              onClick={() => setMenuOpen(false)}
              className="block text-gray-300 hover:text-white text-sm py-2 px-2"
            >
              Label My Data
            </Link>
            <Link
              href="/custom-dataset"
              onClick={() => setMenuOpen(false)}
              className="block text-[#E8690A] text-sm py-2 px-2 font-medium"
            >
              Custom Dataset →
            </Link>
            {loggedIn ? (
              <>
                <Link
                  href="/my-datasets"
                  onClick={() => setMenuOpen(false)}
                  className="block text-gray-300 hover:text-white text-sm py-2 px-2"
                >
                  My Datasets
                </Link>
                <button
                  onClick={handleSignOut}
                  className="block w-full text-left text-gray-300 hover:text-white text-sm py-2 px-2"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  onClick={() => setMenuOpen(false)}
                  className="block text-gray-300 hover:text-white text-sm py-2 px-2"
                >
                  Sign In
                </Link>
                <Link
                  href="/signup"
                  onClick={() => setMenuOpen(false)}
                  className="block bg-[#E8690A] text-white text-sm px-4 py-2 rounded-lg text-center"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
