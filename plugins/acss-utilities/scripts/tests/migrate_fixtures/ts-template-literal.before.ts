// TypeScript: rewrite inside className= and clsx() only
// (bare string assignments are NOT rewritten — see script docstring)
import clsx from "clsx";

const isMobile = true;
const classes = clsx("hide sm:show", isMobile ? "md:flex-row" : "lg:flex-col");
const btn = classnames("bg-primary xl:p-6", active && "sm:font-bold");
