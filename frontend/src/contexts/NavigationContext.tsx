import React, { createContext, useContext, useState } from "react";
import { SetOptionalTextState, SingleChildrenProp } from "../types/types";

interface NavigationContextProps {
  currentPageTitle: string | undefined;
  setCurrentPageTitle: SetOptionalTextState;
}

const NavigationContext = createContext<NavigationContextProps | undefined>(undefined);

export const useNavigationContext = () => {
  const context = useContext(NavigationContext);
  if (!context) throw new Error("useNavigationContext must be used inside UserProvider");
  return context;
};

export default function NavigationProvider({ children }: SingleChildrenProp) {
  const [currentPageTitle, setCurrentPageTitle] = useState<string>();
  const value = {
    currentPageTitle,
    setCurrentPageTitle,
  };
  return <NavigationContext.Provider value={value}>{children}</NavigationContext.Provider>;
}
