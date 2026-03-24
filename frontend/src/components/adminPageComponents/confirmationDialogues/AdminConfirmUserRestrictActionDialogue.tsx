import { useState } from "react";
import useHandleError from "../../../hooks/useHandleError";
import useAxios from "../../../hooks/useAxios";
import { getSelectedCheckboxes } from "../../../utilities/formCheckboxHandlers";
import ConfirmActionDialogue from "../../general/confirmationModals/ConfirmActionDialogue";
import { SetBoolState } from "../../../types/types";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../general/popups/messagePopups/APIResponsePopup";
import { MessageResponseSchema } from "../../../schemas/GenericSchemas";

type Props = {
  restrictUsers: boolean;
  setShowDialogue: SetBoolState;
};
export default function AdminConfirmUserRestrictActionDialogue({
  restrictUsers,
  setShowDialogue,
}: Props) {
  const axios = useAxios({ forAdmin: true });

  const [isFetching, setIsFetching] = useState<boolean>();
  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const APIURLPath = (restrictUsers && "restrict") || "unrestrict";

  const selectedIDs = getSelectedCheckboxes("user");

  if (selectedIDs.length < 1) {
    setShowDialogue(false);
    return;
  }

  const handleClick = () => {
    setErrorMessage(undefined);
    axios
      .patch(`/admin/user/all/${APIURLPath}?id=${selectedIDs.value}`)
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
      <ConfirmActionDialogue setModalDisplayState={setShowDialogue}>
        <p className="title">
          Are you sure you want to {APIURLPath} {selectedIDs.length} users?
        </p>
        <button
          onClick={handleClick}
          disabled={isFetching}
          className={(isFetching && "load") || ""}
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
              setShowDialogue(false);
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
