import React from 'react';
import { List, Datagrid, TextInput, Filter } from 'react-admin';
import StarRatingField from '../modules/StarRatingField';
import FeedbackButton from '../modules/FeedbackButton';
import AvatarField from '../modules/AvatarField';
import LinkDetailField from '../modules/LinkDetailField';


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
        perPage={200}
        actions={<div />}
    >
        <Datagrid>
            <AvatarField source="avatar" title="Avatar" isDetailLink={true} />
            <LinkDetailField source="name" />
            <LinkDetailField source="title" />
            <StarRatingField source="rating_count" isDetailLink={true}/>
            <FeedbackButton {...props}/>
        </Datagrid>
    </List>
);

