import { ChatroomListResponse, ChatroomListResponseSchema } from "../../../schemas/ChatSchemas";
import { useEffect, useState } from "react";
import { useInfiniteQuery, QueryFunction } from "@tanstack/react-query";
import useAxios from "../../../hooks/useAxios";
import { useParams } from "react-router-dom";
import TanstackQueryLoadStateHandler from "../../../components/general/tanstackQueryLoadStateHandler/TanstackQueryLoadStateHandler";
import useDisableButtonsOnNullData from "../../../hooks/useDisableButtonsOnNullData";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import ChatroomFilterBar from "../../../components/pageComponents/chatComponents/ChatroomFilterNav";
import { ChatroomType, ChatroomSortBy, ChatroomMemberRole } from "../../../types/chatroomTypes";
import { ChatroomPages } from "../../../components/pageComponents/chatComponents/ChatroomPages";
import { SortOrder } from "../../../types/types";

function AllChatrooms() {
  const [chatroomType, setRoomType] = useState<ChatroomType>("all");
  const [allChatroomsFetched, setAllChatroomsFetched] = useState<boolean>(false);

  const [sortBy, setSortBy] = useState<ChatroomSortBy>("activity");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [memberRole, setMemberRole] = useState<ChatroomMemberRole>("all");

  const axios = useAxios();

  const { searchString } = useParams();

  const _ = useSetPageTitle((searchString && "matching chatrooms") || "joined chatrooms");

  const fetchChatrooms: QueryFunction<
    ChatroomListResponse,
    [ChatroomType, ChatroomMemberRole, string | undefined, ChatroomSortBy, SortOrder],
    number
  > = async ({ pageParam = 1 }) => {
    setAllChatroomsFetched(false);
    try {
      const chatroomsFetchURLPrefix =
        (searchString && `/chat/search?search_query=${searchString}`) ||
        `/chat/private/room/all?role=${memberRole}&sort=${sortBy}&order=${sortOrder}`;
      const res = await axios.get(
        `${chatroomsFetchURLPrefix}&room_type=${chatroomType}&page=${pageParam}`
      );
      if (res.data.chatrooms && res.data.chatrooms.length < 1) {
        setAllChatroomsFetched(true);
      }
      const parsedChatroomListData = ChatroomListResponseSchema.parse(res.data);
      return parsedChatroomListData;
    } catch (err) {
      throw err;
    }
  };
  const {
    data: allPages,
    isFetching,
    isFetchingNextPage,
    isFetchNextPageError,
    isError,
    refetch,
    error,
    fetchNextPage,
  } = useInfiniteQuery({
    queryKey: [chatroomType, memberRole, searchString, sortBy, sortOrder],
    queryFn: fetchChatrooms,
    initialPageParam: 1,
    getNextPageParam: (_lastPage, allPages) => allPages.length + 1,
    gcTime: 1000 * 60 * 2,
    retry: 1,
  });

  const handleFetchMoreClick = () => {
    fetchNextPage();
  };
  useEffect(() => {
    if (sortBy == "name") {
      setSortOrder("asc");
    } else {
      setSortOrder("desc");
    }
  }, [sortBy]);

  const filterButtonsDisabled = useDisableButtonsOnNullData({ pagesData: allPages });

  return (
    <div className="page-container">
      <ChatroomFilterBar
        roomType={chatroomType}
        memberRole={memberRole}
        setRoomType={setRoomType}
        setMemberRole={setMemberRole}
        searchString={searchString}
        sortBy={sortBy}
        sortOrder={sortOrder}
        setSortBy={setSortBy}
        setSortOrder={setSortOrder}
        buttonsDisabled={filterButtonsDisabled}
      />
      {allPages && allPages.pages.length > 0 && (
        <div className="section grow">
          {searchString && searchString && (
            <p className="title">search results for "{decodeURI(searchString).slice(0, 12)}"</p>
          )}
          <ChatroomPages
            pagesData={allPages}
            isFetchNextPageError={isFetchNextPageError}
            isFetchingNextPage={isFetchingNextPage}
            handleFetchMoreClick={handleFetchMoreClick}
            allChatroomsFetched={allChatroomsFetched}
          />
        </div>
      )}

      <TanstackQueryLoadStateHandler
        isError={isError}
        isFetching={isFetching}
        isFetchingNextPage={isFetchingNextPage}
        refetch={refetch}
        error={error}
      />
    </div>
  );
}

export default AllChatrooms;
