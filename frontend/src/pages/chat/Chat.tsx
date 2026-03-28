import { useRef, useEffect, Suspense } from "react";
import { Outlet } from "react-router-dom";

import "./Chat.css";
import { SiteChatNavLinks } from "../../components/general/siteLinkLists/SiteLinkLists";
import useUserLoggedInStatus from "../../hooks/useUserLoggedInStatus";
import FadingSpinnerLoader from "../../components/general/loaders/FadingCirclesLoader";

function Chat() {
  const mainChatWindowContainer = useRef<HTMLDivElement>(null);
  const { userIsLoggedIn } = useUserLoggedInStatus();

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
        <Suspense fallback={<FadingSpinnerLoader />}>
          <Outlet />
        </Suspense>
      </div>
    </div>
  );
}

export default Chat;
