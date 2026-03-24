import useSetPageTitle from "../../../hooks/useSetPageTitle";
import DeleteAccountForm from "../../../components/forms/DeleteAccountForm";
import ConfirmActionDialogue from "../../../components/general/confirmationModals/ConfirmActionDialogue";
import { useState } from "react";

export default function DeleteAccountWindow() {
  const [showConfirmDialogue, setShowConfirmDialogue] = useState(false);
  const _ = useSetPageTitle("delete account");

  const handleConfirmClick = () => {
    setShowConfirmDialogue(true);
  };
  return (
    <div className="window delete-account-window">
      <div className="window-section grow">
        <button className="btn danger" onClick={handleConfirmClick}>
          permanently deactivate account
        </button>
      </div>
      {showConfirmDialogue && (
        <ConfirmActionDialogue setModalDisplayState={setShowConfirmDialogue}>
          <DeleteAccountForm />
        </ConfirmActionDialogue>
      )}
    </div>
  );
}
