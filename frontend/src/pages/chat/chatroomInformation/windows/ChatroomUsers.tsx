import useAxios from "../../../../hooks/useAxios";
import { UserListResponse } from "../../../../schemas/AuthSchema";
import { QueryFunction, useInfiniteQuery } from "@tanstack/react-query";
import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TanstackQueryLoadStateHandler from "../../../../components/general/tanstackQueryLoadStateHandler/TanstackQueryLoadStateHandler";
import useDisableButtonsOnNullData from "../../../../hooks/useDisableButtonsOnNullData";
import { UUID } from "crypto";
import useSetPageTitle from "../../../../hooks/useSetPageTitle";
import { ChatroomMemberRole } from "../../../../types/chatroomTypes";
import ChatroomMemberFilterNavbar from "../../../../components/pageComponents/chatComponents/ChatroomMemberFilterNav";
import UserPages from "../../../../components/pageComponents/userComponents/userPages/UserPages";
import { UserSortBy } from "../../../../types/userTypes";
import { SortOrder } from "../../../../types/types";

export default function ChatroomUsers() {
  const axios = useAxios();
  const { chatroomUID } = useParams();
  const [allUsersFetched, setAllUsersFetched] = useState(false);

  const [sortBy, setSortBy] = useState<UserSortBy>("username");
  const [sortOrder, setSortOrder] = useState<SortOrder>("asc");
  const [memberRole, setMemberRole] = useState<ChatroomMemberRole>("all");

  const _ = useSetPageTitle("chatroom users");

  const navigate = useNavigate();

  useEffect(() => {
    if (sortBy == "date") {
      setSortOrder("desc");
    }
    if (sortBy == "username") {
      setSortOrder("asc");
    }
  }, [sortBy]);

  const fetchFriends: QueryFunction<
    UserListResponse,
    [string, SortOrder, UserSortBy, ChatroomMemberRole],
    number
  > = async ({ pageParam = 1 }) => {
    setAllUsersFetched(false);
    try {
      const res = await axios.get(
        `/chat/private/room/members/${chatroomUID}?sort=${sortBy}&role=${memberRole}&order=${sortOrder}&page=${pageParam}`
      );
      const ResData = res.data;
      if (ResData.users && ResData.users.length < 1) {
        setAllUsersFetched(true);
      }
      return ResData;
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
    queryKey: ["chatroomUsers", sortOrder, sortBy, memberRole],
    queryFn: fetchFriends,
    initialPageParam: 1,
    getNextPageParam: (_lastPage, pagesData) => pagesData.length + 1,
  });

  const handleFetchMoreClick = () => {
    fetchNextPage();
  };
  const handleMemberSearchSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const searchQuery = String(formData.get("query"));
    navigate(`/chat/meta/chatroom/${chatroomUID}/users/search/${encodeURI(searchQuery)}`);
  };
  const filterButtonsDisabled = useDisableButtonsOnNullData({ pagesData: pagesData });
  
  useEffect(() => {
    if (sortBy == "date") {
      setSortOrder("desc");
    }
    if (sortBy == "username") {
      setSortOrder("asc");
    }
  }, [sortBy]);

  return (
    <div className="window chat-members-window">
      <>
        <div className="window-section form-container">
          <form
            method="POST"
            className="util-form"
            name="search-user-form"
            onSubmit={handleMemberSearchSubmit}
          >
            <input
              name="query"
              id="query"
              key="query"
              type="text"
              placeholder="search with username"
              required
            />
            <button
              type="submit"
              name="button"
              aria-label="submit search user for chatroom form"
              className="btn submit-btn"
              disabled={isFetching || isFetchingNextPage}
            >
              search
            </button>
          </form>
        </div>
        <ChatroomMemberFilterNavbar
          memberRole={memberRole}
          setSortOrder={setSortOrder}
          setMemberRole={setMemberRole}
          sortOrder={sortOrder}
          buttonsDisabled={filterButtonsDisabled}
        />
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
