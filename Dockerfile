# Use Node 20 alpine for small footprint
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files first
COPY package.json package-lock.json* bun.lockb* ./

# Install dependencies
# If bun.lockb exists, we might want to use bun, but for broad compatibility we'll stick to npm/pnpm if available or just npm.
# Assuming standard npm project based on package-lock.json presence.
RUN npm install

# Copy source code
COPY . .

# Expose Vite default port
EXPOSE 8080

# Start development server
# --host 0.0.0.0 is required to expose it outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
