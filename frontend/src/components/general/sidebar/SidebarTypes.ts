export type ParsedLinkItem = {
  heading: string;
  show: boolean;
  sectionLinks: React.ReactNode[];
};
export type UrlObject = {
  to: string;
  linkText: string;
  ariaLabel: string;
  isOuterLink: boolean;
};
export type RawLinkItem = {
  heading: string;
  show: boolean;
  sectionLinks: UrlObject[];
};
export type SidebarProps = {
  position: "bottom-left" | "bottom-right" | "top-left";
  userIsLoggedIn: boolean;
};
export type SidebarMenuProps = Omit<SidebarProps, "buttonIcon"> & {
  toggleButton: React.ReactNode;
};
