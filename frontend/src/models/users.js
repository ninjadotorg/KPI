import React from 'react';
import { List, Datagrid, TextField, EmailField, Show, SimpleShowLayout } from 'react-admin';
import StarRatingField from '../modules/StarRatingField';
import FeedbackButton from '../modules/FeedbackButton';
import AvatarField from '../modules/AvatarField';
import ViewButton from '../modules/ViewButton';

export const UserList = props => (
    <List {...props} bulkActionButtons={false}>
        <Datagrid>
            {<AvatarField source="avatar" title="Avatar" />}
            <TextField source="name" />
            <TextField source="title" />
            <EmailField source="email" />
            <StarRatingField source="rating" />
            <FeedbackButton {...props}/>
            <ViewButton {...props}/>
        </Datagrid>
    </List>
);

