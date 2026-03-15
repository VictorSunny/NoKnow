import { AxiosError } from "axios";
import React, { SetStateAction, useEffect } from "react";
import { ZodError } from "zod";
import {
  APICustomHTTPErrorSchema,
  PydanticValidationFormErrorSchema,
  PydanticValidationURLParamErrorSchema,
} from "../schemas/EndpointQueryErrorSchema";
import { SetOptionalTextState } from "../types/types";

type FunctionProps = {
  err: any;
  forForm?: boolean;
  setErrorMessage: SetOptionalTextState;
  setErrorPath?: SetOptionalTextState;
};
export default function useHandleError() {
  const apiErrorHandler = ({ err, setErrorPath, setErrorMessage }: FunctionProps) => {
    if (err instanceof ZodError) {
      const errorPath = err.issues[0]?.path[0]?.toString();
      const errorMessage = err.issues[0]?.message;

      setErrorPath && setErrorPath(errorPath);
      setErrorMessage(errorMessage);

      const errorElement = document.getElementById(errorPath);
      if (errorElement) {
        errorElement.scrollIntoView({ behavior: "smooth", block: "center" });
        errorElement instanceof HTMLInputElement && errorElement.focus();
      }
    } else if (err instanceof AxiosError) {
      ////// if error has response
      if (err.response) {
        const isCustomHTTPError = APICustomHTTPErrorSchema.safeParse(err.response.data);
        const isFormError = PydanticValidationFormErrorSchema.safeParse(err.response.data);
        const isURLParamError = PydanticValidationURLParamErrorSchema.safeParse(err.response.data);
        
        if (isCustomHTTPError.success) {
          setErrorMessage(isCustomHTTPError.data.detail.message)
        } else if (isFormError.success) {
          // set error message and error path if err is an instance of Pydantic BaseModel error
          setErrorMessage(isFormError.data.detail[0]?.msg);
          const errorPath = isFormError.data.detail[0]?.loc[1];
          if (errorPath) {
            setErrorPath && setErrorPath(errorPath);
            const errorElement = document.getElementById(errorPath);
            if (errorElement) {
              errorElement.scrollIntoView({ behavior: "smooth", block: "center" });
              errorElement instanceof HTMLInputElement && errorElement.focus();
            }
          }
        } else if (isURLParamError.success) {
          // set error message and error path if err is an instance of Pydantic URL query parameter error
          setErrorMessage(isURLParamError.data.detail[0]?.msg);
          const errorPath = isURLParamError.data.detail[0]?.loc[1];
          if (errorPath) {
            setErrorPath && setErrorPath(errorPath);
            const errorElement = document.getElementById(errorPath);
            if (errorElement) {
              errorElement.scrollIntoView({ behavior: "smooth", block: "center" });
              errorElement instanceof HTMLInputElement && errorElement.focus();
            }
          }
        } else if (err.response.data.error) {
          // set error message if err contains error value
          setErrorMessage(err.response.data.error);
        } else if (err.response.data.message) {
          // set error message if err contains message value
          setErrorMessage(err.response.data.message);
        } else if (err.response.data.details?.msg) {
          // set error message if err contains details.msg value
          setErrorMessage(err.response.data.details.msg);
        }
        ///// if error has no response, set error to just error message
      } else if (err.message) {
        setErrorMessage(err.message);
      }
    } else {
      ///// final fallback
      //  if error is unexpected
      setErrorMessage("An unexpected error occured.");
    }
  };
  return apiErrorHandler;
}
