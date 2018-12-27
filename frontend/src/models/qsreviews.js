import React from 'react';
import PropTypes from 'prop-types';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Rater from 'react-rater';
import TextField from '@material-ui/core/TextField';
import Avatar from '@material-ui/core/Avatar';
import DefaultAvatar from '../assets/avatar.svg';


import 'react-rater/lib/react-rater.css'
import './questions.scss';

const styles = theme => ({
    container: {
      display: 'flex',
      flexWrap: 'wrap',
    },
    textField: {
      marginLeft: theme.spacing.unit,
      marginRight: theme.spacing.unit,
    },
    dense: {
      marginTop: 16,
    },
    menu: {
      width: 200,
    },
  });
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
            comment:'',
            commentLength: 0,
        }
    }

    onChangeComment = (value)=> {
        const { item } = this.props;
        const { rating } = this.state;
        this.setState({
            comment: value,
            commentLength: value.length
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
        const { commentLength } = this.state;
        return (
            <div className="wrapperItemComment">
                <div className="commentLength">Letter count: {commentLength}</div>
                <textarea 
                    className="textField"
                    multiline="true"
                    placeholder="Please give detailed proofs for this rating."
                    onChange={(e)=> this.onChangeComment(e.target.value)} 
                    type='text'/>
            </div>
            );
            
    }
   
    render(){
        const { item, index } = this.props;
        const { rating } = this.state;
        return (
            <div className="wrapperReviewItem">
                <ListItemText className="title">{index+1}. {item.name}</ListItemText>
                <div className="reviewRater">
                    <Rater total={5} rating={rating} onRate={this.handleRate}/>
                </div>
                {this.renderPostComments()}
            </div>
        );
    }
}

const QuestionReviewGrid = (props) => (
    <Card>
        {props.avatar && <div className="wrapperAvatar"><Avatar className="avatar" alt="User" src={props.avatar || DefaultAvatar} /></div>}
        <CardHeader title={`Please rate and give feedback to ${props.name}`} />
        <div className="warning">Criteria could be rated with detailed proofs of at least 250 characters. If you do not want to rate, leave it blank. <br />Re-rating and adding new feedback are applicable after 30 days from the previous input, so please think carefully. <br />Both English and Vietnamese are accepted.</div>
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


