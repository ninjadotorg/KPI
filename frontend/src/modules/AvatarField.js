import React from 'react';
import Avatar from '@material-ui/core/Avatar';
import DefaultAvatar from '../assets/avatar.svg';


const AvatarField = ({ record = {}, source, classes }) => <Avatar alt="avatar" src={record[source] || DefaultAvatar} className={classes} />;
AvatarField.defaultProps = { label: 'Avatar' };

export default AvatarField;