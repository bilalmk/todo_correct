"use client";

/**
 * ColorPicker Component
 *
 * A color selection interface with preset colors and custom hex input.
 * Features:
 * - 10 preset colors from PRESET_TAG_COLORS in a grid layout
 * - Custom hex color input with real-time validation
 * - Live preview badge showing selected color
 * - Visual feedback for selected preset
 *
 * Used by: TagModal for tag color selection
 */

import { useState } from "react";
import { PRESET_TAG_COLORS } from "@/types/tag-schema";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
  error?: string;
}

export function ColorPicker({ value, onChange, error }: ColorPickerProps) {
  const [customColor, setCustomColor] = useState(value);

  // Validate hex color format
  const isValidHex = (color: string): boolean => {
    return /^#[0-9A-Fa-f]{6}$/.test(color);
  };

  const handleCustomColorChange = (inputValue: string) => {
    setCustomColor(inputValue);

    // Only propagate valid colors
    if (isValidHex(inputValue)) {
      onChange(inputValue.toUpperCase());
    }
  };

  const handlePresetSelect = (color: string) => {
    setCustomColor(color);
    onChange(color);
  };

  return (
    <div className="space-y-4">
      {/* Preset Colors Grid */}
      <div>
        <label className="text-sm font-medium mb-2 block">Preset Colors</label>
        <div className="grid grid-cols-5 gap-2">
          {PRESET_TAG_COLORS.map((color) => (
            <button
              key={color}
              type="button"
              onClick={() => handlePresetSelect(color)}
              className={cn(
                "h-10 w-full rounded-md border-2 transition-all hover:scale-105",
                value.toUpperCase() === color
                  ? "border-primary ring-2 ring-primary ring-offset-2"
                  : "border-transparent hover:border-gray-300"
              )}
              style={{ backgroundColor: color }}
              aria-label={`Select color ${color}`}
            >
              <span className="sr-only">{color}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Custom Color Input */}
      <div>
        <label htmlFor="custom-color" className="text-sm font-medium mb-2 block">
          Custom Color (Hex)
        </label>
        <Input
          id="custom-color"
          type="text"
          placeholder="#3B82F6"
          value={customColor}
          onChange={(e) => handleCustomColorChange(e.target.value)}
          className={cn(
            "font-mono uppercase",
            error && "border-destructive focus-visible:ring-destructive"
          )}
          maxLength={7}
        />
        {error && <p className="text-sm text-destructive mt-1">{error}</p>}
        {!error && !isValidHex(customColor) && customColor && (
          <p className="text-sm text-muted-foreground mt-1">
            Must be a valid hex color (e.g., #3B82F6)
          </p>
        )}
      </div>

      {/* Live Preview */}
      <div>
        <label className="text-sm font-medium mb-2 block">Preview</label>
        <Badge
          className="px-3 py-1.5 text-white"
          style={{
            backgroundColor: isValidHex(value) ? value : "#6B7280",
          }}
        >
          Sample Tag
        </Badge>
      </div>
    </div>
  );
}
