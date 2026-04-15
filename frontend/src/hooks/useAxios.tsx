import { useEffect } from "react";
import axios from "../api/api";
import { AxiosError, InternalAxiosRequestConfig } from "axios";
import { useAuthContext } from "../contexts/AuthContext";
import useRefresh from "./useRefresh";
import { useLocation, useNavigate } from "react-router-dom";
import { ACCOUNT_SUSPENDED_ERROR_CODE, NOT_ADMIN_ERROR_CODE } from "../constants/environment";
import useUserLoggedInStatus from "./useUserLoggedInStatus";

type Props = {
  forAdmin?: boolean;
};
function useAxios(options?: Props) {
  options = options || {};
  const refreshAccessToken = useRefresh();
  const { accessTokenData } = useAuthContext();
  const { setUserIsLoggedIn } = useUserLoggedInStatus();

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const requestInterceptor = axios.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (!config.headers.Authorization) {
          if (accessTokenData) {
            config.headers["Authorization"] =
              `${accessTokenData.token_type} ${accessTokenData.access_token}`;
          }
        }
        return config;
      },
      (err: AxiosError) => {
        return Promise.reject(err);
      }
    );

    const responseInterceptor = axios.interceptors.response.use(
      (res) => res,
      async (err) => {
        const failedRequest = err?.config;
        if (err?.response?.status == 401 && !failedRequest?.sent) {
          failedRequest.sent = true;
          try {
            const tokenData = await refreshAccessToken();
            if (tokenData) {
              failedRequest.headers["Authorization"] =
                `${tokenData.token_type} ${tokenData.access_token}`;
            }
          } catch (err) {
            setUserIsLoggedIn(false);
            navigate((options.forAdmin && "/admin/auth/login") || "/auth/login", {
              state: { from: location },
              replace: true,
            });
          }
          return axios(failedRequest);
        } else if (
          err?.response?.status == 403 &&
          err.response.data?.detail?.error == ACCOUNT_SUSPENDED_ERROR_CODE
        ) {
          navigate("/auth/suspended");
        } else if (
          err?.response?.status == 403 &&
          err.response.data?.detail?.error == NOT_ADMIN_ERROR_CODE
        ) {
          navigate("/admin/auth/login", { state: { from: location }, replace: true });
        } else {
          throw err;
        }
      }
    );

    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, [accessTokenData, refreshAccessToken]);

  return axios;
}

export default useAxios;
