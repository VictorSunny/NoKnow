import { useNavigationContext } from "../contexts/NavigationContext";
import { useEffect, useLayoutEffect } from "react";

export default function useSetPageTitle(pageTitle: string | undefined) {
  const { currentPageTitle, setCurrentPageTitle } = useNavigationContext();
  useLayoutEffect(() => {
    setCurrentPageTitle(pageTitle);
  }, []);
  return currentPageTitle;
}
