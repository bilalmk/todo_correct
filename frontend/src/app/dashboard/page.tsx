/**
 * Dashboard Page (Protected Route)
 */
import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";
import LogoutButton from "@/components/LogoutButton";

export default async function DashboardPage() {
  // Get session on server side
  const session = await getSession();

  // Redirect if not authenticated
  if (!session || !session.user) {
    redirect("/auth/login");
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow-xl rounded-lg p-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-800">
              Dashboard
            </h1>
            <LogoutButton />
          </div>

          <div className="bg-blue-50 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              Welcome, {session.user.name}!
            </h2>
            <div className="space-y-2 text-gray-700">
              <p>
                <span className="font-medium">Email:</span> {session.user.email}
              </p>
              <p>
                <span className="font-medium">User ID:</span> {session.user.id}
              </p>
            </div>
          </div>

          <div className="mt-8">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">
              Your Tasks
            </h3>
            <p className="text-gray-600">
              Task management features coming in Phase III...
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
