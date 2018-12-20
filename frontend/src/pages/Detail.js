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

import Comments from '../models/comments';
import dataProvider from '../services/dataProvider';
import { getQueryString } from '../utils/utils';

import './Detail.scss';
import './StarRate.scss';

class Detail extends Component {
    constructor(props) {
        super(props);
        this.state = {
            ratings:[],
            category: '',
            id: -1,
            name: ''
        }
    }

    componentDidMount() {
        const query = getQueryString();
        console.log('Query:', query);
        if (query.length === 4){
            const id = query[query.length-1].split('?')[0];
            const queryId = query[query.length-1].slice(1).replace('?','');
            const params = qs.parse(queryId);
            const category = query[query.length-2];
            this.setState({
                category,
                id,
                name: params.name
            })
            this.getDetailData(category, id);
        }
        
    }


    getDetailData = (category, id)=> {
        dataProvider(GET_ONE, category, { id:id })
        .then(response => {
            console.log('Detail Response:', response.data);
            const { ratings } = response.data;
            this.setState({
                ratings,
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
            <div className="wrapperItem" key={id}>
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
        const { name } = this.state;
        return (
        <Card>
            <CardHeader title={`Reviews of ${name}`} />
            <List>
                {ratings.map((item, index)=>this.renderRateItem(item, index))}
            </List>
        </Card>

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