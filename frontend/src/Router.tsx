import { lazy, Suspense, useEffect } from "react";
import AnimatedPageWrapper from "./pages/AnimatedPageWrapper";
import Home from "./pages/home/Home";
import Guide from "./pages/extras/Guide";
import { createBrowserRouter, Outlet, RouterProvider, ScrollRestoration } from "react-router-dom";
import Header from "./layouts/header/Header";
import { QueryClient } from "@tanstack/react-query";
import AdminHeader from "./layouts/adminHeader/AdminHeader";
import useRefresh from "./hooks/useRefresh";
import FadingLineLoadingSignal from "./components/general/loaders/FadingCirclesLoader";
import useUserLoggedInStatus from "./hooks/useUserLoggedInStatus";
import { AxiosError } from "axios";

const Chat = lazy(() => import("./pages/chat/Chat"));
const CreateChatroom = lazy(() => import("./pages/chat/createChatroom/CreateChatroom"));
const CreateChatroomIndex = lazy(() => import("./pages/chat/createChatroom/CreateChatroomIndex"));
const ChatroomPreview = lazy(() => import("./pages/preview/ChatroomPreview"));
const AllChatrooms = lazy(() => import("./pages/chat/allChatrooms/AllChatrooms"));
const AllUserChats = lazy(() => import("./pages/chat/allUserChats/AllUserChats"));
const RecentlyVisitedChatrooms = lazy(() => import("./pages/chat/recentChatrooms/RecentChatrooms"));
const ChatroomUserPreviewWindow = lazy(
  () => import("./pages/chat/chatroomInformation/windows/ChatroomUserPreviewWindow")
);
const ChatroomInformation = lazy(
  () => import("./pages/chat/chatroomInformation/ChatroomInformation")
);
const UserChatInformation = lazy(
  () => import("./pages/chat/userChatInformation/UserChatInformation")
);
const ChatroomMetadataWindow = lazy(
  () => import("./pages/chat/chatroomInformation/windows/ChatroomMetadataWindow")
);
const ChatroomUsers = lazy(() => import("./pages/chat/chatroomInformation/windows/ChatroomUsers"));
const ChatroomUserSearch = lazy(
  () => import("./pages/chat/chatroomInformation/windows/ChatroomUserSearch")
);
const EnterChat = lazy(() => import("./pages/chat/enterChat/EnterChat"));
const EngageChat = lazy(() => import("./pages/chat/engageChat/EngageChat"));

const LoginPage = lazy(() => import("./pages/auth/LoginPage"));
const SignupPage = lazy(() => import("./pages/auth/SignupPage"));
const LogoutPage = lazy(() => import("./pages/auth/LogoutPage"));
const AnonymousUsername = lazy(() => import("./pages/auth/AnonymousUsername"));
const TwoFactorAuthWindow = lazy(() => import("./pages/profile/windows/TwoFactorAuthWindow"));

const BasicDetailsUpdateWindow = lazy(
  () => import("./pages/profile/windows/BasicDetailsUpdateWindow")
);
const DeleteAccountWindow = lazy(() => import("./pages/profile/windows/DeleteAccountWindow"));
const PasswordChangeWindow = lazy(() => import("./pages/profile/windows/PasswordChangeWindow"));
const EmailChangeWindow = lazy(() => import("./pages/profile/windows/EmailChangeWindow"));

const ProfilePreview = lazy(() => import("./pages/preview/ProfilePreview"));
const Friends = lazy(() => import("./pages/friends/Friends"));
const AllFriendsWindow = lazy(() => import("./pages/friends/AllFriendsWindow"));

const AdminIndex = lazy(() => import("./pages/admin/AdminIndex"));
const AdminManagerLayout = lazy(() => import("./pages/admin/AdminManagerLayout"));
const AdminUserListPage = lazy(() => import("./pages/admin/managerListPages/AdminUserListPage"));
const AdminUserView = lazy(() => import("./pages/admin/viewPages/AdminUserView"));
const AdminChatroomListPage = lazy(
  () => import("./pages/admin/managerListPages/AdminChatroomListPage")
);
const AdminChatroomView = lazy(() => import("./pages/admin/viewPages/AdminChatroomView"));
const AdminBlacklistedEmailListPage = lazy(
  () => import("./pages/admin/managerListPages/AdminBlacklistedEmailListPage")
);
const AdminBlacklistedEmailView = lazy(
  () => import("./pages/admin/viewPages/AdminBlacklistedEmailView")
);
const AdminBlacklistedTokenListPage = lazy(
  () => import("./pages/admin/managerListPages/AdminBlacklistedTokenListPage")
);
const AdminBlacklistedTokenView = lazy(
  () => import("./pages/admin/viewPages/AdminBlacklistedTokenView")
);

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

function Layout() {
  return (
    <>
      <Header />
      <main>
        <Suspense fallback={<FadingLineLoadingSignal />}>
          <Outlet />
        </Suspense>
      </main>
      <ScrollRestoration
        getKey={(location, matches) => {
          return location.pathname;
        }}
      />
    </>
  );
}

function AdminLayout() {
  return (
    <>
      <AdminHeader />
      <main>
        <Suspense fallback={<FadingLineLoadingSignal />}>
          <Outlet />
        </Suspense>
      </main>
      <ScrollRestoration
        getKey={(location, matches) => {
          return location.pathname;
        }}
      />
    </>
  );
}

const router = createBrowserRouter([
  // REGULAR ROUTES START
  {
    path: "/",
    element: <Layout />,
    // errorElement:
    children: [
      {
        index: true,
        element: (
          <AnimatedPageWrapper>
            <Home />
          </AnimatedPageWrapper>
        ),
      },

      // AUTH ROUTES START
      {
        path: "auth/",
        children: [
          {
            path: "login",
            element: <LoginPage adminLogin={false} />,
          },
          {
            path: "signup",
            element: <SignupPage />,
          },
          {
            path: "logout",
            element: <LogoutPage />,
          },
          {
            path: "suspended",
            element: <LogoutPage message={"Account suspended"} />,
          },

          // AUTH/ACOUNT ROUTES START
          {
            path: "account",
            element: <Profile />,
            children: [
              {
                index: true,
                element: <BasicDetailsUpdateWindow />,
              },
              {
                path: "email",
                element: <EmailChangeWindow />,
              },
              {
                path: "two-factor-auth",
                element: <TwoFactorAuthWindow />,
              },
              {
                path: "password",
                element: <PasswordChangeWindow />,
              },
              {
                path: "password/recovery",
                element: <PasswordChangeWindow />,
              },
              {
                path: "delete",
                element: <DeleteAccountWindow />,
              },
            ],
          },
          // AUTH/ACOUNT ROUTES END
        ],
      },
      // AUTH ROUTES END

      // PREVIEW ROUTES START
      {
        path: "preview/",
        children: [
          {
            path: "chatroom/:chatroomUID",
            element: <ChatroomPreview />,
          },
          {
            path: "user/:username",
            element: <ProfilePreview />,
          },
        ],
      },
      // PREVIEW ROUTES END

      // FRIEND ROUTES START
      {
        path: "friends/",
        element: <Friends />,
        children: [
          {
            index: true,
            element: <AllFriendsWindow friendshipCategory="friends" />,
          },
          {
            path: "requests",
            element: <AllFriendsWindow friendshipCategory="requests" />,
          },
          {
            path: "sent",
            element: <AllFriendsWindow friendshipCategory="sent" />,
          },
        ],
      },
      // FRIEND ROUTES END

      // CHAT ROUTES START
      {
        path: "chat/",
        element: <Chat />,
        children: [
          {
            index: true,
            element: (
              <AnimatedPageWrapper>
                <EnterChat />
              </AnimatedPageWrapper>
            ),
          },
          {
            path: "alias",
            element: (
              <AnimatedPageWrapper>
                <AnonymousUsername />
              </AnimatedPageWrapper>
            ),
          },
          {
            path: "rooms",
            element: (
              <AnimatedPageWrapper>
                <AllChatrooms />
              </AnimatedPageWrapper>
            ),
          },
          {
            path: "friends",
            element: (
              <AnimatedPageWrapper>
                <AllUserChats />
              </AnimatedPageWrapper>
            ),
          },
          {
            path: "recents",
            element: (
              <AnimatedPageWrapper>
                <RecentlyVisitedChatrooms />
              </AnimatedPageWrapper>
            ),
          },
          {
            path: "users/search/:searchString",
            element: (
              <AnimatedPageWrapper>
                <AllUserChats />
              </AnimatedPageWrapper>
            ),
          },
          {
            path: "rooms/search/:searchString",
            element: (
              <AnimatedPageWrapper>
                <AllChatrooms />
              </AnimatedPageWrapper>
            ),
          },

          // CHAT/CREATE CHATROOM ROUTES START
          {
            path: "create/",
            children: [
              {
                index: true,
                element: (
                  <AnimatedPageWrapper>
                    <CreateChatroomIndex />
                  </AnimatedPageWrapper>
                ),
              },
              {
                path: "public",
                element: (
                  <AnimatedPageWrapper>
                    <CreateChatroom chatroomType="public" />
                  </AnimatedPageWrapper>
                ),
              },
              {
                path: "private",
                element: (
                  <AnimatedPageWrapper>
                    <CreateChatroom chatroomType="private" />
                  </AnimatedPageWrapper>
                ),
              },
            ],
          },
          // CHAT/CREATE CHATROOM ROUTES END

          {
            path: "engage/:chatType/:chatID",
            element: <EngageChat />,
          },

          // CHAT/META ROUTES START /
          {
            path: "meta/",
            children: [
              // CHAT/META/CHATROOM ROUTES START
              {
                path: "chatroom/:chatroomUID/",
                element: <ChatroomInformation />,
                children: [
                  {
                    index: true,
                    element: <ChatroomMetadataWindow />,
                  },
                  {
                    path: "users",
                    element: <ChatroomUsers />,
                  },
                  {
                    path: "users/search/:q",
                    element: <ChatroomUserSearch />,
                  },
                  {
                    path: "users/preview/:username",
                    element: <ChatroomUserPreviewWindow />,
                  },
                ],
              },
              // CHAT/META/CHATROOM ROUTES END /

              // CHAT/META/USER ROUTE START
              {
                path: "user/:chatID",
                element: (
                  <AnimatedPageWrapper>
                    <UserChatInformation />
                  </AnimatedPageWrapper>
                ),
              },
              // CHAT/META/USER ROUTE END
            ],
          },
          // CHAT/META END
        ],
      },
      // CHAT ROUTES END

      // MISC ROUTES START
      {
        path: "guide",
        element: (
          <AnimatedPageWrapper>
            <Guide />
          </AnimatedPageWrapper>
        ),
      },
      // MISC ROUTES END
    ],
  },
  // REGULAR ROUTES END

  // ADMIN ROUTES START
  {
    path: "/admin/",
    element: <AdminLayout />,
    children: [
      {
        path: "auth/login",
        element: <LoginPage adminLogin />,
      },

      // ADMIN/MANAGE ROUTES START
      {
        path: "manage",
        element: <AdminManagerLayout />,
        children: [
          {
            index: true,
            element: (
              <AnimatedPageWrapper>
                <AdminIndex />
              </AnimatedPageWrapper>
            ),
          },

          // ADMIN/MANAGE/USER ROUTES START
          {
            path: "user",
            children: [
              {
                index: true,
                element: <AdminUserListPage />,
              },
              {
                path: "create",
                element: <AdminUserView />,
              },
              {
                path: "update/:userUID",
                element: <AdminUserView forUpdate />,
              },
            ],
          },
          // ADMIN/MANAGE/USER ROUTES END

          // ADMIN/MANAGE/CHATROOM ROUTES START
          {
            path: "chatroom",
            children: [
              {
                index: true,
                element: <AdminChatroomListPage />,
              },
              {
                path: "create",
                element: <AdminChatroomView />,
              },
              {
                path: "update/:chatroomUID",
                element: <AdminChatroomView forUpdate />,
              },
            ],
          },
          // ADMIN/MANAGE/CHATROOM ROUTES END

          // ADMIN/MANAGE/EMAIL-BLACKLIST ROUTES START
          {
            path: "email-blacklist",
            children: [
              {
                index: true,
                element: <AdminBlacklistedEmailListPage />,
              },
              {
                path: "create",
                element: <AdminBlacklistedEmailView />,
              },
              {
                path: "update/:id",
                element: <AdminBlacklistedEmailView forUpdate />,
              },
            ],
          },
          // ADMIN/MANAGE/EMAIL-BLACKLIST ROUTES END

          // ADMIN/MANAGE/TOKEN-BLACKLIST ROUTES START
          {
            path: "token-blacklist",
            children: [
              {
                index: true,
                element: <AdminBlacklistedTokenListPage />,
              },
              {
                path: "update/:id",
                element: <AdminBlacklistedTokenView />,
              },
            ],
          },
          // ADMIN/MANAGE/TOKEN-BLACKLIST ROUTES END
        ],
      },
      // ADMIN/MANAGE ROUTES END
    ],
  },
  // ADMIN ROUTES END
]);

export default function Router() {
  const refreshAccessToken = useRefresh();
  const { setUserIsLoggedIn } = useUserLoggedInStatus();
  useEffect(() => {
    refreshAccessToken().catch((err) => {
      if (err instanceof AxiosError && err.response?.status == 401) {
        setUserIsLoggedIn(false);
      }
    });
  }, []);

  return <RouterProvider router={router} />;
}
