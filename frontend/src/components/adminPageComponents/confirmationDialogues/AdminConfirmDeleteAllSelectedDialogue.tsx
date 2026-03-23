import { useState } from "react";
import useHandleError from "../../../hooks/useHandleError";
import useAxios from "../../../hooks/useAxios";
import { getSelectedCheckboxes, removeItemsbyIDS } from "../../../utilities/formCheckboxHandlers";
import ConfirmActionDialogue from "../../general/confirmationModals/ConfirmActionDialogue";
import { APIModelName, SetBoolState } from "../../../types/types";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../general/fetchModals/APIResponsePopup";

type Props = {
  modelName: APIModelName;
  setShowDeleteMarkedDialougue: SetBoolState;
};
export default function AdminConfirmDeleteAllSelectedDialogue({
  setShowDeleteMarkedDialougue,
  modelName,
}: Props) {
  const axios = useAxios({ forAdmin: true });

  const [isFetching, setIsFetching] = useState<boolean>()
  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const APIDeleteURLPrefix =
    (modelName == "chatroom" && "/admin/chat/all") ||
    (modelName == "user" && "/admin/user/all") ||
    (modelName == "blacklistedEmail" && "/admin/email_blacklist/all") ||
    (modelName == "blacklistedToken" && "/admin/token_blacklist/all");

  const selectedIDs = getSelectedCheckboxes(modelName);

  if (selectedIDs.length < 1) {
    setShowDeleteMarkedDialougue(false);
    return;
  }

  const handleDeleteClick = () => {
    setErrorMessage(undefined);
    setIsFetching(true)
    axios
      .delete(`${APIDeleteURLPrefix}?id=${selectedIDs.value}`)
      .then((res) => {
        removeItemsbyIDS(selectedIDs.value, modelName);
        setSuccessMessage(`successfully deleted.`);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false)
      })
  };
  return (
    <>
      <ConfirmActionDialogue setModalDisplayState={setShowDeleteMarkedDialougue}>
        <p className="title">Are you sure you want to delete {selectedIDs.length} selected?</p>
        <button onClick={handleDeleteClick} disabled={isFetching}>confirm</button>
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
              setShowDeleteMarkedDialougue(false);
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
