import * as React from "react";
import clsx from "clsx";


export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
variant?: "default" | "outline" | "ghost";
size?: "sm" | "md" | "lg";
}


export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
({ className, variant = "default", size = "md", ...props }, ref) => {
const baseStyles =
"inline-flex items-center justify-center font-medium rounded-2xl shadow-sm transition-colors focus:outline-none disabled:opacity-50 disabled:pointer-events-none";


const variants: Record<string, string> = {
default: "bg-blue-600 text-white hover:bg-blue-700",
outline: "border border-gray-300 bg-white hover:bg-gray-50",
ghost: "bg-transparent hover:bg-gray-100",
};


const sizes: Record<string, string> = {
sm: "h-8 px-3 text-sm",
md: "h-10 px-4 text-base",
lg: "h-12 px-6 text-lg",
};


return (
<button
ref={ref}
className={clsx(baseStyles, variants[variant], sizes[size], className)}
{...props}
/>
);
}
);


Button.displayName = "Button";