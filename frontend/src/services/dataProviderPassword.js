import { BASE_API, API} from '../constants';
import $http from './api';

import {
    UPDATE
} from 'react-admin';

const apiUrl = BASE_API.BASE_URL;
const handlerUrl = (type, resource, params) => {
    let url = '';
    console.log('type:', type);
    switch (type) {
        case UPDATE: 
            url = `${apiUrl}/${resource}`;
            break;
        default:
            break;
    }
    console.log('Url:', url);
    return url;
}
const handlerPromise = (type, url, params) => {
    let promise = null;
    console.log('type:', type);
    switch (type) {
        case UPDATE:
            const { data } = params;
            promise = $http({ url, data, method: 'post' });
            break;
        default:
            promise = $http({ url, method: 'get' });
            break;
    }
    return promise;
}
export default (type, resource, params) => {
    const url = handlerUrl(type, resource, params);
    const promise = handlerPromise(type, url, params);
    return promise.then((response) => {
        console.log('Response:', response);
        const { data } = response;
        switch (type) {
            case UPDATE:
                const detail = {
                    ...data
                }
            return {data: detail};

            default:
                return { data: [], total: 123};
        }
    });
};