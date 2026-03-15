import z from "zod";
import dateFormatter from "../utilities/dateFormatter";

export const BlacklistedTokenSchema = z.object({
  id: z.int(),
  jti: z.uuid(),
  exp: z.string().transform((string) => {
    return dateFormatter(string);
  }),
  created_at: z.string().transform((string) => {
    return dateFormatter(string);
  }),
  expired: z.boolean(),
});

export const BlacklistedTokenListResponseSchema = z.object({
  tokens: z.array(BlacklistedTokenSchema),
});

export type BlacklistedToken = z.infer<typeof BlacklistedTokenSchema>;
export type BlacklistedTokenListResponse = z.infer<typeof BlacklistedTokenListResponseSchema>;
