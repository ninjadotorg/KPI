import React, { Component } from 'react';
import { Admin, Resource, ShowGuesser } from 'react-admin';
import { UserList } from './models/users';
import { ProjectList } from './models/projects';
import { TeamList } from './models/teams';
import { CompanyList } from './models/companies';

import authProvider from './services/authProvider';
import dataProvider from './services/dataProvider';
import hrReducer from './stores/reducer';
import routes from './routes';

import './App.css';

//import jsonServerProvider from 'ra-data-json-server';

//const dataProvider = jsonServerProvider('http://jsonplaceholder.typicode.com');
//const customDataProvider = dataProvider('http://jsonplaceholder.typicode.com');
const App = () => (
  <Admin 
  title="KPI"
  authProvider={authProvider} 
  dataProvider={dataProvider}
  customRoutes={routes}
  customReducers={hrReducer}
  >
      <Resource name="people" list={UserList}/>
      {/*<Resource name="project" list={ProjectList} />*/}
      <Resource name="team" list={TeamList} />
      <Resource name="company" list={CompanyList} />

  </Admin>
);
export default App;
