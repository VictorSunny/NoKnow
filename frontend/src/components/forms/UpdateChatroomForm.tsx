import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { Chatroom, ChatroomSchema, ChatroomUpdateSchema } from "../../schemas/ChatSchemas";
import useAxios from "../../hooks/useAxios";
import getFormEntries from "../../utilities/getFormEntries";
import FormErrorModal from "../general/modals/FormErrorModal";
import useHandleError from "../../hooks/useHandleError";
import SpinnerLoader from "../general/popups/loaders/SpinnerLoader";
import { AnimatePresence } from "framer-motion";
import { ChatroomPrivacyTypes } from "../../types/chatroomTypes";
import APIResponsePopup from "../general/popups/messagePopups/APIResponsePopup";
import FetchErrorSignal from "../general/popups/messagePopups/FetchErrorModal";

type Props = {
  chatroomType: ChatroomPrivacyTypes;
};
export default function UpdateChatroomForm({ chatroomType }: Props) {
  const axios = useAxios();

  const { chatroomUID } = useParams();

  const [isFetching, setIsFetching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const [errorPath, setErrorPath] = useState<string>();

  const [viewedChatroomDetails, setViewedChatroomDetails] = useState<Chatroom>();

  const apiErrorHandler = useHandleError();

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);

    const chatroomUpdateFrom = getFormEntries(e.currentTarget);

    setIsFetching(true);
    try {
      const chatroomUpdateData = ChatroomUpdateSchema.parse(chatroomUpdateFrom);
      const res = await axios.patch(`/chat?id=${chatroomUID}`, chatroomUpdateData);
      const parsedChatroomData = ChatroomSchema.parse(res.data);
      setViewedChatroomDetails(parsedChatroomData);
    } catch (err) {
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };

  useEffect(() => {
    setIsFetching(true);
    axios
      .get(`/admin/chat/${chatroomUID}`)
      .then((res) => {
        const parsedData = ChatroomSchema.parse(res.data);
        setViewedChatroomDetails(parsedData);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false);
      });
  }, []);

  return (
    <>
      {(viewedChatroomDetails && (
        <>
          <form
            name="chatroom-create-form"
            data-privacy={chatroomType}
            onSubmit={handleFormSubmit}
            className="compact-form"
          >
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
              </div>
              {errorMessage && errorPath == "name" && (
                <FormErrorModal errorMessage={errorMessage} />
              )}

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
                {errorMessage && errorPath == "about" && (
                  <FormErrorModal errorMessage={errorMessage} />
                )}
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
                      type="text"
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
                update
              </button>
            </div>
          </form>
          <AnimatePresence>
            {errorMessage && !errorPath && (
              <APIResponsePopup
                popupType="fail"
                message={errorMessage}
                setMessage={setErrorMessage}
              />
            )}
          </AnimatePresence>
        </>
      )) ||
        (isFetching && <SpinnerLoader />) ||
        (!isFetching && !viewedChatroomDetails && errorMessage && (
          <FetchErrorSignal errorMessage={errorMessage} />
        ))}
    </>
  );
}
