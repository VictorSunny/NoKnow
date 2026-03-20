import React, { useEffect, useState } from "react";
import { useInfiniteQuery, QueryFunction } from "@tanstack/react-query";
import useAxios from "../../../hooks/useAxios";
import { useOutletContext, useParams } from "react-router-dom";
import TanstackQueryLoadStateHandler from "../../../components/general/tanstackQueryLoadStateHandler/TanstackQueryLoadStateHandler";
import useDisableButtonsOnNullData from "../../../hooks/useDisableButtonsOnNullData";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import { FromDate, SortByDateOrID, SortOrder, Validity } from "../../../types/types";
import { AdminBlacklistedTokenList } from "../../../components/adminPageComponents/pagesLists/AdminBlacklistedTokenList";
import AdminBlacklistedTokenFilterNav from "../../../components/adminPageComponents/navbars/blacklistedToken/AdminBlacklistedTokenNavbars";
import {
  BlacklistedTokenListResponse,
  BlacklistedTokenListResponseSchema,
} from "../../../schemas/BlacklistedRefreshTokenSchema";
import NavContainer from "../../../components/general/dropdownSelect/NavContainer";

export default function AdminBlacklistedTokenListPage() {
  const [allBlacklistedTokensFetched, setAllBlacklistedTokensFetched] = useState<boolean>(false);

  const {
    blkTokenFromDate,
    blkTokenSortBy,
    blkTokenSortOrder,
    blkTokenValidity,
    setBlkTokenFromDate,
    setBlkTokenSortBy,
    setBlkTokenSortOrder,
    setBlkTokenValidity,
  } = useOutletContext<any>();

  const axios = useAxios({ forAdmin: true });

  const { searchString } = useParams();

  const _ = useSetPageTitle((searchString && "matching tokens") || "all tokens");

  const adminFetchBlacklistedTokens: QueryFunction<
    BlacklistedTokenListResponse,
    [string, string | undefined, SortByDateOrID, SortOrder, FromDate, Validity],
    number
  > = async ({ pageParam = 1 }) => {
    setAllBlacklistedTokensFetched(false);
    try {
      const res = await axios.get(
        `/admin/token_blacklist/all?sort=${blkTokenSortBy}&order=${blkTokenSortOrder}&from_date=${blkTokenFromDate}&validity=${blkTokenValidity}&page=${pageParam}`
      );
      if (res.data.tokens && res.data.tokens.length < 1) {
        setAllBlacklistedTokensFetched(true);
      }
      const parsedBlacklistedTokenListData = BlacklistedTokenListResponseSchema.parse(res.data);
      return parsedBlacklistedTokenListData;
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
      "blacklistedTokens",
      searchString,
      blkTokenSortBy,
      blkTokenSortOrder,
      blkTokenFromDate,
      blkTokenValidity,
    ],
    queryFn: adminFetchBlacklistedTokens,
    initialPageParam: 1,
    getNextPageParam: (_lastPage, allPages) => allPages.length + 1,
    gcTime: 1000 * 60 * 2,
    retry: 1,
  });

  const handleFetchMoreClick = () => {
    fetchNextPage();
  };
  useEffect(() => {
    setBlkTokenSortOrder("asc");
  }, [blkTokenSortBy]);

  const filterButtonsDisabled = useDisableButtonsOnNullData({ pagesData: allPages });

  return (
    <div className="page-container admin-token-list-page">
      <AdminBlacklistedTokenFilterNav
        validity={blkTokenValidity}
        sortBy={blkTokenSortBy}
        sortOrder={blkTokenSortOrder}
        fromDate={blkTokenFromDate}
        setFromDate={setBlkTokenFromDate}
        setSortBy={setBlkTokenSortBy}
        setSortOrder={setBlkTokenSortOrder}
        setValidity={setBlkTokenValidity}
        searchString={searchString}
        buttonsDisabled={filterButtonsDisabled}
      />
      {allPages && allPages.pages.length > 0 && (
        <div className="section grow">
          <AdminBlacklistedTokenList
            pagesData={allPages}
            isFetchNextPageError={isFetchNextPageError}
            isFetchingNextPage={isFetchingNextPage}
            handleFetchMoreClick={handleFetchMoreClick}
            allBlacklistedTokensFetched={allBlacklistedTokensFetched}
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
