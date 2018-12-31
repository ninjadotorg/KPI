import React, {Component} from 'react';
import Rater from 'react-rater';
import { Link } from 'react-admin';
import { getDetaiLink } from '../utils/utils';
import ListItemText from '@material-ui/core/ListItemText';


class StarRatingField extends Component {

    renderRatingField=(props)=> {
        const { record = {}} = props;
        return(
            <div className="wrapperStarRatingField">
                <Rater total={5} rating={record.rating_count} interactive={false}/>    
                {record.rating_count > 0 && <ListItemText>({record.comment_count} reviews)</ListItemText>}
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