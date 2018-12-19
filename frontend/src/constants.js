export const BASE_API = {
  BASE_URL: process.env.NODE_ENV === 'production' ? 'https://35.247.16.10' : '',
  TIMEOUT: 10000
};

export const API = {
  AUTH: '/auth',
  PEOPLE: '/people'
};

export const APP = {
  AUTH_TOKEN: 'auth_token'
};
