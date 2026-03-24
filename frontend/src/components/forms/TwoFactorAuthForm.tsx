import useSetPageTitle from "../../hooks/useSetPageTitle";
import FormErrorModal from "../general/modals/FormErrorModal";
import useAxios from "../../hooks/useAxios";
import { TwoFactorAuthStatusResponseSchema } from "../../schemas/AuthSchema";
import { SinglePasswordSchema } from "../../schemas/GenericSchemas";
import getFormEntries from "../../utilities/getFormEntries";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useHandleError from "../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../general/popups/messagePopups/APIResponsePopup";

export default function TwoFactorAuthForm() {
  const [isTwoFactorAuth, setIsTwoFactorAuth] = useState<boolean>();
  const axios = useAxios();
  const navigate = useNavigate();
  const [isFetching, setIsFetching] = useState(false);

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();

  const _ = useSetPageTitle("2 factor auth");

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);
    const passwordForm = getFormEntries(e.currentTarget);

    try {
      const parsedPasswordData = SinglePasswordSchema.parse(passwordForm);
      const res = await axios.patch("/auth/two_factor_authentication", parsedPasswordData);
      const twoFactorAuthActive = TwoFactorAuthStatusResponseSchema.parse(
        res.data
      ).is_two_factor_authenticated;
      setIsTwoFactorAuth(twoFactorAuthActive);
      setSuccessMessage("successfully updated 2 factor authentication status.");
    } catch (err) {
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };

  useEffect(() => {
    axios
      .post("/auth/two_factor_authentication")
      .then((res) => {
        const twoFactorAuthActive = TwoFactorAuthStatusResponseSchema.parse(
          res.data
        ).is_two_factor_authenticated;
        setIsTwoFactorAuth(twoFactorAuthActive);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage, setErrorPath });
      });
  }, []);

  return (
    <>
      <form
        name="two-factor-auth-password-form"
        onSubmit={handleFormSubmit}
        className="spaced-out-form"
      >
        <div className="form-section form-main-content-container">
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
            {(isTwoFactorAuth && "disable") || "enable"}
          </button>
        </div>
      </form>
      <AnimatePresence>
        {errorMessage && !errorPath && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
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
    </>
  );
}
