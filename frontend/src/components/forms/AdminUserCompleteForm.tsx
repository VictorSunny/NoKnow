import useAxios from "../../hooks/useAxios";
import {
  AdminUserCreateFormSchema,
  AdminUserUpdateFormSchema,
  UserComplete,
  UserCompleteSchema,
} from "../../schemas/AuthSchema";
import getFormEntries from "../../utilities/getFormEntries";
import React, { SetStateAction, useState } from "react";
import FormErrorModal from "../general/modals/FormErrorModal";
import useHandleError from "../../hooks/useHandleError";
import { UUID } from "crypto";
import APIResponsePopup from "../general/fetchModals/APIResponsePopup";
import { AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { SetBoolState, SetOptionalTextState } from "../../types/types";

type Props = {
  userUID: UUID;
  errorMessage: string | undefined;
  isFetching: boolean;
  setUserData: React.Dispatch<SetStateAction<UserComplete | undefined>>;
  setErrorMessage: SetOptionalTextState;
  setIsFetching: SetBoolState;
  forUpdate?: boolean;
  userData?: UserComplete;
};
export default function AdminUserCompleteForm({
  userUID,
  userData,
  setUserData,
  errorMessage,
  setErrorMessage,
  setIsFetching,
  forUpdate,
}: Props) {
  const axios = useAxios({ forAdmin: true });
  const navigate = useNavigate();

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();

  const [userID, setUserID] = useState<string>();

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);

    const formData = getFormEntries(e.currentTarget);
    if (!formData) {
      setErrorMessage("please fill at least one field");
      return;
    }
    setIsFetching(true);
    try {
      if (forUpdate) {
        const parsedFormData = AdminUserUpdateFormSchema.parse(formData);
        console.log("parsed", parsedFormData);
        const res = await axios.patch(`/admin/user?id=${userUID}`, parsedFormData);
        const parsedUserData = UserCompleteSchema.parse(res.data);
        setUserData(parsedUserData);
        setUserID(parsedUserData.uid);
        setSuccessMessage("successfully updated user.");
      } else {
        const parsedFormData = AdminUserCreateFormSchema.parse(formData);
        console.log("creating", parsedFormData);
        const res = await axios.post(`/admin/user/`, parsedFormData);
        const parsedUserData = UserCompleteSchema.parse(res.data);
        setUserData(parsedUserData);
        setUserID(parsedUserData.uid);
        setSuccessMessage("successfully created user.");
      }
    } catch (err) {
      console.log(err);
      apiErrorHandler({ err, setErrorMessage, setErrorPath, forForm: true });
    } finally {
      setIsFetching(false);
    }
  };

  return (
    <>
      <form
        name="admin-user-details-change-form"
        onSubmit={handleFormSubmit}
        className="spaced-out-form"
      >
        <div className="form-section form-main-content-container">
          {forUpdate && userData && (
            <div className="input-container">
              <label htmlFor="uid">uid</label>
              <input
                name="uid"
                id="uid"
                key="uid"
                className={(errorPath == "uid" && "error") || "normal"}
                type="text"
                value={userData.uid}
                disabled
              />
            </div>
          )}
          <div className="input-container">
            <label htmlFor="first_name">first name</label>
            <input
              name="first_name"
              id="first_name"
              key="first_name"
              className={(errorPath == "first_name" && "error") || "normal"}
              type="text"
              placeholder="first name"
              defaultValue={userData?.first_name}
              required={!forUpdate}
            />
          </div>
          {errorMessage && errorPath == "first_name" && (
            <FormErrorModal errorMessage={errorMessage} />
          )}
          <div className="input-container">
            <label htmlFor="last_name">last name</label>
            <input
              name="last_name"
              id="last_name"
              key="last_name"
              className={(errorPath == "last_name" && "error") || "normal"}
              type="text"
              defaultValue={userData?.last_name}
              placeholder="last name"
              required={!forUpdate}
            />
          </div>
          {errorMessage && errorPath == "last_name" && (
            <FormErrorModal errorMessage={errorMessage} />
          )}
          <div className="input-container">
            <label htmlFor="username">username</label>
            <input
              name="username"
              id="username"
              key="username"
              className={(errorPath == "username" && "error") || "normal"}
              type="text"
              defaultValue={userData?.username}
              maxLength={25}
              placeholder="username"
              required={!forUpdate}
            />
          </div>
          <div className="input-container">
            <label htmlFor="role">role</label>
            <input
              name="role"
              id="role"
              key="role"
              className={(errorPath == "role" && "error") || "normal"}
              type="text"
              defaultValue={userData?.role}
              placeholder='"user" or "admin"'
              required={!forUpdate}
              disabled={userData?.role == "superuser"}
            />
            {errorMessage && errorPath == "role" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          {errorMessage && errorPath == "username" && (
            <FormErrorModal errorMessage={errorMessage} />
          )}
          <div className="input-container">
            <label htmlFor="email">email</label>
            <input
              name="email"
              id="email"
              key="email"
              className={(errorPath == "email" && "error") || "normal"}
              type="text"
              defaultValue={userData?.email}
              placeholder="email"
              required={!forUpdate}
            />
            {errorMessage && errorPath == "email" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          <div className="input-container">
            <label htmlFor="bio">bio</label>
            <textarea
              name="bio"
              id="bio"
              key="bio"
              className={(errorPath == "bio" && "error") || "normal"}
              defaultValue={userData?.bio}
              maxLength={255}
              placeholder="bio"
            />
            {errorMessage && errorPath == "bio" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          {userData && forUpdate && (
            <>
              <div className="input-container">
                <label htmlFor="is_hidden">hide</label>
                <input
                  name="is_hidden"
                  id="is_hidden"
                  key="is_hidden"
                  className={(errorPath == "is_hidden" && "error") || "normal"}
                  type="checkbox"
                  defaultChecked={userData.is_hidden}
                  disabled={userData?.role == "superuser"}
                />
                {errorMessage && errorPath == "is_hidden" && (
                  <FormErrorModal errorMessage={errorMessage} />
                )}
              </div>
              <div className="input-container">
                <label htmlFor="active">active</label>
                <input
                  name="active"
                  id="active"
                  key="active"
                  className={(errorPath == "active" && "error") || "normal"}
                  type="checkbox"
                  defaultChecked={userData.active}
                  disabled={userData?.role == "superuser"}
                />
                {errorMessage && errorPath == "active" && (
                  <FormErrorModal errorMessage={errorMessage} />
                )}
              </div>
              <div className="input-container">
                <label htmlFor="is_two_factor_authenticated">is_two_factor_authenticated</label>
                <input
                  name="is_two_factor_authenticated"
                  id="is_two_factor_authenticated"
                  key="is_two_factor_authenticated"
                  className={(errorPath == "is_two_factor_authenticated" && "error") || "normal"}
                  type="checkbox"
                  defaultChecked={userData.is_two_factor_authenticated}
                />
                {errorMessage && errorPath == "is_two_factor_authenticated" && (
                  <FormErrorModal errorMessage={errorMessage} />
                )}
              </div>
            </>
          )}
          <div className="input-container">
            <label htmlFor="password">password</label>
            <input
              name="password"
              id="password"
              key="password"
              className={(errorPath == "password" && "error") || "normal"}
              type="password"
              maxLength={25}
              placeholder="password"
              required={!forUpdate}
            />
            {errorMessage && errorPath == "password" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
          <div className="input-container">
            <label htmlFor="confirm_password">confirm password</label>
            <input
              name="confirm_password"
              id="confirm_password"
              key="confirm_password"
              className={(errorPath == "confirm_password" && "error") || "normal"}
              type="password"
              maxLength={25}
              placeholder="confirm_password"
              required={!forUpdate}
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
            aria-label="submit first_name change form"
            className="btn submit-btn"
          >
            submit
          </button>
        </div>
      </form>
      <AnimatePresence>
        {errorMessage && !errorPath && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
        {successMessage && userID && (
          <APIResponsePopup
            popupType="success"
            message={successMessage}
            setMessage={setSuccessMessage}
            successAction={() => {
              navigate(
                (forUpdate && "/admin/manage/user") || `/admin/manage/user/update/${userID}`
              );
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
