import React, {Component} from 'react';
import Avatar from '@material-ui/core/Avatar';
import { Link } from 'react-admin';
import DefaultAvatar from '../assets/avatar.svg';
import { getDetaiLink } from '../utils/utils';


class AvatarField extends Component {

    renderAvatar=(props)=> {
        const { record = {}, source, classes, basePath } = props;
        return(
            <Avatar alt="avatar" src={record[source] || DefaultAvatar} className={classes} onClick={()=>getDetaiLink({basePath, record})}/>
        );
    }
    render(){
        const {record, basePath, isDetailLink } = this.props;
        const url = getDetaiLink({basePath, record});
        if(!isDetailLink) return this.renderAvatar(this.props);
        return (
            <Link to={url}>{this.renderAvatar(this.props)}</Link>
        );
    }
}

AvatarField.defaultProps = { label: 'Avatar' };

export default AvatarField;