import useCreateAxiosInstance from "../../hooks/useCreateAxiosInstance";
import { UserCreate, UserCreateSchema } from "../../schemas/AuthSchema";
import getFormEntries from "../../utilities/getFormEntries";
import React, { FormEventHandler, SetStateAction, useState } from "react";
import useHandleError from "../../hooks/useHandleError";
import FormErrorModal from "../general/modals/FormErrorModal";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../general/modals/APIResponsePopup";
import { SetOptionalTextState } from "../../types/types";

type SignupFormProps = {
  errorMessage: string | undefined;
  setSignupData: React.Dispatch<SetStateAction<UserCreate | undefined>>;
  setErrorMessage: SetOptionalTextState;
};

function SignupForm({ errorMessage, setSignupData, setErrorMessage }: SignupFormProps) {
  const axios = useCreateAxiosInstance();
  const [isFetching, setIsFetching] = useState(false);

  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();

  const handleSignupFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);
    const signupForm = getFormEntries(e.currentTarget);

    try {
      const parsedSignupData = UserCreateSchema.parse(signupForm);
      setIsFetching(true);
      await axios.post("/auth/data/check", parsedSignupData);
      setSignupData(parsedSignupData);
    } catch (err) {
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };
  return (
    <>
      <form
        name="user-create-form"
        onSubmit={handleSignupFormSubmit}
        className="compact-form"
        method="POST"
      >
        <div className="form-section form-main-content-container">
          <div className="input-container">
            <label htmlFor="first_name">first name</label>
            <input
              name="first_name"
              id="first_name"
              key="first_name"
              className={(errorPath == "first_name" && "error") || "normal"}
              type="text"
              placeholder="your first name"
              required
            />
            {errorMessage && errorPath == "first_name" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
          <div className="input-container">
            <label htmlFor="last_name">last name</label>
            <input
              name="last_name"
              id="last_name"
              key="last_name"
              className={(errorPath == "last_name" && "error") || "normal"}
              type="text"
              placeholder="your first name"
              required
            />
            {errorMessage && errorPath == "last_name" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
          <div className="input-container">
            <label htmlFor="email">email</label>
            <input
              name="email"
              id="email"
              key="email"
              className={(errorPath == "email" && "error") || "normal"}
              type="email"
              placeholder="electronic@mail.com"
              required
            />
            {errorMessage && errorPath == "email" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          <div className="input-container">
            <label htmlFor="username">username</label>
            <input
              name="username"
              id="username"
              key="username"
              className={(errorPath == "username" && "error") || "normal"}
              type="text"
              placeholder="enter a username"
              required
            />
            {errorMessage && errorPath == "username" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
          <div className="input-container">
            <label htmlFor="about">bio</label>
            <input
              name="about"
              id="about"
              key="about"
              className={(errorPath == "about" && "error") || "normal"}
              type="text"
              placeholder="maybe tell a bit about yourself (optional)"
            />
            {errorMessage && errorPath == "about" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          <div className="input-container">
            <label htmlFor="password">password</label>
            <input
              name="password"
              id="password"
              key="password"
              className={(errorPath == "password" && "error") || "normal"}
              type="password"
              placeholder="enter password. 8 character combination."
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
              type="password"
              placeholder="confirm entered password."
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
            aria-label="submit signup form"
            className={`btn submit-btn ${(isFetching && "load") || ""}`}
            disabled={isFetching}
          >
            signup
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

export default SignupForm;
