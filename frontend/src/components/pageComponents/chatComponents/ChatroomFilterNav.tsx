import { SetStateAction } from "react";
import { ChatroomType, ChatroomSortBy, ChatroomMemberRole } from "../../../types/chatroomTypes";
import {
  chatroomSortByOptions,
  chatroomSortByTexts,
  chatroomTypeOptions,
  chatroomTypeTexts,
  memberRoleOptions,
  memberRoleTexts,
} from "../../../constants/chatOptions";
import DropdownSelect from "../../general/dropdownSelect/DropdownSelect";
import { sortOrderOptions, sortOrderTexts } from "../../../constants/genericOptions";
import { SortOrder } from "../../../types/types";
import NavContainer from "../../general/dropdownSelect/NavContainer";

type ChatroomFilterBarProps = {
  roomType: ChatroomType;
  searchString: string | undefined;
  memberRole: ChatroomMemberRole;
  sortOrder: SortOrder;
  sortBy: ChatroomSortBy;
  setSortBy: React.Dispatch<SetStateAction<ChatroomSortBy>>;
  setMemberRole: React.Dispatch<SetStateAction<ChatroomMemberRole>>;
  setSortOrder: React.Dispatch<SetStateAction<SortOrder>>;
  setRoomType: React.Dispatch<SetStateAction<ChatroomType>>;
  buttonsDisabled: boolean;
};
export default function ChatroomFilterBar({
  roomType,
  setRoomType,
  memberRole,
  setMemberRole,
  searchString,
  sortBy,
  sortOrder,
  setSortBy,
  setSortOrder,
  buttonsDisabled,
}: ChatroomFilterBarProps) {
  return (
    <>
      <NavContainer forDropdown>
        <nav className={`filter-nav ${(searchString && "double-container") || "quad-container"}`}>
          <div className="nav-section chat-type-options">
            <DropdownSelect
              selectedValue={roomType}
              setStateValue={setRoomType}
              title="type"
              optionsList={chatroomTypeOptions}
              optionTexts={chatroomTypeTexts}
              buttonsDisabled={buttonsDisabled}
            />
          </div>
          {!searchString && (
            <>
              <div className="nav-section sort-by-options">
                <DropdownSelect
                  title="sort"
                  selectedValue={sortBy}
                  setStateValue={setSortBy}
                  optionsList={chatroomSortByOptions}
                  optionTexts={chatroomSortByTexts}
                  buttonsDisabled={buttonsDisabled}
                />
              </div>
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
              {!searchString && (
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
              )}
            </>
          )}
        </nav>
      </NavContainer>
    </>
  );
}
