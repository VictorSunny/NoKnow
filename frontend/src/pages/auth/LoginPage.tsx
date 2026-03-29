import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { AccessTokenDataSchema, UserLogin, UserCompleteSchema } from "../../schemas/AuthSchema";

import { Link } from "react-router-dom";
import OTPForm from "../../components/forms/OTPForm";
import LoginForm from "../../components/forms/LoginForm";
import { useAuthContext } from "../../contexts/AuthContext";
import useAxios from "../../hooks/useAxios";
import useSetPageTitle from "../../hooks/useSetPageTitle";
import useHandleError from "../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import useUserLoggedInStatus from "../../hooks/useUserLoggedInStatus";
import APIResponsePopup from "../../components/general/modals/APIResponsePopup";

type Props = {
  adminLogin?: boolean;
};
export default function LoginPage({ adminLogin }: Props) {

  // This component returns a login form,
  
  // If the targeted account is not two factor auth protected,
  // the user is logged in straight away if credentails are valid.

  // If the targeted user account is two factor auth protected,
  // an otp dialogue is triggered and if all credentails are valid, the user gets logged in

  const [isTwoFactorAuthenticated, setIsTwoFactorAuthenticated] = useState<boolean>(false);
  const [loginData, setLoginData] = useState<UserLogin>();

  const [loginSuccessful, setLogginSuccessful] = useState(false);

  const [OTPJWT, setOTPJWT] = useState<string>();
  const [OTPSent, setOTPSent] = useState(false);
  const { setAccessTokenData, setUserDetails } = useAuthContext();
  const { setUserIsLoggedIn } = useUserLoggedInStatus();

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const navigate = useNavigate();
  const axios = useAxios();
  const location = useLocation();

  const from = location.state?.from.pathname ?? "/";

  const OTPUseCase = "login";

  const _ = useSetPageTitle("login");

  const loginURLPrefix = (adminLogin && "/admin/auth/login") || "/auth/login";

  useEffect(() => {
    if (loginData && OTPJWT) {
      axios
        .post(`${loginURLPrefix}?otp_token=${OTPJWT}`, loginData)
        .then((res) => {
          const accessTokenRes = AccessTokenDataSchema.parse(res.data);
          setAccessTokenData(accessTokenRes);
          setUserIsLoggedIn(true);
          setLogginSuccessful(true);
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        });
    }
  }, [OTPJWT]);

  useEffect(() => {
    if (loginSuccessful) {
      axios
        .get("/user")
        .then((res) => {
          const parsedUserResponse = UserCompleteSchema.parse(res.data);
          setUserDetails(parsedUserResponse);
          // set success message to trigger page navigation
          setSuccessMessage("login successful.");
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        });
    }
  }, [loginSuccessful]);

  return (
    <div className="page-container auth login-page-container">
      <div className="section grow compact-form-container">
        {/* return OTP form if login credentails are provided, otp code has been sent to user email, and user account is two factor auth protected  */}
        {(OTPSent && loginData && isTwoFactorAuthenticated && (
          <OTPForm
            setSuccessMessage={setSuccessMessage}
            setErrorMessage={setErrorMessage}
            email={loginData.email}
            OTPUseCase={OTPUseCase}
            setOTPJWT={setOTPJWT}
            errorMessage={errorMessage}
          />
        )) || (
          <LoginForm
            adminLogin={adminLogin}
            loginUrlPrefix={loginURLPrefix}
            setErrorMessage={setErrorMessage}
            errorMessage={errorMessage}
            setLoginData={setLoginData}
            setOTPSent={setOTPSent}
            OTPUseCase={OTPUseCase}
            setIsTwoFactorAuthenticated={setIsTwoFactorAuthenticated}
          />
        )}
        <Link to={"/auth/signup"} className="link-text">
          no account yet? signup now
        </Link>
        <AnimatePresence>
          {successMessage && (
            <APIResponsePopup
              popupType="success"
              message={successMessage}
              setMessage={setSuccessMessage}
              successAction={() => {
                navigate((adminLogin && "/admin/manage") || from, { replace: true });
              }}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
