import * as React from "react"

import { cn } from "@/lib/utils"

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          // T034a: Updated to frontend-design-system standards
          // Height: h-10 (40px) for desktop, h-11 (44px) for mobile touch targets
          // Border: border-2 (2px solid)
          // Focus: ring-2 with primary orange color, 2px offset
          // Transitions: 300ms duration
          "flex h-10 sm:h-11 w-full rounded-md border-2 border-input bg-transparent px-3 py-2 text-base shadow-sm transition-all duration-300 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
