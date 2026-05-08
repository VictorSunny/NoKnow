import { UserListResponse } from "../../../../schemas/AuthSchema";
import { QueryFunction, useInfiniteQuery } from "@tanstack/react-query";
import React, { SetStateAction, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import useAxios from "../../../../hooks/useAxios";
import useDisableButtonsOnNullData from "../../../../hooks/useDisableButtonsOnNullData";
import TanstackQueryLoadStateHandler from "../../../../components/general/tanstackQueryLoadStateHandler/TanstackQueryLoadStateHandler";
import useSetPageTitle from "../../../../hooks/useSetPageTitle";
import { UUID } from "crypto";
import UserPages from "../../../../components/pageComponents/userComponents/userPages/UserPages";
import { UserSortBy } from "../../../../types/userTypes";
import UserFilterNav from "../../../../components/pageComponents/userComponents/userFilterNavbar/UserFilterNavbar";
import { SortOrder } from "../../../../types/types";
import NavContainer from "../../../../components/general/dropdownSelect/NavContainer";

import { ReactComponent as SearchIcon } from "../../../../assets/icons/search-icon.svg";
import { ReactComponent as UserGroupTwoIcon } from "../../../../assets/icons/users-group-two-icon.svg";
import { ReactComponent as UserGroupThreeIcon } from "../../../../assets/icons/users-group-three-icon.svg";

type ChatroomUserCategoryNav = "friends" | "members";
export default function ChatroomUserSearch() {
  const [allUsersFetched, setAllUsersFetched] = useState(false);
  const [userCategory, setUserCategoryNav] = useState<ChatroomUserCategoryNav>("members");
  const [sortBy, setSortBy] = useState<UserSortBy>("date");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

  const { q, chatroomUID } = useParams();
  const axios = useAxios();

  const _ = useSetPageTitle("chatroom user search");

  const fetchChatroomUsers: QueryFunction<
    UserListResponse,
    [string, ChatroomUserCategoryNav, UserSortBy, SortOrder],
    number
  > = async ({ pageParam = 1 }) => {
    setAllUsersFetched(false);
    try {
      const fetchURL =
        (userCategory == "members" &&
          `/chat/private/room/members/${chatroomUID}?search_query=${q}&page=${pageParam}&sort=${sortBy}&order=${sortOrder}&role=all`) ||
        `/user/friends/all?search_query=${q}&page=${pageParam}&sort=${sortBy}&order=${sortOrder}`;
      const res = await axios.get(fetchURL);
      if (res.data.users && res.data.users.length < 1) {
        setAllUsersFetched(true);
      }
      return res.data;
    } catch (err) {
      throw err;
    }
  };

  const {
    data: pagesData,
    isFetching,
    isFetchingNextPage,
    isFetchNextPageError,
    isError,
    refetch,
    error,
    fetchNextPage,
  } = useInfiniteQuery({
    queryKey: ["searchChatroomUsers", userCategory, sortBy, sortOrder],
    queryFn: fetchChatroomUsers,
    initialPageParam: 1,
    getNextPageParam: (_lastPage, pagesData) => pagesData.length + 1,
  });

  const handleFetchMoreClick = () => {
    fetchNextPage();
  };
  useEffect(() => {
    if (sortBy == "date") {
      setSortOrder("desc");
    }
    if (sortBy == "username") {
      setSortOrder("asc");
    }
  }, [sortBy]);
  useEffect(() => {
    setSortBy("date");
  }, [userCategory]);

  const filterButtonsDisabled = useDisableButtonsOnNullData({ pagesData: pagesData });

  return (
    <div className="window chat-member-search-window">
      <UserCategoryNav
        userCategory={userCategory}
        setUserCategoryNav={setUserCategoryNav}
        filterButtonsDisabled={((error || filterButtonsDisabled) && true) || false}
      />
      <UserFilterNav
        setSortOrder={setSortOrder}
        setSortBy={setSortBy}
        sortOrder={sortOrder}
        sortBy={sortBy}
        buttonsDisabled={filterButtonsDisabled}
      />
      <>
        <div className="window-section title-container">
          <div className="text-icon-container">
            <SearchIcon className="icon" aria-label="search icon" />
            <p className="title">
              search results for{" "}
              {(userCategory == "friends" && "friends to add") || "chatroom members"}
            </p>
          </div>
        </div>
        <div className="window-section grow">
          {pagesData && pagesData.pages && (
            <UserPages
              pagesData={pagesData}
              toPage={"chatroomPreview"}
              chatroomUID={chatroomUID as UUID}
              isFetchNextPageError={isFetchNextPageError}
              isFetchingNextPage={isFetchingNextPage}
              handleFetchMoreClick={handleFetchMoreClick}
              allUsersFetched={allUsersFetched}
            />
          )}
          <TanstackQueryLoadStateHandler
            data={pagesData}
            isError={isError}
            isFetching={isFetching}
            isFetchingNextPage={isFetchingNextPage}
            refetch={refetch}
            error={error}
          />
        </div>
      </>
    </div>
  );
}

type UserCategoryNavProps = {
  userCategory: ChatroomUserCategoryNav;
  setUserCategoryNav: React.Dispatch<SetStateAction<ChatroomUserCategoryNav>>;
  filterButtonsDisabled: boolean;
};
function UserCategoryNav({
  userCategory,
  setUserCategoryNav,
  filterButtonsDisabled,
}: UserCategoryNavProps) {
  const userCateogryOptions: ChatroomUserCategoryNav[] = ["members", "friends"];

  const handleCategoryOptionClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    const buttonValue = e.currentTarget.value as ChatroomUserCategoryNav;
    setUserCategoryNav(buttonValue);
  };

  return (
    <NavContainer>
      <nav className="window-nav">
        <button
          value="members"
          onClick={handleCategoryOptionClick}
          className={`nav-link ${(userCategory == "members" && "active") || ""}`}
          disabled={filterButtonsDisabled}
        >
          <div className="text-icon-container">
            <UserGroupThreeIcon className="icon" aria-label="user group three icon" />
            <span>members</span>
          </div>
        </button>
        <button
          value="friends"
          onClick={handleCategoryOptionClick}
          className={`nav-link ${(userCategory == "friends" && "active") || ""}`}
          disabled={filterButtonsDisabled}
        >
          <div className="text-icon-container">
            <UserGroupTwoIcon className="icon" aria-label="user group two icon" />
            <span>friends</span>
          </div>
        </button>
      </nav>
    </NavContainer>
  );
}
