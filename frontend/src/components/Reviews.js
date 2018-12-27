import React, { Component } from 'react';
import { CREATE } from 'react-admin';
import PropTypes from 'prop-types';
import Button from '@material-ui/core/Button';
import { QuestionReviewList }from '../models/qsreviews';
import dataProviderQuestion from '../services/dataProviderQuestion';

class Reviews extends Component {
    static propTypes = {
        category: PropTypes.string.isRequired,
        userId: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        avatar: PropTypes.string,
        questions: PropTypes.array.isRequired,
        onCompleteReview: PropTypes.func
    }
    constructor(props) {
        super(props);
        this.state = {
            error:null,
            ratings: [],
        }
    }
    validate = () =>{
        const { ratings } = this.state;
        if(ratings.length === 0) return false;
        console.log('Ratings:', ratings);
        for (let i = 0; i< ratings.length; i ++){
            const item = ratings[i];
            const { rating, comment } = item;
            console.log('Comment Length:', comment.length);
            if(comment.length === 0 || rating === 0 || comment.length < 250){
                return false;
            }
        }
        
        return true;
    }
    submitNewReview = (params) => {
        const { category, userId } = this.props;
        dataProviderQuestion(CREATE, 'answer', { category:category, id:userId, data: params })
        .then(response => {
            const { status, message } = response.data;
            console.log('submitNewReview', response);

            if (status){
                this.props.onCompleteReview();
            }else {
                this.setState({
                    error:message
                });
            }
        });
    }
    handlePostReview = ()=> {
        const { ratings } = this.state;
        const params = {
            ratings,
        }
        console.log('Params:', params);
        const isValid = this.validate();
        if(isValid){
            this.submitNewReview(params);
        }else {
            this.setState({
                error:'Please fill at least 1 criterion with at least 250 characters.'
            });
        }
        

    }

    onChangeRating = (id, rate, comment) =>{
        const { ratings } = this.state;
        const aRating = {};
        aRating.question_id = id;
        aRating.rating = rate;
        aRating.comment = comment;
        let found = false;
        ratings.forEach(item=> {
            if(item.question_id === id){
                found = true;
                item.rating = rate;
                item.comment = comment;
            }
        });
        if(!found){
            ratings.push(aRating);
        }

        this.setState({
            ratings: ratings.filter(n=>n)
        })
    }

        
   
    
    renderErrorField = () => {
        const { error } = this.state;
        if(!error) return null;
        return (
            <div className="errorText">*{error}</div>
        )
    }
    renderButtonReview = () => {
        return (
            <Button className="buttonComment" onClick={this.handlePostReview} >Post your reviews</Button>
        );
    }
    renderQuestionReviews = () => {
        const { questions, name, avatar } = this.props;

        const questionListProps = {
            questions,
            onChangeRating:this.onChangeRating,
            name: name,
            avatar: avatar
        }
        return (
            <QuestionReviewList {...questionListProps}/>
        );
    }
    render(){
        return (
            <div className="wrapperReview">
            {this.renderQuestionReviews()}
            {this.renderErrorField()}
            {this.renderButtonReview()}
            </div>
        );
    }
}
export default Reviews;

