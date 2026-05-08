import AnimatedWindowWrapper from "../../AnimatedWindowWrapper";
import { useLocation } from "react-router-dom";
import { Outlet } from "react-router-dom";

import { ReactComponent as InfoIcon } from "../../../assets/icons/info-icon.svg";
import { ReactComponent as MembersIcon } from "../../../assets/icons/users-group-three-icon.svg";

import "./ChatroomInformation.css";
import { NavLink } from "react-router-dom";
import NavContainer from "../../../components/general/dropdownSelect/NavContainer";
import { Suspense } from "react";
import FetchingLoader from "../../../components/general/loaders/FetchingLoader";

export default function ChatroomInformation() {
  const location = useLocation();

  return (
    <div className="page-container chatroom-information-page">
      <NavContainer>
        <nav className="window-nav">
          <NavLink to="" className="nav-link" replace end>
            <div className="text-icon-container">
              <InfoIcon className="icon" aria-label="info icon" />
              <span>info</span>
            </div>
          </NavLink>
          <NavLink to="users" className="nav-link" replace>
            <div className="text-icon-container">
              <MembersIcon className="icon" aria-label="members icon" />
              <span>members</span>
            </div>
          </NavLink>
        </nav>
      </NavContainer>
      <div className="page-main-content grow">
        <AnimatedWindowWrapper key={location.pathname}>
          <Suspense fallback={<FetchingLoader />}>
            <Outlet />
          </Suspense>
        </AnimatedWindowWrapper>
      </div>
    </div>
  );
}
