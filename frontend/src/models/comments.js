import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Avatar from '@material-ui/core/Avatar';
import List from '@material-ui/core/List';
import DefaultAvatar from '../assets/avatar.svg';
import Rater from 'react-rater';
import Button from '@material-ui/core/Button';
import UpVote from './upvote';
import DownVote from './downvote';
import "./comments.scss";


class CommentItem extends Component {

    static propTypes = {
        item: PropTypes.object.isRequired,
    }

    constructor(props) {
        super(props);
        this.state = {
            replyComment: '',
            error: null
        }
    }

    onChangeComment = (value)=> {
        this.setState({replyComment: value})

    }
    handleOnReplyComment = () => {
    }
    validate = () => {
        const { replyComment } = this.state;
        if( replyComment.length === 0) return false;
        return true;
    }
    submitReplyComment = () => {
        if(this.validate()){
            //Submit
        }else {
            this.setState({ error: "Please enter your reply"});
        }
    }
    renderError = () => {
        const {error} = this.state;
        if(!error) return null;
        return (
            <div className="errorField">*{error}</div>
        );
    }

    renderReplyComment = () => {
        return (
            <div className="wrapperReplyComment">
                <textarea 
                        className="textField"
                        multiline="true"
                        placeholder="Please reply your comment"
                        onChange={(e)=> this.onChangeComment(e.target.value)} 
                        type='text'/>
                {this.renderError()}
                <div className="wrapperReplySubmitBtn">
                    <Button variant="contained" color="primary" className="buttonSubmitReplyComment" onClick={this.submitReplyComment}>Submit</Button>
                </div>

            </div>
        );
    }
    renderReplyButton = () => {

    }
    renderLike = () => {
        return (
            <UpVote />
        );
    }
    renderDisLike = () => {
        return (
            <DownVote />
        );
    }
    renderLikeDislike = () => {
        return (
            <div className="wrapperLikeDislikeArea">
                {this.renderLike()}
                {this.renderDisLike()}
            </div>
        );
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
                    <div className="desc">{desc}
                </div>
                {this.renderLikeDislike()}
                {this.renderReplyComment()}
            </div>
        );
    }

    render() {
        const { item } = this.props;
        return (
            this.renderCommentItem(item)
        );
    }
}

class Comments extends Component {
    static propTypes = {
        comments: PropTypes.array.isRequired,
    }
    renderCommentItem = (item) => {
        return (
            <CommentItem item={item} />
        );
    }
    
    renderCommentList = (comments)=>{
        return (
            <List>
                {comments.map(item=> this.renderCommentItem(item))}
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