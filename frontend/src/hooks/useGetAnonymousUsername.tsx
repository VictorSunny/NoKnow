import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { anonymousUsernameLocalStorageKeyword } from "../constants/singleValues";

export default function useGetAnonymousUsername() {
  const anonymousUsername = sessionStorage.getItem(anonymousUsernameLocalStorageKeyword);
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => {
    if (!anonymousUsername) {
      navigate("/chat/alias", { state: { from: location }, replace: true });
    }
  }, []);
  return anonymousUsername;
}
