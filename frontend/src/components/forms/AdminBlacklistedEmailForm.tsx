import useHandleError from "../../hooks/useHandleError";
import useAxios from "../../hooks/useAxios";
import getFormEntries from "../../utilities/getFormEntries";
import React, { SetStateAction, useState } from "react";
import FormErrorModal from "../general/modals/FormErrorModal";
import { SetBoolState, SetOptionalTextState } from "../../types/types";
import { AnimatePresence } from "framer-motion";
import {
  BlacklistedEmail,
  BlacklistedEmailCreateUpdateSchema,
  BlacklistedEmailSchema,
} from "../../schemas/BlacklistedEmailSchemas";
import { useNavigate } from "react-router-dom";
import APIResponsePopup from "../general/modals/APIResponsePopup";

type Props = {
  forUpdate?: boolean;
  blacklistedEmail?: BlacklistedEmail;
  errorMessage: string | undefined;
  isFetching: boolean;
  setBlacklisteEmailData: React.Dispatch<SetStateAction<BlacklistedEmail | undefined>>;
  setErrorMessage: SetOptionalTextState;
  setIsFetching: SetBoolState;
};

function BlacklistedEmailForm({
  forUpdate,
  blacklistedEmail,
  errorMessage,
  setErrorMessage,
  setIsFetching,
  isFetching,
  setBlacklisteEmailData,
}: Props) {
  const axios = useAxios({ forAdmin: true });
  const navigate = useNavigate();

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsFetching(true);
    setErrorMessage(undefined);
    setErrorPath(undefined);

    const formData = getFormEntries(e.currentTarget);
    console.log("hdbhb");
    try {
      const parsedFormData = BlacklistedEmailCreateUpdateSchema.parse(formData);
      if (forUpdate) {
        console.log("for update");
        if (!blacklistedEmail) {
          setErrorMessage("Blacklisted email data has not been loaded.");
          return;
        }
        const res = await axios.patch(
          `/admin/email_blacklist?id=${blacklistedEmail.id}`,
          parsedFormData
        );
        const parsedRes = BlacklistedEmailSchema.parse(res.data);
        setBlacklisteEmailData(parsedRes);
        setSuccessMessage("blacklisted email updated successfully.");
      } else {
        console.log("not for update");
        const res = await axios.post("/admin/email_blacklist", parsedFormData);
        const parsedRes = BlacklistedEmailSchema.parse(res.data);
        setSuccessMessage("blacklisted email created successfully.");
      }
    } catch (err) {
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };
  return (
    <>
      <form name="blacklisted-email-form" onSubmit={handleFormSubmit} className="spaced-out-form">
        <div className="form-section form-main-content-container">
          {forUpdate && blacklistedEmail && (
            <div className="input-container">
              <label htmlFor="email">id</label>
              <input
                name="id"
                id="id"
                key="id"
                className={(errorPath == "id" && "error") || "normal"}
                type="text"
                value={blacklistedEmail.id}
                disabled
              />
              {errorMessage && errorPath == "id" && <FormErrorModal errorMessage={errorMessage} />}
            </div>
          )}
          <div className="input-container">
            <label htmlFor="sub">email</label>
            <input
              name="sub"
              id="sub"
              key="sub"
              className={(errorPath == "sub" && "error") || "normal"}
              type="text"
              placeholder="new@example.com"
              defaultValue={blacklistedEmail?.sub}
              required={!forUpdate}
            />
            {errorMessage && errorPath == "sub" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          {forUpdate && blacklistedEmail && (
            <div className="input-container">
              <label htmlFor="created_at">created at</label>
              <input
                name="created_at"
                id="created_at"
                key="created_at"
                className={(errorPath == "created_at" && "error") || "normal"}
                type="text"
                placeholder="new@example.com"
                defaultValue={blacklistedEmail.created_at}
                disabled
              />
              {errorMessage && errorPath == "created_at" && (
                <FormErrorModal errorMessage={errorMessage} />
              )}
            </div>
          )}
        </div>
        <div className="form-section submit-btn-container">
          <button
            name="button"
            type="submit"
            aria-label="submit email change form"
            className={`btn submit-btn ${(isFetching && "load") || ""}`}
            disabled={isFetching}
          >
            submit
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
              navigate("/admin/manage/email-blacklist");
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}

export default BlacklistedEmailForm;
