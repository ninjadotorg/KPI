export const BASE_API = {
  BASE_URL:
    process.env.NODE_ENV === 'production' ? 'https://kpi.autonomous.ai' : '',
  TIMEOUT: 10000
};

export const API = {
  AUTH: '/auth',
  PEOPLE: '/people'
};

export const APP = {
  AUTH_TOKEN: 'auth_token'
};
