import { useEffect } from "react";
import { useLocation } from "react-router-dom";

export default function useResetStates(
  setStatesList: React.Dispatch<React.SetStateAction<boolean>>[]
) {
  const locator = useLocation();
  useEffect(() => {
    setStatesList.map((setState) => {
      setState(false);
    });
  }, [locator.pathname]);

  return "all required states have been reset";
}
