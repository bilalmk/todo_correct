/**
 * Tags Page - Tag Management Interface
 *
 * Full tag management functionality including:
 * - Create, edit, and archive tags
 * - Sort by name or usage count
 * - Visual tag previews with custom colors
 * - Usage count tracking
 */

import { TagManager } from "@/components/dashboard/TagManager";

export default function TagsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Tag Management
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Create and manage your task tags. Tags help you organize and filter your tasks.
        </p>
      </div>

      <TagManager />
    </div>
  );
}
