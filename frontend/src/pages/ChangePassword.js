import React from 'react';
import { UPDATE } from 'react-admin';
import Card from '@material-ui/core/Card';
import { Title } from 'react-admin';
import Avatar from '@material-ui/core/Avatar';
import ListItem from '@material-ui/core/ListItem';
import DefaultAvatar from '../assets/avatar.svg';
import { ListItemText } from '@material-ui/core';
import { APP } from '../constants';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';

import dataProviderPassword from '../services/dataProviderPassword';
import './ChangePassword.scss';

class ChangePassword extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            user: null,
            error: null,
            openDialog: false
        }
    }
    componentDidMount(){
        const userObject = this.getUser();
        this.setState({
            user: userObject
        });
         
    }
    getUser = () => {
        const avatar = localStorage.getItem(APP.AVATAR)
        const user = {
            email: localStorage.getItem(APP.USER_NAME),
            avatar: avatar !== "null" ? avatar : null
        }
        return user;
    }
    submitChangePassword = (params) => {
        dataProviderPassword(UPDATE, 'change-password', { data: params })
        .then(response => {
            const { status, message } = response.data;
            console.log('submitChangePassword', response);

            if (status){
                this.setState({
                    openDialog: true
                });
            }else {
                this.setState({
                    error:message
                });
            }
        });
    }
    validate = (currentPass, newPass) => {
        if (currentPass === null || currentPass.length === 0 || newPass === null || newPass.length === 0) return false;
        return true;
    }
    handleSubmit = (event) => {
        
        event.preventDefault();
        const currentPass = event.target.currentPass.value;
        const newPass = event.target.newPass.value;
        const isValid = this.validate(currentPass, newPass);

        if(isValid){
            const params = {
                current_password: currentPass,
                new_password: newPass
            }
            this.submitChangePassword(params);
        }else {
            this.setState({
                error:"Please put all fields"
            });
        }
        
    }
    handleLogout = () => {
        this.setState({
            openDialog: false
        })
        localStorage.removeItem(APP.USER_NAME);
        localStorage.removeItem(APP.AUTH_TOKEN);
        localStorage.removeItem(APP.AVATAR);
        this.props.history.push('/login');
    }
    renderErrorField = () => {
        const { error } = this.state;
        if(!error) return null;
        return (
            <div className="errorText">*{error}</div>
        )
    }
    renderUser = (user) => {
        if(!user) return null;
        const { avatar, email } = user;
        return (
            <ListItem className="card">
                <Avatar alt="User" src={avatar || DefaultAvatar} className="avatar" />
                <ListItemText>{email}</ListItemText>
            </ListItem>
        );
    }
    renderNotifyDialog = () => {
        const { openDialog } = this.state;
        return (
            
            <Dialog aria-labelledby="simple-dialog-title" open={openDialog}>
                <div className="wrapperDialog">
                    <div className="dialogTitle">Password Changed</div>
                    <div className="dialogContent">You changed new password successfully!</div>
                    <div className="dialogContent">Please back Login Page</div>
                    <Button 
                    style={{width: '150px', backgroundColor: 'blue', color: 'white', marginTop: '20px'}}
                    className="button" onClick={this.handleLogout}>OK</Button>
                </div>
            </Dialog>
        );
    }
    renderSubmitButton = ()=> {
        return (
            <Button 
            style={{ marginTop: '20px', marginBottom: '20px', backgroundColor: 'blue', color: 'white' }} 
            type="submit">Change Password</Button>
        );
    }
    
    renderPasswordForm = () => {
        const {user} = this.state;

        return (
            <Card>
                <Title title="Welcome to the administration" />
                {this.renderUser(user)}
                <div className="wrapperTextField">
                    <div className="title">Current Password:</div>
                    <TextField 
                    name="currentPass"
                    style={{ marginLeft: '20px', marginRight: '20px', width: '300px', marginBottom: '30px' }} 
                    variant="outlined" 
                    type="password"
                    />
                    <div className="title">New Password:</div>
                    <TextField 
                    name="newPass"
                    style={{ marginLeft: '20px', marginRight: '20px', width: '300px', marginBottom: '30px' }} 
                    variant="outlined" 
                    type="password"
                    />
                </div>
                
            </Card>


        );
    }
    render() {
        return (
            <form onSubmit={this.handleSubmit} noValidate>
                {this.renderPasswordForm()}
                {this.renderErrorField()}
                {this.renderSubmitButton()}
                {this.renderNotifyDialog()}
            </form>

        );
    }
}
export default ChangePassword;

