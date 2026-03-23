import { z } from "zod";
import removeFieldWithEmptyValues from "../utilities/removeFieldWithEmptyValues";

const PASSWORD_CONSTRAINSTS = {
  min: 8,
  max: 32,
};

export const MessageResponseSchema = z.object({ message: z.string() });

export const PasswordSchema = z
  .string()
  .min(
    PASSWORD_CONSTRAINSTS.min,
    `password must be at least ${PASSWORD_CONSTRAINSTS.min} characters long`
  )
  .max(
    PASSWORD_CONSTRAINSTS.max,
    `password must be at less than ${PASSWORD_CONSTRAINSTS.max} characters long`
  )
  .regex(/[a-z]/, "password must contain at least one lowercase letter")
  .regex(/[A-Z]/, "password must contain at least one uppercase letter")
  .regex(/[0-9]/, "password must contain at least one number")
  .regex(/[^A-Za-z0-9]/, "password must contain at least one special letter");

export const ErrorResponseSchema = z.object({
  status: z.number(),
  message: z.string(),
  path: z.string(),
});

export const SinglePasswordSchema = z.object({
  password: z.string(),
});

export const ConfirmationTextSchema = z.object({
  text: z.string(),
});

export const PasswordInputSchema = z
  .object({
    password: PasswordSchema,
    confirm_password: z.string(),
  })
  .refine((data) => data.password == data.confirm_password, {
    message: "passwords do not match. check again",
    path: ["confirm_password"],
  });

export const OptionalPasswordSchema = z
  .object({
    password: z.string().nullish(),
    confirm_password: z.string().nullish(),
  })
  .superRefine((data, ctx) => {
    console.log("hye", typeof data.password)
    if (data.password && data.password.length < 8) {
      ctx.addIssue({
        path: ["password"],
        code: "custom",
        message: "password must be at least 8 characters long",
      });
    }
  })
  .superRefine((data, ctx) => {
    if (data.password && !/[a-z]/.test(data.password)) {
      ctx.addIssue({
        path: ["password"],
        code: "custom",
        message: "password must contain at least one lowercase letter",
      });
    }
  })
  .superRefine((data, ctx) => {
    if (data.password && !/[A-Z]/.test(data.password)) {
      ctx.addIssue({
        path: ["password"],
        code: "custom",
        message: "password must contain at least one uppercase letter",
      });
    }
  })
  .superRefine((data, ctx) => {
    if (data.password && !/[0-9]/.test(data.password)) {
      ctx.addIssue({
        path: ["password"],
        code: "custom",
        message: "password must contain at least one number",
      });
    }
  })
  .superRefine((data, ctx) => {
    if (data.password && !/[^A-Za-z0-9]/.test(data.password)) {
      ctx.addIssue({
        path: ["password"],
        code: "custom",
        message: "password must contain at least one special character",
      });
    }
  })
  .superRefine((data, ctx) => {
    if (data.password && data.password != data.confirm_password) {
      ctx.addIssue({
        path: ["confirm_password"],
        code: "custom",
        message: "passwords do not match. check again",
      });
    }
  })
  .superRefine((data, ctx) => {
    if (data.confirm_password && data.confirm_password != data.password) {
      ctx.addIssue({
        path: ["password"],
        code: "custom",
        message: "passwords do not match. check again",
      });
    }
  });

export const PasswordChangeSchema = z.object({
  password: PasswordSchema,
  confirm_password: z.string(),
  old_password: z.string().nullish(),
});

export type ConfirmationText = z.infer<typeof ConfirmationTextSchema>;
export type PasswordChange = z.infer<typeof PasswordChangeSchema>;
export type OptionalPassword = z.infer<typeof OptionalPasswordSchema>;
export type MessageResponse = z.infer<typeof MessageResponseSchema>;
