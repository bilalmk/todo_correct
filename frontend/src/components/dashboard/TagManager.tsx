"use client";

/**
 * TagManager Component - Tag Management Interface
 *
 * Features:
 * - Display all active (non-archived) tags from TagContext
 * - Create Tag button at the top
 * - Tag pills displayed in responsive 3-4 column grid
 * - Edit and Delete actions in dropdown menu per tag
 * - Sort tags by name or usage count
 * - Archive confirmation with usage count display
 * - Success toast on archive
 *
 * Used by: Tags page for comprehensive tag management
 */

import { useState } from "react";
import { toast } from "sonner";
import { Plus, MoreVertical, Edit, Archive, ArrowUpDown } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TagModal } from "@/components/dashboard/TagModal";
import { useTags } from "@/contexts/TagContext";
import { Tag, CreateTagInput } from "@/types/tag-schema";

type SortOption = "name" | "usage";

export function TagManager() {
  const { tags, isLoading, addTag, updateTag, archiveTag } = useTags();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [tagToArchive, setTagToArchive] = useState<Tag | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sortBy, setSortBy] = useState<SortOption>("name");

  // Get active (non-archived) tags
  const activeTags = tags.filter((tag) => !tag.archived);

  // Sort tags based on selected option
  const sortedTags = [...activeTags].sort((a, b) => {
    if (sortBy === "name") {
      return a.name.localeCompare(b.name);
    } else {
      // Sort by usage count (descending)
      return b.usage_count - a.usage_count;
    }
  });

  const handleCreateTag = async (data: CreateTagInput) => {
    setIsSubmitting(true);
    try {
      await addTag(data);
      toast.success("Tag created successfully", {
        description: `"${data.name}" is now available for organizing tasks.`,
      });
      setIsModalOpen(false);
    } catch (error) {
      toast.error("Failed to create tag", {
        description: "Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateTag = async (data: CreateTagInput) => {
    if (!editingTag) return;

    setIsSubmitting(true);
    try {
      await updateTag(editingTag.id, {
        name: data.name,
        color: data.color,
      });
      toast.success("Tag updated successfully", {
        description: `"${data.name}" has been updated.`,
      });
      setEditingTag(null);
    } catch (error) {
      toast.error("Failed to update tag", {
        description: "Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleArchiveConfirm = async () => {
    if (!tagToArchive) return;

    try {
      await archiveTag(tagToArchive.id);
      toast.success("Tag archived successfully", {
        description:
          tagToArchive.usage_count > 0
            ? `"${tagToArchive.name}" has been archived but remains visible on ${tagToArchive.usage_count} task${tagToArchive.usage_count === 1 ? "" : "s"}.`
            : `"${tagToArchive.name}" has been archived.`,
      });
    } catch (error) {
      toast.error("Failed to archive tag", {
        description: "Please try again.",
      });
    } finally {
      setTagToArchive(null);
    }
  };

  const handleEditClick = (tag: Tag) => {
    setEditingTag(tag);
  };

  const handleDeleteClick = (tag: Tag) => {
    setTagToArchive(tag);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center space-y-2">
          <div className="text-muted-foreground">Loading tags...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Create Button and Sort */}
      <div className="flex items-center justify-between gap-4">
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create Tag
        </Button>

        <div className="flex items-center gap-2">
          <ArrowUpDown className="h-4 w-4 text-muted-foreground" />
          <Select
            value={sortBy}
            onValueChange={(value) => setSortBy(value as SortOption)}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="name">Sort by Name</SelectItem>
              <SelectItem value="usage">Sort by Usage</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Tags Grid */}
      {sortedTags.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed rounded-lg">
          <p className="text-muted-foreground mb-4">No tags yet</p>
          <Button variant="outline" onClick={() => setIsModalOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Create your first tag
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {sortedTags.map((tag) => (
            <div
              key={tag.id}
              className="flex items-center justify-between gap-2 p-3 border rounded-lg hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <Badge
                  className="text-white shrink-0"
                  style={{ backgroundColor: tag.color || "#3B82F6" }}
                >
                  {tag.name}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {tag.usage_count} task{tag.usage_count === 1 ? "" : "s"}
                </span>
              </div>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0">
                    <MoreVertical className="h-4 w-4" />
                    <span className="sr-only">Tag actions</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => handleEditClick(tag)}>
                    <Edit className="mr-2 h-4 w-4" />
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => handleDeleteClick(tag)}
                    className="text-destructive focus:text-destructive"
                  >
                    <Archive className="mr-2 h-4 w-4" />
                    Archive
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Tag Modal */}
      <TagModal
        open={isModalOpen || !!editingTag}
        onClose={() => {
          setIsModalOpen(false);
          setEditingTag(null);
        }}
        onSubmit={editingTag ? handleUpdateTag : handleCreateTag}
        initialData={editingTag}
        isLoading={isSubmitting}
      />

      {/* Archive Confirmation Dialog */}
      <AlertDialog
        open={!!tagToArchive}
        onOpenChange={(open) => !open && setTagToArchive(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Archive Tag?</AlertDialogTitle>
            <AlertDialogDescription>
              {tagToArchive?.usage_count && tagToArchive.usage_count > 0 ? (
                <>
                  This tag is used by <strong>{tagToArchive.usage_count}</strong>{" "}
                  task{tagToArchive.usage_count === 1 ? "" : "s"}. Archiving will
                  hide it from the tag selector, but it will remain visible on
                  existing tasks.
                </>
              ) : (
                <>
                  Archive this unused tag? You can always create a new tag with the
                  same name later.
                </>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleArchiveConfirm}>
              Archive Tag
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
