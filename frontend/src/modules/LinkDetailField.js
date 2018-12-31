import React, {Component} from 'react';
import { Link } from 'react-admin';
import ListItemText from '@material-ui/core/ListItemText';
import { getDetaiLink } from '../utils/utils';


class LinkDetailField extends Component {
   
    render(){
        const { source, record, basePath } = this.props;
        const url = getDetaiLink({basePath, record});
        return (
            <Link to={url}>
                <ListItemText>{record[source]}</ListItemText>
            </Link>
        );
    }
}

export default LinkDetailField;