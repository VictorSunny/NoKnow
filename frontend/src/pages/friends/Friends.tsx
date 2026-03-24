import { AnimatePresence } from "framer-motion";
import AnimatedWindowWrapper from "../AnimatedWindowWrapper";
import { Outlet } from "react-router-dom";

import "./Friends.css";
import { NavLink } from "react-router-dom";
import NavContainer from "../../components/general/dropdownSelect/NavContainer";
import { Suspense } from "react";
import FadingSpinnerLoader from "../../components/general/popups/loaders/FadingCirclesLoader";

export default function Friends() {
  return (
    <div className="page-container friends-page-container">
      <NavContainer>
        <nav className="window-nav">
          <NavLink className="nav-link" to={"/friends"} end replace>
            friends
          </NavLink>
          <NavLink className="nav-link" to={"/friends/requests"} end replace>
            pending
          </NavLink>
          <NavLink className="nav-link" to={"/friends/sent"} end replace>
            requested
          </NavLink>
        </nav>
      </NavContainer>
      <div className="page-main-content grow">
        <AnimatePresence mode="wait">
          <AnimatedWindowWrapper key={location.pathname}>
            <Suspense fallback={<FadingSpinnerLoader />}>
              <Outlet />
            </Suspense>
          </AnimatedWindowWrapper>
        </AnimatePresence>
      </div>
    </div>
  );
}
