import { z } from "zod";
import {
  OptionalPasswordSchema,
  PasswordInputSchema,
  PasswordSchema,
  SinglePasswordSchema,
} from "./GenericSchemas";
import dateFormatter from "../utilities/dateFormatter";
import getTimeAgo from "../utilities/getTimeAgo";
import removeFieldWithEmptyValues from "../utilities/removeFieldWithEmptyValues";
import { userRoleOptions } from "../constants/userOptions";

export const BooleanInput = z
  .enum(["on", "off"])
  .optional()
  .transform((str) => {
    if (str == "on") {
      return "true";
    }
    return "false";
  });

export const AccessTokenDataSchema = z.object({
  access_token: z.string(),
  token_type: z.string(),
});

export const EmailChangeSchema = SinglePasswordSchema.extend({
  email: z.email(),
});

export const TwoFactorAuthStatusResponseSchema = z.object({
  is_two_factor_authenticated: z.boolean(),
});
export const UserPrivacyStatus = z.object({
  is_hidden: z.boolean(),
});

export const UserBasicSchema = z.object({
  uid: z.uuid(),
  first_name: z.string(),
  last_name: z.string(),
  username: z.string(),
  bio: z.string(),
  online: z.boolean(),
  last_seen: z.string().transform((string) => {
    return getTimeAgo(string);
  }),
  joined: z.string().transform((string) => {
    return dateFormatter(string);
  }),
});
export const AdminUserBasicSchema = UserBasicSchema.extend({
  role: z.enum(["user", "admin", "superuser"])
})

export const UserPrivateSchema = UserBasicSchema.safeExtend({
  is_two_factor_authenticated: z.boolean(),
  is_hidden: z.boolean(),
  email: z.email(),
});

export const UserCompleteSchema = UserPrivateSchema.extend({
  role: z.enum(["user", "admin", "superuser"]),
  active: z.boolean(),
});

export const UserListResponseSchema = z.object({
  users: z.array(UserBasicSchema),
});

export const AdminUserListResponseSchema = z.object({
  users: z.array(AdminUserBasicSchema),
});

export const UserCreateSchema = PasswordInputSchema.safeExtend({
  first_name: z.string().nonempty(),
  last_name: z.string().nonempty(),
  username: z.string().nonempty(),
  bio: z.string().max(255, "bio cannot be more than 255 characters").nullish(),
  email: z.email().nonempty(),
}).transform(removeFieldWithEmptyValues)

export const UserLoginSchema = z.object({
  email: z.email(),
  password: z.string(),
});

export const TwoFactorAuthStatusSchema = z.object({
  is_two_factor_authenticated: z.boolean(),
});

export const OTPCodeSchema = z.object({
  otp: z.number(),
});
export const OTPJWTSchema = z.object({
  otp_jwt: z.string(),
});

export const FriendshipStatusResponseSchema = z.object({
  friendship_status: z.enum(["friended", "unfriended", "requested", "pending"]),
});

export const UserDetailsUpdateSchema = z.object({
  first_name: z.string().nullish(),
  last_name: z.string().nullish(),
  username: z.string().nullish(),
  bio: z.string().nullish(),
  is_hidden: z
    .enum(["on", "off"])
    .optional()
    .transform((str) => {
      if (str == "on") {
        return "true";
      }
      return "false";
    }),
}).transform(removeFieldWithEmptyValues)

export const AdminUserUpdateFormSchema = OptionalPasswordSchema.safeExtend({
  first_name: z.string().nullish(),
  last_name: z.string().nullish(),
  username: z.string().nullish(),
  bio: z.string().nullish(),
  is_hidden: BooleanInput,
  active: BooleanInput,
  is_two_factor_authenticated: BooleanInput,
  email: z.email().nullish(),
  role: z.string().nullish(),
}).transform(removeFieldWithEmptyValues)


export const AdminUserCreateFormSchema = PasswordInputSchema.safeExtend({
  first_name: z.string().nonempty(),
  last_name: z.string().nonempty(),
  username: z.string().nonempty(),
  bio: z.string().max(255, "bio cannot be more than 255 characters").nullish(),
  email: z.email().nonempty(),
  role: z.enum(["user", "admin"])
}).transform(removeFieldWithEmptyValues)

export type FriendshipStatus = "friended" | "unfriended" | "requested" | "pending";
export type UserBasic = z.infer<typeof UserBasicSchema>;
export type AdminUserBasic = z.infer<typeof AdminUserBasicSchema>;
export type UserComplete = z.infer<typeof UserCompleteSchema>;
export type UserPrivate = z.infer<typeof UserPrivateSchema>;
export type UserListResponse = z.infer<typeof UserListResponseSchema>;
export type AdminUserListResponse = z.infer<typeof AdminUserListResponseSchema>;
export type UserLogin = z.infer<typeof UserLoginSchema>;
export type UserCreate = z.infer<typeof UserCreateSchema>;
export type AccessTokenData = z.infer<typeof AccessTokenDataSchema>;
export type TwoFactorAuthStatus = z.infer<typeof TwoFactorAuthStatusSchema>;
export type OTPCode = z.infer<typeof OTPCodeSchema>;
export type FrienshipStatusResponse = z.infer<typeof FriendshipStatusResponseSchema>;
export type EmailChange = z.infer<typeof EmailChangeSchema>;
export type PasswordInput = z.infer<typeof PasswordInputSchema>;
export type TwoFactorAuthStatusResponse = z.infer<typeof TwoFactorAuthStatusResponseSchema>;
export type UserChatPrivacyStatusResponse = z.infer<typeof UserPrivacyStatus>;
