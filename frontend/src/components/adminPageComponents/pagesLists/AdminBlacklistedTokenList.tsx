import { Link } from "react-router-dom";
import "../AdminPageComponents.css";

import { InfiniteData } from "@tanstack/react-query";
import FetchErrorSignal from "../../general/modals/FetchErrorModal";
import { motion } from "framer-motion";
import { APIModelName } from "../../../types/types";
import {
  BlacklistedToken,
  BlacklistedTokenListResponse,
} from "../../../schemas/BlacklistedRefreshTokenSchema";
import React from "react";

type AdminBlacklistedTokenListProps = {
  pagesData: InfiniteData<BlacklistedTokenListResponse, unknown>;
  isFetchingNextPage: boolean;
  handleFetchMoreClick: () => void;
  allBlacklistedTokensFetched: boolean;
  isFetchNextPageError: boolean;
};
export function AdminBlacklistedTokenList({
  pagesData,
  isFetchingNextPage,
  handleFetchMoreClick,
  allBlacklistedTokensFetched,
  isFetchNextPageError,
}: AdminBlacklistedTokenListProps) {
  if (pagesData.pages[0].tokens.length < 1) {
    return <FetchErrorSignal errorMessage="sorry. no matches were found." />;
  }
  return (
    <div className="admin-list">
      <div className="table-container">
        <table className="blacklisted-token-table grow">
          <thead>
            <tr>
              <th></th>
              <th>id</th>
              <th>jti</th>
              <th>expiry</th>
              <th>created at</th>
              <th>expired</th>
            </tr>
          </thead>
          <tbody>
            {pagesData.pages?.map((page, index) => {
              return <AdminBlacklistedTokenPage key={index} page={page} />;
            })}
          </tbody>
        </table>
      </div>
      {pagesData.pages[0].tokens.length > 0 && (
        <motion.button
          className={`btn fetch-more-btn ${isFetchingNextPage && "load"}`}
          type="button"
          aria-label="load more blacklisted tokens"
          onClick={handleFetchMoreClick}
          disabled={isFetchingNextPage || allBlacklistedTokensFetched}
          layout
        >
          {/* change button value while fetching next page */}
          {(isFetchingNextPage && "loading") ||
            (isFetchNextPageError && "retry") ||
            (allBlacklistedTokensFetched && "end of list") ||
            "load more tokens"}
        </motion.button>
      )}
    </div>
  );
}

const AdminBlacklistedTokenPage = React.memo(({ page }: { page: BlacklistedTokenListResponse }) => {
  return page.tokens?.map((blacklistedtokenDetails) => {
    return (
      <AdminBlacklistedTokenCard
        key={blacklistedtokenDetails.id}
        modelName={"blacklistedToken"}
        blacklistedtokenDetails={blacklistedtokenDetails}
      />
    );
  });
});

const AdminBlacklistedTokenCard = React.memo(
  ({
    blacklistedtokenDetails,
    modelName,
  }: {
    modelName: APIModelName;
    blacklistedtokenDetails: BlacklistedToken;
  }) => {
    return (
      <tr
        id={`${modelName}-${blacklistedtokenDetails.id}`}
        className="selectable-card"
        data-id={blacklistedtokenDetails.id}
      >
        <td>
          <input
            name={modelName}
            type="checkbox"
            value={blacklistedtokenDetails.id}
            key={blacklistedtokenDetails.id}
          />
        </td>
        <TableData id={blacklistedtokenDetails.id}>{blacklistedtokenDetails.id}</TableData>
        <TableData id={blacklistedtokenDetails.id}>{blacklistedtokenDetails.jti}</TableData>
        <TableData id={blacklistedtokenDetails.id}>{blacklistedtokenDetails.exp}</TableData>
        <TableData id={blacklistedtokenDetails.id}>{blacklistedtokenDetails.created_at}</TableData>
        <TableData id={blacklistedtokenDetails.id}>
          {String(blacklistedtokenDetails.expired)}
        </TableData>
      </tr>
    );
  }
);

function TableData({ children, id }: { children: React.ReactNode; id: number }) {
  return (
    <td className="table-link-container">
      <Link to={`/admin/manage/token-blacklist/update/${id}`} className="table-link">
        {children}
      </Link>
    </td>
  );
}
