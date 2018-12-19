import axios from 'axios';
import { BASE_API, APP } from '../constants';

const $http = ({
  url, data = {}, qs, id = '', headers = {}, method = 'GET', ...rest
}) => {
  // start handle headers
  const parsedMethod = method.toLowerCase();
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  const completedHeaders = Object.assign({}, defaultHeaders);

  if (url.startsWith(BASE_API.BASE_URL)) {
    const token = localStorage.getItem(APP.AUTH_TOKEN);
    if (token) {
      completedHeaders.Authorization = `Bearer ${token}`;
    }
  }
  // end handle headers
  return axios({
    method: parsedMethod,
    timeout: BASE_API.TIMEOUT,
    headers: completedHeaders,
    url: id ? `${url}/${id}` : url, // trimEnd(`${url}/${id}`, '/'),
    params: qs,
    data,
    ...rest,
  });
};

export default $http;
