import { AUTH_LOGIN, AUTH_LOGOUT, AUTH_ERROR, AUTH_CHECK } from 'react-admin';
import { BASE_API, API, APP } from '../constants';
import $http from './api';

// import decodeJwt from 'jwt-decode';
export default (type, params) => {
    // called when the user attempts to log in
    console.log('Login Type:', type);
    if (type === AUTH_LOGIN) {
        const { username, password } = params;
        localStorage.setItem('username', username);
        
        const url = BASE_API.BASE_URL + API.AUTH;
        console.log('Url:', url);
        const data = {
            email:username,
            password
        }

        
        const authPromise = $http({ url, data, method: 'post' });
        return authPromise.then((response) => {
            if (response.status < 200 || response.status >= 300) {
                throw new Error(response.statusText);
            }
            const { data } = response;
            console.log('Login Data:', data);
            const { status } = data;
            
            if (status) {
                const { access_token: accessToken } = data.data;
                localStorage.setItem(APP.AUTH_TOKEN, accessToken);

                return Promise.resolve();

            }else {
                const { message } = data;
                localStorage.removeItem('username');
                console.log('Message:', message);
                return Promise.reject(message);
            }
            
        });   
        
            
    }
    // called when the user clicks on the logout button
    if (type === AUTH_LOGOUT) {
        localStorage.removeItem('username');
        localStorage.removeItem(APP.AUTH_TOKEN);
        return Promise.resolve();
    }
    // called when the API returns an error
    if (type === AUTH_ERROR) {
        const { status } = params;
        if (status === 401 || status === 403) {
            localStorage.removeItem('username');
            return Promise.reject();
        }
        return Promise.resolve();
    }
    // called when the user navigates to a new location
    if (type === AUTH_CHECK) {
        return localStorage.getItem(APP.AUTH_TOKEN)
            ? Promise.resolve()
            : Promise.reject();
    }
    return Promise.reject();
};