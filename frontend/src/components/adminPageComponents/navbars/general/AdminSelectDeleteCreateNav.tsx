import React, { useState } from "react";
import MassSelectCheckboxesButton from "../../../general/selectAllButton/MassSelectCheckboxesButton";
import { APIModelName } from "../../../../types/types";
import AdminConfirmDeleteAllSelectedDialogue from "../../confirmationDialogues/AdminConfirmDeleteAllSelectedDialogue";

import "./AdminSelectDeleteCreateNav.css";
import { useNavigate } from "react-router-dom";

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
      <nav className={`select-delete-create-nav filter-nav ${(noCreate && "single") || "double"}`}>
        {!noCreate && (
          <div className="nav-section">
            <MassSelectCheckboxesButton
              selectAll={selectAll}
              setSelectAll={setSelectAll}
              modelName={modelName}
            />
            <button
              className="btn positive"
              onClick={() => {
                navigate(createEnpoint);
              }}
            >
              new
            </button>
          </div>
        )}
        <div className="nav-section">
          <button className="btn danger" type="button" onClick={handleDeleteMarkedClick}>
            delete
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
