import { useState } from "react";
import MassSelectCheckboxesButton from "../../../general/massSelectCheckboxesButton/MassSelectCheckboxesButton";
import { APIModelName } from "../../../../types/types";
import AdminConfirmDeleteAllSelectedDialogue from "../../confirmationDialogues/AdminConfirmDeleteAllSelectedDialogue";

import "./AdminSelectDeleteCreateNav.css";
import { useNavigate } from "react-router-dom";

import { ReactComponent as PlusIcon } from "../../../../assets/icons/plus-icon.svg";
import { ReactComponent as DeleteIcon } from "../../../../assets/icons/trash-bin-icon.svg";

type Props = {
  modelName: APIModelName;
  noCreate?: boolean;
};
export default function AdminSelectDeleteCreateNav({ modelName, noCreate }: Props) {
  const [showDeleteMarkedDialougue, setShowDeleteMarkedDialougue] = useState(false);
  const navigate = useNavigate();

  const createEnpoint =
    (modelName == "blacklistedEmail" && "/admin/manage/email-blacklist/create") ||
    (modelName == "user" && "/admin/manage/user/create") ||
    (modelName == "chatroom" && "/admin/manage/chatroom/create") ||
    "/admin";

  const [selectAll, setSelectAll] = useState(false);
  const handleDeleteMarkedClick = () => {
    setShowDeleteMarkedDialougue(true);
  };

  return (
    <>
      <nav className="select-delete-create-nav filter-nav double">
        <div className="nav-section">
          <>
            <MassSelectCheckboxesButton
              selectAll={selectAll}
              setSelectAll={setSelectAll}
              modelName={modelName}
            />
            {!noCreate && (
              <button
                className="btn positive"
                onClick={() => {
                  navigate(createEnpoint);
                }}
              >
                <div className="text-icon-container">
                  <PlusIcon className="icon" aria-label="plus icon" />
                  <span>new</span>
                </div>
              </button>
            )}
          </>
        </div>
        <div className="nav-section">
          <button className="btn danger" type="button" onClick={handleDeleteMarkedClick}>
            <div className="text-icon-container">
              <DeleteIcon className="icon" aria-label="trash bin icon" />
              <span>delete</span>
            </div>
          </button>
        </div>
      </nav>
      {showDeleteMarkedDialougue && (
        <AdminConfirmDeleteAllSelectedDialogue
          modelName={modelName}
          setShowDeleteMarkedDialougue={setShowDeleteMarkedDialougue}
        />
      )}
    </>
  );
}
