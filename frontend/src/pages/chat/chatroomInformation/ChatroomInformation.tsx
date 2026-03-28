import AnimatedWindowWrapper from "../../AnimatedWindowWrapper";
import { AnimatePresence } from "framer-motion";
import { useLocation } from "react-router-dom";
import { Outlet } from "react-router-dom";

import "./ChatroomInformation.css";
import { NavLink } from "react-router-dom";
import NavContainer from "../../../components/general/dropdownSelect/NavContainer";
import { Suspense } from "react";
import FadingSpinnerLoader from "../../../components/general/loaders/FadingCirclesLoader";

type WindowLink = "" | "users";
export default function ChatroomInformation() {
  const location = useLocation();

  return (
    <div className="page-container chatroom-information-page">
      <NavContainer>
        <nav className="window-nav">
          <NavLink to="" className="nav-link" replace end>
            info
          </NavLink>
          <NavLink to="users" className="nav-link" replace>
            members
          </NavLink>
        </nav>
      </NavContainer>
      <div className="page-main-content grow">
        <AnimatePresence>
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
