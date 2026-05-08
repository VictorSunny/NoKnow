import { useAuthContext } from "../../../contexts/AuthContext";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../../components/general/modals/APIResponsePopup";

import { ReactComponent as UserGroupTwo } from "../../../assets/icons/users-group-two-icon.svg";
import { ReactComponent as UserGroupThree } from "../../../assets/icons/users-group-chat.svg";

import { ReactComponent as RecentClockIcon } from "../../../assets/icons/clock-history-anti-clockwise-icon.svg";
import { ReactComponent as CreateChatIcon } from "../../../assets/icons/create-icon.svg";

import { ReactComponent as UserIcon } from "../../../assets/icons/user-neutral-icon.svg";
import { ReactComponent as UserGroupThreeIcon } from "../../../assets/icons/users-group-chat.svg";

type SearchType = "users" | "rooms";

export default function EnterChat() {
  const { userDetails } = useAuthContext();
  const navigate = useNavigate();
  const [searchType, setSearchType] = useState<SearchType>("rooms");
  const [errorMessage, setErrorMessage] = useState<string>();

  const _ = useSetPageTitle("enter chat");

  const handleSearchFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    if (!searchType) {
      setErrorMessage("select search type first");
      return;
    }
    const formData = new FormData(e.currentTarget);
    const searchQuery = String(formData.get("search-chatroom-name"));
    navigate(`/chat/${searchType}/search/${encodeURI(searchQuery)}`);
  };

  const handleSearchButtonTypeClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    const buttonValue = e.currentTarget.value as SearchType;
    setSearchType(buttonValue);
  };

  const searchTypeOptions: SearchType[] = ["users", "rooms"];

  return (
    <div className="page-container enter-chatroom-index-page">
      <div className="section util-form-container">
        <form className="util-form" onSubmit={handleSearchFormSubmit}>
          <input
            type="text"
            placeholder="what're you looking for?"
            name="search-chatroom-name"
            id="search-chatroom-name"
            className="search-input"
            required
          />
          <div className="btns-container">
            <button
              className={`${(searchType == "users" && "active") || ""}`}
              value="users"
              onClick={handleSearchButtonTypeClick}
              type="button"
            >
              <div className="text-icon-container">
                <UserIcon className="icon" aria-label="user icon" />
                <span>users</span>
              </div>
            </button>
            <button
              className={`${(searchType == "rooms" && "active") || ""}`}
              value="rooms"
              onClick={handleSearchButtonTypeClick}
              type="button"
            >
              <div className="text-icon-container">
                <UserGroupThreeIcon className="icon" aria-label="user icon" />
                <span>rooms</span>
              </div>
            </button>
          </div>
          <AnimatePresence>
            {errorMessage && (
              <APIResponsePopup
                popupType="fail"
                message={errorMessage}
                setMessage={setErrorMessage}
              />
            )}
          </AnimatePresence>
        </form>
      </div>

      <div className="section grow">
        {userDetails && (
          <>
            <Link className="link-text capitalize" to="/chat/rooms">
              <div className="text-icon-container">
                <UserGroupThree className="icon" aria-label="three users icon" />
                <span>joined chatrooms</span>
              </div>
            </Link>
            <Link className="link-text capitalize" to="/chat/friends">
              <div className="text-icon-container">
                <UserGroupTwo className="icon" aria-label="two users icon" />
                <span>chat with friends</span>
              </div>
            </Link>
          </>
        )}
        <Link className="link-text capitalize" to="/chat/recents">
          <div className="text-icon-container">
            <RecentClockIcon className="icon" aria-label="clock history anti-clockwise icon" />
            <span>recently visited</span>
          </div>
        </Link>
        <Link className="link-text capitalize" to="/chat/create">
          <div className="text-icon-container">
            <CreateChatIcon className="icon" aria-label="create edit icon" />
            <span>create chatroom</span>
          </div>
        </Link>
      </div>
    </div>
  );
}
