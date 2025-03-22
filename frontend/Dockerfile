#  node image
FROM node:20

# set working dir
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the entire frontend app
COPY . .

# Build the React app
RUN npm run build

# Expose the port React runs on
EXPOSE 3000

# Start the app
CMD ["npm", "start"]