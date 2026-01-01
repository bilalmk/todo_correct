"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useCallback,
  useRef,
} from "react";
import { User } from "@/types/user-schema";
import { MOCK_USER, delay } from "@/lib/mock-data";
import { getFromLocalStorage, setToLocalStorage } from "@/lib/utils";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

const STORAGE_KEY = "todo_app_auth";
const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 minutes

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
  });
  const router = useRouter();
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Load auth state from localStorage on mount
  useEffect(() => {
    const stored = getFromLocalStorage<AuthState>(STORAGE_KEY, {
      isAuthenticated: false,
      user: null,
    });
    setAuthState(stored);
  }, []);

  // Sync to localStorage on auth state change
  useEffect(() => {
    setToLocalStorage(STORAGE_KEY, authState);
  }, [authState]);

  // Reset inactivity timer
  const resetInactivityTimer = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (authState.isAuthenticated) {
      timeoutRef.current = setTimeout(() => {
        setAuthState({ isAuthenticated: false, user: null });
        toast.error("Session expired. Please log in again.");
        router.push("/auth/login");
      }, INACTIVITY_TIMEOUT);
    }
  }, [authState.isAuthenticated, router]);

  // Activity listeners for inactivity timeout
  useEffect(() => {
    const events = ["mousemove", "keydown", "click", "scroll"];

    const handleActivity = () => {
      resetInactivityTimer();
    };

    events.forEach((event) => {
      document.addEventListener(event, handleActivity);
    });

    resetInactivityTimer();

    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleActivity);
      });
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [resetInactivityTimer]);

  const login = async (_email: string, _password: string) => {
    await delay("updateTask");
    // Mock authentication - always succeeds
    setAuthState({
      isAuthenticated: true,
      user: MOCK_USER,
    });
  };

  const register = async (name: string, email: string, _password: string) => {
    await delay("createTask");
    // Mock registration - always succeeds
    setAuthState({
      isAuthenticated: true,
      user: {
        id: "user_" + Date.now(),
        name,
        email,
        avatar_url: null,
      },
    });
  };

  const logout = async () => {
    await delay("deleteTask");
    setAuthState({
      isAuthenticated: false,
      user: null,
    });
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  };

  return (
    <AuthContext.Provider
      value={{ ...authState, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
