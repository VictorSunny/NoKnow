import React, { SetStateAction, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  AdminChatroomCreateSchema,
  Chatroom,
  ChatroomSchema,
  ChatroomUpdateSchema,
} from "../../schemas/ChatSchemas";
import useAxios from "../../hooks/useAxios";
import getFormEntries from "../../utilities/getFormEntries";
import FormErrorModal from "../general/modals/FormErrorModal";
import useHandleError from "../../hooks/useHandleError";
import { UUID } from "crypto";
import APIResponsePopup from "../general/fetchModals/APIResponsePopup";
import { AnimatePresence } from "framer-motion";
import { SetBoolState, SetOptionalTextState } from "../../types/types";

type Props = {
  chatroomUID: UUID;
  chatroomData?: Chatroom;
  errorMessage: string | undefined;
  isFetching: boolean;
  setChatroomData: React.Dispatch<SetStateAction<Chatroom | undefined>>;
  setErrorMessage: SetOptionalTextState;
  setIsFetching: SetBoolState;
  forUpdate?: boolean;
};
export default function AdminChatroomCompleteForm({
  chatroomUID,
  chatroomData,
  forUpdate,
  errorMessage,
  setChatroomData,
  setErrorMessage,
  setIsFetching,
  isFetching,
}: Props) {
  const navigate = useNavigate();
  const axios = useAxios({ forAdmin: true });
  const [errorPath, setErrorPath] = useState<string>();
  const [successMessage, setSuccessMessage] = useState<string>();

  const apiErrorHandler = useHandleError();

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);

    const chatroomUpdateFrom = getFormEntries(e.currentTarget);

    setIsFetching(true);
    try {
      if (forUpdate) {
        const chatroomUpdateData = ChatroomUpdateSchema.parse(chatroomUpdateFrom);
        const res = await axios.patch(`/admin/chat?id=${chatroomUID}`, chatroomUpdateData);
        const parsedChatroomData = ChatroomSchema.parse(res.data);
        setChatroomData(parsedChatroomData);
        setSuccessMessage("updated chatroom successfully.");
      } else {
        const chatroomCreateData = AdminChatroomCreateSchema.parse(chatroomUpdateFrom);
        const res = await axios.post(`/admin/chat`, chatroomCreateData);
        const parsedChatroomData = ChatroomSchema.parse(res.data);
        setChatroomData(parsedChatroomData);
        navigate(`/admin/manage/chatroom/update/${parsedChatroomData.uid}`);
      }
    } catch (err) {
      console.log(err);
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };

  return (
    <>
      <form
        name="chatroom-create-form"
        onSubmit={handleFormSubmit}
        className="spaced-out-form admin-form"
      >
        <div className="form-section form-main-content-container">
          {forUpdate && (
            <div className="input-container">
              <label htmlFor="uid">uid</label>
              <input
                name="uid"
                id="uid"
                key="uid"
                className={(errorPath == "uid" && "error") || "normal"}
                type="text"
                value={chatroomData?.uid}
                disabled
              />
            </div>
          )}
          <div className="input-container">
            <label htmlFor="room_type">type</label>
            <input
              name="room_type"
              id="room_type"
              key="room_type"
              className={(errorPath == "room_type" && "error") || "normal"}
              type="text"
              maxLength={64}
              placeholder='"private" or "public"'
              defaultValue={chatroomData?.room_type}
              disabled={forUpdate}
              required={!forUpdate}
            />
            {errorMessage && errorPath == "room_type" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
          <div className="input-container">
            <label htmlFor="name">name</label>
            <input
              name="name"
              id="name"
              key="name"
              className={(errorPath == "name" && "error") || "normal"}
              type="text"
              maxLength={64}
              defaultValue={chatroomData?.name}
              required={!forUpdate}
            />
            {errorMessage && errorPath == "name" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          <div className="input-container">
            <label htmlFor="about">about</label>
            <input
              name="about"
              id="about"
              key="about"
              className={(errorPath == "about" && "error") || "normal"}
              type="text"
              maxLength={255}
              defaultValue={chatroomData?.about}
              required={!forUpdate}
            />
            {errorMessage && errorPath == "about" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          <div className="input-container">
            <label htmlFor="original_creator_username">owner username</label>
            <input
              name="original_creator_username"
              id="original_creator_username"
              key="original_creator_username"
              className={(errorPath == "original_creator_username" && "error") || "normal"}
              type="text"
              maxLength={255}
              value={chatroomData?.original_creator_username}
              disabled={forUpdate}
            />
            {errorMessage && errorPath == "original_creator_username" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
          <div className="input-container">
            <label htmlFor="chatroom-password">password</label>
            <input
              name="password"
              id="password"
              key="password"
              className={(errorPath == "password" && "error") || "normal"}
              type="password"
              placeholder="enter password. 8 character combination."
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
            />
            {errorMessage && errorPath == "confirm_password" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
        </div>

        <div className="form-section submit-btn-container">
          <button
            type="submit"
            name="button"
            aria-label="submit otp form"
            className={`btn submit-btn ${(isFetching && "load") || ""}`}
            disabled={isFetching}
          >
            submit
          </button>
        </div>
      </form>
      <AnimatePresence>
        {errorMessage && !errorPath && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
        {successMessage && (
          <APIResponsePopup
            popupType="success"
            message={successMessage}
            setMessage={setSuccessMessage}
            successAction={() => {
              navigate("/admin/manage/chatroom");
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
