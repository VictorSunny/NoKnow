import { SetStateAction, useState } from "react";
import { UserRoleChoices, AdminUserSortBy } from "../../../../types/userTypes";
import DropdownSelect from "../../../general/dropdownSelect/DropdownSelect";
import {
  adminUserSortByOptions,
  adminUserSortByTexts,
  userRoleOptions,
  userRoleTexts,
} from "../../../../constants/userOptions";
import {
  FromDateOptions,
  fromDateTexts,
  optionalBooleanOptions,
  optionalBooleanTexts,
  sortOrderOptions,
  sortOrderTexts,
} from "../../../../constants/genericOptions";
import AdminConfirmDeleteAllSelectedDialogue from "../../confirmationDialogues/AdminConfirmDeleteAllSelectedDialogue";
import { APIModelName, FromDate, OptionalBooleanString, SortOrder } from "../../../../types/types";
import { UserComplete } from "../../../../schemas/AuthSchema";
import AdminConfirmModelDeleteDialogue from "../../confirmationDialogues/AdminConfirmModelDeleteDialogue";
import AdminConfirmAddToSuperuserDialogue from "../../confirmationDialogues/AdminConfirmAddToSuperuserDialogue";
import AdminUserUtilsNav from "./AdminUserUtilsNav";
import NavContainer from "../../../general/dropdownSelect/NavContainer";

type Props = {
  fromDate: FromDate;
  setFromDate: React.Dispatch<SetStateAction<FromDate>>;
  sortBy: AdminUserSortBy;
  setSortBy: React.Dispatch<SetStateAction<AdminUserSortBy>>;
  sortOrder: SortOrder;
  setSortOrder: React.Dispatch<SetStateAction<SortOrder>>;
  userRole: UserRoleChoices;
  setUserRoleChoices: React.Dispatch<SetStateAction<UserRoleChoices>>;
  googleSignup: OptionalBooleanString;
  setGoogleSignup: React.Dispatch<SetStateAction<OptionalBooleanString>>;
  userActive: OptionalBooleanString;
  setUserActive: React.Dispatch<SetStateAction<OptionalBooleanString>>;

  buttonsDisabled: boolean;
};

/**
 * A function that can be used to update state values for user sorting and ordering
 */
export default function AdminUserFilterNav({
  sortBy,
  setSortBy,
  sortOrder,
  setSortOrder,
  googleSignup,
  setGoogleSignup,
  userActive,
  setUserActive,
  userRole,
  setUserRoleChoices,
  fromDate,
  setFromDate,
  buttonsDisabled,
}: Props) {
  const modelName: APIModelName = "user";

  const [showDeleteMarkedDialougue, setShowDeleteMarkedDialougue] = useState(false);

  return (
    <>
      <NavContainer forDropdown>
        <nav className="filter-nav">
          <div className="nav-section">
            <DropdownSelect
              title="sort"
              selectedValue={sortBy}
              setStateValue={setSortBy}
              optionsList={adminUserSortByOptions}
              optionTexts={adminUserSortByTexts}
              buttonsDisabled={buttonsDisabled}
            />
          </div>
          <div className="nav-section">
            <DropdownSelect
              title="order"
              selectedValue={sortOrder}
              setStateValue={setSortOrder}
              optionsList={sortOrderOptions}
              optionTexts={sortOrderTexts}
              buttonsDisabled={buttonsDisabled}
            />
          </div>
          <div className="nav-section">
            <DropdownSelect
              title="date"
              selectedValue={fromDate}
              setStateValue={setFromDate}
              optionsList={FromDateOptions}
              optionTexts={fromDateTexts}
              buttonsDisabled={buttonsDisabled}
            />
          </div>
          <div className="nav-section">
            <DropdownSelect
              title="role"
              selectedValue={userRole}
              setStateValue={setUserRoleChoices}
              optionsList={userRoleOptions}
              optionTexts={userRoleTexts}
              buttonsDisabled={buttonsDisabled}
            />
          </div>
          <div className="nav-section">
            <DropdownSelect
              title="google signed-up"
              selectedValue={googleSignup}
              setStateValue={setGoogleSignup}
              optionsList={optionalBooleanOptions}
              optionTexts={optionalBooleanTexts}
              buttonsDisabled={buttonsDisabled}
            />
          </div>
          <div className="nav-section">
            <DropdownSelect
              title="active"
              selectedValue={userActive}
              setStateValue={setUserActive}
              optionsList={optionalBooleanOptions}
              optionTexts={optionalBooleanTexts}
              buttonsDisabled={buttonsDisabled}
            />
          </div>
        </nav>
      </NavContainer>
      <AdminUserUtilsNav />
      {showDeleteMarkedDialougue && (
        <AdminConfirmDeleteAllSelectedDialogue
          modelName={modelName}
          setShowDeleteMarkedDialougue={setShowDeleteMarkedDialougue}
        />
      )}
    </>
  );
}

type AdminUserUtilityNavSectionProps = {
  userData: UserComplete;
  loggedInUser: UserComplete;
};
export function AdminUserUtilityNavSection({
  userData,
  loggedInUser,
}: AdminUserUtilityNavSectionProps) {
  const [showDeleteDialogue, setShowDeleteDialogue] = useState(false);
  const [showSuperuserAddDialogue, setShowSuperuserAddDialogue] = useState(false);

  return (
    <>
      <div className="nav-section">
        {userData.role != "superuser" && (
          <>
            <button
              onClick={() => {
                setShowDeleteDialogue(true);
              }}
              className="btn danger"
              aria-label="delete user"
            >
              delete
            </button>
            {loggedInUser?.role == "superuser" && (
              <button
                onClick={() => {
                  setShowSuperuserAddDialogue(true);
                }}
                aria-label="add user to superusers"
              >
                make superuser
              </button>
            )}
          </>
        )}
      </div>

      {showDeleteDialogue && (
        <AdminConfirmModelDeleteDialogue
          id={userData.uid}
          setShowDeleteDialogue={setShowDeleteDialogue}
          modelName="user"
        />
      )}
      {showSuperuserAddDialogue && (
        <AdminConfirmAddToSuperuserDialogue
          userData={userData}
          setShowConfirmDialogue={setShowSuperuserAddDialogue}
        />
      )}
    </>
  );
}
