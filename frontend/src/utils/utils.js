export const getQueryString=() => {
    const querystring = window.location.hash.split('/');
    return querystring;
}

export const getDetaiLink = ({basePath, record}) => {
    const encodeAvatar = encodeURIComponent(record.avatar || '');
    return (`/detail${basePath}/${record.id}?name=${record.name}&avatar=${encodeAvatar}`);

}