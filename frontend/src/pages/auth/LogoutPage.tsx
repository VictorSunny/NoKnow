import ConfirmActionDialogue from "../../components/general/confirmationModals/ConfirmActionDialogue";
import useCreateAxiosInstance from "../../hooks/useCreateAxiosInstance";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthContext } from "../../contexts/AuthContext";
import useSetPageTitle from "../../hooks/useSetPageTitle";
import useHandleError from "../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../components/general/popups/messagePopups/APIResponsePopup";
import useUserLoggedInStatus from "../../hooks/useUserLoggedInStatus";

type Props = {
  message?: string;
};
export default function LogoutPage(props?: Props) {
  const [logoutNotCanceled, setLogoutNotCancelled] = useState(true);
  const { setAccessTokenData, setUserDetails } = useAuthContext();
  const { setUserIsLoggedIn } = useUserLoggedInStatus();

  const navigate = useNavigate();
  const axios = useCreateAxiosInstance();

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const _ = useSetPageTitle("logout");

  useEffect(() => {
    if (!logoutNotCanceled) {
      navigate(-1);
    }
  }, [logoutNotCanceled]);

  const handlelogoutClick = () => {
    setErrorMessage(undefined);
    axios
      .post("/auth/logout")
      .then(() => {
        setAccessTokenData(undefined);
        setUserIsLoggedIn(false);
        setUserDetails(undefined);
        sessionStorage.removeItem("anon_username");
        setSuccessMessage("you are now logged out.");
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      });
  };

  return (
    <div className="page-container auth logout-page">
      <div className="section">
        <ConfirmActionDialogue setModalDisplayState={setLogoutNotCancelled}>
          <p className="title">{props?.message ?? "Are you sure you want to logout?"}</p>
          <button onClick={handlelogoutClick} className="btn danger">
            Logout
          </button>
          <AnimatePresence>
            {errorMessage && (
              <APIResponsePopup
                popupType="fail"
                message={errorMessage}
                setMessage={setErrorMessage}
              />
            )}
            {successMessage && (
              <APIResponsePopup
                popupType="success"
                message={successMessage}
                setMessage={setSuccessMessage}
                successAction={() => {
                  navigate("/");
                }}
              />
            )}
          </AnimatePresence>
        </ConfirmActionDialogue>
      </div>
    </div>
  );
}
