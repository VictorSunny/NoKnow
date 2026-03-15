import { NavLink } from "react-router-dom";

export function AdminMainPagesLinks() {
  return (
    <div className="site-nav-section">
      <p className="title">go to</p>
      <div className="links-container">
        <NavLink className="section-link" to="/admin/manage/user">
          users
        </NavLink>
        <NavLink className="section-link" to="/admin/manage/chatroom">
          chatrooms
        </NavLink>
        <NavLink className="section-link" to="/admin/manage/email-blacklist">
          blacklisted emails
        </NavLink>
        <NavLink className="section-link" to="/admin/manage/token-blacklist">
          blacklisted tokens
        </NavLink>
      </div>
    </div>
  );
}
