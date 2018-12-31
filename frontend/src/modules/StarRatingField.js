import React, {Component} from 'react';
import Rater from 'react-rater';
import { Link } from 'react-admin';
import { getDetaiLink } from '../utils/utils';
import ListItemText from '@material-ui/core/ListItemText';


class StarRatingField extends Component {

    renderRatingField=(props)=> {
        const { record = {}} = props;
        const reviewText = record.comment_count > 1 ? 'reviews' : 'review';
        return(
            <div className="wrapperStarRatingField">
                <Rater total={5} rating={record.rating_count} interactive={false}/>    
                {<ListItemText>({record.comment_count} {reviewText})</ListItemText>}
            </div>
        );
    }
    render(){
        const {record, basePath, isDetailLink } = this.props;
        const url = getDetaiLink({basePath, record});
        if(!isDetailLink) return this.renderRatingField(this.props);
        return (
            <Link to={url}>{this.renderRatingField(this.props)}</Link>
        );
    }
}
StarRatingField.defaultProps = { label: 'Reviews' };

export default StarRatingField;