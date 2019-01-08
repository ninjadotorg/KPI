import React, { Component } from 'react';
import { getQueryString } from '../utils/utils';
import qs from 'querystring';

import dataProviderQuestion from '../services/dataProviderQuestion';
import { GET_LIST } from 'react-admin';

import Reviews from '../components/Reviews';
import './WriteReview.scss';
import './StarRate.scss';


class WriteReview extends Component {
    constructor(props) {
        super(props);
        this.state = {
            questions:[],
            category: null,
            userId: -1,
            name: '',
            avatar: ''
        }
    }
    componentDidMount() {
        const query = getQueryString();
        if (query.length === 4){
            const category = query[query.length-2];
            const lastQuery = query[query.length-1].split('?');
            const queryId = lastQuery[1];
            const id = lastQuery[0];
            const params = qs.parse(queryId);
            console.log('Params:', params);
            this.setState({
                category,
                userId: id,
                name: params.name,
                avatar: params.avatar
            });
            this.getQuestionList(category);

        }

    }
    getQuestionList = (category)=> {
        dataProviderQuestion(GET_LIST, 'question', { category })
        .then(response => {
            this.setState({
                questions: response.data,
            })
        });
    }
    backAction = () => {
        this.props.history.go(-1);
    }

    handleCompleteReview = () => {
        const { category, userId, name, avatar } = this.state;
        const url = `/detail/${category}/${userId}?name=${name}&avatar=${encodeURIComponent(avatar)}`;
        this.props.history.push(url);
    }

    renderReviews = () => {
        const { questions, category, userId, name, avatar } = this.state;
        if (questions.length === 0) return null;

        return (
            <Reviews 
            category={category}
            userId={userId}
            name={name}
            avatar={avatar}
            questions={questions} 
            onCompleteReview={this.handleCompleteReview}
            />
        );
    }
   
    render() {
        
        return (
            <div className="wrapperReview">
                {/*this.renderCriteria()*/}
                {this.renderReviews()}
            </div>

        );
    }
}
export default WriteReview;