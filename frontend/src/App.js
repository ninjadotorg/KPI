import React, { Component } from 'react';
import { Admin, Resource, ShowGuesser } from 'react-admin';
import { UserList } from './models/users';
import { TeamList } from './models/teams';
import { CompanyList } from './models/companies';

import authProvider from './services/authProvider';
import dataProvider from './services/dataProvider';
import hrReducer from './stores/reducer';
import routes from './routes';
import Menu from './Menu';

import './App.css';
const App = () => (
  <Admin 
  title="KPI"
  authProvider={authProvider} 
  dataProvider={dataProvider}
  customRoutes={routes}
  customReducers={hrReducer}
  //dashboard={ChangePassword}
  menu={Menu}
  >
      <Resource name="people" list={UserList}/>
      <Resource name="team" list={TeamList} />
      <Resource name="company" list={CompanyList} />

  </Admin>
);
export default App;
