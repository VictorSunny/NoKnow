type Routes = {
  [parentRoutes: string]: {
    [route: string]: {
      path: string;
      ariaLabel: string;
      text: string;
    };
  };
};

export const APP_ROUTES: Routes = {
  PROFILE_ROUTES: {
    dashboard: {
      path: "/profile",
      ariaLabel: "visit profile page",
      text: "profile",
    },
    emailChange: {
      path: "/profile/settings/change-email",
      ariaLabel: "visit profile page",
      text: "profile",
    },
  },
};

export const COMPONENT_ROUTES: Routes = {
  PROFILE_ROUTES: {
    dashboard: {
      path: "/profile",
      ariaLabel: "visit profile page",
      text: "profile",
    },
    emailChange: {
      path: "/profile/settings/change-email",
      ariaLabel: "visit profile page",
      text: "profile",
    },
  },
};
