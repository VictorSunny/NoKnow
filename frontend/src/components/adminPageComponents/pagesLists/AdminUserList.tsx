import "../AdminPageComponents.css";
import { InfiniteData } from "@tanstack/react-query";
import { motion } from "framer-motion";

// import "./UserPages.css";
import { AdminUserBasic, AdminUserListResponse } from "../../../schemas/AuthSchema";
import FetchErrorSignal from "../../general/popups/messagePopups/FetchErrorModal";
import { APIModelName } from "../../../types/types";
import { Link } from "react-router-dom";

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
            {pagesData.pages.map((page) => {
              return page.users.map((userDetails, index) => {
                return <AdminUserCard key={index} userDetails={userDetails} modelName={"user"} />;
              });
            })}
          </tbody>
        </table>
      </div>
      {pagesData.pages[0].users.length > 1 && (
        <motion.button
          className={`btn fetch-more-btn ${isFetchingNextPage && "load"}`}
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
    </div>
  );
}

type AdminUserCardProps = {
  userDetails: AdminUserBasic;
  modelName: APIModelName;
};
function AdminUserCard({ userDetails, modelName }: AdminUserCardProps) {
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
}

function TableData({ children, id }: { children: React.ReactNode; id: string }) {
  return (
    <td className="table-link-container">
      <Link to={`/admin/manage/user/update/${id}`} className="table-link">
        {children}
      </Link>
    </td>
  );
}
