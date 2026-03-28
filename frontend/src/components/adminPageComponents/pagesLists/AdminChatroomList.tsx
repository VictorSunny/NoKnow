import { Link } from "react-router-dom";
import "../AdminPageComponents.css";

import { Chatroom, ChatroomListResponse } from "../../../schemas/ChatSchemas";
import { InfiniteData } from "@tanstack/react-query";
import FetchErrorSignal from "../../general/modals/FetchErrorModal";
import { motion } from "framer-motion";
import { APIModelName } from "../../../types/types";
import React from "react";

type AdminChatroomListProps = {
  pagesData: InfiniteData<ChatroomListResponse, unknown>;
  isFetchingNextPage: boolean;
  handleFetchMoreClick: () => void;
  allChatroomsFetched: boolean;
  isFetchNextPageError: boolean;
};
export function AdminChatroomList({
  pagesData,
  isFetchingNextPage,
  handleFetchMoreClick,
  allChatroomsFetched,
  isFetchNextPageError,
}: AdminChatroomListProps) {
  if (pagesData.pages[0].chatrooms.length < 1) {
    return <FetchErrorSignal errorMessage="sorry. no matches were found." />;
  }

  return (
    <div className="admin-list">
      <div className="table-container">
        <table className="chatroom-table">
          <thead>
            <tr>
              <th></th>
              <th>id</th>
              <th>name</th>
              <th>type</th>
              <th>created at</th>
              <th>last active</th>
              <th>members</th>
            </tr>
          </thead>
          <tbody>
            {pagesData.pages?.map((page, index) => {
              return <AdminChatroomPage key={index} page={page} />;
            })}
          </tbody>
        </table>
      </div>
      {pagesData.pages[0].chatrooms.length > 0 && (
        <motion.button
          className={`btn fetch-more-btn ${isFetchingNextPage && "load"}`}
          type="button"
          aria-label="load more chatrooms"
          onClick={handleFetchMoreClick}
          disabled={isFetchingNextPage || allChatroomsFetched}
          layout
        >
          {/* change button value while fetching next page */}
          {(isFetchingNextPage && "loading") ||
            (isFetchNextPageError && "retry") ||
            (allChatroomsFetched && "end of list") ||
            "load more rooms"}
        </motion.button>
      )}
    </div>
  );
}

const AdminChatroomPage = React.memo(({ page }: { page: ChatroomListResponse }) => {
  return page.chatrooms?.map((chatroomDetails) => {
    return (
      <AdminChatroomCard
        key={chatroomDetails.uid}
        modelName={"chatroom"}
        chatroomDetails={chatroomDetails}
      />
    );
  });
});
const AdminChatroomCard = React.memo(
  ({ chatroomDetails, modelName }: { modelName: APIModelName; chatroomDetails: Chatroom }) => {
    return (
      <tr
        id={`${modelName}-${chatroomDetails.uid}`}
        className="selectable-card"
        data-to={`room/${chatroomDetails.uid}`}
      >
        <td>
          <input
            name={modelName}
            type="checkbox"
            value={chatroomDetails.uid}
            key={chatroomDetails.uid}
          />
        </td>
        <TableData id={chatroomDetails.uid}>{chatroomDetails.uid}</TableData>
        <TableData id={chatroomDetails.uid}>{chatroomDetails.name}</TableData>
        <TableData id={chatroomDetails.uid}>{chatroomDetails.room_type}</TableData>
        <TableData id={chatroomDetails.uid}>{chatroomDetails.created_at}</TableData>
        <TableData id={chatroomDetails.uid}>{chatroomDetails.modified_at}</TableData>
        <TableData id={chatroomDetails.uid}>{chatroomDetails.members_count}</TableData>
      </tr>
    );
  }
);

function TableData({ children, id }: { children: React.ReactNode; id: string }) {
  return (
    <td className="table-link-container">
      <Link to={`/admin/manage/chatroom/update/${id}`} className="table-link">
        {children}
      </Link>
    </td>
  );
}
