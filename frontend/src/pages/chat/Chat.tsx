import { useRef, useEffect } from "react";
import { Outlet } from "react-router-dom";

import "./Chat.css";
import { SiteChatNavLinks } from "../../components/general/siteLinkLists/SiteLinkLists";
import useCheckUserIsAuthenticated from "../../hooks/useCheckUserIsAuthenticated";

function Chat() {
  const mainChatWindowContainer = useRef<HTMLDivElement>(null);
  const userIsLoggedIn = useCheckUserIsAuthenticated();

  useEffect(() => {
    if (mainChatWindowContainer.current) {
      mainChatWindowContainer.current.scrollTop = mainChatWindowContainer.current.scrollHeight;
    }
  }, []);

  return (
    <div className="layout-container chat-page-container">
      <aside className="layout-sidebar" id="chat-sidebar">
        <div className="sidebar-section">
          <SiteChatNavLinks userIsLoggedIn={userIsLoggedIn} />
        </div>
      </aside>
      <div className="layout-main-content" ref={mainChatWindowContainer}>
        <Outlet />
      </div>
    </div>
  );
}

export default Chat;
