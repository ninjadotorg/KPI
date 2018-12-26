import React from 'react';
import PropTypes from 'prop-types';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Checkbox from '../modules/Checkbox';
import './questions.scss';


class QuestionItem extends React.Component {
    static propTypes = {
        item: PropTypes.object.isRequired,
        index: PropTypes.number.isRequired,
        onChangeRating: PropTypes.func,
        onChangeCheckQuestion: PropTypes.func
    }
    constructor(props) {
        super(props);
        this.state = {
            checked: false
        }
    }

    onChangeCheckBox = ()=>{
        const {checked} = this.state;
        const { item } = this.props;
        this.setState({
            checked: !checked
        })
        const checkItem = item;
        checkItem.checked = !checked;
        this.props.onChangeCheckQuestion(checkItem);
    }
   
    render(){
        const { item, index } = this.props;
        const { checked } = this.state;
        return (
            <ListItem className="card">
                <Checkbox checked={checked}
                name={item.name}
                onChange={this.onChangeCheckBox}/>
                <ListItemText className="title">{index + 1}. {item.name}</ListItemText>
            </ListItem>
        );
    }
}

const QuestionGrid = (props) => (
    <Card className="card">
        <CardHeader title={`Please select criteria for assessing ${props.name}`} />
        <div className="warning">When assessing a criterion, you must give detailed proofs. So think carefully to select criteria that you can give clear assessments.</div>
        <List>
            {props.questions.map((item, index)=>
                <QuestionItem 
                key={item.id} 
                index={index}
                item={item} 
                onChangeCheckQuestion={props.onChangeCheckQuestion}/>
            )}
        </List>
    </Card>
);



export const QuestionList = (props) => (
    <QuestionGrid {...props} />
);


