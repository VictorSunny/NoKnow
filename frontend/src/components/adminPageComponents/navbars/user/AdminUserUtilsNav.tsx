import { useState } from "react";
import MassSelectCheckboxesButton from "../../../general/selectAllButton/MassSelectCheckboxesButton";
import AdminConfirmDeleteAllSelectedDialogue from "../../confirmationDialogues/AdminConfirmDeleteAllSelectedDialogue";

import { useNavigate } from "react-router-dom";
import { getSelectedCheckboxes } from "../../../../utilities/formCheckboxHandlers";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../../general/popups/messagePopups/APIResponsePopup";
import AdminConfirmUserGroupDialogue from "../../confirmationDialogues/AdminConfirmUserGroupDialogue";
import { AdminUserMoveGroups } from "../../../../types/userTypes";
import AdminConfirmUserRestrictActionDialogue from "../../confirmationDialogues/AdminConfirmUserRestrictActionDialogue";
import NavContainer from "../../../general/dropdownSelect/NavContainer";

type Props = {
  noCreate?: boolean;
};
export default function AdminUserUtilsNav({ noCreate }: Props) {
  const modelName = "user";

  const [errorMessage, setErrorMessage] = useState<string>();
  const [successMessage, setSuccessMessage] = useState<string>();

  const navigate = useNavigate();
  const [showDeleteMarkedDialougue, setShowDeleteMarkedDialougue] = useState(false);
  const [showMoveMarkedDialougue, setShowMoveMarkedDialougue] = useState(false);
  const [showRestrictMarkedDialogue, setShowRestrictMarkedDialogue] = useState(false);

  const [selectAll, setSelectAll] = useState(false);
  const [groupName, setGroupName] = useState<AdminUserMoveGroups>();
  const [restrictUsers, setRestrictUsers] = useState<boolean>(false);

  const selectedIDs = getSelectedCheckboxes(modelName);

  const addToUserGroupClick = () => {
    setGroupName("user");
    setShowMoveMarkedDialougue(true);
  };

  const addToAdminGroupClick = () => {
    setGroupName("admin");
    setShowMoveMarkedDialougue(true);
  };

  const restrictUsersClick = () => {
    setRestrictUsers(true);
    setShowRestrictMarkedDialogue(true);
  };
  const unrestrictUsersClick = () => {
    setRestrictUsers(false);
    setShowRestrictMarkedDialogue(true);
  };

  return (
    <>
      <NavContainer>
        <nav
          className={`select-delete-create-nav filter-nav ${(noCreate && "single") || "double"}`}
        >
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
                  navigate("/admin/manage/user/create");
                }}
              >
                new
              </button>
              <button className="btn" onClick={addToUserGroupClick}>
                to users
              </button>
              <button className="btn" onClick={addToAdminGroupClick}>
                to admins
              </button>
            </div>
          )}
          <div className="nav-section">
            <button className="btn" onClick={restrictUsersClick}>
              restrict
            </button>
            <button className="btn" onClick={unrestrictUsersClick}>
              unrestrict
            </button>
            <button
              className="btn danger"
              type="button"
              onClick={() => {
                selectedIDs.length > 0 && setShowDeleteMarkedDialougue(true);
              }}
            >
              delete
            </button>
          </div>
        </nav>
      </NavContainer>
      {showDeleteMarkedDialougue && (
        <AdminConfirmDeleteAllSelectedDialogue
          modelName={modelName}
          setShowDeleteMarkedDialougue={setShowDeleteMarkedDialougue}
        />
      )}
      {showMoveMarkedDialougue && groupName && (
        <AdminConfirmUserGroupDialogue
          groupName={groupName}
          setShowMoveMarkedDialougue={setShowMoveMarkedDialougue}
        />
      )}
      {showRestrictMarkedDialogue && (
        <AdminConfirmUserRestrictActionDialogue
          restrictUsers={restrictUsers}
          setShowDialogue={setShowRestrictMarkedDialogue}
        />
      )}
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
              navigate("/admin/manage/email-blacklist");
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
