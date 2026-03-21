import { useState } from "react";
import { Outlet } from "react-router-dom";
import { AdminMainPagesLinks } from "../../components/general/siteLinkLists/AdminSiteLinkLists";
import {
  FromDate,
  OptionalBooleanString,
  SortByDateOrID,
  SortOrder,
  Validity,
} from "../../types/types";
import { ChatroomSortBy, ChatroomType } from "../../types/chatroomTypes";
import { AdminUserSortBy, UserRoleChoices } from "../../types/userTypes";

import "./Admin.css";

export default function AdminManagerLayout() {
  const [chatRoomType, setChatRoomType] = useState<ChatroomType>("all");
  const [chatSortBy, setChatSortBy] = useState<ChatroomSortBy>("name");
  const [chatSortOrder, setChatSortOrder] = useState<SortOrder>("asc");
  const [chatFromDate, setChatFromDate] = useState<FromDate>("all");
  const [chatMinMembers, setChatMinMembers] = useState(0);

  const [userRole, setUserRoleChoices] = useState<UserRoleChoices>("all");
  const [userSortBy, setUserSortBy] = useState<AdminUserSortBy>("name");
  const [userSortOrder, setUserSortOrder] = useState<SortOrder>("asc");
  const [userFromDate, setUserFromDate] = useState<FromDate>("all");
  const [userActive, setUserActive] = useState<OptionalBooleanString>("all");
  const [userGoogleSignup, setUserGoogleSignup] = useState<OptionalBooleanString>("all");

  const [blkTokenSortBy, setBlkTokenSortBy] = useState<SortByDateOrID>("id");
  const [blkTokenSortOrder, setBlkTokenSortOrder] = useState<SortOrder>("asc");
  const [blkTokenFromDate, setBlkTokenFromDate] = useState<FromDate>("all");
  const [blkTokenValidity, setBlkTokenValidity] = useState<Validity>("all");

  const [blkEmailSortBy, setBlkEmailSortBy] = useState<SortByDateOrID>("id");
  const [blkEmailSortOrder, setBlkEmailSortOrder] = useState<SortOrder>("asc");
  const [blkEmailFromDate, setBlkEmailFromDate] = useState<FromDate>("all");

  const context = {
    // chat filter context
    chatRoomType,
    setChatRoomType,
    chatSortBy,
    chatMinMembers,
    chatSortOrder,
    chatFromDate,
    setChatSortBy,
    setChatSortOrder,
    setChatFromDate,
    setChatMinMembers,

    // user filter context
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

    // blacklisted token filter context
    blkTokenFromDate,
    blkTokenSortBy,
    blkTokenSortOrder,
    blkTokenValidity,
    setBlkTokenFromDate,
    setBlkTokenSortBy,
    setBlkTokenSortOrder,
    setBlkTokenValidity,

    // blacklisted email filter context
    blkEmailFromDate,
    blkEmailSortBy,
    blkEmailSortOrder,
    setBlkEmailFromDate,
    setBlkEmailSortBy,
    setBlkEmailSortOrder,
  };
  return (
    <div className="layout-container admin-page-container">
      <aside className="layout-sidebar" id="admin-layout-sidebar">
        <AdminMainPagesLinks />
      </aside>
      <div className="layout-main-content">
        <Outlet context={context} />
      </div>
    </div>
  );
}
