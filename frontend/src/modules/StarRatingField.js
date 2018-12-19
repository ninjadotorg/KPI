import React from 'react';
import Rater from 'react-rater';

const StarRatingField = ({ record = {} }) => <Rater total={5} rating={record.point} interactive={false}/>;
StarRatingField.defaultProps = { label: 'Reviews' };

export default StarRatingField;