import { KeyText } from "../types/types";
import { AdminUserSortBy, UserRoleChoices, UserSortBy } from "../types/userTypes";

export const userRoleOptions: UserRoleChoices[] = ["all", "user", "admin", "superuser"];

export const userSortByOptions: UserSortBy[] = ["date", "username"];
export const adminUserSortByOptions: AdminUserSortBy[] = ["name", "username", "date"];

export const userSortByTexts: KeyText<UserSortBy> = {
  date: "date",
  username: "username",
};

export const adminUserSortByTexts: KeyText<AdminUserSortBy> = {
  date: "date",
  name: "name",
  username: "username",
};
export const userRoleTexts: KeyText<UserRoleChoices> = {
  all: "all",
  user: "user",
  admin: "admin",
  superuser: "superuser",
};
