import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Button from '@material-ui/core/Button';
import './FeedbackButton.scss';

class FeebackButton extends Component {

    static propTypes = {
        record: PropTypes.object,
    }
    handleClickFeeback = () => {
        const { basePath, record } = this.props;
        this.props.history.push(`/review${basePath}/${record.id}?name=${record.name}`);
    }
    componentDidMount(){
    }
    render() {
        return (
            <Button className="buttonFeedback" onClick={this.handleClickFeeback}>Give Feedback</Button>
        );
    }
}
export default FeebackButton;