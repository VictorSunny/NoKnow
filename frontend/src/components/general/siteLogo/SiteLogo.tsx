import { ReactComponent as SiteLogoSVG } from "../../../assets/site-logo-colored.svg";
import { Link } from "react-router-dom";

import "./SiteLogo.css";

function SiteLogo(props?: { to?: string }) {
  /////   SITE LOGO

  // Directs user to homepage on click
  return (
    <Link
      to={props?.to ?? ""}
      className={`site-logo-link ${(props?.to && "show") || ""}`}
      aria-label="visit homepage"
    >
      <SiteLogoSVG className="site-main-logo" aria-label="site logo" />
    </Link>
  );
}

export default SiteLogo;
