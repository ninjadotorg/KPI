import { BASE_API} from '../constants';
import $http from './api';

import {
    GET_LIST,
    GET_ONE,
} from 'react-admin';
const apiUrl = BASE_API.BASE_URL;
const handlerUrl = (type, resource, params) => {
    let url = '';
    console.log('type:', type);
    switch (type) {
        case GET_LIST:
            const { page, perPage } = params.pagination;
            url = `${apiUrl}/${resource}/list?page=${page-1}&offset=${perPage}`;
            break;
        case GET_ONE:
            const { id } = params;
            url = `${apiUrl}/answer/view?type=${resource}&id=${id}`;
            break;
        default:
            break;
    }
    console.log('Url:', url);
    return url;
}
export default (type, resource, params) => {
    const url = handlerUrl(type, resource, params);
    const promise = $http({ url, method: 'get' });
    return promise.then((response) => {
        console.log('Response:', response);
        const { data } = response;
        switch (type) {
            
            case GET_LIST:
                const { perPage } = params.pagination;
                const { filter } = params;
                console.log('Filter:', filter);
                const { total } = data.data;
                let totalNumber = total * perPage;
                switch (resource) {
                    case 'people':
                        let { people } = data.data;
                        const { keywords, title } = filter;
                        if(keywords){
                            people = people.filter(item => item.keywords.toUpperCase().match(keywords.toUpperCase()));                       
                        }
                        if (title){
                            people = people.filter(item => item.title && item.title.toUpperCase().match(title.toUpperCase()));

                        }
                        if(keywords || title){
                            totalNumber = people.length;
                        }

                        return {data: people, total: totalNumber };
                    case 'project':
                        const { projects } = data.data;
                        return {data: projects, total: totalNumber } ;
                    case 'team':
                        const { teams } = data.data;
                        return {data: teams, total: totalNumber };
                    case 'company':
                        const companies = data.data;
                        return {data: companies, total: companies.length};
                    default:
                    break;
                }
                break;
            case GET_ONE: 
                const detail = {
                    ...data.data
                }
                return {data: detail};
                
            default:
                return { data: [], total: 123};
        }
    });
};