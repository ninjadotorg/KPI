import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Button from '@material-ui/core/Button';
import DownIcon from '@material-ui/icons/ThumbDown';
class DownVote extends Component {

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
                <DownIcon  />
                <span>20</span>
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
export default DownVote;