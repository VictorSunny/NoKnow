import { Link } from "react-router-dom";
import "../AdminPageComponents.css";

import { InfiniteData } from "@tanstack/react-query";
import FetchErrorSignal from "../../general/fetchModals/FetchErrorModal";
import { motion } from "framer-motion";
import { APIModelName } from "../../../types/types";
import {
  BlacklistedEmail,
  BlacklistedEmailListResponse,
} from "../../../schemas/BlacklistedEmailSchemas";

type AdminBlacklistedEmailListProps = {
  pagesData: InfiniteData<BlacklistedEmailListResponse, unknown>;
  isFetchingNextPage: boolean;
  handleFetchMoreClick: () => void;
  allBlacklistedEmailsFetched: boolean;
  isFetchNextPageError: boolean;
};
export function AdminBlacklistedEmailList({
  pagesData,
  isFetchingNextPage,
  handleFetchMoreClick,
  allBlacklistedEmailsFetched,
  isFetchNextPageError,
}: AdminBlacklistedEmailListProps) {
  if (pagesData.pages[0].emails.length < 1) {
    return <FetchErrorSignal errorMessage="sorry. no matches were found." />;
  }

  return (
    <div className="admin-list">
      <div className="table-container">
        <table className="blacklisted-email-table grow">
          <thead>
            <tr>
              <th></th>
              <th>id</th>
              <th>sub</th>
              <th>created at</th>
            </tr>
          </thead>
          <tbody>
            {pagesData.pages?.map((page) => {
              return page.emails?.map((blacklistedemailDetails, index) => {
                return (
                  <AdminBlacklistedEmailCard
                    modelName={"blacklistedEmail"}
                    key={index}
                    blacklistedemailDetails={blacklistedemailDetails}
                  />
                );
              });
            })}
          </tbody>
        </table>
      </div>
      {pagesData.pages[0].emails.length > 0 && (
        <motion.button
          className={`btn fetch-more-btn ${isFetchingNextPage && "load"}`}
          type="button"
          aria-label="load more blacklistedemails"
          onClick={handleFetchMoreClick}
          disabled={isFetchingNextPage || allBlacklistedEmailsFetched}
          layout
        >
          {/* change button value while fetching next page */}
          {(isFetchingNextPage && "loading") ||
            (isFetchNextPageError && "retry") ||
            (allBlacklistedEmailsFetched && "end of list") ||
            "load more emails"}
        </motion.button>
      )}
    </div>
  );
}

export function AdminBlacklistedEmailCard({
  blacklistedemailDetails,
  modelName,
}: {
  modelName: APIModelName;
  blacklistedemailDetails: BlacklistedEmail;
}) {
  console.log(blacklistedemailDetails);
  return (
    <tr
      id={`${modelName}-${blacklistedemailDetails.id}`}
      className="selectable-card"
      data-id={blacklistedemailDetails.id}
    >
      <td>
        <input
          name={modelName}
          type="checkbox"
          value={blacklistedemailDetails.id}
          key={blacklistedemailDetails.id}
        />
      </td>
      <TableData id={blacklistedemailDetails.id}>{blacklistedemailDetails.id}</TableData>
      <TableData id={blacklistedemailDetails.id}>{blacklistedemailDetails.sub}</TableData>
      <TableData id={blacklistedemailDetails.id}>{blacklistedemailDetails.created_at}</TableData>
    </tr>
  );
}

function TableData({ children, id }: { children: React.ReactNode; id: number }) {
  return (
    <td className="table-link-container">
      <Link to={`/admin/manage/email-blacklist/update/${id}`} className="table-link">
        {children}
      </Link>
    </td>
  );
}
