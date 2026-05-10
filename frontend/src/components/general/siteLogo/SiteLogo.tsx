import { ReactComponent as SiteLogoFullSVG } from "../../../assets/site-logo-colored.svg";
import { ReactComponent as SiteLogoMiniSVG } from "../../../assets/site-logo-shortened.svg";
import { Link } from "react-router-dom";

import "./SiteLogo.css";

export default function SiteLogo(props?: { to?: string }) {
  /////   SITE LOGO

  // Directs user to homepage on click
  return (
    <>
      <Link
        to={props?.to ?? ""}
        className={`site-logo-link ${(props?.to && "show") || ""}`}
        aria-label="visit homepage"
      >
        <SiteLogoFullSVG className="icon site-main-logo" aria-label="site logo" />
      </Link>
      <Link
        to={props?.to ?? ""}
        className={`site-logo-link mini ${(props?.to && "show") || ""}`}
        aria-label="visit homepage"
      >
        <SiteLogoMiniSVG className="icon site-main-logo mini" aria-label="site logo" />
      </Link>
    </>
  );
}
