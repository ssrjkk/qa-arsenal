FROM mcr.microsoft.com/playwright:v1.42.0-bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
RUN npm ci

COPY . .

RUN npx playwright install --with-deps

ENV NODE_ENV=production
ENV CI=true

CMD ["npm", "test"]