import produce from 'immer';
import { selectPeople } from './action';

const initialState = {
    selectedPeople: {}
}
const hrReducer = (state = initialState, action) => {
    return produce(state, draft => {
        switch (action.type) {
            case selectPeople().type:
                draft.selectedPeople = action.payload;
                break;
            default:
                break;
        }
    });
}
export default hrReducer;