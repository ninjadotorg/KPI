import React from 'react';
import { List, Datagrid, TextField, ReferenceField } from 'react-admin';

export const ProjectList = props => (
    <List {...props}>
        <Datagrid rowClick={(id, basePath)=>{
            const url = `/detail/project/${id}`;
            props.history.push(url);
            
        }}>
            <TextField source="id" />
            <TextField source="name" />
        </Datagrid>
    </List>
);
