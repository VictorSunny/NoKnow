import { SetStateAction, useRef, useState } from "react";
import DropdownSelect from "../../../general/dropdownSelect/DropdownSelect";
import {
  FromDateOptions,
  fromDateTexts,
  sortByDateOrIDOptions,
  sortByDateOrIDTexts,
  sortOrderOptions,
  sortOrderTexts,
} from "../../../../constants/genericOptions";
import AdminConfirmDeleteAllSelectedDialogue from "../../confirmationDialogues/AdminConfirmDeleteAllSelectedDialogue";
import { APIModelName, FromDate, SortByDateOrID, SortOrder } from "../../../../types/types";
import AdminSelectDeleteCreateNav from "../general/AdminSelectDeleteCreateNav";
import NavContainer from "../../../general/dropdownSelect/NavContainer";

type AdminBlacklistedEmailFilterNavProps = {
  searchString: string | undefined;

  sortOrder: SortOrder;
  sortBy: SortByDateOrID;

  setSortBy: React.Dispatch<SetStateAction<SortByDateOrID>>;
  setSortOrder: React.Dispatch<SetStateAction<SortOrder>>;

  fromDate: FromDate;
  setFromDate: React.Dispatch<SetStateAction<FromDate>>;

  buttonsDisabled: boolean;
};
export default function AdminBlacklistedEmailFilterNav({
  searchString,
  sortBy,
  sortOrder,
  fromDate,
  setSortBy,
  setSortOrder,
  setFromDate,
  buttonsDisabled,
}: AdminBlacklistedEmailFilterNavProps) {
  const modelName: APIModelName = "blacklistedEmail";

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
            </>
          )}
        </nav>
      </NavContainer>
      <AdminSelectDeleteCreateNav modelName={modelName} />
      {showDeleteMarkedDialougue && (
        <AdminConfirmDeleteAllSelectedDialogue
          modelName={modelName}
          setShowDeleteMarkedDialougue={setShowDeleteMarkedDialougue}
        />
      )}
    </>
  );
}
