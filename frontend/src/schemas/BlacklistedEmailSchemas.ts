import z from "zod";
import dateFormatter from "../utilities/dateFormatter";

export const BlacklistedEmailSchema = z.object({
  id: z.int(),
  sub: z.string(),
  created_at: z.string().transform((string) => {
    return dateFormatter(string);
  }),
});

export const BlacklistedEmailListResponseSchema = z.object({
  emails: z.array(BlacklistedEmailSchema),
});

export const BlacklistedEmailCreateUpdateSchema = z.object({
  sub: z.email(),
});

export type BlacklistedEmail = z.infer<typeof BlacklistedEmailSchema>;
export type BlacklistedEmailListResponse = z.infer<typeof BlacklistedEmailListResponseSchema>;
export type BlacklistedEmailCreateUpdate = z.infer<typeof BlacklistedEmailCreateUpdateSchema>;
