import AnimatedWindowWrapper from "../AnimatedWindowWrapper";
import { Outlet, useLocation } from "react-router-dom";

import { ReactComponent as GeneralIcon } from "../../assets/icons/profile-user-details.svg";
import { ReactComponent as PasswordIcon } from "../../assets/icons/profile-password.svg";
import { ReactComponent as EmailIcon } from "../../assets/icons/profile-email.svg";
import { ReactComponent as TwoFactorAuthIcon } from "../../assets/icons/profile-two-factor-auth.svg";
import { ReactComponent as DeactivateIcon } from "../../assets/icons/profile-deactivate.svg";

import useGetLoggedInUser from "../../hooks/useGetLoggedInUser";
import { NavLink } from "react-router-dom";

import "./Profile.css";
import { Suspense, useState } from "react";
import FetchErrorSignal from "../../components/general/modals/FetchErrorModal";
import NavContainer from "../../components/general/dropdownSelect/NavContainer";
import FetchingLoader from "../../components/general/loaders/FetchingLoader";

function Profile() {
  const location = useLocation();
  const [errorMessage, setErrorMessage] = useState<string>();
  const userDetails = useGetLoggedInUser({ setErrorMessage });

  return (
    <>
      {(!userDetails && !errorMessage && <FetchingLoader />) ||
        (!userDetails && errorMessage && <FetchErrorSignal errorMessage={errorMessage} />) ||
        (userDetails && (
          <div className="page-container profile-page-container">
            <div className="section">
              <div className="basic-info-container">
                <p className="user-names">
                  <span className="username title">{userDetails?.username}</span>.{" "}
                  {userDetails?.first_name} {userDetails?.last_name}
                </p>
                <p className="bio medium-spaced">{userDetails.bio}</p>
                <p className="date-joined">Joined: {userDetails?.joined!}</p>
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
                  <div className="text-icon-container">
                    <GeneralIcon className="icon" aria-label="user general window icon" />
                    <span>user details</span>
                  </div>
                </NavLink>
                <NavLink
                  to={"password"}
                  className="nav-link"
                  aria-label="go to password change page"
                  replace
                  end
                >
                  <div className="text-icon-container">
                    <PasswordIcon className="icon" aria-label="user password window icon" />
                    <span>change password</span>
                  </div>
                </NavLink>
                <NavLink
                  to={"email"}
                  className="nav-link"
                  aria-label="go to email update page"
                  replace
                  end
                >
                  <div className="text-icon-container">
                    <EmailIcon className="icon" aria-label="user email window icon" />
                    <span>change email</span>
                  </div>
                </NavLink>
                <NavLink
                  to={"two-factor-auth"}
                  className="nav-link"
                  aria-label="go to two factor auth update page"
                  replace
                  end
                >
                  <div className="text-icon-container">
                    <TwoFactorAuthIcon
                      className="icon"
                      aria-label="user two factor authentication window icon"
                    />
                    <span>two factor authentication</span>
                  </div>
                </NavLink>
                <NavLink
                  to={"delete"}
                  className="nav-link"
                  aria-label="go to account deactivation page"
                  replace
                  end
                >
                  <div className="text-icon-container">
                    <DeactivateIcon className="icon" aria-label="user deactivate window icon" />
                    <span>deactivate</span>
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
        ))}
    </>
  );
}

export default Profile;
