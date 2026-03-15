import { ChatroomType, ChatroomMemberRole, ChatroomSortBy } from "../types/chatroomTypes";
import { KeyText } from "../types/types";
import { UserRoleChoices } from "../types/userTypes";

export const chatroomSortByOptions: ChatroomSortBy[] = ["name", "activity", "popularity", "date"];
export const chatroomTypeOptions: ChatroomType[] = ["all", "public", "private"];
export const memberRoleOptions: ChatroomMemberRole[] = ["all", "moderator", "creator", "removed"];

export const chatroomSortByTexts: KeyText<ChatroomSortBy> = {
  activity: "activity",
  date: "date created",
  popularity: "popularity",
  name: "name",
};
export const chatroomTypeTexts: KeyText<ChatroomType> = {
  all: "all",
  private: "private",
  public: "public",
};

export const memberRoleTexts: KeyText<ChatroomMemberRole> = {
  all: "all",
  moderator: "moderator",
  creator: "creator",
  removed: "removed",
};
