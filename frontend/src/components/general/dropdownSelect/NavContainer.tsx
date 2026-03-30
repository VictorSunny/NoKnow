import "./NavContainer.css";
type Props = {
  children: React.ReactNode;
  forDropdown?: boolean;
};
/**
 * Returns a container which handles how navbars are laid out depending on device width.
 * Should be used to wrap over JSX elements containing `DropdownSelect` components.
 *
 * @returns HTMLDivElement
 */
export default function NavContainer({ children, forDropdown }: Props) {
  return (
    <div className={`nav-container ${(forDropdown && "dropdown-nav-container") || ""}`}>
      <div className="navs-content">{children}</div>
    </div>
  );
}
