import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import { GET_ONE } from 'react-admin';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Rater from 'react-rater';
import Button from '@material-ui/core/Button';
import qs from 'querystring';
import Avatar from '@material-ui/core/Avatar';
import DefaultAvatar from '../assets/avatar.svg';
import EditIcon from '@material-ui/icons/Edit';
import classNames from 'classnames';

import Comments from '../models/comments';
import dataProvider from '../services/dataProvider';
import { getQueryString } from '../utils/utils';

import './Detail.scss';
import './StarRate.scss';

const styles = theme => ({
    leftIcon: {
      marginRight: theme.spacing.unit,
    },
    iconSmall: {
      fontSize: 20,
    },
  });

class Detail extends Component {
    constructor(props) {
        super(props);
        this.state = {
            ratings:[],
            category: '',
            id: -1,
            name: '',
            avatar: '',
            reviewCount: 0
        }
    }

    componentDidMount() {
        const query = getQueryString();
        if (query.length === 4){
            const lastQuery = query[query.length-1].split('?');
            const id = lastQuery[0];
            const queryId = lastQuery[1];
            const params = qs.parse(queryId);
            const category = query[query.length-2];
            this.setState({
                category,
                id,
                name: params.name,
                avatar: params.avatar

            })
            this.getDetailData(category, id);
        }
        
    }


    getDetailData = (category, id)=> {
        dataProvider(GET_ONE, category, { id:id })
        .then(response => {
            console.log('Detail Response:', response.data);
            const { ratings, reviewed_object: reviewedObject } = response.data;
            this.setState({
                ratings,
                reviewCount: reviewedObject.comment_count
            })
        });
    }
    goToReviewPage=()=>{
        const { category, id } = this.state;
        this.props.history.push(`/review/${category}/${id}`);
    }
    renderReviewButton=()=>{
        return(
            <Button className="buttonDetail" onClick={()=>this.goToReviewPage()}>Post a review</Button>
        );
    }

    renderSeeMore = (questionId) => {
        const { id, category } = this.state;
        const url = `/question/${category}/${id}/${questionId}`;
        return (
            <Link className="seeMore" to={url}>
            See more comments
            </Link>
        );
    }

    
    renderRateItem=(item, index)=>{
        const { name, average, id, comments }  = item;
        return (
            <div className="wrapperDetailItem" key={id}>
                <ListItem>
                    <ListItemText>{index+1}. {name}</ListItemText>
                    <div className="rater">
                        <Rater total={5} rating={average} interactive={false}/>
                        <div className="raterNumber">({average})</div>
                    </div>
                </ListItem>
                <Comments comments={comments} />
                {this.renderSeeMore(id)}
            </div>
        );
    }
    renderRatingList = (ratings)=>{
        const { name, avatar, reviewCount } = this.state;
        let reviewText = reviewCount > 1 ? 'reviews' : 'review';
        return (
        <Card>
            {avatar && 
                <div className="wrapperAvatar">
                    <Avatar alt="User" src={avatar || DefaultAvatar} className="avatar" />
                </div>
            }
            {this.renderEditButton()}
            <CardHeader title={`Reviews of ${name} (${reviewCount} ${reviewText})`} />
            <List>
                {ratings.map((item, index)=>this.renderRateItem(item, index))}
            </List>
        </Card>

        );        
    }
    handleClickFeeback=()=> {
        const { category, id, avatar, name } = this.state;
        const encodeAvatar = encodeURIComponent(avatar || '');
        this.props.history.push(`/review/${category}/${id}?name=${name}&avatar=${encodeAvatar || ''}`);
    }
    renderEditButton=()=>{
        return (
            <div className="wrapperButtonFeedback">
            <Button className="buttonFeedback" onClick={this.handleClickFeeback}>
                <EditIcon className={classNames(styles.leftIcon, styles.iconSmall)} />
            Feedback
            </Button>
            </div>
        );
    }
    render() {
        const { ratings } = this.state;
        return (
            <div className="wrapperDetail">
                {this.renderRatingList(ratings)}
                {/*this.renderCommentList(comments)*/}
                {/*this.renderReviewButton()*/}
            </div>
        );
    }
}
export default Detail;