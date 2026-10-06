// Prefix root-absolute paths with the deploy base (e.g. /aisf-astro).
// Locally BASE_URL is "/", in the Pages build it's "/aisf-astro/".
// External URLs pass through untouched.
export function u(path: string): string {
  if (/^(https?:|mailto:|#)/.test(path)) return path;
  const base = import.meta.env.BASE_URL || "/";
  const clean = "/" + path.replace(/^\/+/, "");
  return base.replace(/\/$/, "") + clean;
}
