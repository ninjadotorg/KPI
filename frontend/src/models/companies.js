import React from 'react';
import { List, Datagrid, TextField } from 'react-admin';
import StarRatingField from '../modules/StarRatingField';
import FeedbackButton from '../modules/FeedbackButton';
import ViewButton from '../modules/ViewButton';

export const CompanyList = props => (
    <List {...props} bulkActionButtons={false} perPage={25}>
        <Datagrid>
            <TextField source="name" />
            <StarRatingField source="rating" />
            <FeedbackButton {...props}/>
            <ViewButton {...props}/>
        </Datagrid>
    </List>
);
