import React from 'react';
import { List, Datagrid, TextField, EmailField, TextInput, Filter } from 'react-admin';
import StarRatingField from '../modules/StarRatingField';
import FeedbackButton from '../modules/FeedbackButton';
import AvatarField from '../modules/AvatarField';
import ViewButton from '../modules/ViewButton';

const UserFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="name" resettable placeholder="Name" alwaysOn/>
    </Filter>
);

export const UserList = props => (
    <List {...props} bulkActionButtons={false} filters={<UserFilter />}>
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

