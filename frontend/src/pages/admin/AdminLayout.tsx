import { Link, Outlet } from "react-router-dom";
import "./Admin.css";
import "../../pages/chat/Chat.css";
import AdminHeader from "../../layouts/adminHeader/AdminHeader";

export default function AdminLayout() {
  return (
    <>
      <AdminHeader />
      <main>
        <Outlet />
      </main>
    </>
  );
}

export function AdminIndex() {
  return (
    <div className="page-container admin-index-page-container">
      <div className="section grow">
        <Link
          className="link-text"
          aria-label="go to user model management page"
          to="/admin/manage/user"
        >
          manage users
        </Link>
        <Link
          className="link-text"
          aria-label="go to chatroom model management page"
          to="/admin/manage/chatroom"
        >
          manage chatrooms
        </Link>
        <Link
          className="link-text"
          aria-label="go to blacklisted email model management page"
          to="/admin/manage/email-blacklist"
        >
          manage blacklisted emails
        </Link>
        <Link
          className="link-text"
          aria-label="go to blacklisted email model management page"
          to="/admin/manage/token-blacklist"
        >
          manage blacklisted tokens
        </Link>
      </div>
    </div>
  );
}
