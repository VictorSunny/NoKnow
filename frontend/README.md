
# NOKNOW - ABOUT

NoKnow is a realtime chat web app where user's can join discussions anonymously in public chat rooms, openly in  password protected private chats, or a one-on-one discussion with a friend.
No signup is required for public chats, but joining private chat rooms and adding friends requires user signup.

## Tech stack

Typescript, React, HTML, CSS, Tanstack query


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`VITE_EMAILJS_SERVICE_ID`
`VITE_EMAILJS_PUBLIC_KEY`
`VITE_EMAILJS_TEMPLATE_ID`


## Installation

- Fork repository.

- Clone repository to your local machine.

- Run `npm install` to install all necessary dependencies.

- Create your .env file and set the necessary environment variables.

- Fin...

```bash
  npm run dev
```

## Project ordering
- Folders are heirarchical and nested in a consistent pattern across the project

- Components are stored within their own exclusive folders with a matching name. e.g "Button.tsx" inside "/button".
  Any css styling file name matches the target component's name, and is stored within the same folder.
  e.g ["Button.tsx", "Button.css"] inside "/button".

- In some cases, multiple *related* components may be stored within a folder with:
    (1) the name main focus component's name matching the folder name. e.g ["Form.tsx", "Button.tsx", "Popup.tsx",...] inside "/form"
    (2) all components within the folder serving similar purpose. e.g ["LoginForm.tsx", "CreateForm.tsx",...] inside "/forms"


- Page/Window components are stored within their respective folders with "PageComponent.tsx" and "/pageComponent" folder
  having matching names, Except in rare cases where such splitting would be unnecessary as pages serve similar purposes
  with differences only being in hooks used within.
### Project Structure
The frontend code is structured as follows:

* `frontend/src` - The main frontend code.
* `frontend/src/assets` - Static assets.
* `frontend/src/client` - The generated OpenAPI client.
* `frontend/src/components` -  The different components of the frontend.
* `frontend/src/hooks` - Custom hooks.
* `frontend/src/routes` - The different routes of the frontend which include the pages.
* `theme.tsx` - The Chakra UI custom theme.
    
## Authors

- [LinkedIn@victorsunny](https://www.linkedin.com/in/victor-sunny-6b06ba220)

- [Github@victorsunny](https://www.github.com/victorsunny/)

- [Discord](https://discordapp.com/users/1296969973155102761)

- [Portfolio](https://victorsunny.github.io)


## 🚀 About Me
Hello there, Victor here.

I'm a full-stack web developer with strong backend expertise, and i believe every problem that can be fixed, will be fixed if given enough effort & dedication; skills of which are in possession.

I am highly proficient in web/app developement using Python, Javascript, Typescript, HTML, CSS, Django, FastAPI, React, and other related technologies. Readily adopting and adapting to new/required technologies.
