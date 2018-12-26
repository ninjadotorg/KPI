import React from 'react';
import { List, Datagrid, TextField } from 'react-admin';
import StarRatingField from '../modules/StarRatingField';
import FeedbackButton from '../modules/FeedbackButton';
import ViewButton from '../modules/ViewButton';

export const TeamList = props => (
    <List {...props} bulkActionButtons={false}>
        <Datagrid>
            <TextField source="name" />
            <StarRatingField source="rating" />
            <FeedbackButton {...props}/>
            <ViewButton {...props}/>
        </Datagrid>
    </List>
);

