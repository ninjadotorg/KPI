import React from 'react';
import { List, Datagrid } from 'react-admin';
import StarRatingField from '../modules/StarRatingField';
import FeedbackButton from '../modules/FeedbackButton';
import LinkDetailField from '../modules/LinkDetailField';

export const TeamList = props => (
    <List {...props} 
        bulkActionButtons={false} 
        perPage={25}
        actions={<div />}
    >
        <Datagrid >
            <LinkDetailField source="name" />
            <StarRatingField source="rating" isDetailLink={true} />
            <FeedbackButton {...props}/>
        </Datagrid>
    </List>
);

