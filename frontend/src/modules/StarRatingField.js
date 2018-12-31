import React, {Component} from 'react';
import Rater from 'react-rater';
import { Link } from 'react-admin';
import { getDetaiLink } from '../utils/utils';


class StarRatingField extends Component {

    renderRatingField=(props)=> {
        const { record = {}} = props;
        return(
            <Rater total={5} rating={record.rating} interactive={false}/>    
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