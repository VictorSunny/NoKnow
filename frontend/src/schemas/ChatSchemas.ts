import { z } from "zod";
import { OptionalPasswordSchema } from "./GenericSchemas";
import dateFormatter from "../utilities/dateFormatter";
import getTimeAgo from "../utilities/getTimeAgo";
import messageDateFormatter from "../utilities/messageDateFormatter";
import { ChatroomPrivacyTypes } from "../types/chatroomTypes";
import { UserBasicSchema } from "./AuthSchema";
import removeFieldWithEmptyValues from "../utilities/removeFieldWithEmptyValues";
import { v4 as uuidv4 } from "uuid";

export const CHATROOM_PRIVACY_OPTIONS: ChatroomPrivacyTypes[] = ["public", "private"];

export const ChatroomSchema = z.object({
  uid: z.uuid(),
  name: z.string(),
  about: z.string(),
  created_at: z.string().transform((dateString) => {
    return dateFormatter(dateString);
  }),
  modified_at: z.string().transform((dateString) => {
    return getTimeAgo(dateString);
  }),
  original_creator_username: z.string(),
  room_type: z.enum(["private", "public", "personal"]),
  members_count: z.number(),
  record_messages: z.boolean(),
});
export const ChatroomExtendedSchema = ChatroomSchema.extend({
  active_visitors: z.number(),
  user_status: z.enum(["member", "moderator", "creator", "removed", "successor"]),
  user_is_hidden: z.boolean(),
});

export const ChatroomListResponseSchema = z.object({
  chatrooms: z.array(ChatroomSchema),
});
export const ChatroomExtendedListSchema = z.object({
  chatrooms: z.array(ChatroomExtendedSchema),
});

export const ChatroomCreateSchema = OptionalPasswordSchema.safeExtend({
  name: z.string(),
  about: z.string(),
  room_type: z.enum(["public", "private"]),
});

export const AdminChatroomCreateSchema = ChatroomCreateSchema.safeExtend({
  original_creator_username: z
    .string()
    .nonempty({ error: "please enter a valid username to assign ownership." }),
}).transform(removeFieldWithEmptyValues);

export const ChatroomUserSchema = UserBasicSchema.extend({
  user_status: z.enum(["creator", "moderator", "member", "successor", "removed"]),
});
export const ChatroomUserListSchema = z.object({
  users: z.array(ChatroomUserSchema),
});

export const MessageSchema = z.object({
  id: z.number().nullish(),
  uid: z
    .uuid()
    .nullish()
    .transform((str) => {
      return uuidv4();
    }),
  sender_username: z.string().nullish(),
  sender_uid: z.uuid().nullish(),
  content: z.string(),
  content_type: z.string(),
  type: z.enum(["announcement", "user", "alert", "info"]),
  recorded: z.boolean().nullish(),
  created_at: z
    .string()
    .nullish()
    .transform((dateString) => {
      if (dateString) {
        return messageDateFormatter(dateString);
      }
    }),
});

export const MessageListResponseSchema = z.object({
  room_type: z.string(),
  messages: z.array(MessageSchema),
});

export const ChatroomUpdateSchema = OptionalPasswordSchema.safeExtend({
  name: z.string().nullish(),
  about: z.string().max(255, "Description cannot be more than 255 characters").nullish(),
}).transform(removeFieldWithEmptyValues);

export type Chatroom = z.infer<typeof ChatroomSchema>;
export type ChatroomListResponse = z.infer<typeof ChatroomListResponseSchema>;
export type ChatroomCreate = z.infer<typeof ChatroomCreateSchema>;
export type Message = z.infer<typeof MessageSchema>;
export type MessageListResponse = z.infer<typeof MessageListResponseSchema>;
export type ChatroomExtended = z.infer<typeof ChatroomExtendedSchema>;
export type ChatroomExtendedList = z.infer<typeof ChatroomExtendedListSchema>;
export type ChatroomUser = z.infer<typeof ChatroomUserSchema>;
export type ChatroomUserList = z.infer<typeof ChatroomUserListSchema>;
