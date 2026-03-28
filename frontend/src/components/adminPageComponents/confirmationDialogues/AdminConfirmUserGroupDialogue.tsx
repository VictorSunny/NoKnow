import { useState } from "react";
import useHandleError from "../../../hooks/useHandleError";
import useAxios from "../../../hooks/useAxios";
import { getSelectedCheckboxes } from "../../../utilities/formCheckboxHandlers";
import ConfirmActionDialogue from "../../general/modals/ConfirmActionDialogue";
import { SetBoolState } from "../../../types/types";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../general/modals/APIResponsePopup";
import { MessageResponseSchema } from "../../../schemas/GenericSchemas";
import { AdminUserMoveGroups } from "../../../types/userTypes";

type Props = {
  groupName: AdminUserMoveGroups;
  setShowMoveMarkedDialougue: SetBoolState;
};
export default function AdminConfirmUserGroupDialogue({
  groupName,
  setShowMoveMarkedDialougue,
}: Props) {
  const axios = useAxios({ forAdmin: true });

  const [isFetching, setIsFetching] = useState<boolean>();
  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const selectedIDs = getSelectedCheckboxes("user");

  if (selectedIDs.length < 1) {
    setShowMoveMarkedDialougue(false);
    return;
  }

  const handleMoveUsersClick = () => {
    setErrorMessage(undefined);
    axios
      .patch(`/admin/user/groups/${groupName}/add?id=${selectedIDs.value}`)
      .then((res) => {
        const parsedRes = MessageResponseSchema.parse(res.data);
        setSuccessMessage(parsedRes.message);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false);
      });
  };
  return (
    <>
      <ConfirmActionDialogue setModalDisplayState={setShowMoveMarkedDialougue}>
        <p className="title">
          Are you sure you want to move {selectedIDs.length} users to {groupName} group?
        </p>
        <button
          onClick={handleMoveUsersClick}
          className={(isFetching && "load") || ""}
          disabled={isFetching}
        >
          confirm
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
              setShowMoveMarkedDialougue(false);
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
