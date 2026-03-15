import { useEffect } from "react";
import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes, Outlet, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import Header from "./layouts/header/Header";

import LeftRightLoadingSignal from "./components/general/fetchModals/LeftRightLoadModal";

import AnimatedPageWrapper from "./pages/AnimatedPageWrapper";

import Home from "./pages/home/Home";
import Chat from "./pages/chat/Chat";

import CreateChatroom from "./pages/chat/createChatroom/CreateChatroom";
import EngageChat from "./pages/chat/engageChat/EngageChat";
import { UserProvider } from "./contexts/AuthContext";
import ChatroomPreview from "./pages/Preview/ChatroomPreview";
import ProfilePreview from "./pages/Preview/ProfilePreview";
import AllChatrooms from "./pages/chat/allChatrooms/AllChatrooms";
import AllUserChats from "./pages/chat/allUserChats/AllUserChats";
import TwoFactorAuthWindow from "./pages/profile/windows/TwoFactorAuthWindow";
import Friends from "./pages/friends/Friends";
import AllFriendsWindow from "./pages/friends/AllFriendsWindow";
import ChatroomInformation from "./pages/chat/chatroomInformation/ChatroomInformation";
import ChatroomDetailsWindow from "./pages/chat/chatroomInformation/windows/ChatroomDetailsWindow";
import BasicDetailsUpdateWindow from "./pages/profile/windows/BasicDetailsUpdateWindow";
import DeleteAccountWindow from "./pages/profile/windows/DeleteAccountWindow";
import { ChatroomUserSearch } from "./pages/chat/chatroomInformation/windows/ChatroomUserSearch";
import { ChatroomUsers } from "./pages/chat/chatroomInformation/windows/ChatroomUsers";
import ChatroomUserPreviewWindow from "./pages/chat/chatroomInformation/windows/ChatroomUserPreviewWindow";
import LoginPage from "./pages/auth/LoginPage";
import { SignupPage } from "./pages/auth/SignupPage";
import { NavigationProvider } from "./contexts/NavigationContext";
import LogoutPage from "./pages/auth/LogoutPage";
import RecentlyVisitedChatrooms from "./pages/chat/recentChatrooms/RecentChatrooms";
import AnonymousUsername from "./pages/auth/AnonymousUsername";
import CreateChatroomIndex from "./pages/chat/createChatroom/CreateChatroomIndex";
import useRefresh from "./hooks/useRefresh";
import UserChatInformation from "./pages/chat/userChatInformation/UserChatInformation";
import EnterChat from "./pages/chat/enterChat/EnterChat";
import PasswordChangeWindow from "./pages/profile/windows/PasswordChangeWindow";
import EmailChangeWindow from "./pages/profile/windows/EmailChangeWindow";
import Guide from "./pages/extras/Guide";
import AnimatedWindowWrapper from "./pages/AnimatedWindowWrapper";

import AdminBlacklistedEmailListPage from "./pages/admin/managerListPages/AdminBlacklistedEmailListPage";
import AdminBlacklistedEmailView from "./pages/admin/viewPages/AdminBlacklistedEmailView";
import AdminChatroomListPage from "./pages/admin/managerListPages/AdminChatroomListPage";
import AdminUserListPage from "./pages/admin/managerListPages/AdminUserListPage";
import AdminLayout, { AdminIndex } from "./pages/admin/AdminLayout";
import AdminBlacklistedTokenListPage from "./pages/admin/managerListPages/AdminBlacklistedTokenListPage";
import AdminBlacklistedTokenView from "./pages/admin/viewPages/AdminBlacklistedTokenView";
import AdminChatroomView from "./pages/admin/viewPages/AdminChatroomView";
import AdminUserView from "./pages/admin/viewPages/AdminUserView";
import AdminManagerLayout from "./pages/admin/AdminManagerLayout";

const Profile = lazy(() => import("./pages/profile/Profile"));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 0,
      refetchOnWindowFocus: false,
      staleTime: 0,
      retry: 1,
    },
  },
});

function App() {
  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <NavigationProvider>
          <UserProvider>
            <AnimatedRoutes />
            <AnimatedAdminRoutes />
          </UserProvider>
        </NavigationProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );
}

function AnimatedRoutes() {
  const location = useLocation();
  const refreshAccessToken = useRefresh();

  useEffect(() => {
    refreshAccessToken().catch((err) => {
      console.log("failed first login", err);
    });
  }, []);

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Layout />}>
          {/* INDEX ROUTE */}
          <Route
            index
            element={
              <AnimatedPageWrapper>
                <Home />
              </AnimatedPageWrapper>
            }
          />
          {/* END OF INDEX ROUTE */}

          {/* PREVIEW ROUTES */}
          <Route path="preview/">
            <Route
              path="chatroom/:chatroomUID"
              element={
                <AnimatedPageWrapper>
                  <ChatroomPreview />
                </AnimatedPageWrapper>
              }
            />
            <Route
              path="user/:username"
              element={
                <AnimatedPageWrapper>
                  <ProfilePreview />
                </AnimatedPageWrapper>
              }
            />
          </Route>
          {/* END OF PREVIEW ROUTES */}

          {/* CHAT ROUTES */}
          <Route path="chat/" element={<Chat />}>
            {/* CHAT/ SUB-ROUTES */}
            <Route
              index
              element={
                <AnimatedPageWrapper>
                  <EnterChat />
                </AnimatedPageWrapper>
              }
            />
            <Route
              path="alias"
              element={
                <AnimatedPageWrapper>
                  <AnonymousUsername />
                </AnimatedPageWrapper>
              }
            />
            <Route path="rooms" element={<AllChatrooms />} />
            <Route path="friends" element={<AllUserChats />} />
            <Route path="recents" element={<RecentlyVisitedChatrooms />} />
            <Route path="users/search/:searchString" element={<AllUserChats />} />
            <Route path="rooms/search/:searchString" element={<AllChatrooms />} />

            {/* CREATE NEW CHATROOM - PRIVATE/PUBLIC */}
            <Route path="create/">
              <Route
                index
                element={
                  <AnimatedPageWrapper>
                    <CreateChatroomIndex />
                  </AnimatedPageWrapper>
                }
              />
              <Route
                path=":chatroomType"
                element={
                  <AnimatedPageWrapper>
                    <CreateChatroom />
                  </AnimatedPageWrapper>
                }
              />
            </Route>

            {/* ENTER CHATROOM OR CHAT WITH FRIEND */}
            <Route path="engage/:chatType/:chatID/" element={<EngageChat />} />

            <Route path="meta/chatroom/:chatroomUID/" element={<ChatroomInformation />}>
              <Route index element={<ChatroomDetailsWindow />} />
              <Route path="users/" element={<ChatroomUsers />} />
              <Route path="users/search/:q" element={<ChatroomUserSearch />} />
              <Route path="users/preview/:username" element={<ChatroomUserPreviewWindow />} />
            </Route>

            <Route
              path="meta/user/:chatID"
              element={
                <AnimatedPageWrapper>
                  <UserChatInformation />
                </AnimatedPageWrapper>
              }
            />
          </Route>
          {/* END OF CHAT ROUTES */}

          {/* AUTH ROUTES */}
          <Route path="auth/">
            <Route path="login" element={<LoginPage />} />
            <Route path="signup" element={<SignupPage />} />
            <Route path="logout" element={<LogoutPage />} />
            <Route path="suspended" element={<LogoutPage message={"Account suspended."} />} />
          </Route>
          {/* AUTH PROFILE ROUTES */}
          <Route path="auth/account" element={<Profile />}>
            <Route index element={<BasicDetailsUpdateWindow />} />
            <Route path="update/email" element={<EmailChangeWindow />} />
            <Route path="update/two-factor-auth" element={<TwoFactorAuthWindow />} />
            <Route path="update/password" element={<PasswordChangeWindow />} />
            <Route path="update/password/recovery" element={<PasswordChangeWindow />} />
            <Route path="delete" element={<DeleteAccountWindow />} />
          </Route>
          {/* END OF AUTH ROUTES */}

          {/* FRIEND ROUTES */}
          <Route path="friends" element={<Friends />}>
            <Route index element={<AllFriendsWindow friendshipCategory="friends" />} />
            <Route path="requests" element={<AllFriendsWindow friendshipCategory="requests" />} />
            <Route path="sent" element={<AllFriendsWindow friendshipCategory="sent" />} />
            {/* END OF FRIEND ROUTES */}
          </Route>
          <Route path="guide" element={<Guide />} />
        </Route>
      </Routes>
    </AnimatePresence>
  );
}

function AnimatedAdminRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location}>
        {/* ADMIN ROUTES */}
        <Route path="/#/admin" element={<AdminLayout />}>
          {/* auth routes */}
          <Route path="auth/login" element={<LoginPage adminLogin />} />
          {/* end of auth routes */}

          <Route path="manage" element={<AdminManagerLayout />}>
            {/* index route */}
            <Route
              index
              element={
                <AnimatedWindowWrapper>
                  <AdminIndex />
                </AnimatedWindowWrapper>
              }
            />
            {/* end of index route */}

            {/* chatroom routes */}
            <Route path="chatroom">
              <Route index element={<AdminChatroomListPage />} />
              <Route path="create" element={<AdminChatroomView />} />
              <Route path="update/:chatroomUID" element={<AdminChatroomView forUpdate />} />
            </Route>
            {/* end of chatroom routes */}

            {/* user routes */}
            <Route path="user">
              <Route index element={<AdminUserListPage />} />
              <Route path="create" element={<AdminUserView />} />
              <Route path="update/:userUID" element={<AdminUserView forUpdate />} />
            </Route>
            {/* end of user routes */}

            {/* blacklisted email routes */}
            <Route path="email-blacklist">
              <Route index element={<AdminBlacklistedEmailListPage />} />
              <Route path="create" element={<AdminBlacklistedEmailView />} />
              <Route path="update/:id" element={<AdminBlacklistedEmailView forUpdate />} />
            </Route>
            {/* end of blacklisted email routes */}

            {/* blacklisted tokens routes */}
            <Route path="token-blacklist">
              <Route index element={<AdminBlacklistedTokenListPage />} />
              <Route path="update/:id" element={<AdminBlacklistedTokenView />} />
            </Route>
            {/* end of blacklisted email routes */}

            {/* ADMIN ROUTES */}
          </Route>
        </Route>
      </Routes>
    </AnimatePresence>
  );
}

export default App;

function Layout() {
  return (
    <>
      <Header />
      <main>
        <Suspense fallback={<LeftRightLoadingSignal />}>
          <Outlet />
        </Suspense>
      </main>
    </>
  );
}
