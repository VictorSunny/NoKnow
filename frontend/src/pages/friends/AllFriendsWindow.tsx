import TanstackQueryLoadStateHandler from "../../components/general/tanstackQueryLoadStateHandler/TanstackQueryLoadStateHandler";
import useAxios from "../../hooks/useAxios";
import { UserListResponse } from "../../schemas/AuthSchema";
import { QueryFunction, useInfiniteQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import useDisableButtonsOnNullData from "../../hooks/useDisableButtonsOnNullData";
import useSetPageTitle from "../../hooks/useSetPageTitle";
import UserPages from "../../components/pageComponents/userComponents/userPages/UserPages";
import { UserSortBy } from "../../types/userTypes";
import UserFilterNav from "../../components/pageComponents/userComponents/userFilterNavbar/UserFilterNavbar";
import { SortOrder } from "../../types/types";
import NoDataSignal from "../../components/general/popups/messagePopups/NoDataModal";

type FriendshipCategory = "friends" | "requests" | "sent";
type Props = {
  friendshipCategory: FriendshipCategory;
};
export default function AllFriendsWindow({ friendshipCategory }: Props) {
  const axios = useAxios();
  const [allUsersFetched, setAllUsersFetched] = useState(false);
  const [sortBy, setSortBy] = useState<UserSortBy>("username");
  const [sortOrder, setSortOrder] = useState<SortOrder>("asc");

  const friendURLPrefix =
    (friendshipCategory == "requests" && "/user/friends/requests/all") ||
    (friendshipCategory == "sent" && "/user/friends/requests/sent/all") ||
    "/user/friends/all";

  const pageTitle =
    (friendshipCategory == "requests" && "friend requests") ||
    (friendshipCategory == "sent" && "sent requests") ||
    "all friends";

  const _ = useSetPageTitle(pageTitle);

  const fetchFriends: QueryFunction<
    UserListResponse,
    [FriendshipCategory, UserSortBy, SortOrder],
    number
  > = async ({ pageParam = 1 }) => {
    setAllUsersFetched(false);
    try {
      const res = await axios.get(
        `${friendURLPrefix}?sort=${sortBy}&order=${sortOrder}&page=${pageParam}`
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
    queryKey: [friendshipCategory, sortBy, sortOrder],
    queryFn: fetchFriends,
    initialPageParam: 1,
    getNextPageParam: (_lastPage, pagesData) => pagesData.length + 1,
  });

  const handleFetchMoreClick = () => {
    fetchNextPage();
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
    <div className="window friends-window all-friends-window">
      <UserFilterNav
        setSortOrder={setSortOrder}
        setSortBy={setSortBy}
        sortOrder={sortOrder}
        sortBy={sortBy}
        buttonsDisabled={((error || filterButtonsDisabled) && true) || false}
      />
      <div className="window-section grow">
        {(pagesData && pagesData.pages && pagesData.pages[0].users.length > 0 && (
          <UserPages
            pagesData={pagesData}
            toPage={"preview"}
            isFetchNextPageError={isFetchNextPageError}
            isFetchingNextPage={isFetchingNextPage}
            handleFetchMoreClick={handleFetchMoreClick}
            allUsersFetched={allUsersFetched}
            showOnlineStatus
          />
        )) ||
          (pagesData?.pages && pagesData.pages[0].users.length < 1 && !error && (
            <NoDataSignal expectedData={pageTitle} />
          ))}
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
