import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Avatar from '@material-ui/core/Avatar';
import List from '@material-ui/core/List';
import DefaultAvatar from '../assets/avatar.svg';

class Comments extends Component {
    static propTypes = {
        comments: PropTypes.array.isRequired,
    }
    renderCommentItem=(item)=>{
        const { desc , id, user }  = item;
        let userName = "";
        let avatar = ""
        if(user){ 
            userName = user.name; 
            avatar = user.avatar;
        }
        return (
            <div className="wrapperCommentItem" key={id}>
                <div className="wrapperUser">
                    <Avatar alt="User" src={avatar || DefaultAvatar} className="avatar" />
                    <div className="name">{userName}:</div>
                </div>
                <div className="desc">{desc}</div>

            </div>
        );
    }
    renderCommentList = (comments)=>{
        return (
            <List>
                {comments.map(item=>this.renderCommentItem(item))}
            </List>
        );        
    }
    render(){
        const { comments } = this.props;
        return (
            <div className="wrapperCommentsList">
            {this.renderCommentList(comments)}
            </div>
        );
    }
}
export default Comments;