import { NavLink } from "react-router-dom";

import { ReactComponent as UserIcon } from "../../../assets/icons/user-neutral-icon.svg";
import { ReactComponent as UserGroupThreeIcon } from "../../../assets/icons/users-group-chat.svg";
import { ReactComponent as CrossedOutEnvelopeIcon } from "../../../assets/icons/crossed-out-envelope-icon.svg";
import { ReactComponent as CrossedOutKeyIcon } from "../../../assets/icons/crossed-out-key-icon.svg";

export function AdminMainPagesLinks() {
  return (
    <div className="site-nav-section">
      <p className="title">go to</p>
      <div className="links-container">
        <NavLink className="section-link" to="/admin/manage/user">
          <div className="text-icon-container">
            <UserIcon className="icon" aria-label="user icon" />
            <span>users</span>
          </div>
        </NavLink>
        <NavLink className="section-link" to="/admin/manage/chatroom">
          <div className="text-icon-container">
            <UserGroupThreeIcon className="icon" aria-label="user group icon" />
            <span>chatrooms</span>
          </div>
        </NavLink>
        <NavLink className="section-link" to="/admin/manage/email-blacklist">
          <div className="text-icon-container">
            <CrossedOutEnvelopeIcon className="icon" aria-label="crossed out envelope icon" />
            <span>blacklisted emails</span>
          </div>
        </NavLink>
        <NavLink className="section-link" to="/admin/manage/token-blacklist">
          <div className="text-icon-container">
            <CrossedOutKeyIcon className="icon" aria-label="crossed out key icon" />
            <span>blacklisted tokens</span>
          </div>
        </NavLink>
      </div>
    </div>
  );
}
