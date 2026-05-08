import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

import "./ProfilePreview.css";
import "./Preview.css";

import {
  FriendshipStatus,
  FriendshipStatusResponseSchema,
  UserBasic,
  UserBasicSchema,
  UserPrivate,
  UserPrivateSchema,
} from "../../schemas/AuthSchema";
import useAxios from "../../hooks/useAxios";
import { Link } from "react-router-dom";
import FetchingLoader from "../../components/general/loaders/FetchingLoader";
import FetchErrorSignal from "../../components/general/modals/FetchErrorModal";
import useSetPageTitle from "../../hooks/useSetPageTitle";
import ConfirmActionDialogue from "../../components/general/modals/ConfirmActionDialogue";
import useHandleError from "../../hooks/useHandleError";
import { useAuthContext } from "../../contexts/AuthContext";

import { ReactComponent as ChatIcon } from "../../assets/icons/header-chat-icon.svg";
import { ReactComponent as UserNeutralIcon } from "../../assets/icons/user-neutral-icon.svg";
import { ReactComponent as UserAcceptIcon } from "../../assets/icons/friend-accept-icon.svg";
import { ReactComponent as UserRejectIcon } from "../../assets/icons/friend-reject-icon.svg";
import { ReactComponent as UserAddIcon } from "../../assets/icons/friend-request-icon.svg";
import { ReactComponent as UserRemoveIcon } from "../../assets/icons/friend-unfriend-icon.svg";
import APIResponsePopup from "../../components/general/modals/APIResponsePopup";
import { AnimatePresence } from "framer-motion";

function ProfilePreview() {
  const { username } = useParams();
  const { userDetails } = useAuthContext();

  const isLoggedInUser = username == userDetails?.username;

  // const isLoggedInUserBasic
  const axios = useAxios();

  const [profileDetails, setProfileDetails] = useState<UserBasic | UserPrivate | null>(null);
  const [friendshipStatus, setFriendshipStatus] = useState<FriendshipStatus>();

  const [isFetching, setIsFetching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const _ = useSetPageTitle(`user: ${username}`);

  const checkFriendship = async () => {
    if (!isLoggedInUser) {
      setIsFetching(true);
      axios
        .get(`/user/friends/check?username=${username}`)
        .then((res) => {
          const isFriend = FriendshipStatusResponseSchema.parse(res.data);
          setFriendshipStatus(isFriend.friendship_status);
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        })
        .finally(() => {
          setIsFetching(false);
        });
    }
  };

  const handleFriendshipButtonClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    const frienshipActionSuffix = e.currentTarget.value;
    const friendshipURLPrefix =
      (frienshipActionSuffix != "remove" && "/user/friends/requests") || "/user/friends";
    setIsFetching(true);
    axios
      .post(`${friendshipURLPrefix}/${frienshipActionSuffix}?id=${profileDetails?.uid}`, {})
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        checkFriendship();
      });
  };

  useEffect(() => {
    setIsFetching(true);
    const getUserInfoURL = (isLoggedInUser && "/user") || `/user?username=${username}`;
    const userParseSchema = (isLoggedInUser && UserPrivateSchema) || UserBasicSchema;
    axios
      .get(getUserInfoURL)
      .then((res) => {
        const validatedUserData = userParseSchema.parse(res.data);
        setProfileDetails(validatedUserData);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false);
      });
    checkFriendship();
  }, [isLoggedInUser]);

  return (
    <>
      <div className="page-container preview-page-container profile-preview-page-container">
        {(!profileDetails && isFetching && <FetchingLoader />) ||
          (!profileDetails && !isFetching && errorMessage && (
            <FetchErrorSignal errorMessage={errorMessage} />
          )) ||
          (profileDetails && (
            <>
              <div className="section">
                <div className="preview-intro">
                  <span className="title username">{profileDetails.username}</span>
                  <p className="info medium-spaced">{profileDetails.bio}</p>
                  <p className={`active-status ${(profileDetails.online && "positive") || ""}`}>
                    {(profileDetails.online && "online") || (
                      <>
                        last seen -<i>{profileDetails.last_seen}</i>
                      </>
                    )}
                  </p>
                </div>
              </div>

              <div className="section">
                <div className="preview-btns-container">
                  {(isLoggedInUser && <Link to={"/auth/account"}>my account</Link>) || (
                    <AllFriendshipButtons
                      friendshipStatus={friendshipStatus}
                      handleFriendshipButtonClick={handleFriendshipButtonClick}
                      username={profileDetails?.username}
                      disabled={isFetching}
                    />
                  )}
                </div>
              </div>
            </>
          ))}
      </div>
      <AnimatePresence>
        {errorMessage && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
      </AnimatePresence>
    </>
  );
}

export default ProfilePreview;

type FriendshipEndpointActions = "send" | "unsend" | "accept" | "reject" | "remove";
type FriendshipButtonProps = {
  frienshipActionSuffix: FriendshipEndpointActions;
  onClick: React.MouseEventHandler<HTMLButtonElement>;
  children: React.ReactNode;
  useExternal?: boolean;
  disabled: boolean | undefined;
};
function FriendshipButton({
  frienshipActionSuffix,
  onClick,
  children,
  useExternal,
  disabled,
}: FriendshipButtonProps) {
  return (
    <button
      className={`btn ${(!useExternal && "preview-btn") || ""} ${(children == "unfriend" && "danger") || (frienshipActionSuffix == "send" && "positive") || ""}`}
      value={frienshipActionSuffix}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
type AllFriendshipButtonsProps = {
  friendshipStatus: FriendshipStatus | undefined;
  handleFriendshipButtonClick: (e: React.MouseEvent<HTMLButtonElement>) => void;
  username: string;
  disabled: boolean | undefined;
};
function AllFriendshipButtons({
  friendshipStatus,
  handleFriendshipButtonClick,
  username,
  disabled,
}: AllFriendshipButtonsProps) {
  const [showConfirmDialogue, setShowConfirmDialogue] = useState(false);

  return (
    <>
      {(friendshipStatus == "friended" && (
        <>
          <FriendshipButton
            frienshipActionSuffix="remove"
            onClick={() => {
              setShowConfirmDialogue(true);
            }}
            disabled={disabled}
          >
            <div className="text-icon-container">
              <UserNeutralIcon className="icon" aria-label="user icon" />
              <span>friend</span>
            </div>
          </FriendshipButton>
          {showConfirmDialogue && (
            <ConfirmActionDialogue setModalDisplayState={setShowConfirmDialogue}>
              <p className="title">are you sure you want to unfriend {username}?</p>
              <FriendshipButton
                useExternal
                frienshipActionSuffix="remove"
                onClick={handleFriendshipButtonClick}
                disabled={disabled}
              >
                <div className="text-icon-container">
                  <UserRemoveIcon className="icon" aria-label="user remove icon" />
                  <span>unfriend</span>
                </div>
              </FriendshipButton>
            </ConfirmActionDialogue>
          )}
          <Link to={`/chat/engage/user/${username}`} className="preview-btn btn">
            <div className="text-icon-container">
              <ChatIcon className="icon" aria-label="speech bubble icon" />
              <span>chat</span>
            </div>
          </Link>
        </>
      )) ||
        (friendshipStatus == "unfriended" && (
          <FriendshipButton
            frienshipActionSuffix="send"
            onClick={handleFriendshipButtonClick}
            disabled={disabled}
          >
            <div className="text-icon-container">
              <UserAddIcon className="icon" aria-label="user add icon" />
              <span>add</span>
            </div>
          </FriendshipButton>
        )) ||
        (friendshipStatus == "requested" && (
          <FriendshipButton
            frienshipActionSuffix="unsend"
            onClick={handleFriendshipButtonClick}
            disabled={disabled}
          >
            <div className="text-icon-container">
              <UserRejectIcon className="icon" aria-label="user reject icon" />
              <span>cancel request</span>
            </div>
          </FriendshipButton>
        )) ||
        (friendshipStatus == "pending" && (
          <>
            <FriendshipButton
              frienshipActionSuffix="accept"
              onClick={handleFriendshipButtonClick}
              disabled={disabled}
            >
              <div className="text-icon-container">
                <UserAcceptIcon className="icon" aria-label="user accept icon" />
                <span>accept</span>
              </div>
            </FriendshipButton>
            <FriendshipButton
              frienshipActionSuffix="reject"
              onClick={handleFriendshipButtonClick}
              disabled={disabled}
            >
              <div className="text-icon-container">
                <UserRejectIcon className="icon" aria-label="user reject icon" />
                <span>reject</span>
              </div>
            </FriendshipButton>
          </>
        ))}
    </>
  );
}
