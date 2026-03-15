import { InfiniteData } from "@tanstack/react-query";
import { UUID } from "crypto";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

import "./UserPages.css";
import FetchErrorSignal from "../../../general/fetchModals/FetchErrorModal";
import { useEffect } from "react";
import { UserListResponse } from "../../../../schemas/AuthSchema";

type UserToPage = "chat" | "preview" | "chatroomPreview";
type UserPagesProps = {
  pagesData: InfiniteData<UserListResponse, unknown>;
  toPage: UserToPage;
  chatroomUID?: UUID;
  isFetchingNextPage: boolean;
  handleFetchMoreClick: () => void;
  allUsersFetched: boolean;
  isFetchNextPageError: boolean;
  showOnlineStatus?: boolean;
  showLastSeen?: boolean;
};
export default function UserPages({
  pagesData,
  toPage,
  chatroomUID,
  isFetchingNextPage,
  handleFetchMoreClick,
  allUsersFetched,
  isFetchNextPageError,
  showOnlineStatus,
  showLastSeen,
}: UserPagesProps) {
  if (pagesData.pages[0].users.length < 1) {
    return <FetchErrorSignal errorMessage="sorry. no matches were found." />;
  }
  const urlPrefix =
    (toPage == "chatroomPreview" && `/chat/meta/chatroom/${chatroomUID}/users/preview`) ||
    (toPage == "chat" && "/chat/engage/user") ||
    `/preview/user`;

  return (
    <>
      <div className="user-list">
        {pagesData.pages.map((page) => {
          return page.users.map((userDetails, index) => {
            return (
              <Link key={index} to={`${urlPrefix}/${userDetails.username}`} className="user-link">
                <p className="username">{userDetails.username}</p>
                {showOnlineStatus && (
                  <p className={`base-background ${(userDetails.online && "positive") || ""}`}>
                    {(userDetails.online && "online") ||
                      (showLastSeen && userDetails.last_seen) ||
                      "offline"}
                  </p>
                )}
              </Link>
            );
          });
        })}
      </div>
      {pagesData.pages[0].users.length > 1 && (
        <motion.button
          className={`btn fetch-more-btn ${isFetchingNextPage && "loading"}`}
          type="button"
          aria-label="load more users"
          onClick={handleFetchMoreClick}
          disabled={isFetchingNextPage || allUsersFetched}
          layout
        >
          {/* change button value while fetching next page */}
          {(isFetchingNextPage && "loading") ||
            (isFetchNextPageError && "retry") ||
            (allUsersFetched && "end of list") ||
            "load more"}
        </motion.button>
      )}
    </>
  );
}
