import React from 'react';
import { connect } from 'react-redux';
import compose from 'recompose/compose';
import { withRouter } from 'react-router-dom';
import TeamIcon from '@material-ui/icons/People';
import PeopleIcon from '@material-ui/icons/Person';
import HomeIcon from '@material-ui/icons/Home';
import SettingsIcon from '@material-ui/icons/Settings';

import {
    translate,
    MenuItemLink,
    Responsive,
} from 'react-admin';

const items = [
    { name: 'people', title: 'People', icon: <PeopleIcon />},
    { name: 'team', title: 'Team', icon: <TeamIcon /> },
    { name: 'company', title: 'Company', icon: <HomeIcon /> },
];
const Menu = ({ onMenuClick, translate, logout }) => (
    <div className="wrapperMenu">
    <Responsive
            xsmall={null}
            medium={<MenuItemLink
                to="/change_password"
                primaryText="Change Password"
                leftIcon={<SettingsIcon />}
                onClick={onMenuClick}
            />}
        />
    {items.map(item => (
        <MenuItemLink
            key={item.name}
            to={`/${item.name}`}
            primaryText={item.title}
            leftIcon={item.icon}
            onClick={onMenuClick}
        />
    ))}
    </div>
);

const enhance = compose(
    withRouter,
    connect(
        state => ({
            theme: state.theme,
            locale: state.i18n.locale,
        }),
        {}
    ),
    translate
);

export default enhance(Menu);
