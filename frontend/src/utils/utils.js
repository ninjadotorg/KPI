export const getQueryString=() => {
    const querystring = window.location.hash.split('/');
    return querystring;
}