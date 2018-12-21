import React, { Component } from 'react';
import { GET_ONE } from 'react-admin';

import dataProviderQuestion from '../services/dataProviderQuestion';
import { getQueryString } from '../utils/utils';
import Comments from '../models/comments';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import ListItem from '@material-ui/core/ListItem';
import Rater from 'react-rater';
import DefaultAvatar from '../assets/avatar.svg';

import './QuestionDetail.scss';

class QuestionDetail extends Component {
    constructor(props) {
        super(props);
        this.state = {
            comments: [],
            user: {},
            title: '',
            rating: 0,
            questionId: -1,
            userId: -1,
            category: ''
        }
    }
    componentDidMount() {
        
        const query = getQueryString();
        if (query.length === 5){
            const questionId = query[query.length-1];
            const userId = query[query.length-2];
            const category = query[query.length-3];
            this.setState({
                questionId,
                userId,
                category
            })
            this.getQuestionDetailData(questionId, userId, category);
        }
    }
    getQuestionDetailData = (questionId, userId, category)=> {
        dataProviderQuestion(GET_ONE, 'answer', { questionId:questionId, userId: userId, category: category })
        .then(response => {
            console.log('Question Detail Response:', response.data);
            const { ratings, reviewed_object: reviewObject={} } = response.data;
            const { comments, name, average } = ratings;
            this.setState({
                comments,
                user: reviewObject,
                title: name,
                rating: average
            })
        });
    }
    renderUser = (user) => {
        const { name="", avatar="" } = user;
        const { rating } = this.state;
        return (
            <div className="wrapperQuestionUser">
                <ListItem className="card">
                    <Avatar alt="User" src={avatar || DefaultAvatar} className="avatar" />
                    <div className="userName">{name}</div>
                    <Rater total={5} rating={rating} onRate={this.handleRate}/>
                </ListItem>
            </div>
        );
    }
    render(){
        const {comments, user, title} = this.state;
        return (
            <Card>
                <CardHeader title={`${title}`} />
                {this.renderUser(user)}
                <Comments comments={comments} />
            </Card>
        );
    }
}
export default QuestionDetail;
