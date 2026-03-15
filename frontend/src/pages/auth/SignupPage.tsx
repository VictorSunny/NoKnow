import OTPForm from "../../components/forms/OTPForm";
import SignupForm from "../../components/forms/SignupForm";
import useCreateAxiosInstance from "../../hooks/useCreateAxiosInstance";
import { UserCreate } from "../../schemas/AuthSchema";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import useSetPageTitle from "../../hooks/useSetPageTitle";
import useHandleError from "../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../components/general/fetchModals/APIResponsePopup";

export function SignupPage() {
  const [signupData, setSignupData] = useState<UserCreate>();
  const [OTPSent, setOTPSent] = useState(false);
  const [OTPJWT, setOTPJWT] = useState<string>();
  const axios = useCreateAxiosInstance();

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from.pathname ?? "/";

  const OTPUseCase = "signup";

  const _ = useSetPageTitle("signup");

  useEffect(() => {
    if (signupData) {
      axios
        .post(`/auth/otp/request?use_case=${OTPUseCase}`, { email: signupData.email })
        .then((res) => {
          if (res.status == 202) {
            setOTPSent(true);
          }
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        });
    }
  }, [signupData]);

  useEffect(() => {
    if (OTPJWT && signupData) {
      axios
        .post(`/auth/signup?otp_token=${OTPJWT}`, signupData)
        .then((res) => {
          setSuccessMessage("Welcome!");
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        });
    }
  }, [OTPJWT]);

  return (
    <div className="page-container auth">
      <div className="section grow">
        {(signupData && OTPSent && (
          <OTPForm
            email={signupData.email}
            setSuccessMessage={setSuccessMessage}
            setErrorMessage={setErrorMessage}
            OTPUseCase={OTPUseCase}
            setOTPJWT={setOTPJWT}
            errorMessage={errorMessage}
          />
        )) || (
          <SignupForm
            errorMessage={errorMessage}
            setErrorMessage={setErrorMessage}
            setSignupData={setSignupData}
          />
        )}
        <a href="api/auth/google/login" className="link-text">
          signup with google
        </a>
      </div>
      <AnimatePresence>
        {successMessage && (
          <APIResponsePopup
            popupType="success"
            message={successMessage}
            setMessage={setSuccessMessage}
            successAction={() => {
              navigate(from, { replace: true });
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
