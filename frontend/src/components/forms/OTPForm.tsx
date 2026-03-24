import useAxios from "../../hooks/useAxios";
import getFormEntries from "../../utilities/getFormEntries";
import React, { useRef, useState } from "react";
import FormErrorModal from "../general/modals/FormErrorModal";
import useHandleError from "../../hooks/useHandleError";
import { OTPType, SetOptionalTextState } from "../../types/types";
import { OTPJWTSchema } from "../../schemas/AuthSchema";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../general/popups/messagePopups/APIResponsePopup";
import { AxiosError } from "axios";

type OTPFormProps = {
  setErrorMessage: SetOptionalTextState;
  setSuccessMessage: SetOptionalTextState;
  OTPUseCase: OTPType;
  email: string | undefined;
  setOTPJWT: SetOptionalTextState;
  errorMessage: string | undefined;
};

function OTPForm({
  setErrorMessage,
  email,
  OTPUseCase,
  setOTPJWT,
  errorMessage,
  setSuccessMessage,
}: OTPFormProps) {
  const axios = useAxios();
  const [OTPExpired, setOTPExpired] = useState(false);
  const [isFetching, setIsFetching] = useState(false);

  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();
  const OTPFormRef = useRef<HTMLFormElement>(null);

  const handleOTPFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);
    const OTPForm = getFormEntries(e.currentTarget);
    const OTPCode = OTPForm["otp_code"];
    const OTPTokenRequestForm = {
      email: email,
      otp: Number(OTPCode),
    };
    setIsFetching(true);
    axios
      .post(`/auth/otp/token?use_case=${OTPUseCase}`, OTPTokenRequestForm)
      .then((res) => {
        const OTPJWT = OTPJWTSchema.parse(res.data).otp_jwt;
        setOTPJWT(OTPJWT);
        setSuccessMessage("successfully confirmed.");
      })
      .catch((err) => {
        if (err instanceof AxiosError && err.response?.data.message) {
          "expired".search(err.response.data.message) && setOTPExpired(true);
        }
        apiErrorHandler({ err, setErrorMessage, setErrorPath });
      })
      .finally(() => {
        setIsFetching(false);
      });
  };

  const handleRefreshOTPClick = () => {
    axios
      .post(`/auth/otp/request?use_case=${OTPUseCase}`, { email: email })
      .then((res) => {
        setOTPExpired(false);
        setErrorMessage(undefined);
        setErrorPath(undefined);
        OTPFormRef.current?.reset();
        setSuccessMessage(
          `an OTP has been sent to ${email}. please check your spam if you can't find the mail.`
        );
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage, setErrorPath });
      });
  };

  return (
    <>
      <form
        name="otp-form"
        onSubmit={handleOTPFormSubmit}
        className="spaced-out-form"
        method="POST"
        ref={OTPFormRef}
      >
        <div className="form-section form-main-content-container">
          <div className="input-container">
            <label htmlFor="otp_code">OTP</label>
            <input
              name="otp_code"
              id="otp_code"
              key="otp_code"
              className={(errorPath == "otp_code" && "error") || "normal"}
              type="text"
              placeholder="enter OTP"
              required
            />
            {errorMessage && errorPath == "otp_code" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
        </div>
        <div className="form-section submit-btn-container">
          <button
            type="submit"
            name="button"
            aria-label="submit signup otp form"
            className="btn submit-btn"
          >
            enter
          </button>
        </div>
        {}
        {OTPExpired && (
          <button
            className={`btn ${(isFetching && "load") || ""}`}
            onClick={handleRefreshOTPClick}
            disabled={isFetching}
          >
            request new otp
          </button>
        )}
      </form>
      <AnimatePresence>
        {errorMessage && !errorPath && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
      </AnimatePresence>
    </>
  );
}

export default OTPForm;
