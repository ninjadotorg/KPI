import React from 'react';
import { Route } from 'react-router-dom';
import WriteReview from './pages/WriteReview';
import Detail from './pages/Detail';
import QuestionDetail from './pages/QuestionDetail';
export default [
    <Route path="/review" component={WriteReview} />,
    <Route path="/detail" component={Detail} />,
    <Route path="/question" component={QuestionDetail} />,

];