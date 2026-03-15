import { SetStateAction, useEffect, useRef, useState } from "react";
import DropdownSelect from "../../../general/dropdownSelect/DropdownSelect";
import {
  FromDateOptions,
  fromDateTexts,
  sortByDateOrIDOptions,
  sortByDateOrIDTexts,
  sortOrderOptions,
  sortOrderTexts,
  validityOptions,
  validityTexts,
} from "../../../../constants/genericOptions";
import AdminConfirmDeleteAllSelectedDialogue from "../../confirmationDialogues/AdminConfirmDeleteAllSelectedDialogue";
import MassSelectCheckboxesButton from "../../../general/selectAllButton/MassSelectCheckboxesButton";
import {
  APIModelName,
  FromDate,
  SortByDateOrID,
  SortOrder,
  Validity,
} from "../../../../types/types";
import { Link } from "react-router-dom";
import AdminSelectDeleteCreateNav from "../general/AdminSelectDeleteCreateNav";
import NavContainer from "../../../general/dropdownSelect/NavContainer";

type AdminBlacklistedTokenFilterNavProps = {
  searchString: string | undefined;

  validity: Validity;
  setValidity: React.Dispatch<SetStateAction<Validity>>;

  sortOrder: SortOrder;
  sortBy: SortByDateOrID;

  setSortBy: React.Dispatch<SetStateAction<SortByDateOrID>>;
  setSortOrder: React.Dispatch<SetStateAction<SortOrder>>;

  fromDate: FromDate;
  setFromDate: React.Dispatch<SetStateAction<FromDate>>;

  buttonsDisabled: boolean;
};
export default function AdminBlacklistedTokenFilterNav({
  searchString,
  sortBy,
  sortOrder,
  fromDate,
  validity,
  setSortBy,
  setSortOrder,
  setFromDate,
  setValidity,
  buttonsDisabled,
}: AdminBlacklistedTokenFilterNavProps) {
  const modelName: APIModelName = "blacklistedToken";

  const [showDeleteMarkedDialougue, setShowDeleteMarkedDialougue] = useState(false);

  return (
    <>
      <NavContainer forDropdown>
        <nav className="filter-nav">
          {!searchString && (
            <>
              <div className="nav-section sort-by-options">
                <DropdownSelect
                  title="sort"
                  selectedValue={sortBy}
                  optionsList={sortByDateOrIDOptions}
                  optionTexts={sortByDateOrIDTexts}
                  setStateValue={setSortBy}
                  buttonsDisabled={buttonsDisabled}
                />
              </div>
              <div className="nav-section sort-order-options">
                <DropdownSelect
                  title="order"
                  selectedValue={sortOrder}
                  optionsList={sortOrderOptions}
                  optionTexts={sortOrderTexts}
                  setStateValue={setSortOrder}
                  buttonsDisabled={buttonsDisabled}
                />
              </div>
              <div className="nav-section from-date-options">
                <DropdownSelect
                  title="date"
                  selectedValue={fromDate}
                  optionsList={FromDateOptions}
                  optionTexts={fromDateTexts}
                  setStateValue={setFromDate}
                  buttonsDisabled={buttonsDisabled}
                />
              </div>
              <div className="nav-section from-date-options">
                <DropdownSelect
                  title="validity"
                  selectedValue={validity}
                  optionsList={validityOptions}
                  optionTexts={validityTexts}
                  setStateValue={setValidity}
                  buttonsDisabled={buttonsDisabled}
                />
              </div>
            </>
          )}
        </nav>
      </NavContainer>
      <AdminSelectDeleteCreateNav modelName={modelName} noCreate />
      {showDeleteMarkedDialougue && (
        <AdminConfirmDeleteAllSelectedDialogue
          modelName={modelName}
          setShowDeleteMarkedDialougue={setShowDeleteMarkedDialougue}
        />
      )}
    </>
  );
}
