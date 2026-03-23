import { ChatroomListResponse, ChatroomListResponseSchema } from "../../../schemas/ChatSchemas";
import { useEffect, useState } from "react";
import { useInfiniteQuery, QueryFunction } from "@tanstack/react-query";
import useAxios from "../../../hooks/useAxios";
import { useOutletContext, useParams } from "react-router-dom";
import TanstackQueryLoadStateHandler from "../../../components/general/tanstackQueryLoadStateHandler/TanstackQueryLoadStateHandler";
import useDisableButtonsOnNullData from "../../../hooks/useDisableButtonsOnNullData";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import { ChatroomType, ChatroomSortBy } from "../../../types/chatroomTypes";
import { AdminChatroomList } from "../../../components/adminPageComponents/pagesLists/AdminChatroomList";
import { FromDate, SortOrder } from "../../../types/types";
import AdminChatroomFilterNav from "../../../components/adminPageComponents/navbars/chatroom/AdminChatroomNavbars";

export default function AdminChatroomListPage() {
  const [allChatroomsFetched, setAllChatroomsFetched] = useState<boolean>(false);

  const {
    chatRoomType,
    setChatRoomType,
    chatSortBy,
    chatMinMembers,
    chatSortOrder,
    chatFromDate,
    setChatSortBy,
    setChatSortOrder,
    setChatFromDate,
    setChatMinMembers,
  } = useOutletContext<any>();

  const axios = useAxios({ forAdmin: true });

  const { searchString } = useParams();

  const _ = useSetPageTitle((searchString && "matching chatrooms") || "joined chatrooms");

  const adminFetchChatrooms: QueryFunction<
    ChatroomListResponse,
    [ChatroomType, string | undefined, ChatroomSortBy, SortOrder, FromDate, number],
    number
  > = async ({ pageParam = 1 }) => {
    setAllChatroomsFetched(false);
    try {
      const res = await axios.get(
        `/admin/chat/all?room_type=${chatRoomType}&sort=${chatSortBy}&order=${chatSortOrder}&min_members=${chatMinMembers}&from_date=${chatFromDate}&page=${pageParam}`
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
    data: pagesData,
    isFetching,
    isFetchingNextPage,
    isFetchNextPageError,
    isError,
    refetch,
    error,
    fetchNextPage,
  } = useInfiniteQuery({
    queryKey: [chatRoomType, searchString, chatSortBy, chatSortOrder, chatFromDate, chatMinMembers],
    queryFn: adminFetchChatrooms,
    initialPageParam: 1,
    getNextPageParam: (_lastPage, pagesData) => pagesData.length + 1,
    gcTime: 1000 * 60 * 2,
    retry: 1,
  });

  const handleFetchMoreClick = () => {
    fetchNextPage();
  };
  useEffect(() => {
    setChatSortOrder("asc");
  }, [chatSortBy]);

  const filterButtonsDisabled = useDisableButtonsOnNullData({ pagesData: pagesData });

  return (
    <div className="page-container admin-chatroom-list-page">
      <AdminChatroomFilterNav
        roomType={chatRoomType}
        setRoomType={setChatRoomType}
        searchString={searchString}
        sortBy={chatSortBy}
        fromDate={chatFromDate}
        sortOrder={chatSortOrder}
        setSortBy={setChatSortBy}
        setSortOrder={setChatSortOrder}
        setFromDate={setChatFromDate}
        minMembers={chatMinMembers}
        setMinMembers={setChatMinMembers}
        buttonsDisabled={((error || filterButtonsDisabled) && true) || false}
      />
      <div className="section grow">
        {pagesData && pagesData.pages.length > 0 && (
          <AdminChatroomList
            pagesData={pagesData}
            isFetchNextPageError={isFetchNextPageError}
            isFetchingNextPage={isFetchingNextPage}
            handleFetchMoreClick={handleFetchMoreClick}
            allChatroomsFetched={allChatroomsFetched}
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
    </div>
  );
}
