import AnimatedWindowWrapper from "../AnimatedWindowWrapper";
import { Outlet, useLocation } from "react-router-dom";

import { ReactComponent as FriendIcon } from "../../assets/icons/friend-users-neutral-icon.svg";
import { ReactComponent as FriendSentRequestsIcon } from "../../assets/icons/friend-users-sent-requests-icon.svg";
import { ReactComponent as FriendReceivedRequestsIcon } from "../../assets/icons/friend-users-received-requests-icon.svg";

import "./Friends.css";
import { NavLink } from "react-router-dom";
import NavContainer from "../../components/general/dropdownSelect/NavContainer";
import { Suspense } from "react";
import FetchingLoader from "../../components/general/loaders/FetchingLoader";

export default function Friends() {
  const location = useLocation();
  return (
    <div className="page-container friends-page-container">
      <NavContainer>
        <nav className="window-nav">
          <NavLink className="nav-link" to={"/friends"} end replace>
            <div className="text-icon-container">
              <FriendIcon className="icon" aria-label="user icon" />
              <span>friends</span>
            </div>
          </NavLink>
          <NavLink className="nav-link" to={"/friends/requests"} end replace>
            <div className="text-icon-container">
              <FriendReceivedRequestsIcon className="icon" aria-label="user arrow left icon" />
              <span>pending</span>
            </div>
          </NavLink>
          <NavLink className="nav-link" to={"/friends/sent"} end replace>
            <div className="text-icon-container">
              <FriendSentRequestsIcon className="icon" aria-label="user arrow right icon" />
              <span>requested</span>
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
