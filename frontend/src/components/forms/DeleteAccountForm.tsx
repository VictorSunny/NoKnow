import useAxios from "../../hooks/useAxios";
import { ConfirmationTextSchema } from "../../schemas/GenericSchemas";
import getFormEntries from "../../utilities/getFormEntries";
import React, { useState } from "react";
import FormErrorModal from "../general/modals/FormErrorModal";
import { useNavigate } from "react-router-dom";
import useGetLoggedInUser from "../../hooks/useGetLoggedInUser";
import useHandleError from "../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../general/fetchModals/APIResponsePopup";

export default function DeleteAccountForm() {
  const axios = useAxios();
  const [isFetching, setIsFetching] = useState(false);
  const navigate = useNavigate();
  
  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();
  
  const userDetails = useGetLoggedInUser({setErrorMessage});

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    setErrorMessage(undefined);
    setErrorPath(undefined);
    e.preventDefault();

    const formData = getFormEntries(e.currentTarget);

    try {
      const parsedFormData = ConfirmationTextSchema.parse(formData);
      setIsFetching(true);
      const res = await axios.post("/auth/confirm_delete", parsedFormData);
      setSuccessMessage("account successfully deleted. sorry to see you go.");
    } catch (err) {
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };

  return (
    <>
      <form
        name="delete-account-form"
        method="DELETE"
        className="delete-account-form confirm-form"
        onSubmit={handleFormSubmit}
      >
        <p className="title">type "i {userDetails!.username} want to delete my account"</p>
        <input
          name="text"
          id="text"
          key="text"
          className={(errorPath == "text" && "error") || "normal"}
          type="text"
          placeholder="electronic@mail.com"
          required
        />
        {errorMessage && errorPath == "text" && <FormErrorModal errorMessage={errorMessage} />}
        <button
          type="submit"
          name="button"
          aria-label="submit account delete confirmation form"
          className="btn danger submit-btn"
          disabled={isFetching}
        >
          deactivate
        </button>
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
              navigate("/");
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
