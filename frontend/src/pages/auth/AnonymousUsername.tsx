import AnonymousUsernameForm from "../../components/forms/AnonymousUsernameForm";
import { useEffect, useState } from "react";
import useSetPageTitle from "../../hooks/useSetPageTitle";
import useAxios from "../../hooks/useAxios";
import useCheckUserIsAuthenticated from "../../hooks/useCheckUserIsAuthenticated";
import { UserPrivacyStatus } from "../../schemas/AuthSchema";
import FetchErrorSignal from "../../components/general/fetchModals/FetchErrorModal";
import useHandleError from "../../hooks/useHandleError";

export default function AnonymousUsername() {
  const [userIsHidden, setUserIsHidden] = useState(false);
  const userIsLoggedIn = useCheckUserIsAuthenticated();

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
      <div className="section form-container grow">
        <AnonymousUsernameForm />
        {userIsLoggedIn && (
          <>
            <button
              className={`toggle-btn btn ${(userIsHidden && "active") || ""} ${(isFetching && "load") || ""}`}
              onClick={handleHiddenStatusClick}
              disabled={isFetching}
            >
              {(userIsHidden && "unhide") || "hide"}
            </button>
            {errorMessage && <FetchErrorSignal errorMessage={errorMessage} />}
          </>
        )}
      </div>
    </div>
  );
}
