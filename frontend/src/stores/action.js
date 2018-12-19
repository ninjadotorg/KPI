export const selectPeople = (payload = {}) => {
    return {
        type: 'SELECTED_PEOPLE',
        payload
    }
}