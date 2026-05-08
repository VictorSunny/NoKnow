import { NavLink } from "react-router-dom";
import "./siteLinkLists.css";

import { ReactComponent as HomeIcon } from "../../../assets/icons/header-home-icon.svg";
import { ReactComponent as ChatIcon } from "../../../assets/icons/header-chat-icon.svg";
import { ReactComponent as ProfileIcon } from "../../../assets/icons/header-profile-icon.svg";
import { ReactComponent as UserGroupTwo } from "../../../assets/icons/users-group-two-icon.svg";
import { ReactComponent as UserGroupThree } from "../../../assets/icons/users-group-chat.svg";

import { ReactComponent as RecentClockIcon } from "../../../assets/icons/clock-history-anti-clockwise-icon.svg";
import { ReactComponent as CreateChatIcon } from "../../../assets/icons/create-icon.svg";
import { ReactComponent as AnonymousIcon } from "../../../assets/icons/face-unknown.svg";

import { ReactComponent as FriendIcon } from "../../../assets/icons/friend-users-neutral-icon.svg";
import { ReactComponent as FriendSentRequestsIcon } from "../../../assets/icons/friend-users-sent-requests-icon.svg";
import { ReactComponent as FriendReceivedRequestsIcon } from "../../../assets/icons/friend-users-received-requests-icon.svg";

import { ReactComponent as LinkedinIcon } from "../../../assets/logos/linkedin-square-icon.svg";
import { ReactComponent as GithubIcon } from "../../../assets/logos/github-icon.svg";
import { ReactComponent as DiscordLogo } from "../../../assets/logos/discord-logo.svg";
import { ReactComponent as EnvelopeIcon } from "../../../assets/logos/envelope-icon.svg";
import { ReactComponent as BriefcaseIcon } from "../../../assets/logos/briefcase-icon.svg";

export type InnerLinksProps = {
  userIsLoggedIn: boolean;
  isMobile?: boolean;
  forHeader?: boolean;
};

export function SiteMainInnerLinks({ userIsLoggedIn, isMobile, forHeader }: InnerLinksProps) {
  return (
    <div className={`${(forHeader && "header-nav-links") || ""} site-nav-section"`}>
      <div className="links-container">
        {isMobile && (
          <NavLink end className={`section-link ${(forHeader && "header-link") || ""}`} to="/">
            <div className="text-icon-container">
              <HomeIcon className="icon" aria-label="home icon" />
              <span>home</span>
            </div>
          </NavLink>
        )}
        {userIsLoggedIn && (
          <>
            <NavLink
              className={`section-link ${(forHeader && "header-link") || ""}`}
              to="auth/account"
            >
              <div className="text-icon-container">
                <ProfileIcon className="icon" aria-label="home icon" />
                <span>profile</span>
              </div>
            </NavLink>
            <NavLink className={`section-link ${(forHeader && "header-link") || ""}`} to="friends">
              <div className="text-icon-container">
                <UserGroupTwo className="icon" aria-label="home icon" />
                <span>friends</span>
              </div>
            </NavLink>
          </>
        )}
        <NavLink className={`section-link ${(forHeader && "header-link") || ""}`} to="chat">
          <div className="text-icon-container">
            <ChatIcon className="icon" aria-label="home icon" />
            <span>chat</span>
          </div>
        </NavLink>
      </div>
    </div>
  );
}

export function SiteChatNavLinks({ userIsLoggedIn }: InnerLinksProps) {
  return (
    <div className="site-nav-section">
      <div className="title">chat</div>
      <div className="links-container">
        <NavLink to="/chat/recents" aria-label="create public chatroom" className="section-link">
          <div className="text-icon-container">
            <RecentClockIcon className="icon" aria-label="clock history anti-clockwise icon" />
            <span>recently visited</span>
          </div>
        </NavLink>
        {userIsLoggedIn && (
          <>
            <NavLink
              to="/chat/rooms"
              aria-label="go to joined chatrooms page"
              className="section-link"
            >
              <div className="text-icon-container">
                <UserGroupThree className="icon" aria-label="three users icon" />
                <span>joined chatrooms</span>
              </div>
            </NavLink>
            <NavLink
              to="/chat/friends"
              aria-label="to to friend chats page"
              className="section-link"
            >
              <div className="text-icon-container">
                <UserGroupTwo className="icon" aria-label="two users icon" />
                <span>friend chats</span>
              </div>
            </NavLink>
            <NavLink
              to="/chat/create/private"
              aria-label="create public chatroom"
              className="section-link"
            >
              <div className="text-icon-container">
                <CreateChatIcon className="icon" aria-label="create edit icon" />
                <span>create private chatroom</span>
              </div>
            </NavLink>
          </>
        )}
        <NavLink
          to="/chat/create/public"
          aria-label="create public chatroom"
          className="section-link"
        >
          <div className="text-icon-container">
            <CreateChatIcon className="icon" aria-label="create edit icon" />
            <span>create public chatroom</span>
          </div>
        </NavLink>
        <NavLink to="/chat/alias" aria-label="create public chatroom" className="section-link">
          <div className="text-icon-container">
            <AnonymousIcon className="icon" aria-label="disguised face icon" />
            <span>set anonymous username</span>
          </div>
        </NavLink>
      </div>
    </div>
  );
}

export function SiteFriendNavLinks() {
  return (
    <div className="site-nav-section">
      <div className="title">friends</div>
      <div className="links-container">
        <NavLink to="/friends" aria-label="go to all friends page" className="section-link">
          <div className="text-icon-container">
            <FriendIcon className="icon" aria-label="user icon" />
            <span>all</span>
          </div>
        </NavLink>
        <NavLink
          to="/friends/requests"
          aria-label="go to friend requests page"
          className="section-link"
        >
          <div className="text-icon-container">
            <FriendReceivedRequestsIcon className="icon" aria-label="user arrow right icon" />
            <span>requests</span>
          </div>
        </NavLink>
        <NavLink
          to="/friends/sent"
          aria-label="go to sent friend requests page"
          className="section-link"
        >
          <div className="text-icon-container">
            <FriendSentRequestsIcon className="icon" aria-label="user arrow left icon" />
            <span>sent requests</span>
          </div>
        </NavLink>
      </div>
    </div>
  );
}

export function SiteMainOuterLinks() {
  return (
    <div className="site-nav-section">
      <div className="title">contact developer</div>
      <div className="links-container">
        <a
          target="_blank"
          className="section-link"
          rel="noopener noreferrer"
          aria-label="go to developer's linkedin profile"
          href="https://www.linkedin.com/in/victor-sunny-6b06ba220"
        >
          <div className="text-icon-container">
            <LinkedinIcon className="icon" aria-label="linkedin logo" />
            <span>Linkedin</span>
          </div>
        </a>
        <a
          target="_blank"
          className="section-link"
          rel="noopener noreferrer"
          aria-label="go to developer's github page"
          href="https://www.github.com/victorsunny"
        >
          <div className="text-icon-container">
            <GithubIcon className="icon" aria-label="github logo" />
            <span>Github</span>
          </div>
        </a>
        <a
          target="_blank"
          className="section-link"
          rel="noopener noreferrer"
          href="mailto:victorsunny432@gmail.com"
          aria-label="email developer"
        >
          <div className="text-icon-container">
            <EnvelopeIcon className="icon" aria-label="envelope icon" />
            <span>Mail</span>
          </div>
        </a>
        <a
          target="_blank"
          className="section-link"
          rel="noopener noreferrer"
          aria-label="go to developer's portfolio page"
          href="https://victorsunny.vercel.app"
        >
          <div className="text-icon-container">
            <BriefcaseIcon className="icon" aria-label="briefcase icon" />
            <span>Portfolio</span>
          </div>
        </a>
        <a
          target="_blank"
          className="section-link"
          rel="noopener noreferrer"
          aria-label="go to developer's discord page"
          href="https://discordapp.com/users/1296969973155102761"
        >
          <div className="text-icon-container">
            <DiscordLogo className="icon" aria-label="discord logo" />
            <span>Discord</span>
          </div>
        </a>
      </div>
    </div>
  );
}
