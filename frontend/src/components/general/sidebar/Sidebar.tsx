import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useLocation } from "react-router-dom";
import { ReactComponent as SiteLogoButtonSVG } from "../../../assets/site-logo-shortened.svg";

import "./Sidebar.css";
import Backdrop from "../backdrop/Backdrop";
import { AnimatePresence } from "framer-motion";

import { SidebarProps } from "./SidebarTypes";
import {
  SiteChatNavLinks,
  SiteFriendNavLinks,
  SiteMainInnerLinks,
  SiteMainOuterLinks,
} from "../siteLinkLists/SiteLinkLists";
import SiteLogo from "../siteLogo/SiteLogo";
import useResetStates from "../../../hooks/useResetStates";
import { Link } from "react-router-dom";

export default function Sidebar({ userIsLoggedIn, position }: SidebarProps) {
  ////    SIDEBAR MENU

  // set state to monitor when sidebar is opened
  const [sidebarActive, setSidebarActive] = useState(false);

  // function to handle sidebar button toggle
  const toggleSideBar = () => {
    setSidebarActive((prev) => !prev);
  };

  // close sidebar if page is switched; when user clicks on any link in sidebar
  const _ = useResetStates([setSidebarActive]);

  // make webpage unscrollable while sidebar is open to avoid scroll behaviour leaking
  // user can scroll within sidebar without unwantedly scrolling page behind sidebar popup

  return (
    <>
      <motion.button
        onClick={toggleSideBar}
        className={`sidebar-btn btn ${position} ${(sidebarActive && "active") || ""}`}
        type="button"
        aria-label="open sidebar menu"
        layout
      >
        <SiteLogoButtonSVG className="primary-sidebar-logo" aria-label="site logo" />
      </motion.button>{" "}
      <AnimatePresence>
        {sidebarActive && (
          <motion.div
            id="mobile-main-sidebar"
            initial={{
              x: "100%",
            }}
            animate={{
              x: 0,
            }}
            exit={{
              x: "100%",
            }}
            transition={{
              duration: 0.15,
            }}
          >
            <div id="content">
              <SiteMainInnerLinks isMobile userIsLoggedIn={userIsLoggedIn} />
              <SiteChatNavLinks userIsLoggedIn={userIsLoggedIn} />
              {userIsLoggedIn && <SiteFriendNavLinks />}
              <SiteMainOuterLinks />
              {(userIsLoggedIn && (
                <Link className="btn auth-btn danger" to={"/auth/logout"}>
                  logout
                </Link>
              )) || (
                <Link className="btn auth-btn" to={"/auth/login"}>
                  login
                </Link>
              )}
              <SiteLogo />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
