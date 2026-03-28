import { SetStateAction, useEffect } from "react";
import { useAuthContext } from "../contexts/AuthContext";
import {
  AccessTokenDataSchema,
  UserCompleteSchema,
  AccessTokenData,
  UserComplete,
} from "../schemas/AuthSchema";
import useCreateAxiosInstance from "./useCreateAxiosInstance";
import useUserLoggedInStatus from "./useUserLoggedInStatus";

function useRefresh() {
  const { setAccessTokenData, setUserDetails } = useAuthContext();
  const { setUserIsLoggedIn } = useUserLoggedInStatus();
  const axiosInstance = useCreateAxiosInstance();

  const refreshAccessToken = async () => {
    const controller = new AbortController();
    const refreshResponse = await axiosInstance.get("/auth/token", { signal: controller.signal });
    const parsedRefreshResponse = AccessTokenDataSchema.parse(refreshResponse.data);
    setAccessTokenData(parsedRefreshResponse);
    setUserIsLoggedIn(true);
    refreshUserDetails({ accessTokenData: parsedRefreshResponse, setUserDetails: setUserDetails });
    controller.abort();
    return parsedRefreshResponse;
  };

  // return function for refreshing access token
  return refreshAccessToken;
}

export default useRefresh;

type RefreshUserDetailsProps = {
  setUserDetails: React.Dispatch<SetStateAction<UserComplete | undefined>>;
  accessTokenData: AccessTokenData;
};
export const refreshUserDetails = ({
  accessTokenData,
  setUserDetails,
}: RefreshUserDetailsProps) => {
  const axiosInstance = useCreateAxiosInstance();
  if (accessTokenData) {
    const controller = new AbortController();
    axiosInstance
      .get("/user", {
        signal: controller.signal,
        headers: {
          Authorization: `${accessTokenData.token_type} ${accessTokenData.access_token}`,
        },
      })
      .then((res) => {
        const parsedUserResponse = UserCompleteSchema.parse(res.data);
        setUserDetails(parsedUserResponse);
        return parsedUserResponse;
      })
      .finally(() => {
        controller.abort();
      });
  }
};
