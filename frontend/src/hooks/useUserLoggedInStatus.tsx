export default function useUserLoggedInStatus() {
  const storageKey = "userLoggedIn";
  const userIsLoggedIn = localStorage.getItem(storageKey) != null;
  const setUserIsLoggedIn = (loggedIn: boolean) => {
    if (loggedIn) {
      localStorage.setItem(storageKey, "true");
    } else if (userIsLoggedIn) {
      localStorage.removeItem(storageKey);
    }
  };
  return {
    userIsLoggedIn: userIsLoggedIn,
    setUserIsLoggedIn: setUserIsLoggedIn,
  };
}
