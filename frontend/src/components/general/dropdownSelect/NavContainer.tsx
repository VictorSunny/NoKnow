import "./NavContainer.css";
type Props = {
  children: React.ReactNode;
  forDropdown?: boolean
}
export default function NavContainer({ children, forDropdown }: Props) {
  return (
    <div className={`nav-container ${forDropdown && "dropdown-nav-container"}`}>
      <div className="navs-content">{children}</div>
    </div>
  );
}
