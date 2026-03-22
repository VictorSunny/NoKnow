import useAxios from "../../../hooks/useAxios";
import { UserListResponse, UserListResponseSchema } from "../../../schemas/AuthSchema";
import { QueryFunction, useInfiniteQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";
import TanstackQueryLoadStateHandler from "../../../components/general/tanstackQueryLoadStateHandler/TanstackQueryLoadStateHandler";
import useSetPageTitle from "../../../hooks/useSetPageTitle";

import "./AllUserChats.css";
import UserPages from "../../../components/pageComponents/userComponents/userPages/UserPages";

function AllUserChats() {
  const { searchString } = useParams();
  const axios = useAxios();
  const [allUsersFetched, setAllUsersFetched] = useState(false);

  const _ = useSetPageTitle((searchString && "matching users") || "friend chats");

  const fetchUsers: QueryFunction<UserListResponse, [string, string | undefined], number> = async ({
    pageParam = 1,
  }) => {
    setAllUsersFetched(false);
    try {
      const fetchURL =
        (searchString && `/user/search?search_query=${searchString}&page=${pageParam}`) ||
        `/chat/private/room/friends/all?page=${pageParam}`;
      const res = await axios.get(fetchURL);
      const parsedUserList = UserListResponseSchema.parse(res.data);
      if (parsedUserList.users && parsedUserList.users.length < 1) {
        setAllUsersFetched(true);
      }
      return parsedUserList;
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
    queryKey: ["users", searchString],
    queryFn: fetchUsers,
    initialPageParam: 1,
    getNextPageParam: (_lastPage, allPages) => allPages.length + 1,
  });

  const handleFetchMoreClick = () => {
    return fetchNextPage();
  };
  return (
    <div className="page-container all-user-chats-page">
      <div className="section grow">
        {searchString && (
          <p className="title">search results for {decodeURI(searchString).slice(0, 12)}</p>
        )}
        {pagesData && pagesData.pages && (
          <UserPages
            pagesData={pagesData}
            toPage={"chat"}
            isFetchNextPageError={isFetchNextPageError}
            isFetchingNextPage={isFetchingNextPage}
            handleFetchMoreClick={handleFetchMoreClick}
            allUsersFetched={allUsersFetched}
            showOnlineStatus
            showLastSeen
          />
        )}
        <TanstackQueryLoadStateHandler
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

export default AllUserChats;
