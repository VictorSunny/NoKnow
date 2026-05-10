import { useNavigationContext } from "../contexts/NavigationContext";
import { ReactNode, useLayoutEffect } from "react";

export default function useSetPageTitle(pageTitle: string | ReactNode | undefined) {
  const { setCurrentPageTitle } = useNavigationContext();

  const title = (typeof pageTitle == "string") && <p>{pageTitle}</p> || pageTitle
  console.log(typeof title)
  useLayoutEffect(() => {
    setCurrentPageTitle(title);
  }, []);
  return title;
}
