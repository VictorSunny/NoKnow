import { useAuthContext } from "../contexts/AuthContext";
import { useEffect } from "react";
import useAxios from "./useAxios";
import { UserCompleteSchema } from "../schemas/AuthSchema";
import { SetOptionalTextState } from "../types/types";
import useHandleError from "./useHandleError";

type Props = {
  setErrorMessage: SetOptionalTextState;
};
export default function useGetLoggedInUser({ setErrorMessage }: Props) {
  const axios = useAxios();

  const { userDetails, setUserDetails } = useAuthContext();
  const apiErrorHandler = useHandleError();

  useEffect(() => {
    const controller = new AbortController();
    axios
      .get("/user", { signal: controller.signal })
      .then((res) => {
        const userInfo = UserCompleteSchema.parse(res.data);
        setUserDetails(userInfo);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        controller.abort();
      });
  }, []);
  return userDetails;
}
