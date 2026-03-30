import { useAuthContext } from "../../contexts/AuthContext";
import useAxios from "../../hooks/useAxios";
import useGetLoggedInUser from "../../hooks/useGetLoggedInUser";
import { UserCompleteSchema, UserDetailsUpdateSchema } from "../../schemas/AuthSchema";
import getFormEntries from "../../utilities/getFormEntries";
import React, { useState } from "react";
import FormErrorModal from "../general/modals/FormErrorModal";
import useHandleError from "../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../general/modals/APIResponsePopup";

export default function BasicDetailsUpdateForm() {
  const [isFetching, setIsFetching] = useState(false);
  const { setUserDetails } = useAuthContext();
  const axios = useAxios();

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();

  const userDetails = useGetLoggedInUser({ setErrorMessage });

  const [formDisabled, setFormDisabled] = useState(true);

  const handleEditFormClick = () => {
    setFormDisabled((prev) => !prev);
    setErrorMessage(undefined);
    setErrorPath(undefined);
  };

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setErrorPath(undefined);
    const formData = getFormEntries(e.currentTarget);
    if (!formData) {
      setErrorMessage("please fill at least one field");
      return;
    }

    try {
      const parsedFormData = UserDetailsUpdateSchema.parse(formData);
      setIsFetching(true);
      const res = await axios.patch("/auth", parsedFormData);
      const parsedUserData = UserCompleteSchema.parse(res.data);
      setUserDetails(parsedUserData); 
      setFormDisabled(true);
      setSuccessMessage("user data successfully updated.");
    } catch (err) {
      apiErrorHandler({ err, setErrorMessage, setErrorPath });
    } finally {
      setIsFetching(false);
    }
  };
  return (
    <>
      <form name="user-details-change-form" onSubmit={handleFormSubmit} className="spaced-out-form">
        <div className="form-section utils-container">
          <button type="button" onClick={handleEditFormClick} className={`toggle-btn ${formDisabled && "active" || ""}`}>
            {formDisabled && "edit" || "disable"}
          </button>
        </div>
        <div className="form-section form-main-content-container">
          <div className="input-container">
            <label htmlFor="first_name">first name</label>
            <input
              name="first_name"
              id="first_name"
              key="first_name"
              className={(errorPath == "first_name" && "error") || "normal"}
              type="text"
              defaultValue={userDetails?.first_name}
              disabled={formDisabled}
            />
            {errorMessage && errorPath == "first_name" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
          <div className="input-container">
            <label htmlFor="last_name">last name</label>
            <input
              name="last_name"
              id="last_name"
              key="last_name"
              className={(errorPath == "last_name" && "error") || "normal"}
              type="text"
              defaultValue={userDetails?.last_name}
              placeholder="last name"
              disabled={formDisabled}
            />
            {errorMessage && errorPath == "last_name" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
          <div className="input-container">
            <label htmlFor="username">username</label>
            <input
              name="username"
              id="username"
              key="username"
              className={(errorPath == "username" && "error") || "normal"}
              type="text"
              defaultValue={userDetails?.username}
              maxLength={25}
              placeholder="username"
              disabled={formDisabled}
            />
            {errorMessage && errorPath == "username" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
          <div className="input-container">
            <label htmlFor="bio">bio</label>
            <textarea
              name="bio"
              id="bio"
              key="bio"
              className={(errorPath == "bio" && "error") || "normal"}
              defaultValue={userDetails?.bio}
              maxLength={255}
              placeholder="tell about yourself"
              disabled={formDisabled}
            />
            {errorMessage && errorPath == "bio" && <FormErrorModal errorMessage={errorMessage} />}
          </div>
          {userDetails &&
            <div className="input-container">
            <label htmlFor="is_hidden">hide in chatrooms</label>
            <input
              name="is_hidden"
              id="is_hidden"
              key="is_hidden"
              className={(errorPath == "is_hidden" && "error") || "normal"}
              type="checkbox"
              defaultChecked={userDetails.is_hidden}
              disabled={formDisabled}
              />
            {errorMessage && errorPath == "is_hidden" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
          }
        </div>
        <div className="form-section submit-btn-container">
          {!formDisabled && (
            <button
              type="submit"
              name="button"
              aria-label="submit first_name change form"
              className={`btn submit-btn ${(isFetching && "load") || ""}`}
              disabled={isFetching}
            >
              save changes
            </button>
          )}
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
          />
        )}
      </AnimatePresence>
    </>
  );
}
