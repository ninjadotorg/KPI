import React from 'react';
import { List, Datagrid, TextField, TextInput, Filter, CardActions } from 'react-admin';
import StarRatingField from '../modules/StarRatingField';
import FeedbackButton from '../modules/FeedbackButton';
import AvatarField from '../modules/AvatarField';
import ViewButton from '../modules/ViewButton';


const UserFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="keywords" resettable placeholder="Name" alwaysOn/>
        <TextInput label="Title" source="title" resettable  alwaysOn />

    </Filter>
);

export const UserList = props => (
    <List {...props} 
        bulkActionButtons={false} 
        filters={<UserFilter />} 
        perPage={25}
        actions={<CardActions />}
    >
        <Datagrid>
            {<AvatarField source="avatar" title="Avatar" />}
            <TextField source="name" />
            <TextField source="title" />
            <StarRatingField source="rating" />
            <FeedbackButton {...props}/>
            <ViewButton {...props}/>
        </Datagrid>
    </List>
);

