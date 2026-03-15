import useSetPageTitle from "../../../hooks/useSetPageTitle";
import EmailChangeForm from "../../../components/forms/EmailChangeForm";
import OTPForm from "../../../components/forms/OTPForm";
import useAxios from "../../../hooks/useAxios";
import { EmailChange } from "../../../schemas/AuthSchema";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useHandleError from "../../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../../components/general/fetchModals/APIResponsePopup";

function EmailChangeWindow() {
  const axios = useAxios();
  const [emailChangeData, setEmailChangeData] = useState<EmailChange>();
  const [OTPSent, setOTPSent] = useState(false);
  const [OTPJWT, setOTPJWT] = useState<string>();
  const navigate = useNavigate();

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const _ = useSetPageTitle("email change");

  const OTPUseCase = "email_change";

  useEffect(() => {
    if (OTPJWT && emailChangeData) {
      setOTPSent(false);
      axios
        .patch(`/auth/email?otp_token=${OTPJWT}`, emailChangeData)
        .then((res) => {
          if (res.status == 200) {
            setSuccessMessage("email updated successfully.");
          }
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        });
    }
  }, [OTPJWT]);

  return (
    <div className="window email-change-window">
      <div className="window-section grow">
        {(!OTPSent && (
          <EmailChangeForm
            setSuccessMessage={setSuccessMessage}
            OTPUseCase={OTPUseCase}
            setEmailChangeData={setEmailChangeData}
            setOTPSent={setOTPSent}
            errorMessage={errorMessage}
            setErrorMessage={setErrorMessage}
          />
        )) || (
          <OTPForm
            setSuccessMessage={setSuccessMessage}
            setErrorMessage={setErrorMessage}
            errorMessage={errorMessage}
            email={emailChangeData?.email}
            OTPUseCase={OTPUseCase}
            setOTPJWT={setOTPJWT}
          />
        )}
      </div>
      <AnimatePresence>
        {successMessage && (
          <APIResponsePopup
            popupType="success"
            message={successMessage}
            setMessage={setSuccessMessage}
            successAction={() => {navigate("/auth/account")}}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default EmailChangeWindow;
