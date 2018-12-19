import { stringify } from 'query-string';
import { BASE_API, API} from '../constants';
import $http from './api';

import {
    GET_LIST,
    GET_ONE,
    CREATE,
} from 'react-admin';

const apiUrl = BASE_API.BASE_URL;
const handlerUrl = (type, resource, params) => {
    let url = '';
    console.log('type:', type);
    console.log('Params:', params);
    const { category, id } = params;
    switch (type) {
        case GET_LIST:
            url = `${apiUrl}/${resource}/list?type=${category}`;
            break;
        case GET_ONE:
            const { userId, questionId } = params;
            url = `${apiUrl}/${resource}/view-detail?question_id=${questionId}&id=${userId}&type=${category}`;
            break;
        case CREATE:
            url = `${apiUrl}/${resource}/submit?type=${category}&id=${id}`;
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
        case CREATE:
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
            case GET_LIST:
                const list = data.data;
                return {data: data.data, total: list.length};
            case GET_ONE:
                return { data: data.data}
            case CREATE: 
                return { data: data }
            default:
                return { data: [], total: 123};
        }
    });
};