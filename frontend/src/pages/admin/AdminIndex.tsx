import { Link } from "react-router-dom";
import { ReactComponent as UserIcon } from "../../assets/icons/user-neutral-icon.svg";
import { ReactComponent as UserGroupThreeIcon } from "../../assets/icons/users-group-chat.svg";
import { ReactComponent as CrossedOutEnvelopeIcon } from "../../assets/icons/crossed-out-envelope-icon.svg";
import { ReactComponent as CrossedOutKeyIcon } from "../../assets/icons/crossed-out-key-icon.svg";

export default function AdminIndex() {
  return (
    <div className="page-container admin-index-page-container">
      <div className="section grow">
        <Link
          className="link-text"
          aria-label="go to user model management page"
          to="/admin/manage/user"
        >
          <div className="text-icon-container">
            <UserIcon className="icon" aria-label="user icon" />
            <span>manage users</span>
          </div>
        </Link>
        <Link
          className="link-text"
          aria-label="go to chatroom model management page"
          to="/admin/manage/chatroom"
        >
          <div className="text-icon-container">
            <UserGroupThreeIcon className="icon" aria-label="user group icon" />
            <span>manage chatrooms</span>
          </div>
        </Link>
        <Link
          className="link-text"
          aria-label="go to blacklisted email model management page"
          to="/admin/manage/email-blacklist"
        >
          <div className="text-icon-container">
            <CrossedOutEnvelopeIcon className="icon" aria-label="crossed out envelope icon" />
            <span>manage blacklisted emails</span>
          </div>
        </Link>
        <Link
          className="link-text"
          aria-label="go to blacklisted email model management page"
          to="/admin/manage/token-blacklist"
        >
          <div className="text-icon-container">
            <CrossedOutKeyIcon className="icon" aria-label="crossed out key icon" />
            <span>manage blacklisted tokens</span>
          </div>
        </Link>
      </div>
    </div>
  );
}
