import { UUID } from "crypto";
import { useState } from "react";
import AdminConfirmModelDeleteDialogue from "../../confirmationDialogues/AdminConfirmModelDeleteDialogue";
import { APIModelName } from "../../../../types/types";

type Props = {
  id: string | UUID | number;
  modelName: APIModelName;
};
export function AdminDeleteUtilityNav({ id, modelName }: Props) {
  const [showDeleteDialogue, setShowDeleteDialogue] = useState(false);
  return (
    <>
      <nav className="admin-util-nav">
        <button
          onClick={() => {
            setShowDeleteDialogue(true);
          }}
          className="btn danger"
          aria-label="delete user"
        >
          delete
        </button>
      </nav>
      {showDeleteDialogue && (
        <AdminConfirmModelDeleteDialogue
          modelName={modelName}
          id={id}
          setShowDeleteDialogue={setShowDeleteDialogue}
        />
      )}
    </>
  );
}
