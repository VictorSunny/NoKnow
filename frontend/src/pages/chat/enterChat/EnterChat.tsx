import { useAuthContext } from "../../../contexts/AuthContext";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../../components/general/popups/messagePopups/APIResponsePopup";

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
            {searchTypeOptions.map((searchOption, index) => {
              return (
                <button
                  key={index}
                  className={`${(searchOption == searchType && "active") || ""}`}
                  value={searchOption}
                  onClick={handleSearchButtonTypeClick}
                  type="button"
                >
                  {searchOption}
                </button>
              );
            })}
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
              joined rooms
            </Link>
            <Link className="link-text capitalize" to="/chat/friends">
              chat with friends
            </Link>
          </>
        )}
        <Link className="link-text capitalize" to="/chat/recents">
          recently engaged
        </Link>
        <Link className="link-text capitalize" to="/chat/create">
          create chatroom
        </Link>
      </div>
    </div>
  );
}
