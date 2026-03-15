import { SetStateAction } from "react";
import { ChatroomMemberRole } from "../../../types/chatroomTypes";
import DropdownSelect from "../../general/dropdownSelect/DropdownSelect";
import { memberRoleOptions, memberRoleTexts } from "../../../constants/chatOptions";
import { UserSortBy } from "../../../types/userTypes";
import { sortOrderOptions, sortOrderTexts } from "../../../constants/genericOptions";
import { SortOrder } from "../../../types/types";
import NavContainer from "../../general/dropdownSelect/NavContainer";

type ChatroomMemberFilterNavProps = {
  sortBy: UserSortBy;
  sortOrder: SortOrder;
  memberRole: ChatroomMemberRole;
  setSortBy: React.Dispatch<SetStateAction<UserSortBy>>;
  setSortOrder: React.Dispatch<SetStateAction<SortOrder>>;
  setMemberRole: React.Dispatch<SetStateAction<ChatroomMemberRole>>;
  buttonsDisabled: boolean;
  forChatroomUsers?: boolean;
};

/**
 * A function that can be used to update state values for user sorting and ordering
 */
export default function ChatroomMemberFilterNav({
  sortBy,
  sortOrder,
  memberRole,
  setSortBy,
  setSortOrder,
  setMemberRole,
  buttonsDisabled,
}: ChatroomMemberFilterNavProps) {
  const sortByOptions: UserSortBy[] = ["username", "date"];

  const handleSortTypeButtonClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    const selectedSortTypeValue = e.currentTarget.value as UserSortBy;
    setSortBy(selectedSortTypeValue);
  };

  return (
    <NavContainer forDropdown>
      <nav className="filter-nav">
        <div className="nav-section sort-order-options">
          <DropdownSelect
            title="order"
            selectedValue={sortOrder}
            setStateValue={setSortOrder}
            optionsList={sortOrderOptions}
            optionTexts={sortOrderTexts}
            buttonsDisabled={buttonsDisabled}
          />
        </div>
        <div className="nav-section member-role-options">
          <DropdownSelect
            title="role"
            selectedValue={memberRole}
            setStateValue={setMemberRole}
            optionsList={memberRoleOptions}
            optionTexts={memberRoleTexts}
            buttonsDisabled={buttonsDisabled}
          />
        </div>
      </nav>
    </NavContainer>
  );
}
