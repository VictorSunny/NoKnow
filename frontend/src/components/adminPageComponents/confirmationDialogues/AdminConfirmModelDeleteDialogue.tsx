import { UUID } from "crypto";
import useAxios from "../../../hooks/useAxios";
import useHandleError from "../../../hooks/useHandleError";
import { APIModelName, SetBoolState } from "../../../types/types";
import ConfirmActionDialogue from "../../general/confirmationModals/ConfirmActionDialogue";
import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../general/fetchModals/APIResponsePopup";
import { useNavigate } from "react-router-dom";

type Props = {
  setShowDeleteDialogue: SetBoolState;
  modelName: APIModelName;
  id: UUID | string | number;
};
export default function AdminConfirmModelDeleteDialogue({
  setShowDeleteDialogue,
  modelName,
  id,
}: Props) {
  const axios = useAxios({ forAdmin: true });
  const navigate = useNavigate();
  const apiErrorHandler = useHandleError();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [successMessage, setSuccessMessage] = useState<string>();

  const deleteURLPrefix =
    (modelName == "chatroom" && "/admin/chat/all") ||
    (modelName == "user" && "/admin/user/all") ||
    (modelName == "blacklistedEmail" && "/admin/email_blacklist/all") ||
    (modelName == "blacklistedToken" && "/admin/token_blacklist/all");

  const redirectPath =
    (modelName == "user" && "/admin/manage/user") ||
    (modelName == "chatroom" && "/admin/manage/chatroom") ||
    (modelName == "blacklistedEmail" && "/admin/manage/email-blacklist") ||
    (modelName == "blacklistedToken" && "/admin/manage/token-blacklist") ||
    "/admin";

  const handleDeleteClick = () => {
    const controller = new AbortController();
    axios
      .delete(`${deleteURLPrefix}/?id=${id}`)
      .then(() => {
        setSuccessMessage("successfully deleted.");
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        controller.abort();
      });
  };
  return (
    <>
      <ConfirmActionDialogue setModalDisplayState={setShowDeleteDialogue}>
        <p className="title">please confirm you want to delete.</p>
        <button onClick={handleDeleteClick} className="danger">
          delete
        </button>
      </ConfirmActionDialogue>
      <AnimatePresence>
        {errorMessage && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
        {successMessage && (
          <APIResponsePopup
            popupType="success"
            message={successMessage}
            setMessage={setSuccessMessage}
            successAction={() => {
              navigate(redirectPath);
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
