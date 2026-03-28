import React, { useState } from "react";
import ConfirmActionDialogue from "../../general/modals/ConfirmActionDialogue";
import { SetBoolState } from "../../../types/types";
import useAxios from "../../../hooks/useAxios";
import useHandleError from "../../../hooks/useHandleError";
import getFormEntries from "../../../utilities/getFormEntries";
import { SinglePasswordSchema } from "../../../schemas/GenericSchemas";
import { UserComplete } from "../../../schemas/AuthSchema";
import { AnimatePresence } from "framer-motion";
import FormErrorModal from "../../general/modals/FormErrorModal";
import APIResponsePopup from "../../general/modals/APIResponsePopup";

type Props = {
  userData: UserComplete;
  setShowConfirmDialogue: SetBoolState;
};
export default function AdminConfirmAddToSuperuserDialogue({
  setShowConfirmDialogue,
  userData,
}: Props) {
  const axios = useAxios({ forAdmin: true });

  const apiErrorHandler = useHandleError();

  const [isFetching, setIsFetching] = useState<boolean>();
  const [errorPath, setErrorPath] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [successMessage, setSuccessMessage] = useState<string>();

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const controller = new AbortController();
    const passwordForm = getFormEntries(e.currentTarget);

    setIsFetching(true);
    try {
      const parsedPasswordData = SinglePasswordSchema.parse(passwordForm);
      await axios.post(`/admin/user/groups/superuser/add?id=${userData.uid}`, parsedPasswordData, {
        signal: controller.signal,
      });
      setSuccessMessage("successfully added user to superusers.");
    } catch (err) {
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };

  return (
    <>
      <ConfirmActionDialogue setModalDisplayState={setShowConfirmDialogue}>
        <form method="POST" className="confirm-form" onSubmit={handleFormSubmit}>
          <p className="title">
            enter your password to confirm you want to add user to superusers.
            <br />
            candidate will be granted equal privileges and this action cannot be undone.
          </p>
          <input
            name="password"
            id="password"
            key="password"
            type="password"
            className={(errorPath == "password" && "error") || "normal"}
          />
          {errorMessage && errorPath == "password" && (
            <FormErrorModal errorMessage={errorMessage} />
          )}
          <button
            name="submit"
            type="submit"
            className={`btn submit-btn ${(isFetching && "load") || ""}`}
            aria-label="confirm adding candidate to superusers"
            disabled={isFetching}
          >
            confirm
          </button>
        </form>
      </ConfirmActionDialogue>
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
              setShowConfirmDialogue(false);
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
