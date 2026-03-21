import { NavLink } from "react-router-dom";
import "./siteLinkLists.css";

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
            home
          </NavLink>
        )}
        {userIsLoggedIn && (
          <>
            <NavLink
              className={`section-link ${(forHeader && "header-link") || ""}`}
              to="auth/account"
            >
              profile
            </NavLink>
            <NavLink className={`section-link ${(forHeader && "header-link") || ""}`} to="friends">
              friends
            </NavLink>
          </>
        )}
        <NavLink className={`section-link ${(forHeader && "header-link") || ""}`} to="chat">
          chat
        </NavLink>
        {/* <NavLink
          end
          className={`section-link ${(forHeader && "header-link") || ""}`}
          to="chat/recents"
        >
          recents
        </NavLink> */}
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
          recently visited
        </NavLink>
        {userIsLoggedIn && (
          <>
            <NavLink
              to="/chat/rooms"
              aria-label="go to joined chatrooms page"
              className="section-link"
            >
              joined chatrooms
            </NavLink>
            <NavLink
              to="/chat/friends"
              aria-label="to to friend chats page"
              className="section-link"
            >
              friend chats
            </NavLink>
            <NavLink
              to="/chat/create/private"
              aria-label="create public chatroom"
              className="section-link"
            >
              create private chatroom
            </NavLink>
          </>
        )}
        <NavLink
          to="/chat/create/public"
          aria-label="create public chatroom"
          className="section-link"
        >
          create public chatroom
        </NavLink>
        <NavLink to="/chat/alias" aria-label="create public chatroom" className="section-link">
          set anonymous username
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
          all
        </NavLink>
        <NavLink
          to="/friends/requests"
          aria-label="go to friend requests page"
          className="section-link"
        >
          requests
        </NavLink>
        <NavLink
          to="/friends/sent"
          aria-label="go to sent friend requests page"
          className="section-link"
        >
          sent requests
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
          Linkedin
        </a>
        <a
          target="_blank"
          className="section-link"
          rel="noopener noreferrer"
          aria-label="go to developer's github page"
          href="https://www.github.com/victorsunny"
        >
          Github
        </a>
        <a
          target="_blank"
          className="section-link"
          rel="noopener noreferrer"
          href="mailto:victorsunny432@gmail.com"
          aria-label="email developer"
        >
          Mail
        </a>
        <a
          target="_blank"
          className="section-link"
          rel="noopener noreferrer"
          aria-label="go to developer's portfolio page"
          href="https://victorsunny.vercel.app"
        >
          Portfolio
        </a>
        <a
          target="_blank"
          className="section-link"
          rel="noopener noreferrer"
          aria-label="go to developer's discord page"
          href="https://discordapp.com/users/1296969973155102761"
        >
          Discord
        </a>
      </div>
    </div>
  );
}
