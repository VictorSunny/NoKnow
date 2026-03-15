import { SetStateAction } from "react";
import { UserSortBy } from "../../../../types/userTypes";
import DropdownSelect from "../../../general/dropdownSelect/DropdownSelect";
import { userSortByOptions, userSortByTexts } from "../../../../constants/userOptions";
import { sortOrderOptions, sortOrderTexts } from "../../../../constants/genericOptions";
import { SortOrder } from "../../../../types/types";
import NavContainer from "../../../general/dropdownSelect/NavContainer";

type UserFilterNavabarProps = {
  sortBy: UserSortBy;
  sortOrder: SortOrder;
  setSortBy: React.Dispatch<SetStateAction<UserSortBy>>;
  setSortOrder: React.Dispatch<SetStateAction<SortOrder>>;
  buttonsDisabled: boolean;
};

/**
 * A function that can be used to update state values for user sorting and ordering
 */
export default function UserFilterNav({
  sortBy,
  sortOrder,
  setSortBy,
  setSortOrder,
  buttonsDisabled,
}: UserFilterNavabarProps) {
  return (
    <NavContainer forDropdown>
      <nav className="filter-nav">
        <div className="nav-section">
          <DropdownSelect
            title="sort"
            selectedValue={sortBy}
            setStateValue={setSortBy}
            optionsList={userSortByOptions}
            optionTexts={userSortByTexts}
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
      </nav>
    </NavContainer>
  );
}
