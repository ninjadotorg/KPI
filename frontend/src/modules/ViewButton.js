import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Button from '@material-ui/core/Button';

class ViewButton extends Component {

    static propTypes = {
        record: PropTypes.object,
    }
    handleClickButton = () => {
        const { basePath, record } = this.props;
        const encodeAvatar = encodeURIComponent(record.avatar || '');
        this.props.history.push(`/detail${basePath}/${record.id}?name=${record.name}&avatar=${encodeAvatar}`);
    }
    componentDidMount(){
    }
    render() {
        return (
            <Button className="buttonFeedback" onClick={this.handleClickButton}>View</Button>
        );
    }
}
export default ViewButton;