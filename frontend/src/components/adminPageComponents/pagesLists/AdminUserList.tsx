import "../AdminPageComponents.css";
import { InfiniteData } from "@tanstack/react-query";
import { motion } from "framer-motion";

// import "./UserPages.css";
import { AdminUserBasic, AdminUserListResponse } from "../../../schemas/AuthSchema";
import FetchErrorSignal from "../../general/modals/FetchErrorModal";
import { APIModelName } from "../../../types/types";
import { Link } from "react-router-dom";
import React from "react";
import LoadMoreButton from "../../general/loadMoreButton/LoadMoreButton";

type UserPagesProps = {
  pagesData: InfiniteData<AdminUserListResponse, unknown>;
  isFetchingNextPage: boolean;
  handleFetchMoreClick: () => void;
  allUsersFetched: boolean;
  isFetchNextPageError: boolean;
};
export default function AdminUserList({
  pagesData,
  isFetchingNextPage,
  handleFetchMoreClick,
  allUsersFetched,
  isFetchNextPageError,
}: UserPagesProps) {
  if (pagesData.pages[0].users.length < 1) {
    return <FetchErrorSignal errorMessage="sorry. no users were found." />;
  }
  if (pagesData.pages[0].users.length < 1) {
    return <FetchErrorSignal errorMessage="sorry. no matches were found." />;
  }

  return (
    <div className="admin-list">
      <div className="table-container">
        <table className="user-table">
          <thead>
            <tr>
              <th></th>
              <th>id</th>
              <th>name</th>
              <th>username</th>
              <th>joined</th>
              <th>role</th>
              <th>online</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {pagesData.pages?.map((page, index) => {
              return <AdminUserPage key={index} page={page} />;
            })}
          </tbody>
        </table>
      </div>
      {pagesData.pages[0].users.length > 1 && (
        <LoadMoreButton
          itemName="user"
          isFetchingNextPage={isFetchingNextPage}
          isFetchNextPageError={isFetchNextPageError}
          allFetched={allUsersFetched}
          onClick={handleFetchMoreClick}
        />
      )}
    </div>
  );
}

const AdminUserPage = React.memo(({ page }: { page: AdminUserListResponse }) => {
  return page.users?.map((userDetails) => {
    return <AdminUserCard key={userDetails.uid} modelName={"user"} userDetails={userDetails} />;
  });
});

type AdminUserCardProps = {
  userDetails: AdminUserBasic;
  modelName: APIModelName;
};
const AdminUserCard = React.memo(({ userDetails, modelName }: AdminUserCardProps) => {
  return (
    <tr
      id={`${modelName}-${userDetails.uid}`}
      data-to={`user/${userDetails.uid}`}
      className="seletable-card"
    >
      <td>
        <input
          name={modelName}
          type="checkbox"
          value={userDetails.uid}
          id={userDetails.uid}
          key={userDetails.uid}
        />
      </td>
      <TableData id={userDetails.uid}>{userDetails.uid}</TableData>
      <TableData id={userDetails.uid}>
        {userDetails.first_name} {userDetails.last_name}
      </TableData>
      <TableData id={userDetails.uid}>{userDetails.username}</TableData>
      <TableData id={userDetails.uid}>{userDetails.joined}</TableData>
      <TableData id={userDetails.uid}>{userDetails.role}</TableData>
      <TableData id={userDetails.uid}>{String(userDetails.online)}</TableData>
    </tr>
  );
});

function TableData({ children, id }: { children: React.ReactNode; id: string }) {
  return (
    <td className="table-link-container">
      <Link to={`/admin/manage/user/update/${id}`} className="table-link">
        {children}
      </Link>
    </td>
  );
}
