import { AccessTokenData, UserComplete } from "../schemas/AuthSchema";
import { useContext, createContext, useState } from "react";
import React from "react";
import { SingleChildrenProp } from "../types/types";

interface UserContextPropsType {
  userDetails: UserComplete | undefined;
  accessTokenData: AccessTokenData | undefined;
  setUserDetails: React.Dispatch<React.SetStateAction<UserComplete | undefined>>;
  setAccessTokenData: React.Dispatch<React.SetStateAction<AccessTokenData | undefined>>;
}

const UserContext = createContext<UserContextPropsType | undefined>(undefined);

export const useAuthContext = () => {
  const context = useContext(UserContext);
  if (!context) throw new Error("useAuthContext must be used inside UserProvider");
  return context;
};

export const UserProvider = ({ children }: SingleChildrenProp) => {
  ////    CONTEXT PROVIDER FOR SITE THEME

  const [userDetails, setUserDetails] = useState<UserComplete | undefined>();
  const [accessTokenData, setAccessTokenData] = useState<AccessTokenData | undefined>();

  const value = {
    userDetails,
    accessTokenData,
    setUserDetails,
    setAccessTokenData,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};
