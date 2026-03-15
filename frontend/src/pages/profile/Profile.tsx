import AnimatedWindowWrapper from "../AnimatedWindowWrapper";
import { AnimatePresence } from "framer-motion";
import { Outlet, useLocation } from "react-router-dom";

import useGetLoggedInUser from "../../hooks/useGetLoggedInUser";
import { NavLink } from "react-router-dom";
import LineLoadingSignal from "../../components/general/fetchModals/LineLoadingModal";

import "./Profile.css";
import { useState } from "react";
import FetchErrorSignal from "../../components/general/fetchModals/FetchErrorModal";
import NavContainer from "../../components/general/dropdownSelect/NavContainer";

function Profile() {
  const location = useLocation();
  const [errorMessage, setErrorMessage] = useState<string>();
  const userDetails = useGetLoggedInUser({ setErrorMessage });

  return (
    <>
      {(!userDetails && !errorMessage && <LineLoadingSignal />) ||
        (!userDetails && errorMessage && <FetchErrorSignal errorMessage={errorMessage} />) ||
        (userDetails && (
          <div className="page-container profile-page-container">
            <div className="section">
              <div className="basic-info-container">
                <p className="user-names">
                  <span className="username title">{userDetails?.username}</span> -{" "}
                  <strong>
                    {userDetails?.first_name} {userDetails?.last_name}
                  </strong>
                </p>
                <p className="bio medium-spaced">{userDetails.bio}</p>
                <p className="date-joined">
                  <strong>joined:</strong> {userDetails?.joined!}
                </p>
              </div>
            </div>

            <NavContainer>
              <nav className="window-nav">
                <NavLink
                  className="nav-link"
                  to={""}
                  aria-label="go to user details update page"
                  replace
                  end
                >
                  user details
                </NavLink>
                <NavLink
                  to={"update/password"}
                  className="nav-link"
                  aria-label="go to password change page"
                  replace
                  end
                >
                  change password
                </NavLink>
                <NavLink
                  to={"update/email"}
                  className="nav-link"
                  aria-label="go to email update page"
                  replace
                  end
                >
                  change email
                </NavLink>
                <NavLink
                  to={"update/two-factor-auth"}
                  className="nav-link"
                  aria-label="go to two factor auth update page"
                  replace
                  end
                >
                  two factor authentication
                </NavLink>
                <NavLink
                  to={"delete"}
                  className="nav-link"
                  aria-label="go to account deactivation page"
                  replace
                  end
                >
                  deactivate
                </NavLink>
              </nav>
            </NavContainer>
            <div className="page-main-content grow">
              <AnimatePresence mode="wait">
                <AnimatedWindowWrapper key={location.pathname}>
                  <Outlet />
                </AnimatedWindowWrapper>
              </AnimatePresence>
            </div>
          </div>
        ))}
    </>
  );
}

export default Profile;
