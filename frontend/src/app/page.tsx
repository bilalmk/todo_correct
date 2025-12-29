/**
 * Home page - Landing page for the application
 */
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8 text-center">
          Todo Evolution
        </h1>
        <p className="text-xl mb-8 text-center">
          Multi-user todo application with AI chatbot
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/auth/login"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Login
          </Link>
          <Link
            href="/auth/register"
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Register
          </Link>
        </div>
      </div>
    </main>
  );
}
