import isAlNum from "../../utilities/isAlNum";
import getFormEntries from "../../utilities/getFormEntries";
import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import FormErrorModal from "../general/modals/FormErrorModal";
import { v4 as uuidv4 } from "uuid";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../general/modals/APIResponsePopup";

export default function AnonymousUsernameForm() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from.pathname ?? "/chat";

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [errorPath, setErrorPath] = useState<string>();

  const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);
    const formData = getFormEntries(e.currentTarget);
    const anonUsernameValue = formData["anon_username"].toString();
    const isValid = isAlNum(anonUsernameValue);
    if (!isValid) {
      setErrorPath("anon_username");
      setErrorMessage("username must can contain only letters and numbers");
      return;
    }
    const randomID = uuidv4().toString().slice(0, 5);
    const anonUsername = anonUsernameValue + "-" + randomID;
    sessionStorage.setItem("anon_username", anonUsername);

    // set anonymous username to trigger page navigation
    setSuccessMessage("anonymous username has been set.");
  };
  return (
    <>
      <form
        name="anonymous-username-form"
        onSubmit={handleFormSubmit}
        className="compact-form"
        method="POST"
      >
        <div className="form-section-form-title-container">
          <p className="title">set anonymous username</p>
        </div>
        <div className="form-section form-main-content-container">
          <div className="input-container">
            <label htmlFor="anon_username">username</label>
            <input
              name="anon_username"
              id="anon_username"
              key="anon_username"
              type="text"
              className={(errorPath == "anon_username" && "error") || "normal"}
              maxLength={25}
              placeholder="who do you want to be?"
              required
            />
            {errorMessage && errorPath == "anon_username" && (
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
              navigate(from, { replace: true });
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
