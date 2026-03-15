import useHandleError from "../../hooks/useHandleError";
import useAxios from "../../hooks/useAxios";
import { EmailChange, EmailChangeSchema } from "../../schemas/AuthSchema";
import getFormEntries from "../../utilities/getFormEntries";
import React, { SetStateAction, useState } from "react";
import FormErrorModal from "../general/modals/FormErrorModal";
import { OTPType, SetBoolState, SetOptionalTextState } from "../../types/types";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../general/fetchModals/APIResponsePopup";

type EmailChangeFormProps = {
  errorMessage: string | undefined;
  setEmailChangeData: React.Dispatch<SetStateAction<EmailChange | undefined>>;
  setOTPSent: SetBoolState;
  setErrorMessage: SetOptionalTextState;
  setSuccessMessage: SetOptionalTextState;
  OTPUseCase: OTPType;
};

function EmailChangeForm({
  setEmailChangeData,
  setOTPSent,
  errorMessage,
  setErrorMessage,
  setSuccessMessage,
  OTPUseCase,
}: EmailChangeFormProps) {
  const axios = useAxios();
  const [isFetching, setIsFetching] = useState(false);

  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);
    const formData = getFormEntries(e.currentTarget);
    setIsFetching(true);

    try {
      const parsedFormData = EmailChangeSchema.parse(formData);
      setEmailChangeData(parsedFormData);
      const res = await axios.post(`/auth/otp/request?use_case=${OTPUseCase}`, {
        email: parsedFormData.email,
      });
      setOTPSent(true);
      setSuccessMessage(`an OTP has been sent to ${parsedFormData.email}. please confirm.`);
    } catch (err) {
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };
  return (
    <>
      <form name="email-change-form" onSubmit={handleFormSubmit} className="spaced-out-form">
        <div className="form-section form-main-content-container">
          <div className="input-container">
            <label htmlFor="email">new email</label>
            <input
              name="email"
              id="email"
              key="email"
              className={(errorPath == "email" && "error") || "normal"}
              type="text"
              placeholder="new@example.com"
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
              placeholder="enter password"
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
            aria-label="submit email change form"
            className="btn submit-btn"
            disabled={isFetching}
          >
            change email
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

export default EmailChangeForm;
