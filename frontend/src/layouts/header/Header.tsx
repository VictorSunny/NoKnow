import SiteLogo from "../../components/general/siteLogo/SiteLogo";
import "./Header.css";
import Sidebar from "../../components/general/sidebar/Sidebar";
import { motion } from "framer-motion";

import useCheckUserIsAuthenticated from "../../hooks/useCheckUserIsAuthenticated";
import { useNavigationContext } from "../../contexts/NavigationContext";
import {
  InnerLinksProps,
  SiteChatNavLinks,
  SiteFriendNavLinks,
  SiteMainInnerLinks,
  SiteMainOuterLinks,
} from "../../components/general/siteLinkLists/SiteLinkLists";
import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import useResetStates from "../../hooks/useResetStates";
import { Link } from "react-router-dom";
import { OPEN_FROM_TOP_TO_BOTTOM } from "../../animations/ModuleOpenAnimations";

function Header() {
  const userIsLoggedIn = useCheckUserIsAuthenticated();
  const { currentPageTitle } = useNavigationContext();
  const [showExtraMenu, setShowExtraMenu] = useState(false);
  const handleExtraMenuClick = () => {
    setShowExtraMenu((prev) => !prev);
  };

  const _ = useResetStates([setShowExtraMenu]);

  return (
    <header>
      <Sidebar userIsLoggedIn={userIsLoggedIn} position={"top-left"} />
      <SiteLogo />
      <nav id="header-nav" className={(userIsLoggedIn && "full") || "normal"}>
        <SiteMainInnerLinks forHeader userIsLoggedIn={userIsLoggedIn} />
        <button
          id="header-menu-btn"
          className={(showExtraMenu && "active") || ""}
          onClick={handleExtraMenuClick}
        >
          . . .
        </button>
        <AnimatePresence>
          {showExtraMenu && (
            <>
              <ExtraMenu userIsLoggedIn={userIsLoggedIn} />
            </>
          )}
        </AnimatePresence>
      </nav>
      <div id="page-title-container">
        <p>{currentPageTitle}</p>
      </div>
    </header>
  );
}

export default Header;

function ExtraMenu({ userIsLoggedIn }: InnerLinksProps) {
  return (
    <motion.div
      variants={OPEN_FROM_TOP_TO_BOTTOM}
      initial={"initial"}
      animate={"animate"}
      exit={"exit"}
      id="header-extra-menu"
    >
      <SiteChatNavLinks userIsLoggedIn={userIsLoggedIn} />
      {userIsLoggedIn && <SiteFriendNavLinks />}
      <SiteMainOuterLinks />
      {(userIsLoggedIn && (
        <Link className="auth-btn danger btn" to={"/auth/logout"}>
          logout
        </Link>
      )) || (
        <Link className="auth-btn btn" to={"/auth/login"}>
          login
        </Link>
      )}
    </motion.div>
  );
}
