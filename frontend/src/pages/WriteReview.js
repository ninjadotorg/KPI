import React, { Component } from 'react';
import { getQueryString } from '../utils/utils';
import qs from 'querystring';

import Criteria from '../components/Criteria';
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
            name: ''
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
            this.setState({
                category,
                userId: id,
                name: params.name
            })
        }

    }
    backAction = () => {
        this.props.history.go(-1);
    }

    handleCompleteReview = () => {
        const { category, userId, name } = this.state;
        const url = `/detail/${category}/${userId}?name=${name}`;
        this.props.history.push(url);
    }

    handleCompleteChoseQuestion = (questions) => {
        this.setState({
            questions,
        });
    }
    
    renderCriteria = () => {
        const { questions, category, name } = this.state;
        if (!category) return null;
        if (questions.length > 0) return null;
        return (
            <Criteria 
            category={category}
            name={name}
            onChoseQuestions={this.handleCompleteChoseQuestion}/>
        );
    }
    renderReviews = () => {
        const { questions, category, userId, name } = this.state;
        if (questions.length === 0) return null;
        console.log('Selected Questions:', questions);

        return (
            <Reviews 
            category={category}
            userId={userId}
            name={name}
            questions={questions} 
            onCompleteReview={this.handleCompleteReview}
            />
        );
    }
   
    render() {
        
        return (
            <div className="wrapperReview">
                {this.renderCriteria()}
                {this.renderReviews()}
            </div>

        );
    }
}
export default WriteReview;