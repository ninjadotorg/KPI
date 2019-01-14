import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Avatar from '@material-ui/core/Avatar';
import List from '@material-ui/core/List';
import DefaultAvatar from '../assets/avatar.svg';
import Rater from 'react-rater';

class Comments extends Component {
    static propTypes = {
        comments: PropTypes.array.isRequired,
    }
    renderCommentItem=(item)=>{
        const { desc , id, user, point }  = item;
        let userName = "";
        let avatar = ""
        if(user){ 
            userName = user.name; 
            avatar = user.avatar;
        }
        return (
            <div className="wrapperCommentItem" key={id}>
                <div className="wrapperUser">
                    <Avatar alt="User" src={DefaultAvatar} className="avatar" />
                    {/*<div className="name">{userName}</div>*/}
                    <div className="ratedText">rated</div>
                    {<div className="commentRater">
                        <Rater total={5} rating={point} interactive={false}/>
                    </div>}
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