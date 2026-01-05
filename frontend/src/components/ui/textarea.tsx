import * as React from "react"

import { cn } from "@/lib/utils"

const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.ComponentProps<"textarea">
>(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        // T034a: Updated to frontend-design-system standards
        // Border: border-2 (2px solid)
        // Focus: ring-2 with primary orange color, 2px offset
        // Transitions: 300ms duration
        "flex min-h-[80px] w-full rounded-md border-2 border-input bg-transparent px-3 py-2 text-base shadow-sm placeholder:text-muted-foreground transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Textarea.displayName = "Textarea"

export { Textarea }
