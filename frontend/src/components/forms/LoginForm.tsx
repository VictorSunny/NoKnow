import { refreshUserDetails } from "../../hooks/useRefresh";
import { useAuthContext } from "../../contexts/AuthContext";
import {
  AccessTokenDataSchema,
  TwoFactorAuthStatusSchema,
  UserLogin,
  UserLoginSchema,
} from "../../schemas/AuthSchema";
import getFormEntries from "../../utilities/getFormEntries";
import { SetStateAction, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import useCreateAxiosInstance from "../../hooks/useCreateAxiosInstance";
import FormErrorModal from "../general/modals/FormErrorModal";
import useHandleError from "../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../general/modals/APIResponsePopup";
import { SetBoolState, SetOptionalTextState } from "../../types/types";
import useUserLoggedInStatus from "../../hooks/useUserLoggedInStatus";

type LoginFormProps = {
  adminLogin: boolean | undefined;
  setIsTwoFactorAuthenticated: SetBoolState;
  setLoginData: React.Dispatch<SetStateAction<UserLogin | undefined>>;
  setOTPSent: SetBoolState;
  OTPUseCase: string;
  setErrorMessage: SetOptionalTextState;
  errorMessage: string | undefined;
  loginUrlPrefix: string;
};

function LoginForm({
  adminLogin,
  setIsTwoFactorAuthenticated,
  setLoginData,
  setOTPSent,
  OTPUseCase,
  setErrorMessage,
  errorMessage,
  loginUrlPrefix,
}: LoginFormProps) {
  // This component takes the required login credentails and updates login data state value,
  // then checks if the matching user account is two factor auth protected.
  // If the user account is not two factor auth protected, the user is logged in straight away

  // otherwise, if the user account is two factor auth protected,
  // an otp code is requested, and the `OTPSent` and `isTwoFactorAuthenticated` state values are updated
  // with these state values updated,
  // the parent component containing this login form component should then display an otp form window which will then handle the user login from there

  const axios = useCreateAxiosInstance();
  const { setAccessTokenData, accessTokenData, setUserDetails } = useAuthContext();
  const { setUserIsLoggedIn } = useUserLoggedInStatus();

  const [loginSuccessful, setLogginSuccessful] = useState(false);
  const [isFetching, setIsFetching] = useState(false);

  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();

  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from.pathname ?? "/";

  const handleLoginFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);
    const loginForm = getFormEntries(e.currentTarget);
    const parsedLoginData = UserLoginSchema.parse(loginForm);
    setLoginData(parsedLoginData);

    setIsFetching(true);
    // upon login form submission
    // check if user account is two factor auth protected
    axios
      .post("/auth/two_factor_authentication", { email: parsedLoginData.email })
      .then((res) => {
        const twoFactorAuthStatusActive = TwoFactorAuthStatusSchema.parse(
          res.data
        ).is_two_factor_authenticated;
        setIsTwoFactorAuthenticated(twoFactorAuthStatusActive);

        // request for otp code if user account is two factor auth protected
        // set state to indicate that otp code has been requested for
        // login page which is the parent component to this form component would then update it's state to display an otp form
        // login page would then handle login directly upon provision of necessary credentials
        if (twoFactorAuthStatusActive) {
          axios
            .post(`auth/otp/request?use_case=${OTPUseCase}`, { email: parsedLoginData.email })
            .then((res) => {
              if (res.status == 202) {
                setOTPSent(true);
              }
            })
            .catch((err) => {
              apiErrorHandler({ err, setErrorMessage, setErrorPath });
            });
        } else {
          // login straight away if user account is not two factor auth protected
          axios
            .post(loginUrlPrefix, parsedLoginData)
            .then((res) => {
              const accessTokenResponse = AccessTokenDataSchema.parse(res.data);
              setAccessTokenData(accessTokenResponse);
              setUserIsLoggedIn(true);
              setLogginSuccessful(true);
            })
            .catch((err) => {
              apiErrorHandler({ err, setErrorMessage, setErrorPath });
            });
        }
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage, setErrorPath });
      })
      .finally(() => {
        setIsFetching(false);
      });
  };

  useEffect(() => {
    if (loginSuccessful && accessTokenData) {
      refreshUserDetails({ accessTokenData: accessTokenData, setUserDetails: setUserDetails });
      navigate((adminLogin && "/admin/manage") || from, { replace: true });
    }
  }, [loginSuccessful]);

  return (
    <>
      <form
        name="login-form"
        onSubmit={handleLoginFormSubmit}
        className="compact-form"
        method="POST"
      >
        <div className="form-section form-title-container">
          <p className="title">{adminLogin && "admin login" || "user login"}</p>
        </div>
        <div className="form-section form-main-content-container">
          <div className="input-container">
            <label htmlFor="email">email</label>
            <input
              name="email"
              id="email"
              key="email"
              className={(errorPath == "email" && "error") || "normal"}
              type="text"
              placeholder="electronic@mail.com"
              required
            />
            {errorMessage && errorPath == "email" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          <div className="input-container">
            <label htmlFor="password">password</label>
            <input
              name="password"
              id="password"
              key="password"
              className={(errorPath == "password" && "error") || "normal"}
              type="password"
              placeholder="enter your password"
              required
            />
            {errorMessage && errorPath == "password" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
        </div>
        <div className="form-section submit-btn-container">
          <button
            type="submit"
            name="button"
            aria-label="submit login form"
            className={`btn submit-btn ${(isFetching && "load") || ""}`}
            disabled={isFetching}
          >
            login
          </button>
        </div>
      </form>
      <AnimatePresence>
        {errorMessage && !errorPath && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
      </AnimatePresence>
    </>
  );
}

export default LoginForm;
