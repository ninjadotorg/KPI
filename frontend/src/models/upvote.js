import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Button from '@material-ui/core/Button';
import Icon from '@material-ui/core/Icon';
import UpIcon from '@material-ui/icons/ThumbUp';
class UpVote extends Component {

    static propTypes = {
        total: PropTypes.number,
    }

    static defaultProp = {
        total: 10
    }

    handleLike = () => {

    }

    renderLikeButton = () => {
        const { total } = this.props;
        return (
            <Button className="buttonLike" onClick={this.handleLike}>
                <UpIcon  />
                10
            </Button>
        );
    }
    render(){
        return (
            <div className="wrapperLike">
            {this.renderLikeButton()}
            </div>
        );
    }
}
export default UpVote;