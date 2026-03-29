import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { ChatroomCreateSchema, ChatroomSchema } from "../../schemas/ChatSchemas";
import useAxios from "../../hooks/useAxios";
import getFormEntries from "../../utilities/getFormEntries";
import FormErrorModal from "../general/modals/FormErrorModal";
import useGetAnonymousUsername from "../../hooks/useGetAnonymousUsername";
import useHandleError from "../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../general/modals/APIResponsePopup";

type Props = {
  chatroomType: "public" | "private";
};
export default function CreateChatroomForm({ chatroomType }: Props) {
  const anonymousUsername = useGetAnonymousUsername();
  const navigate = useNavigate();
  const axios = useAxios();

  const [chatroomUID, setChatroomUID] = useState<string>();
  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [isFetching, setIsFetching] = useState(false);
  const [errorPath, setErrorPath] = useState<string>();

  const apiErrorHandler = useHandleError();

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);
    setIsFetching(true);

    const chatroomCreateFrom = getFormEntries(e.currentTarget);

    try {
      const chatroomCreateData = ChatroomCreateSchema.parse(chatroomCreateFrom);
      const res = await axios.post(`/chat?&anon_username=${anonymousUsername}`, chatroomCreateData);
      const chatroomDetails = ChatroomSchema.parse(res.data);
      setChatroomUID(chatroomDetails.uid);
      setSuccessMessage("chatroom successfully created. taking you there now.");
    } catch (err) {
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };
  return (
    <>
      <form
        name="chatroom-create-form"
        data-privacy={chatroomType}
        onSubmit={handleFormSubmit}
        className="compact-form"
      >
        <div className="form-section-form-title-container">
          <p className="title">create {chatroomType} chatroom</p>
        </div>
        <div className="form-section form-main-content-container">
          <div className="input-container">
            <label htmlFor="name">name</label>
            <input
              name="name"
              id="name"
              key="name"
              className={(errorPath == "name" && "error") || "normal"}
              type="text"
              maxLength={64}
              placeholder="enter name for chat"
              required
            />
            {errorMessage && errorPath == "name" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          <div className="input-container">
            <label htmlFor="room_type">room type</label>
            <input
              name="room_type"
              id="room_type"
              key="room_type"
              className={(errorPath == "room_type" && "error") || "normal"}
              type="text"
              maxLength={64}
              placeholder="enter room_type for chat"
              value={chatroomType}
            />
            {errorMessage && errorPath == "room_type" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>

          <div className="input-container">
            <label htmlFor="about">description</label>
            <input
              name="about"
              id="about"
              key="about"
              className={(errorPath == "about" && "error") || "normal"}
              type="text"
              maxLength={255}
              placeholder="state your business"
              required
            />
            {errorMessage && errorPath == "about" && <FormErrorModal errorMessage={errorMessage} />}
          </div>

          {chatroomType == "private" && (
            <>
              <div className="input-container">
                <label htmlFor="chatroom-password">password</label>
                <input
                  name="password"
                  id="password"
                  key="password"
                  className={(errorPath == "password" && "error") || "normal"}
                  type="password"
                  placeholder="enter password. 8 character combination."
                  required
                />
                {errorMessage && errorPath == "password" && (
                  <FormErrorModal errorMessage={errorMessage} />
                )}
              </div>

              <div className="input-container">
                <label htmlFor="confirm_password">confirm</label>
                <input
                  name="confirm_password"
                  id="confirm_password"
                  className={(errorPath == "confirm_password" && "error") || "normal"}
                  key="confirm_password"
                  type="password"
                  placeholder="confirm password."
                  required
                />
                {errorMessage && errorPath == "confirm_password" && (
                  <FormErrorModal errorMessage={errorMessage} />
                )}
              </div>
            </>
          )}
        </div>
        <div className="form-section submit-btn-container">
          <button
            type="submit"
            name="button"
            aria-label="submit otp form"
            className={`btn submit-btn ${(isFetching && "load") || ""}`}
            disabled={isFetching}
          >
            create
          </button>
        </div>
      </form>
      <AnimatePresence>
        {errorMessage && !errorPath && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
        {successMessage && chatroomUID && (
          <APIResponsePopup
            popupType="success"
            message={successMessage}
            setMessage={setSuccessMessage}
            successAction={() => {
              navigate(`/chat/engage/chatroom/${chatroomUID}`);
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
