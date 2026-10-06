export interface NavLink {
  label: string;
  href: string;
}

export const NAV_LINKS: NavLink[] = [
  { label: "Chi siamo", href: "/chi-siamo" },
  { label: "Eventi", href: "/eventi" },
  { label: "Progetti", href: "/#projects" },
  { label: "Comitati", href: "/comitati" },
  { label: "Documenti", href: "/documenti" },
];
