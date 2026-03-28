import useSetPageTitle from "../../../hooks/useSetPageTitle";
import OTPForm from "../../../components/forms/OTPForm";
import PasswordChangeForm from "../../../components/forms/PasswordChangeForm";
import useAxios from "../../../hooks/useAxios";
import useGetLoggedInUser from "../../../hooks/useGetLoggedInUser";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import useHandleError from "../../../hooks/useHandleError";
import { PasswordChange } from "../../../schemas/GenericSchemas";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../../components/general/modals/APIResponsePopup";

function PasswordChangeWindow() {
  const [OTPJWT, setOTPJWT] = useState<string>();
  const [passwordChangeData, setPasswordChangeData] = useState<PasswordChange>();

  const [OTPSent, setOTPSent] = useState(false);

  const location = useLocation();
  const navigate = useNavigate();
  const axios = useAxios();

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const userDetails = useGetLoggedInUser({ setErrorMessage });

  const isRecovery = location.pathname.toLowerCase().includes("recovery");

  const OTPUseCase = "password_change";

  useEffect(() => {
    if (isRecovery && userDetails) {
      axios
        .post(`/auth/otp/request?use_case=${OTPUseCase}`, { email: userDetails.email })
        .then((res) => {
          if (res.status == 202) {
            setOTPSent(true);
            setSuccessMessage(
              `an OTP has been sent to ${userDetails.email}. please check your spam if you can't find the mail.`
            );
          }
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        });
    }
  }, [userDetails]);

  const _ = useSetPageTitle((isRecovery && "password recovery") || "password change");

  useEffect(() => {
    const passwordUpdateURL =
      (isRecovery && `/auth/password?otp_token=${OTPJWT}`) || "/auth/password";
    if (passwordChangeData) {
      axios
        .patch(passwordUpdateURL, passwordChangeData)
        .then((res) => {
          if (res.status == 200) {
            setSuccessMessage("password updated successfully.");
          }
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        });
    }
  }, [passwordChangeData, OTPJWT]);

  return (
    <div className="window password-change-window">
      <div className="window-section grow">
        {(isRecovery && OTPSent && !OTPJWT && (
          <OTPForm
            setSuccessMessage={setSuccessMessage}
            setErrorMessage={setErrorMessage}
            OTPUseCase={OTPUseCase}
            email={userDetails!.email}
            setOTPJWT={setOTPJWT}
            errorMessage={errorMessage}
          />
        )) || (
          <PasswordChangeForm
            errorMessage={errorMessage}
            isRecovery={isRecovery}
            setPasswordChangeData={setPasswordChangeData}
            setErrorMessage={setErrorMessage}
          />
        )}
      </div>
      <AnimatePresence>
        {successMessage && (
          <APIResponsePopup
            popupType="success"
            message={successMessage}
            setMessage={setSuccessMessage}
            successAction={() => {
              navigate("/auth/account");
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default PasswordChangeWindow;
