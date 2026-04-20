############
###### START - BUILDER STAGE ######
############
FROM node:24-slim AS builder

# set working directory
WORKDIR /builder_app    
# copy package.json and package-lock.json for installation of dependencies
# "COPY" command 1 to copy, "requirements.txt" command 2 to be copied, "." command 3 of target path to tansfer copy
COPY package.json .
COPY package-lock.json .
# install dependencies  
RUN npm ci
# copy the rest of the source code
COPY . .
# build distribution folder
RUN npm run build
############
###### END - BUILDER STAGE ######
############


############
###### START - FINAL STAGE ######
############
FROM nginx:1.30.0-alpine AS final
COPY --from=builder /builder_app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]
############
###### END - FINAL STAGE ######
############