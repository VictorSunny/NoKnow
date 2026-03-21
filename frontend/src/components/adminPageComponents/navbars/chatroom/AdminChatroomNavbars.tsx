import { SetStateAction, useRef } from "react";
import {
  chatroomSortByOptions,
  chatroomSortByTexts,
  chatroomTypeOptions,
  chatroomTypeTexts,
} from "../../../../constants/chatOptions";
import {
  FromDateOptions,
  fromDateTexts,
  sortOrderOptions,
  sortOrderTexts,
} from "../../../../constants/genericOptions";
import { APIModelName, FromDate, SortOrder } from "../../../../types/types";

import { ChatroomSortBy, ChatroomType } from "../../../../types/chatroomTypes";
import DropdownSelect from "../../../general/dropdownSelect/DropdownSelect";
import AdminSelectDeleteCreateNav from "../general/AdminSelectDeleteCreateNav";

import "./AdminChatroomNavbars.css";
import NavContainer from "../../../general/dropdownSelect/NavContainer";

type AdminChatroomFilterNavProps = {
  searchString: string | undefined;

  roomType: ChatroomType;
  setRoomType: React.Dispatch<SetStateAction<ChatroomType>>;

  sortOrder: SortOrder;
  sortBy: ChatroomSortBy;

  setSortBy: React.Dispatch<SetStateAction<ChatroomSortBy>>;
  setSortOrder: React.Dispatch<SetStateAction<SortOrder>>;

  fromDate: FromDate;
  setFromDate: React.Dispatch<SetStateAction<FromDate>>;

  minMembers: number;
  setMinMembers: React.Dispatch<SetStateAction<number>>;

  buttonsDisabled: boolean;
};
export default function AdminChatroomFilterNav({
  roomType,
  setRoomType,
  searchString,
  sortBy,
  sortOrder,
  fromDate,
  setSortBy,
  setSortOrder,
  setFromDate,
  setMinMembers,
  buttonsDisabled,
}: AdminChatroomFilterNavProps) {
  const modelName: APIModelName = "chatroom";

  const minMembersInputRef = useRef<HTMLInputElement>(null);

  const handleSetMinMembersClick = () => {
    if (minMembersInputRef.current) {
      if (!minMembersInputRef.current.value) {
        setMinMembers(0);
        return;
      }
      try {
        const newMinMembersValue = Number(minMembersInputRef.current.value);
        if (newMinMembersValue >= 0) {
          setMinMembers(newMinMembersValue);
        } else {
          setMinMembers(0);
        }
      } catch (err) {
        setMinMembers(0);
      }
    }
  };

  return (
    <>
      <NavContainer forDropdown>
        <nav className="filter-nav">
          <div className="nav-section chat-type-options">
            <DropdownSelect
              title="type"
              selectedValue={roomType}
              setStateValue={setRoomType}
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
                  optionsList={chatroomSortByOptions}
                  optionTexts={chatroomSortByTexts}
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
              <div className="nav-section min-members">
                <span className="filter-title">set min members</span>
                <input
                  name="min_members"
                  id="min_members"
                  key="min_members"
                  type="number"
                  className="btn filter-btn"
                  defaultValue={0}
                  onClick={handleSetMinMembersClick}
                  ref={minMembersInputRef}
                />
                <button onClick={handleSetMinMembersClick} className="filter-btn">
                  set
                </button>
              </div>
            </>
          )}
        </nav>
      </NavContainer>
      <AdminSelectDeleteCreateNav modelName={modelName} />
    </>
  );
}
