import React from 'react';
import PropTypes from 'prop-types';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Rater from 'react-rater';
import TextField from '@material-ui/core/TextField';
import 'react-rater/lib/react-rater.css'
import './questions.scss';

class QuestionReviewItem extends React.Component {
    static propTypes = {
        item: PropTypes.object.isRequired,
        index: PropTypes.number.isRequired,
        onChangeRating: PropTypes.func
    }
    constructor(props) {
        super(props);
        this.state = {
            rating: 0,
            comment:''
        }
    }

    onChangeComment = (value)=> {
        const { item } = this.props;
        const { rating } = this.state;
        this.setState({
            comment: value
        })
        this.props.onChangeRating(item.id, rating, value);

    }
    handleRate = ({rating}) => {
        const { item } = this.props;
        const { comment } = this.state;
        this.setState({
            rating,
        })
        this.props.onChangeRating(item.id, rating, comment);

    }

    renderPostComments = () => {
        return (
            <TextField 
            style={{ marginLeft: '20px', marginRight: '20px', width: '500px' }} 
            multiline variant="outlined" 
            placeholder="Please state reasons for rating this by giving detailed proofs."
            onChange={(e)=> this.onChangeComment(e.target.value)} type='text'/>
        );
    }
   
    render(){
        const { item, index } = this.props;
        const { rating } = this.state;
        return (
            <div className="wrapperReviewItem">
            <ListItem className="card">
                <ListItemText className="title">{index+1}. {item.name}</ListItemText>
                <Rater total={5} rating={rating} onRate={this.handleRate}/>
            </ListItem>
            {this.renderPostComments()}
            </div>
        );
    }
}

const QuestionReviewGrid = (props) => (
    <Card>
        <CardHeader title={`Please add rating and comment for ${props.name}`} />
        <div className="warning">***You only can re-rate and add your feedbacks for each criteria after 30 days so please think carefully.</div>
        <List>
            {props.questions.map((item, index)=>
                <QuestionReviewItem key={item.id} index={index} item={item} onChangeRating={props.onChangeRating}/>
            )}
        </List>
    </Card>
);



export const QuestionReviewList = (props) => (
    <QuestionReviewGrid {...props} />
);


