import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { QuestionList } from '../models/questions';
import dataProviderQuestion from '../services/dataProviderQuestion';
import { GET_LIST } from 'react-admin';
import Card from '@material-ui/core/Card';
import Button from '@material-ui/core/Button';

class Criteria extends Component {
    static propTypes = {
        category: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        avatar: PropTypes.string,
        onChoseQuestions: PropTypes.func,
    }
    constructor(props) {
        super(props);
        this.state = {
            questions: [],
            checkQuestions: []

        }
    }
    componentDidMount() {
        const { category } = this.props;
        if(category){
            this.getQuestionList(category);
        }

    }
    handleNext = () => {
        const { checkQuestions } = this.state;
        const selectedQuestions = checkQuestions.filter(item=>item.checked===true);
        this.props.onChoseQuestions(selectedQuestions);
    }
    handleCheckQuestion = (checkedItem) => {
        const { checkQuestions } = this.state;
        checkQuestions.forEach(questionItem => {
            if (questionItem.id === checkedItem.id){
                questionItem.checked = checkedItem.checked;
            }
        });
        this.setState({
            checkQuestions: checkQuestions
        })

    }
    getQuestionList = (category)=> {
        dataProviderQuestion(GET_LIST, 'question', { category })
        .then(response => {
            this.setState({
                questions: response.data,
                checkQuestions: response.data
            })
        });
    }
    renderQuestionList = () => {
        const { questions } = this.state;
        const { name, avatar } = this.props;
        const questionListProps = {
            questions,
            onChangeCheckQuestion: this.handleCheckQuestion,
            name:name,
            avatar: avatar
        }

        return (
            <Card>
                <QuestionList {...questionListProps}/>
            </Card>

        );
    }
    renderButtonNext = () => {
        return (
            <Button className="buttonComment" onClick={this.handleNext} >Next</Button>
        );
    }
    render() {
        return (
            <div className="wrapperCriteria">
                {this.renderQuestionList()}
                {this.renderButtonNext()}
            </div>

        );
    }
}
export default Criteria;
