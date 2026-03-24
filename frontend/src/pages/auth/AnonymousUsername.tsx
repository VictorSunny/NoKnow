import AnonymousUsernameForm from "../../components/forms/AnonymousUsernameForm";
import { useEffect, useState } from "react";
import useSetPageTitle from "../../hooks/useSetPageTitle";
import useAxios from "../../hooks/useAxios";
import useUserLoggedInStatus from "../../hooks/useUserLoggedInStatus";
import { UserPrivacyStatus } from "../../schemas/AuthSchema";
import useHandleError from "../../hooks/useHandleError";
import FetchErrorSignal from "../../components/general/popups/messagePopups/FetchErrorModal";

export default function AnonymousUsername() {
  const [userIsHidden, setUserIsHidden] = useState(false);
  const {userIsLoggedIn} = useUserLoggedInStatus();

  const [isFetching, setIsFetching] = useState<boolean>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const _ = useSetPageTitle("anonymous username");
  const axios = useAxios();

  const handleHiddenStatusClick = () => {
    axios
      .patch("/auth/privacy")
      .then((res) => {
        const userHiddenStatus = UserPrivacyStatus.parse(res.data).is_hidden;
        setUserIsHidden(userHiddenStatus);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false);
      });
  };

  useEffect(() => {
    if (userIsLoggedIn) {
      axios.get("/auth/privacy").then((res) => {
        const userHiddenStatus = UserPrivacyStatus.parse(res.data).is_hidden;
        setUserIsHidden(userHiddenStatus);
      });
    }
  }, [userIsLoggedIn]);

  return (
    <div className="page-container auth anon-username-page-container">
      <div className="section grow compact-form-container">
        <AnonymousUsernameForm />
        {userIsLoggedIn && (
          <>
            <button
              className={`toggle-btn centered ${(userIsHidden && "active") || ""} ${(isFetching && "load") || ""}`}
              onClick={handleHiddenStatusClick}
              disabled={isFetching}
            >
              {(userIsHidden && "unknown") || "known"}
            </button>
            {errorMessage && <FetchErrorSignal errorMessage={errorMessage} />}
          </>
        )}
      </div>
    </div>
  );
}
