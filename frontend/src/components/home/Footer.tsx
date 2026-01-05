"use client";

import Link from "next/link";
import { Github, Twitter, Linkedin, Mail } from "lucide-react";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-50 dark:bg-gray-950 border-t border-gray-200 dark:border-gray-800">
      <div className="container mx-auto px-4 md:px-6 lg:px-8 max-w-7xl">
        {/* Main footer content */}
        <div className="py-12 md:py-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 md:gap-12">
          {/* Brand section */}
          <div className="lg:col-span-2">
            <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary dark:from-primary dark:to-secondary mb-4">
              Todo Evolution
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
              Transform your productivity with the next generation of task
              management. Built with modern technology and designed for
              efficiency.
            </p>
            {/* Social links */}
            <div className="flex gap-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors"
                aria-label="GitHub"
              >
                <Github className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors"
                aria-label="Twitter"
              >
                <Twitter className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              </a>
              <a
                href="mailto:hello@todoevolution.com"
                className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors"
                aria-label="Email"
              >
                <Mail className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              </a>
            </div>
          </div>

          {/* Product links */}
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-4">
              Product
            </h4>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/auth/register"
                  className="text-gray-600 dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors"
                >
                  Get Started
                </Link>
              </li>
              <li>
                <Link
                  href="/auth/login"
                  className="text-gray-600 dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors"
                >
                  Sign In
                </Link>
              </li>
              <li>
                <span className="text-gray-400 dark:text-gray-600 cursor-not-allowed">
                  Pricing
                </span>
              </li>
              <li>
                <span className="text-gray-400 dark:text-gray-600 cursor-not-allowed">
                  Features
                </span>
              </li>
            </ul>
          </div>

          {/* Company links */}
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-4">
              Company
            </h4>
            <ul className="space-y-3">
              <li>
                <span className="text-gray-400 dark:text-gray-600 cursor-not-allowed">
                  About Us
                </span>
              </li>
              <li>
                <span className="text-gray-400 dark:text-gray-600 cursor-not-allowed">
                  Blog
                </span>
              </li>
              <li>
                <span className="text-gray-400 dark:text-gray-600 cursor-not-allowed">
                  Privacy Policy
                </span>
              </li>
              <li>
                <span className="text-gray-400 dark:text-gray-600 cursor-not-allowed">
                  Terms of Service
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Image Attributions (T025) */}
        <div className="py-6 border-t border-gray-200 dark:border-gray-800">
          <div className="text-center mb-4">
            <p className="text-xs text-gray-500 dark:text-gray-600 mb-2">
              Professional images from{" "}
              <a
                href="https://unsplash.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Unsplash
              </a>{" "}
              and{" "}
              <a
                href="https://pexels.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Pexels
              </a>
            </p>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="py-6 border-t border-gray-200 dark:border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              © {currentYear} Todo Evolution. Built with{" "}
              <a
                href="https://claude.com/claude-code"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary dark:text-primary hover:underline"
              >
                Claude Code
              </a>{" "}
              and Spec-Driven Development.
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Hackathon Project • Phase III Submission
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
