import TanstackQueryLoadStateHandler from "../../../components/general/tanstackQueryLoadStateHandler/TanstackQueryLoadStateHandler";
import useAxios from "../../../hooks/useAxios";
import { AdminUserListResponse, AdminUserListResponseSchema } from "../../../schemas/AuthSchema";
import { QueryFunction, useInfiniteQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import useDisableButtonsOnNullData from "../../../hooks/useDisableButtonsOnNullData";
import NoDataSignal from "../../../components/general/fetchModals/NoDataModal";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import { UserRoleChoices, AdminUserSortBy } from "../../../types/userTypes";
import AdminUserList from "../../../components/adminPageComponents/pagesLists/AdminUserList";
import AdminUserFilterNav from "../../../components/adminPageComponents/navbars/user/AdminUserNavbars";
import { FromDate, OptionalBooleanString, SortOrder } from "../../../types/types";
import { useOutletContext } from "react-router-dom";

export default function AdminUserListPage() {
  const axios = useAxios({ forAdmin: true });
  const [allUsersFetched, setAllUsersFetched] = useState(false);

  const {
    userRole,
    userActive,
    userSortOrder,
    userSortBy,
    userFromDate,
    userGoogleSignup,
    setUserRoleChoices,
    setUserSortBy,
    setUserSortOrder,
    setUserFromDate,
    setUserActive,
    setUserGoogleSignup,
  } = useOutletContext<any>();

  const _ = useSetPageTitle("all users");

  const fetchFriends: QueryFunction<
    AdminUserListResponse,
    [
      string,
      AdminUserSortBy,
      SortOrder,
      UserRoleChoices,
      OptionalBooleanString,
      OptionalBooleanString,
      FromDate,
    ],
    number
  > = async ({ pageParam = 1 }) => {
    setAllUsersFetched(false);
    try {
      const res = await axios.get(
        `/admin/user/all?page=${pageParam}&sort=${userSortBy}&order=${userSortOrder}&google_signup=${userGoogleSignup}&active=${userActive}&role=${userRole}&from_date=${userFromDate}`
      );
      if (res.data.users && res.data.users.length < 1) {
        setAllUsersFetched(true);
      }
      const parsedUserList = AdminUserListResponseSchema.parse(res.data);
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
    queryKey: [
      "users",
      userSortBy,
      userSortOrder,
      userRole,
      userActive,
      userGoogleSignup,
      userFromDate,
    ],
    queryFn: fetchFriends,
    initialPageParam: 1,
    getNextPageParam: (_lastPage, allPages) => allPages.length + 1,
  });

  const handleFetchMoreClick = () => {
    fetchNextPage();
  };

  const filterButtonsDisabled = useDisableButtonsOnNullData({ pagesData: pagesData });
  useEffect(() => {
    setUserSortOrder("asc");
  }, [userSortBy]);

  return (
    <div className="page-container admin-all-users-pages">
      <AdminUserFilterNav
        sortBy={userSortBy}
        setSortBy={setUserSortBy}
        sortOrder={userSortOrder}
        setSortOrder={setUserSortOrder}
        userActive={userActive}
        setUserActive={setUserActive}
        userRole={userRole}
        setUserRoleChoices={setUserRoleChoices}
        fromDate={userFromDate}
        setFromDate={setUserFromDate}
        googleSignup={userGoogleSignup}
        setGoogleSignup={setUserGoogleSignup}
        buttonsDisabled={((error || filterButtonsDisabled) && true) || false}
      />
      <div className="section grow">
        {(pagesData && pagesData.pages && pagesData.pages[0].users.length > 0 && (
          <>
            <AdminUserList
              pagesData={pagesData}
              isFetchNextPageError={isFetchNextPageError}
              isFetchingNextPage={isFetchingNextPage}
              handleFetchMoreClick={handleFetchMoreClick}
              allUsersFetched={allUsersFetched}
            />
          </>
        )) ||
          (pagesData?.pages && pagesData.pages[0].users.length < 1 && !error && (
            <NoDataSignal expectedData={"user"} />
          ))}
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
