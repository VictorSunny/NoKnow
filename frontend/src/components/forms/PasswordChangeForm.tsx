import { Link } from "react-router-dom";
import getFormEntries from "../../utilities/getFormEntries";
import React, { SetStateAction, useState } from "react";
import useHandleError from "../../hooks/useHandleError";
import { PasswordChange, PasswordChangeSchema } from "../../schemas/GenericSchemas";
import FormErrorModal from "../general/modals/FormErrorModal";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../general/modals/APIResponsePopup";
import { SetOptionalTextState } from "../../types/types";

type PasswordChangeFormProps = {
  isRecovery: boolean;
  errorMessage: string | undefined;
  setPasswordChangeData: React.Dispatch<SetStateAction<PasswordChange | undefined>>;
  setErrorMessage: SetOptionalTextState;
};
function PasswordChangeForm({
  isRecovery,
  errorMessage,
  setPasswordChangeData,
  setErrorMessage,
}: PasswordChangeFormProps) {
  // This component updates sets the `passwordChangeData` state value if the valid credentails are provided
  // The parent component containing this password change form would then use the new `passwordChangeData` value

  // if `isRecovery` is set True, then this component would be used in a recovery context,
  // and would not require the user to provide their previous password value

  const [isFetching, setIsFetching] = useState(false);

  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);
    const passwordChangeForm = getFormEntries(e.currentTarget);
    setIsFetching(true);
    try {
      const parsedFormData = PasswordChangeSchema.parse(passwordChangeForm);
      setPasswordChangeData(parsedFormData);
    } catch (err) {
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };
  return (
    <>
      <form name="password-chage-form" className="window-form spaced-out-form" onSubmit={onSubmit}>
        <div className="form-section form-main-content-container">
          {!isRecovery && (
            <>
              <div className="input-container">
                <label htmlFor="old_password">current password</label>
                <input
                  name="old_password"
                  id="old_password"
                  key="old_password"
                  className={(errorPath == "old_password" && "error") || "normal"}
                  type="text"
                  placeholder="enter current password"
                  required
                />
              </div>
              {errorMessage && errorPath == "old_password" && (
                <FormErrorModal errorMessage={errorMessage} />
              )}
            </>
          )}
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
          <div className="input-container">
            <label htmlFor="confirm_password">confirm</label>
            <input
              name="confirm_password"
              id="confirm_password"
              key="confirm_password"
              className={(errorPath == "confirm_password" && "error") || "normal"}
              type="text"
              placeholder="enter password"
              required
            />
            {errorMessage && errorPath == "confirm_password" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
        </div>
        <div className="form-section submit-btn-container">
          <button
            type="submit"
            name="button"
            aria-label="submit password change form"
            className={`btn submit-btn ${(isFetching && "load") || ""}`}
            disabled={isFetching}
          >
            submit
          </button>
        </div>
        {!isRecovery && (
          <Link replace to={"recovery"} className="link-btn">
            forgot password?
          </Link>
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

export default PasswordChangeForm;
