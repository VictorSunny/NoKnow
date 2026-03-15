import "./Guide.css";

export default function Guide() {
  return (
    <div className="page-container guide-page-container">
      <div className="section">
        <h1 className="title">NoKnow</h1>
        <p>A web app for easy animate messaging with, no signup required</p>
      </div>
      <div className="section">
        <h2 className="title">User</h2>
        <div className="sub-section">
          <h3>Types of users</h3>
          <p>
            User is either a guest, or signed in
            <br />
            Signed in users can choose to stay hidden and use anonymous usernames when engaging in
            chats
          </p>
          <p>
            On signup, user must provide a valid email which will be confirmed via OTP verification.
          </p>
          <p>User can activate two factor authentication for future logins to be OTP protected.</p>
        </div>
        <div className="sub-section">
          <h3>User features</h3>
          <ul>
            <h4>Guest user</h4>
            <li>create and engage public chatrooms only</li>
            <li>switch anonymous username at will</li>
          </ul>
          <ul>
            <h4>Signed in user</h4>
            <li>create and engage public chatrooms, as well as private chatrooms</li>
            <li>switch anonymous username at will</li>
            <li>send, recieve, accept, and reject friend requests</li>
            <li>view sent friend requests</li>
            <li>update bio information, email, username, and password</li>
            <li>recover account via email if password is forgotten</li>
            <li>choose stay hidden like a guest</li>
            <li>
              when hiding, all messages sent in private and public chatrooms will use set anonymous
              username except for friend chats.
            </li>
            <li>
              when hiding, user cannot be seen by fellow chatroom members except for moderators and
              chatroom creator.
            </li>
            <li>when hiding, user cannot be found by other users in search.</li>
          </ul>
        </div>
      </div>
      <div className="section">
        <h2 className="title">Chat</h2>
        <div className="sub-section">
          <h3>Types of chats</h3>
          <p>
            There are three type of chats namely; Public chatroom, private chatroom, and friend
            chat.
          </p>
          <p>Public chatrooms can be created and engaged with no signup required</p>
          <p>All users, anonymous and signed in, can create only 3 chatrooms per hour</p>
          <p>
            Broadcasts are sent to chat on events such as moderator assignment or demotion, user
            leaving or user becoming a member, user connecting or disconnecting from chat.
          </p>
          <p>
            Private chatroooms require user to be signed. To engaged a private chatroom, user must
            first join by providing the correct password for the chatroom.
          </p>
          <p>
            Friend chats require user to be signed in. user can only engage another user in friend
            chat if they are already friends.
          </p>
        </div>
        <div className="sub-section">
          <h3>Chatroom features</h3>
          <ul>
            <h4>Public chatroom</h4>
            <li>standard messaging.</li>
            <li>no login required to create and engage.</li>
            <li>members and non members can engage</li>
            <li>join and leave chatroom if signed in.</li>
            <li>free for all. users cannot be added or removed.</li>
            <li>creator cannot assign moderators.</li>
            <li>
              if logged in, user who creates chatroom automatically becomes creator and member
            </li>
          </ul>

          <ul>
            <h4>Private chatroom</h4>
            <li>standard messaging</li>
            <li>login required to create and engaged</li>
            <li>only members can engaged</li>
            <li>password required to join and create</li>
            <li>user who creates chatroom automatically becomes creator and member</li>
            <li>
              messages recording can be turned off (secret mode) for fully private messaging with no
              saving to database
            </li>
            <li>messages sent when in secret mode can only be viewed by users currently in chat</li>
            <li>
              messages recieved in secret mode are cleared upon refresh as they are not stored in
              database
            </li>
            <li>
              secret mode is turned off automatically after the last active user in chatroom
              disconnects
            </li>
            <li>unlimited number of members allowed to join and engage</li>
            <li>creator can make members into moderators</li>
            <li>only creator can remove moderators. a moderator cannot remove a moderator</li>
            <li>creator and moderators can add their friends to members</li>
            <li>creator and moderators can remove members</li>
            <li>chatroom can have a maximum of nine (9) moderators, plus creator (10 in total)</li>
            <li>
              removing a member automatically bans them from re-entering chatroom even with password
              provided until they are re-added/unbanned by a moderator or creator
            </li>
            <li>
              removed users are banned and restricted from joining chatroom unless re-added by a
              moderator or creator
            </li>
            <li>creator cannot leave chatroom without assigning a successor first</li>
            <li>only a moderator can be made into a successor</li>
            <li>
              unlike the creator, the successor is allowed to leave the chatroom. on leaving, they
              forfeit the role of successor
            </li>
            <li>
              if a successor is demoted from moderator to regular member, they automatically lose
              the title of successor
            </li>
            <li>
              when creator leaves chatroom, the successor automatically gets assigned the role of
              creator along with all privileges attached
            </li>
            <li>
              in chatroom information page, a member can view all fellow members except for hidden
              members
            </li>
            <li>hidden members can only be viewed by moderators and creator</li>
          </ul>

          <ul>
            <h4>Friend chat</h4>
            <li>standard messaging</li>
            <li>login required to engage</li>
            <li>user must be a friend to be engaged</li>
            <li>
              messages recording can be turned off (secret mode) for fully private messaging with no
              saving to database
            </li>
            <li>messages sent when in secret mode can only be viewed by users currently in chat</li>
            <li>
              messages recieved in secret mode are cleared upon refresh as they are not stored in
              database
            </li>
            <li>
              secret mode is turned off automatically after the last active user in chatroom
              disconnects
            </li>
            <li>only 2 members can engage. user and friend</li>
            <li>chat can be deleted</li>
            <li>deleting chat clears chat for both parties</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
