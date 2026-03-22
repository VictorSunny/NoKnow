import { useEffect, useState } from "react";
import { useInfiniteQuery, QueryFunction } from "@tanstack/react-query";
import useAxios from "../../../hooks/useAxios";
import { useOutletContext, useParams } from "react-router-dom";
import TanstackQueryLoadStateHandler from "../../../components/general/tanstackQueryLoadStateHandler/TanstackQueryLoadStateHandler";
import useDisableButtonsOnNullData from "../../../hooks/useDisableButtonsOnNullData";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import { FromDate, SortByDateOrID, SortOrder } from "../../../types/types";
import {
  BlacklistedEmailListResponse,
  BlacklistedEmailListResponseSchema,
} from "../../../schemas/BlacklistedEmailSchemas";
import { AdminBlacklistedEmailList } from "../../../components/adminPageComponents/pagesLists/AdminBlacklistedEmailList";
import AdminBlacklistedEmailFilterNav from "../../../components/adminPageComponents/navbars/blacklistedEmail/AdminBlacklistedEmailNavbars";

export default function AdminBlacklistedEmailListPage() {
  const [allBlacklistedEmailsFetched, setAllBlacklistedEmailsFetched] = useState<boolean>(false);

  const {
    blkEmailFromDate,
    blkEmailSortBy,
    blkEmailSortOrder,
    setBlkEmailFromDate,
    setBlkEmailSortBy,
    setBlkEmailSortOrder,
  } = useOutletContext<any>();

  const axios = useAxios({ forAdmin: true });

  const { searchString } = useParams();

  const _ = useSetPageTitle((searchString && "matching emails") || "all emails");

  const adminFetchBlacklistedEmails: QueryFunction<
    BlacklistedEmailListResponse,
    [string, string | undefined, SortByDateOrID, SortOrder, FromDate],
    number
  > = async ({ pageParam = 1 }) => {
    setAllBlacklistedEmailsFetched(false);
    try {
      const res = await axios.get(
        `/admin/email_blacklist/all?sort=${blkEmailSortBy}&order=${blkEmailSortOrder}&from_date=${blkEmailFromDate}&page=${pageParam}`
      );
      if (res.data.emails && res.data.emails.length < 1) {
        setAllBlacklistedEmailsFetched(true);
      }
      const parsedBlacklistedEmailListData = BlacklistedEmailListResponseSchema.parse(res.data);
      return parsedBlacklistedEmailListData;
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
    queryKey: [
      "blacklistedEmails",
      searchString,
      blkEmailSortBy,
      blkEmailSortOrder,
      blkEmailFromDate,
    ],
    queryFn: adminFetchBlacklistedEmails,
    initialPageParam: 1,
    getNextPageParam: (_lastPage, allPages) => allPages.length + 1,
    gcTime: 1000 * 60 * 2,
    retry: 1,
  });

  const handleFetchMoreClick = () => {
    fetchNextPage();
  };
  useEffect(() => {
    setBlkEmailSortOrder("asc");
  }, [blkEmailSortBy]);

  const filterButtonsDisabled = useDisableButtonsOnNullData({ pagesData: allPages });

  return (
    <div className="page-container admin-email-list-page">
      <AdminBlacklistedEmailFilterNav
        sortBy={blkEmailSortBy}
        sortOrder={blkEmailSortOrder}
        fromDate={blkEmailFromDate}
        setFromDate={setBlkEmailFromDate}
        setSortBy={setBlkEmailSortBy}
        setSortOrder={setBlkEmailSortOrder}
        searchString={searchString}
        buttonsDisabled={filterButtonsDisabled}
      />
      <div className="section grow">
        {allPages && allPages.pages.length > 0 && (
          <AdminBlacklistedEmailList
            pagesData={allPages}
            isFetchNextPageError={isFetchNextPageError}
            isFetchingNextPage={isFetchingNextPage}
            handleFetchMoreClick={handleFetchMoreClick}
            allBlacklistedEmailsFetched={allBlacklistedEmailsFetched}
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
