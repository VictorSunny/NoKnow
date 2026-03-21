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
import LineLoadingSignal from "../../components/general/fetchModals/LineLoadingModal";
import FetchErrorSignal from "../../components/general/fetchModals/FetchErrorModal";
import useSetPageTitle from "../../hooks/useSetPageTitle";
import ConfirmActionDialogue from "../../components/general/confirmationModals/ConfirmActionDialogue";
import useHandleError from "../../hooks/useHandleError";
import { useAuthContext } from "../../contexts/AuthContext";

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

  const handleFriendshipButtonClick = async (e: React.MouseEvent<HTMLButtonElement>) => {
    const frienshipActionSuffix = e.currentTarget.value;
    const friendshipURLPrefix =
      (frienshipActionSuffix != "remove" && "/user/friends/requests") || "/user/friends";
    setIsFetching(true);
    await axios.post(
      `${friendshipURLPrefix}/${frienshipActionSuffix}?id=${profileDetails?.uid}`,
      {}
    );
    checkFriendship();
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
    <div className="page-container preview-page-container profile-preview-page-container">
      {(!profileDetails && isFetching && <LineLoadingSignal />) ||
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
                  />
                )}
              </div>
            </div>
          </>
        ))}
    </div>
  );
}

export default ProfilePreview;

type FriendshipEndpointActions = "send" | "unsend" | "accept" | "reject" | "remove";
type FriendshipButtonProps = {
  frienshipActionSuffix: FriendshipEndpointActions;
  onClick: React.MouseEventHandler<HTMLButtonElement>;
  children: React.ReactNode;
  useExternal?: boolean;
};
function FriendshipButton({
  frienshipActionSuffix,
  onClick,
  children,
  useExternal,
}: FriendshipButtonProps) {
  return (
    <button
      className={`btn ${(!useExternal && "preview-btn") || ""} ${(children == "unfriend" && "danger") || (frienshipActionSuffix == "send" && "positive") || ""}`}
      value={frienshipActionSuffix}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
type AllFriendshipButtonsProps = {
  friendshipStatus: FriendshipStatus | undefined;
  handleFriendshipButtonClick: (e: React.MouseEvent<HTMLButtonElement>) => Promise<void>;
  username: string;
};
function AllFriendshipButtons({
  friendshipStatus,
  handleFriendshipButtonClick,
  username,
}: AllFriendshipButtonsProps) {
  const [showConfirmDialogue, setShowConfirmDialogue] = useState(false);
  const handleConfirmUnfriendClick = () => {
    setShowConfirmDialogue(true);
  };
  return (
    <>
      {(friendshipStatus == "friended" && (
        <>
          <FriendshipButton frienshipActionSuffix="remove" onClick={handleConfirmUnfriendClick}>
            friend
          </FriendshipButton>
          {showConfirmDialogue && (
            <ConfirmActionDialogue setModalDisplayState={setShowConfirmDialogue}>
              <p className="title">are you sure you want to unfriend {username}?</p>
              <FriendshipButton
                useExternal
                frienshipActionSuffix="remove"
                onClick={handleConfirmUnfriendClick}
              >
                unfriend
              </FriendshipButton>
            </ConfirmActionDialogue>
          )}
          <Link to={`/chat/engage/user/${username}`} className="preview-btn btn">
            chat
          </Link>
        </>
      )) ||
        (friendshipStatus == "unfriended" && (
          <FriendshipButton frienshipActionSuffix="send" onClick={handleFriendshipButtonClick}>
            add
          </FriendshipButton>
        )) ||
        (friendshipStatus == "requested" && (
          <FriendshipButton frienshipActionSuffix="unsend" onClick={handleFriendshipButtonClick}>
            cancel request
          </FriendshipButton>
        )) ||
        (friendshipStatus == "pending" && (
          <>
            <FriendshipButton frienshipActionSuffix="accept" onClick={handleFriendshipButtonClick}>
              accept
            </FriendshipButton>
            <FriendshipButton frienshipActionSuffix="reject" onClick={handleFriendshipButtonClick}>
              reject
            </FriendshipButton>
          </>
        ))}
    </>
  );
}
