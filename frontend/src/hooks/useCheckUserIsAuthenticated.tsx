import { useAuthContext } from "../contexts/AuthContext";

export default function useCheckUserIsAuthenticated() {
  const { accessTokenData } = useAuthContext();
  const userIsLoggedIn = accessTokenData && true || false
  return userIsLoggedIn
}
