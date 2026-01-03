"use client";

/**
 * TagModal Component - Create/Edit Tag Dialog
 *
 * Features:
 * - React Hook Form + createTagSchema validation
 * - Name field (required, with unique name validation)
 * - ColorPicker integration for color selection
 * - ESC key and close button to dismiss (no outside click)
 * - Edit mode support via initialData prop
 * - Loading states during submission
 *
 * Used by: TagManager for creating and editing tags
 */

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { ColorPicker } from "@/components/ui/ColorPicker";
import { createTagSchema, CreateTagInput } from "@/types/tag-schema";
import { Tag } from "@/types/tag-schema";
import { useTags } from "@/contexts/TagContext";

interface TagModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CreateTagInput) => Promise<void>;
  initialData?: Tag | null;
  isLoading?: boolean;
}

export function TagModal({
  open,
  onClose,
  onSubmit,
  initialData,
  isLoading = false,
}: TagModalProps) {
  const { tags } = useTags();
  const isEditMode = !!initialData;

  const form = useForm<CreateTagInput>({
    resolver: zodResolver(createTagSchema),
    defaultValues: {
      name: "",
      color: "#3B82F6", // Default blue color
    },
  });

  // Populate form when editing
  useEffect(() => {
    if (initialData) {
      form.reset({
        name: initialData.name,
        color: initialData.color || "#3B82F6", // Default to blue if no color
      });
    } else {
      form.reset({
        name: "",
        color: "#3B82F6",
      });
    }
  }, [initialData, form]);

  // Reset form when modal closes
  useEffect(() => {
    if (!open) {
      form.reset({
        name: "",
        color: "#3B82F6",
      });
    }
  }, [open, form]);

  const handleSubmit = async (data: CreateTagInput) => {
    // Check for duplicate name (case-insensitive, excluding current tag in edit mode)
    const normalizedName = data.name.trim().toLowerCase();
    const isDuplicate = tags.some((tag) => {
      const isDifferentTag = isEditMode ? tag.id !== initialData.id : true;
      return isDifferentTag && tag.name.toLowerCase() === normalizedName;
    });

    if (isDuplicate) {
      form.setError("name", {
        type: "manual",
        message: "A tag with this name already exists",
      });
      return;
    }

    try {
      await onSubmit(data);
      form.reset();
      onClose();
    } catch (error) {
      // Error handling done by parent component
      console.error("Tag submission error:", error);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent
        onEscapeKeyDown={(e) => {
          if (isLoading) {
            e.preventDefault();
          }
        }}
        onPointerDownOutside={(e) => {
          // Prevent closing on outside click
          e.preventDefault();
        }}
        onInteractOutside={(e) => {
          // Prevent closing on outside interaction
          e.preventDefault();
        }}
      >
        <DialogHeader>
          <DialogTitle>
            {isEditMode ? "Edit Tag" : "Create New Tag"}
          </DialogTitle>
          <DialogDescription>
            {isEditMode
              ? "Update the tag name and color. Changes will apply to all tasks using this tag."
              : "Add a new tag to organize your tasks. Choose a name and color."}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            {/* Tag Name Field */}
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tag Name</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="e.g., Work, Personal, Urgent"
                      {...field}
                      disabled={isLoading}
                      autoFocus
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Color Picker Field */}
            <FormField
              control={form.control}
              name="color"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Color</FormLabel>
                  <FormControl>
                    <ColorPicker
                      value={field.value}
                      onChange={field.onChange}
                      error={form.formState.errors.color?.message}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {isEditMode ? "Updating..." : "Creating..."}
                  </>
                ) : (
                  <>{isEditMode ? "Update Tag" : "Create Tag"}</>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
