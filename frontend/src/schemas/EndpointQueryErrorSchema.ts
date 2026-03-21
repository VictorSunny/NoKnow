import z from "zod";

const FormError = z.object({
  type: z.string(),
  loc: z.array(z.string()),
  msg: z.string(),
  input: z.any(),
});
const URLParamError = FormError.extend({
  ctx: z.object({
    error: z.string(),
  }),
});
const CustomHTTPErrorDetail = z.object({
  error: z.string(),
  message: z.string(),
});

export const PydanticValidationURLParamErrorSchema = z.object({
  detail: z.array(URLParamError),
});

export const PydanticValidationFormErrorSchema = z.object({
  detail: z.array(FormError),
});

export const APICustomHTTPErrorSchema = z.object({
  status: z.number(),
  detail: CustomHTTPErrorDetail,
  path: z.string(),
});
