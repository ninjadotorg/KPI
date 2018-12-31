import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Button from '@material-ui/core/Button';
import EditIcon from '@material-ui/icons/Edit';
import classNames from 'classnames';

import './FeedbackButton.scss';

const styles = theme => ({
    leftIcon: {
      marginRight: theme.spacing.unit,
    },
    iconSmall: {
      fontSize: 20,
    },
  });
class FeebackButton extends Component {

    static propTypes = {
        record: PropTypes.object,
    }
    handleClickFeeback = () => {
        const { basePath, record } = this.props;
        const encodeAvatar = encodeURIComponent(record.avatar || '');
        this.props.history.push(`/review${basePath}/${record.id}?name=${record.name}&avatar=${encodeAvatar || ''}`);
    }
    componentDidMount(){
    }
    render() {
        return (
            <Button className="buttonFeedback" onClick={this.handleClickFeeback}>
                <EditIcon className={classNames(styles.leftIcon, styles.iconSmall)} />
                Feedback
            </Button>
        );
    }
}
export default FeebackButton;